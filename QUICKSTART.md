# QUICK START GUIDE

## Cài đặt và Chạy (Windows)

### Cách 1: Sử dụng file run.bat (Đơn giản nhất)

1. Double-click vào file `run.bat`
2. Script sẽ tự động:
   - Tạo virtual environment
   - Cài đặt dependencies
   - Khởi tạo database
   - Chạy server
3. Mở trình duyệt và truy cập: http://localhost:5000

### Cách 2: Chạy thủ công

```powershell
# 1. Tạo virtual environment
python -m venv venv

# 2. Kích hoạt virtual environment
.\venv\Scripts\Activate

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Khởi tạo database
python init_db.py

# 5. Chạy ứng dụng
python app.py
```

## Đăng nhập

### Tài khoản Admin:
- Username: `admin`
- Password: `admin123`

### Tài khoản User:
- Username: `user1` đến `user9`
- Password: `password1` đến `password9`

## Hướng dẫn sử dụng

### Chat:
1. Đăng nhập với bất kỳ tài khoản nào
2. Nhập tin nhắn và nhấn Enter
3. Click icon 📎 để gửi file/hình
4. Paste (Ctrl+V) để gửi hình ảnh từ clipboard

### Quản lý (Admin):
1. Đăng nhập với tài khoản `admin`
2. Click nút "Quản lý" ở góc trên
3. Click "Sửa" để thay đổi username/password của user
4. Nhập thông tin mới và click "Lưu"

## Tính năng chính

✅ Chat real-time giữa tối đa 10 người
✅ Gửi hình ảnh (tất cả định dạng)
✅ Gửi file nén < 5MB (.zip, .rar, .7z)
✅ Tự động xóa tin nhắn sau 30 ngày
✅ Tự động xóa file sau 7 ngày
✅ Thông báo tin nhắn mới (🔴 trên tab)
✅ Giao diện giống Google Chat
✅ Hỗ trợ tiếng Việt và tiếng Nhật

## Lưu ý

- Chỉ 1 Admin và 9 User
- Admin có quyền sửa thông tin của tất cả user
- Tin nhắn hiển thị: Bên phải = bạn, Bên trái = người khác
- Dọn dẹp tự động khi admin đăng nhập lần đầu trong ngày

## Port đang sử dụng

- Server: http://localhost:5000
- Database: SQLite (file chat.db)

---

**Chúc bạn sử dụng vui vẻ!** 🚀
