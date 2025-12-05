# Hướng dẫn Deploy lên PythonAnywhere

## 1. Chuẩn bị

### Upload code lên PythonAnywhere
1. Đăng nhập vào [PythonAnywhere](https://www.pythonanywhere.com/)
2. Vào tab **Files** và upload toàn bộ project (hoặc dùng Git)
3. Hoặc dùng Git:
   ```bash
   cd ~
   git clone https://github.com/your-username/Chat.git
   cd Chat
   ```

## 2. Tạo Virtual Environment

Mở **Bash console** trên PythonAnywhere:

```bash
cd ~/Chat  # Hoặc thư mục project của bạn
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Khởi tạo Database

```bash
python init_db.py
```

Điều này sẽ tạo database với:
- **Admin**: `admin` / `admin123`
- **User1-9**: `user1` / `password1`, `user2` / `password2`, ...

## 4. Cấu hình Web App

1. Vào tab **Web**
2. Click **Add a new web app**
3. Chọn **Manual configuration** (không phải Flask)
4. Chọn **Python 3.11**

### 4.1. Cấu hình WSGI File

Click vào link **WSGI configuration file** và thay thế toàn bộ nội dung bằng:

```python
import sys
import os

# Thêm đường dẫn project vào sys.path
path = '/home/YOUR_USERNAME/Chat'  # Thay YOUR_USERNAME bằng username của bạn
if path not in sys.path:
    sys.path.append(path)

# Kích hoạt virtual environment
activate_this = '/home/YOUR_USERNAME/Chat/.venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Flask app
from app import app as application
```

**Lưu ý**: Thay `YOUR_USERNAME` bằng username PythonAnywhere của bạn!

### 4.2. Cấu hình Virtual Environment

Trong tab **Web**, tìm section **Virtualenv**:
- Click **Enter path to a virtualenv**
- Nhập: `/home/YOUR_USERNAME/Chat/.venv`

### 4.3. Cấu hình Static Files

Trong section **Static files**:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/Chat/static/`

Thêm static file cho uploads:
- URL: `/uploads/`
- Directory: `/home/YOUR_USERNAME/Chat/uploads/`

## 5. Reload Web App

Click nút **Reload** màu xanh lá ở đầu trang.

## 6. Truy cập

Truy cập web app tại: `https://YOUR_USERNAME.pythonanywhere.com`

## 7. Lưu ý quan trọng

### ✅ Ưu điểm của HTMX + Polling trên PythonAnywhere:
- ✅ **Hoạt động tốt**: Không cần WebSocket hay SSE
- ✅ **Polling 2 giây**: Cập nhật tin nhắn mới khá nhanh
- ✅ **Ổn định**: HTTP requests ngắn, không bị timeout
- ✅ **Free tier**: Hoàn toàn hoạt động trên tài khoản miễn phí

### ⚠️ Hạn chế:
- Polling 2 giây có độ trễ nhỏ (2s) so với real-time
- Tiêu tốn nhiều requests hơn WebSocket (nhưng vẫn OK với 10 users)

### 🔧 Tối ưu hóa (nếu cần):
Nếu muốn giảm polling interval, sửa trong `templates/chat.html`:

```html
<!-- Thay đổi từ 2s xuống 1s -->
<div hx-get="/api/messages"
     hx-trigger="every 1s"  <!-- Đổi từ 2s -->
     ...>
</div>
```

**Cảnh báo**: Polling quá nhanh (<1s) có thể bị PythonAnywhere giới hạn requests.

## 8. Troubleshooting

### Lỗi 500 Internal Server Error
- Kiểm tra **Error log** trong tab Web
- Thường do đường dẫn sai trong WSGI file
- Hoặc thiếu dependencies trong virtual environment

### Database không có dữ liệu
- Chạy lại `python init_db.py` trong Bash console
- Đảm bảo file `instance/chat.db` được tạo

### Static files không load
- Kiểm tra đường dẫn trong **Static files** section
- Đảm bảo folder `static/` và `uploads/` tồn tại

### Tin nhắn không cập nhật
- Kiểm tra tab **Network** trong DevTools
- Đảm bảo requests `/api/messages` chạy mỗi 2 giây
- Kiểm tra HTMX CDN có load được không

## 9. Bảo mật (Production)

**Quan trọng**: Trước khi deploy production, sửa `config.py`:

```python
class Config:
    SECRET_KEY = 'your-very-secret-random-key-here'  # Đổi key mới!
    # ... các config khác ...
```

Tạo secret key ngẫu nhiên:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 10. Nâng cấp (Optional)

Nếu cần WebSocket thật (không phải polling), có thể:
- Deploy lên **Heroku** (có hỗ trợ WebSocket)
- Deploy lên **Railway.app** (có hỗ trợ WebSocket)
- Deploy lên **Render.com** (có hỗ trợ WebSocket)
- Mua tài khoản **PythonAnywhere paid** (có hỗ trợ WebSocket)

Nhưng với 10 users, **HTMX + polling hoàn toàn đủ dùng**! 🎉
