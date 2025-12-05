# Developer Guide - Chat App

## Kiến trúc ứng dụng

### Backend (Flask)

#### app.py
- Main application file
- Routes: login, logout, chat, admin
- Socket.IO events: connect, disconnect, send_message, upload_file, typing
- Cleanup functions: Tự động xóa tin nhắn và file cũ

#### models.py
- **User**: Quản lý người dùng (admin/user), authentication
- **Message**: Lưu trữ tin nhắn chat
- **File**: Quản lý file upload (images, archives)

#### config.py
- Cấu hình ứng dụng
- Database URI
- Upload folder và file size limits
- Retention policies (30 days messages, 7 days files)

### Frontend

#### Templates (Jinja2)
- **login.html**: Trang đăng nhập
- **chat.html**: Giao diện chat chính
- **admin.html**: Trang quản lý user (admin only)

#### JavaScript
- **chat.js**: Socket.IO client, real-time messaging, file upload, notifications
- **admin.js**: Admin panel để sửa user info

#### CSS
- **style.css**: Custom styling, Google Chat-like UI, responsive design

## Database Schema

### User Table
```sql
- id: Integer, Primary Key
- username: String(80), Unique
- password_hash: String(200)
- is_admin: Boolean
- last_login: DateTime
- created_at: DateTime
```

### Message Table
```sql
- id: Integer, Primary Key
- user_id: Integer, Foreign Key -> User.id
- content: Text
- timestamp: DateTime (indexed)
```

### File Table
```sql
- id: Integer, Primary Key
- user_id: Integer, Foreign Key -> User.id
- filename: String(255) - unique generated name
- original_filename: String(255) - user's filename
- file_type: String(50) - 'image' or 'file'
- file_size: Integer
- upload_time: DateTime (indexed)
```

## Socket.IO Events

### Client -> Server
- `send_message`: Gửi tin nhắn text
- `upload_file`: Upload file/image
- `typing`: Thông báo đang nhập

### Server -> Client
- `new_message`: Broadcast tin nhắn mới
- `new_file`: Broadcast file mới
- `user_typing`: Thông báo user đang nhập
- `user_connected`: User kết nối
- `user_disconnected`: User ngắt kết nối

## API Endpoints

### Authentication
- `GET /`: Redirect to login or chat
- `GET /login`: Hiển thị trang login
- `POST /login`: Xử lý đăng nhập
- `GET /logout`: Đăng xuất

### Chat
- `GET /chat`: Trang chat (requires login)
- `GET /uploads/<filename>`: Serve uploaded files

### Admin
- `GET /admin`: Trang quản lý (admin only)
- `POST /admin/update_user/<user_id>`: Cập nhật user info (admin only)

## Tính năng Real-time

### Message Broadcasting
```javascript
// Client gửi
socket.emit('send_message', { message: 'Hello' });

// Server broadcast
emit('new_message', messageObject, broadcast=True);

// Clients nhận
socket.on('new_message', (message) => { ... });
```

### File Upload
```javascript
// Client upload (base64)
socket.emit('upload_file', {
    file: base64Data,
    filename: 'image.jpg',
    file_type: 'image'
});

// Server lưu file và broadcast
emit('new_file', fileObject, broadcast=True);
```

### Typing Indicator
```javascript
// Client typing
socket.emit('typing', { is_typing: true });

// Server broadcast (exclude sender)
emit('user_typing', data, broadcast=True, include_self=False);
```

## Cleanup Logic

### Automatic Cleanup (Admin First Login of Day)

```python
def cleanup_old_data(user):
    if not user.is_admin:
        return
    
    # Check if already ran today
    today = datetime.utcnow().date()
    if user.last_login.date() == today:
        return
    
    # Delete old messages (>30 days)
    message_cutoff = datetime.utcnow() - timedelta(days=30)
    old_messages = Message.query.filter(Message.timestamp < message_cutoff).all()
    
    # Delete old files (>7 days)
    file_cutoff = datetime.utcnow() - timedelta(days=7)
    old_files = File.query.filter(File.upload_time < file_cutoff).all()
```

