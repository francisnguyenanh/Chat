from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import Config
from models import db, User, Message, File
import os
import uuid
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add JSON filter for Jinja2
@app.template_filter('from_json')
def from_json_filter(value):
    if not value:
        return {}
    try:
        return json.loads(value)
    except:
        return {}

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
    return render_template('chat.html', user=current_user)


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


# ============ HTMX API ENDPOINTS ============

@app.route('/api/messages')
@login_required
def get_messages():
    """Get all messages and files (for polling)"""
    last_check = request.args.get('last_check', type=float, default=0)
    
    # Debug logging
    print(f"[DEBUG] User {current_user.username} polling with last_check={last_check}")
    
    if last_check > 0:
        # Convert JavaScript timestamp (milliseconds since epoch) to datetime
        # JavaScript uses milliseconds, Python uses seconds
        # Also, we need to use UTC time to match database
        last_check_dt = datetime.utcfromtimestamp(last_check / 1000.0)  # Chia cho 1000!
    else:
        last_check_dt = datetime.min
    
    # Get new messages
    new_messages = Message.query.filter(Message.timestamp > last_check_dt).order_by(Message.timestamp.asc()).all()
    
    # Get new files
    new_files = File.query.filter(File.upload_time > last_check_dt).order_by(File.upload_time.asc()).all()
    
    # Check for edited messages
    edited_messages = Message.query.filter(Message.edited_at > last_check_dt).all() if last_check > 0 else []
    
    # Debug logging
    print(f"[DEBUG] Found {len(new_messages)} new messages, {len(new_files)} new files, {len(edited_messages)} edited")
    if new_messages:
        print(f"[DEBUG] New message timestamps: {[m.timestamp for m in new_messages]}")
    
    # If nothing changed, return empty (HTMX will not update DOM)
    if not new_messages and not new_files and not edited_messages:
        return '', 204
    
    return render_template('partials/messages.html', 
                         messages=new_messages, 
                         files=new_files,
                         current_user=current_user)


@app.route('/api/messages/all')
@login_required
def get_all_messages():
    """Get all messages and files (initial load)"""
    messages = Message.query.order_by(Message.timestamp.desc()).limit(100).all()
    messages.reverse()
    
    files = File.query.order_by(File.upload_time.desc()).limit(50).all()
    files.reverse()
    
    return render_template('partials/messages.html', 
                         messages=messages, 
                         files=files,
                         current_user=current_user)


@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a new message"""
    content = request.form.get('message', '').strip()
    if not content:
        return '', 204
    
    # Save message to database
    message = Message(user_id=current_user.id, content=content)
    db.session.add(message)
    db.session.commit()
    
    # Return the new message HTML
    return render_template('partials/message_item.html', 
                         message=message,
                         current_user=current_user)


@app.route('/api/edit_message/<int:message_id>', methods=['POST'])
@login_required
def edit_message(message_id):
    """Edit a message"""
    message = Message.query.get_or_404(message_id)
    
    # Only author can edit
    if message.user_id != current_user.id:
        return 'Permission denied', 403
    
    new_content = request.form.get('content', '').strip()
    if not new_content:
        return 'Content cannot be empty', 400
    
    message.content = new_content
    message.edited_at = datetime.utcnow()
    db.session.commit()
    
    # Return updated message HTML
    return render_template('partials/message_item.html', 
                         message=message,
                         current_user=current_user)


@app.route('/api/delete_message/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Delete a message"""
    message = Message.query.get_or_404(message_id)
    
    # Only author or admin can delete
    if message.user_id != current_user.id and not current_user.is_admin:
        return 'Permission denied', 403
    
    db.session.delete(message)
    db.session.commit()
    
    return '', 200


@app.route('/api/upload_file', methods=['POST'])
@login_required
def upload_file():
    """Upload one or multiple files"""
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return 'No file', 400

    allowed_images = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    allowed_archives = {'.zip', '.rar', '.7z'}
    file_items = []

    for file in files:
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext in allowed_images:
            file_type = 'image'
        elif ext in allowed_archives:
            file_type = 'file'
        else:
            continue  # skip unsupported

        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            os.remove(file_path)
            continue  # skip too large

        file_record = File(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=filename,
            file_type=file_type,
            file_size=file_size
        )
        db.session.add(file_record)
        file_items.append(file_record)

    db.session.commit()

    # Trả về HTML của tất cả file vừa upload
    rendered = ""
    for file_record in file_items:
        rendered += render_template('partials/file_item.html', file=file_record, current_user=current_user)
    return rendered, 200


@app.route('/api/delete_file/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """Delete a file"""
    file_record = File.query.get_or_404(file_id)
    
    # Only author or admin can delete
    if file_record.user_id != current_user.id and not current_user.is_admin:
        return 'Permission denied', 403
    
    # Delete physical file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(file_record)
    db.session.commit()
    
    return '', 200


@app.route('/api/add_reaction/<int:message_id>', methods=['POST'])
@login_required
def add_reaction(message_id):
    """Add or remove a reaction"""
    message = Message.query.get_or_404(message_id)
    emoji = request.form.get('emoji')
    
    if not emoji:
        return 'No emoji', 400
    
    # Parse reactions JSON
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
    
    # Return updated reactions HTML
    return render_template('partials/reactions.html', 
                         message=message,
                         current_user=current_user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)

