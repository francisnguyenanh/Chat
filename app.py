from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import Config
from models import db, User, Message, File
import os
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def cleanup_old_data(user):
    """Clean up old messages and files (called on admin's first login of the day)"""
    if not user.is_admin:
        return
    
    today = datetime.utcnow().date()
    last_login_date = user.last_login.date() if user.last_login else None
    
    # Only run cleanup once per day
    if last_login_date == today:
        return
    
    # Delete messages older than 30 days
    message_cutoff = datetime.utcnow() - timedelta(days=app.config['MESSAGE_RETENTION_DAYS'])
    old_messages = Message.query.filter(Message.timestamp < message_cutoff).all()
    for msg in old_messages:
        db.session.delete(msg)
    
    # Delete files older than 7 days
    file_cutoff = datetime.utcnow() - timedelta(days=app.config['FILE_RETENTION_DAYS'])
    old_files = File.query.filter(File.upload_time < file_cutoff).all()
    for file in old_files:
        # Delete physical file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        # Delete database record
        db.session.delete(file)
    
    db.session.commit()
    flash(f'Đã dọn dẹp {len(old_messages)} tin nhắn cũ và {len(old_files)} file cũ.', 'info')


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            # Run cleanup on admin's first login of the day
            cleanup_old_data(user)
            
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redirect based on role
            if user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('chat'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất thành công.', 'success')
    return redirect(url_for('login'))


@app.route('/chat')
@login_required
def chat():
    # Get recent messages (last 100)
    messages = Message.query.order_by(Message.timestamp.desc()).limit(100).all()
    messages.reverse()
    
    # Get recent files
    files = File.query.order_by(File.upload_time.desc()).limit(50).all()
    files.reverse()
    
    return render_template('chat.html', messages=messages, files=files, user=current_user)


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập trang này.', 'danger')
        return redirect(url_for('chat'))
    
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin.html', users=users)


@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'success': False, 'message': 'Không thể sửa tài khoản admin'}), 403
    
    data = request.json
    new_username = data.get('username')
    new_password = data.get('password')
    
    # Check if username already exists (except current user)
    if new_username and new_username != user.username:
        existing = User.query.filter_by(username=new_username).first()
        if existing:
            return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại'}), 400
        user.username = new_username
    
    if new_password:
        user.set_password(new_password)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Cập nhật thành công'})


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Socket.IO events
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        emit('user_connected', {
            'username': current_user.username,
            'user_id': current_user.id
        }, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        emit('user_disconnected', {
            'username': current_user.username,
            'user_id': current_user.id
        }, broadcast=True)


@socketio.on('send_message')
def handle_message(data):
    if not current_user.is_authenticated:
        return
    
    content = data.get('message', '').strip()
    if not content:
        return
    
    # Save message to database
    message = Message(user_id=current_user.id, content=content)
    db.session.add(message)
    db.session.commit()
    
    # Broadcast message to all users
    emit('new_message', message.to_dict(), broadcast=True)


@socketio.on('upload_file')
def handle_file_upload(data):
    if not current_user.is_authenticated:
        return {'success': False, 'message': 'Not authenticated'}
    
    try:
        file_data = data.get('file')
        filename = data.get('filename')
        file_type = data.get('file_type', 'file')
        
        if not file_data or not filename:
            return {'success': False, 'message': 'Missing file data'}
        
        # Generate unique filename
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        import base64
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(file_data.split(',')[1]))
        
        file_size = os.path.getsize(file_path)
        
        # Check file size
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            os.remove(file_path)
            return {'success': False, 'message': 'File quá lớn (tối đa 5MB)'}
        
        # Save to database
        file_record = File(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=filename,
            file_type=file_type,
            file_size=file_size
        )
        db.session.add(file_record)
        db.session.commit()
        
        # Broadcast to all users
        emit('new_file', file_record.to_dict(), broadcast=True)
        
        return {'success': True, 'file': file_record.to_dict()}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}


@socketio.on('typing')
def handle_typing(data):
    if current_user.is_authenticated:
        emit('user_typing', {
            'username': current_user.username,
            'user_id': current_user.id,
            'is_typing': data.get('is_typing', False)
        }, broadcast=True, include_self=False)


@socketio.on('delete_message')
def handle_delete_message(data):
    if not current_user.is_authenticated:
        return {'success': False, 'message': 'Not authenticated'}
    
    message_id = data.get('message_id')
    message = Message.query.get(message_id)
    
    if not message:
        return {'success': False, 'message': 'Message not found'}
    
    # Only author or admin can delete
    if message.user_id != current_user.id and not current_user.is_admin:
        return {'success': False, 'message': 'Permission denied'}
    
    db.session.delete(message)
    db.session.commit()
    
    emit('message_deleted', {'message_id': message_id}, broadcast=True)
    return {'success': True}


@socketio.on('edit_message')
def handle_edit_message(data):
    if not current_user.is_authenticated:
        return {'success': False, 'message': 'Not authenticated'}
    
    message_id = data.get('message_id')
    new_content = data.get('content', '').strip()
    
    if not new_content:
        return {'success': False, 'message': 'Content cannot be empty'}
    
    message = Message.query.get(message_id)
    
    if not message:
        return {'success': False, 'message': 'Message not found'}
    
    # Only author can edit
    if message.user_id != current_user.id:
        return {'success': False, 'message': 'Permission denied'}
    
    message.content = new_content
    message.edited_at = datetime.utcnow()
    db.session.commit()
    
    emit('message_edited', message.to_dict(), broadcast=True)
    return {'success': True}


@socketio.on('delete_file')
def handle_delete_file(data):
    if not current_user.is_authenticated:
        return {'success': False, 'message': 'Not authenticated'}
    
    file_id = data.get('file_id')
    file_record = File.query.get(file_id)
    
    if not file_record:
        return {'success': False, 'message': 'File not found'}
    
    # Only author or admin can delete
    if file_record.user_id != current_user.id and not current_user.is_admin:
        return {'success': False, 'message': 'Permission denied'}
    
    # Delete physical file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(file_record)
    db.session.commit()
    
    emit('file_deleted', {'file_id': file_id}, broadcast=True)
    return {'success': True}


@socketio.on('add_reaction')
def handle_add_reaction(data):
    if not current_user.is_authenticated:
        return {'success': False, 'message': 'Not authenticated'}
    
    message_id = data.get('message_id')
    emoji = data.get('emoji')
    
    message = Message.query.get(message_id)
    if not message:
        return {'success': False, 'message': 'Message not found'}
    
    # Parse reactions JSON
    import json
    try:
        reactions = json.loads(message.reactions) if message.reactions else {}
    except:
        reactions = {}
    
    # Add or remove user's reaction
    if emoji not in reactions:
        reactions[emoji] = []
    
    user_id_str = str(current_user.id)
    if user_id_str in reactions[emoji]:
        reactions[emoji].remove(user_id_str)
        if not reactions[emoji]:
            del reactions[emoji]
    else:
        reactions[emoji].append(user_id_str)
    
    message.reactions = json.dumps(reactions)
    db.session.commit()
    
    emit('reaction_updated', {
        'message_id': message_id,
        'reactions': reactions
    }, broadcast=True)
    
    return {'success': True}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
