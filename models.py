from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('Message', backref='author', lazy=True, cascade='all, delete-orphan')
    files = db.relationship('File', backref='uploader', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    edited_at = db.Column(db.DateTime, nullable=True)
    reactions = db.Column(db.Text, default='{}')  # JSON string for reactions

    # ================== THÊM 3 CỘT CHO QUOTE / REPLY ==================
    quoted_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    quoted_author_username = db.Column(db.String(80), nullable=True)   # Lưu tên để hiển thị nếu user bị xóa
    quoted_message_content = db.Column(db.Text, nullable=True)         # Nội dung gốc (khi tin nhắn bị xóa)
    # ===================================================================

    # Optional: nếu bạn muốn hiển thị các reply của tin nhắn này
    # replies = db.relationship('Message', backref=db.backref('quoted_message', remote_side=[id]), lazy=True)

    def get_reactions_dict(self):
        try:
            return json.loads(self.reactions) if self.reactions else {}
        except:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.author.username if self.author else self.quoted_author_username,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'reactions': self.get_reactions_dict(),
            'is_admin': self.author.is_admin if self.author else False,
            # Thông tin quote
            'quoted_message_id': self.quoted_message_id,
            'quoted_author_username': self.quoted_author_username,
            'quoted_message_content': self.quoted_message_content,
        }
    
    def __repr__(self):
        return f'<Message {self.id} by {self.author.username if self.author else "Unknown"}>'


class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'image' or 'file'
    file_size = db.Column(db.Integer, nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.uploader.username if self.uploader else "Unknown",
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_time': self.upload_time.isoformat(),
            'is_admin': self.uploader.is_admin if self.uploader else False
        }

    def __repr__(self):
        return f'<File {self.original_filename}>'