## Security

### Password Hashing
- Sử dụng Werkzeug's `generate_password_hash` và `check_password_hash`
- SHA-256 with salt

### Session Management
- Flask-Login với secure session cookies
- `@login_required` decorator

### File Upload Security
- Secure filename với `secure_filename()`
- Validate file type và size
- UUID-based filename để tránh conflicts

### XSS Prevention
- HTML escaping trong chat messages
- Jinja2 auto-escaping

## Notifications

### New Message Notification
```javascript
// Khi tab không active và có tin nhắn mới
if (!isPageVisible && message.user_id !== CURRENT_USER_ID) {
    pageTitle.textContent = '🔴 Tin nhắn mới - Chat App';
}

// Clear khi tab active
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        pageTitle.textContent = 'Chat App';
    }
});
```

## Responsive Design

### Breakpoints
- Desktop: > 768px
- Mobile: ≤ 768px

### Mobile Optimizations
- Touch-friendly buttons
- Responsive message bubbles (80% width)
- Collapsible header on scroll
- Virtual keyboard friendly

## Font Support

### Vietnamese
- Primary: 'Segoe UI'
- Fallback: Tahoma, Geneva, Verdana

### Japanese
- Primary: 'MS PGothic', 'ヒラギノ角ゴ Pro'
- Fallback: 'Yu Gothic', 'Meiryo'

## Testing

### Manual Testing
```bash
# Test database
python test_setup.py

# Initialize database
python init_db.py

# Run server
python app.py
```

### Test Scenarios
1. Login với admin và user
2. Chat giữa nhiều user (mở nhiều tab)
3. Upload image và file
4. Admin sửa user info
5. Typing indicator
6. New message notification
7. Auto cleanup (test bằng cách sửa ngày trong database)

## Deployment

### Development
```bash
python app.py
# Debug=True, host=0.0.0.0, port=5000
```

### Production
1. Set `SECRET_KEY` trong environment
2. Set `debug=False`
3. Use production WSGI server (Gunicorn + Eventlet)
4. Use reverse proxy (Nginx)
5. Enable HTTPS
6. Regular database backups

### Environment Variables
```bash
export SECRET_KEY="your-secret-key-here"
export FLASK_ENV="production"
```

## Performance Tips

### Database
- Index trên `timestamp` và `upload_time` để tăng tốc cleanup queries
- Regular VACUUM cho SQLite

### File Storage
- Tối ưu: Chuyển sang cloud storage (S3, Azure Blob) cho production
- Implement CDN cho file serving

### Socket.IO
- Eventlet async mode cho better performance
- Redis adapter nếu scale lên nhiều workers

## Troubleshooting

### Common Issues

**Port already in use**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Database locked**
```bash
# Xóa và tạo lại
del chat.db
python init_db.py
```

**Socket.IO connection issues**
- Check firewall
- Verify eventlet installed
- Check browser console for errors

## Future Enhancements

### Planned Features
- [ ] Private messaging
- [ ] User avatars
- [ ] Message reactions
- [ ] Voice messages
- [ ] Video chat
- [ ] Message search
- [ ] Export chat history
- [ ] User status (online/offline)
- [ ] Read receipts
- [ ] Message editing/deletion

### Scalability Improvements
- [ ] PostgreSQL/MySQL instead of SQLite
- [ ] Redis for session storage
- [ ] Celery for background tasks
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Load balancing
- [ ] CDN for static files

## Contributing

### Code Style
- PEP 8 for Python
- 4 spaces indentation
- Meaningful variable names
- Comments for complex logic

### Git Workflow
1. Create feature branch
2. Make changes
3. Test thoroughly
4. Commit with clear messages
5. Create pull request

---

**Happy Coding!** 💻
