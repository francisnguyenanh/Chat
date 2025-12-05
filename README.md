# Chat App - Ứng dụng Chat Real-time

Ứng dụng chat đa người dùng được xây dựng bằng Flask, Socket.IO, SQLite và Bootstrap.

## Tính năng

✅ **Quản lý người dùng**
- 1 Admin và 9 User
- Admin có quyền thay đổi username và password của users
- Phân quyền tự động dựa trên login

✅ **Quản lý tin nhắn**
- Lưu trữ tin nhắn trong 30 ngày
- Tự động xóa tin nhắn quá hạn khi admin đăng nhập lần đầu trong ngày
- Chat real-time với Socket.IO

✅ **Giao diện**
- Thiết kế giống Google Chat
- Tin nhắn của mình hiển thị bên phải, tin nhắn người khác bên trái
- Responsive, hỗ trợ mobile

✅ **Upload file**
- Cho phép gửi hình ảnh (tất cả định dạng: jpg, png, gif, bmp, webp, svg)
- Cho phép gửi file nén (zip, rar, 7z) < 5MB
- Tự động xóa file sau 7 ngày

✅ **Thông báo**
- Hiển thị chấm đỏ trên tiêu đề tab khi có tin nhắn mới (giống Google Chat)
- Typing indicator (hiển thị khi người khác đang nhập)

✅ **Hỗ trợ đa ngôn ngữ**
- Font hỗ trợ tiếng Việt
- Font hỗ trợ tiếng Nhật

## Cài đặt

### 1. Clone repository hoặc tải source code

### 2. Cài đặt môi trường ảo (khuyến nghị)

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Cài đặt các thư viện cần thiết

```powershell
pip install -r requirements.txt
```

### 4. Khởi tạo database

```powershell
python init_db.py
```

Lệnh này sẽ tạo:
- 1 tài khoản Admin: `admin` / `admin123`
- 9 tài khoản User: `user1` / `password1`, `user2` / `password2`, ..., `user9` / `password9`

### 5. Chạy ứng dụng

```powershell
python app.py
```

Ứng dụng sẽ chạy tại: http://localhost:5000

## Sử dụng

### Đăng nhập

1. Truy cập http://localhost:5000
2. Đăng nhập với một trong các tài khoản:
   - Admin: `admin` / `admin123`
   - User: `user1` / `password1` (hoặc user2, user3, ..., user9)

### Tính năng Chat

- **Gửi tin nhắn**: Nhập văn bản và nhấn Enter hoặc nút "Gửi"
- **Gửi hình ảnh**: Click icon đính kèm hoặc paste (Ctrl+V) hình ảnh
- **Gửi file nén**: Click icon đính kèm và chọn file .zip, .rar, hoặc .7z
- **Xem file**: Click vào hình ảnh hoặc file để xem/tải về

### Tính năng Admin

1. Đăng nhập với tài khoản admin
2. Click nút "Quản lý" trên thanh header
3. Sửa thông tin user:
   - Click nút "Sửa"
   - Thay đổi username
   - Nhập mật khẩu mới (để trống nếu không đổi)
   - Click "Lưu"

### Tự động dọn dẹp dữ liệu

- **Tin nhắn**: Tự động xóa tin nhắn > 30 ngày khi admin đăng nhập lần đầu trong ngày
- **File**: Tự động xóa file > 7 ngày khi admin đăng nhập lần đầu trong ngày

## Cấu trúc thư mục

```
Chat/
├── app.py                 # Ứng dụng Flask chính
├── models.py              # Database models
├── config.py              # Cấu hình
├── init_db.py             # Script khởi tạo database
├── requirements.txt       # Dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Custom CSS
│   ├── js/
│   │   ├── chat.js        # Socket.IO chat logic
│   │   └── admin.js       # Admin panel logic
│   └── uploads/           # Thư mục lưu file upload
├── templates/
│   ├── login.html         # Trang đăng nhập
│   ├── chat.html          # Trang chat
│   └── admin.html         # Trang quản lý
└── chat.db                # SQLite database (tự động tạo)
```

## Cấu hình

Chỉnh sửa file `config.py` để thay đổi:

- `SECRET_KEY`: Khóa bí mật cho session
- `MESSAGE_RETENTION_DAYS`: Số ngày lưu trữ tin nhắn (mặc định: 30)
- `FILE_RETENTION_DAYS`: Số ngày lưu trữ file (mặc định: 7)
- `MAX_CONTENT_LENGTH`: Kích thước file tối đa (mặc định: 5MB)

## Lưu ý

- Ứng dụng sử dụng SQLite nên phù hợp cho số lượng người dùng nhỏ (10 người)
- File upload được lưu trong thư mục `static/uploads`
- Chỉ cho phép upload file ảnh và file nén < 5MB
- Thông báo tin nhắn mới chỉ hoạt động khi tab không active

## Troubleshooting

### Lỗi "Address already in use"
- Port 5000 đã được sử dụng
- Thay đổi port trong `app.py`: `socketio.run(app, debug=True, host='0.0.0.0', port=5001)`

### Lỗi import eventlet
- Chạy lại: `pip install eventlet`

### Database locked
- Đóng tất cả kết nối đến database
- Xóa file `chat.db` và chạy lại `python init_db.py`

## Công nghệ sử dụng

- **Backend**: Flask, Flask-SocketIO, SQLAlchemy
- **Frontend**: Bootstrap 5, Socket.IO Client, Vanilla JavaScript
- **Database**: SQLite
- **Real-time**: Socket.IO với eventlet

## License

MIT License - Free to use and modify

## Tác giả

Phát triển bởi GitHub Copilot

---

**Chúc bạn sử dụng vui vẻ! 🎉**
