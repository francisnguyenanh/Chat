# 🔧 TROUBLESHOOTING GUIDE

## Các vấn đề thường gặp và cách khắc phục

### 1. Lỗi khi cài đặt packages

#### Vấn đề: `pip install -r requirements.txt` báo lỗi

**Nguyên nhân:**
- Python version không tương thích
- pip chưa được update
- Network issues

**Giải pháp:**

```powershell
# 1. Check Python version (cần >= 3.8)
python --version

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Install từng package nếu requirements.txt fail
pip install Flask
pip install Flask-SQLAlchemy
pip install Flask-Login
pip install Flask-SocketIO
pip install eventlet

# 4. Nếu eventlet gặp vấn đề, thử:
pip install eventlet==0.33.3 --force-reinstall
```

---

### 2. Port 5000 đã được sử dụng

#### Vấn đề: `Address already in use` hoặc `OSError: [WinError 10048]`

**Giải pháp:**

**Option 1: Tìm và kill process đang dùng port 5000**
```powershell
# Tìm process
netstat -ano | findstr :5000

# Kill process (thay <PID> bằng số hiển thị ở cột cuối)
taskkill /PID <PID> /F
```

**Option 2: Đổi port trong app.py**
```python
# Mở app.py, tìm dòng cuối:
socketio.run(app, debug=True, host='0.0.0.0', port=5000)

# Đổi thành port khác (ví dụ 5001):
socketio.run(app, debug=True, host='0.0.0.0', port=5001)

# Sau đó truy cập: http://localhost:5001
```

---

### 3. Database locked

#### Vấn đề: `sqlite3.OperationalError: database is locked`

**Nguyên nhân:**
- Nhiều process đang truy cập database
- Process cũ chưa đóng kết nối

**Giải pháp:**

```powershell
# 1. Dừng tất cả process Python
taskkill /F /IM python.exe

# 2. Xóa database và tạo lại
del chat.db
python init_db.py

# 3. Restart application
python app.py
```

---

### 4. Socket.IO không kết nối

#### Vấn đề: Chat không real-time, messages không broadcast

**Kiểm tra:**

1. **Browser Console** (F12 → Console tab)
   - Tìm lỗi Socket.IO connection
   - Check: "WebSocket connection to 'ws://localhost:5000/socket.io/' failed"

2. **Eventlet có được cài đúng không?**
   ```powershell
   pip show eventlet
   # Nếu không có, install lại:
   pip install eventlet==0.33.3
   ```

3. **Firewall blocking?**
   ```powershell
   # Tạm thời tắt firewall để test
   # Hoặc thêm exception cho Python
   ```

4. **Restart server sau khi sửa code**
   ```powershell
   # Ctrl+C để dừng
   # python app.py để chạy lại
   ```

---

### 5. File upload không hoạt động

#### Vấn đề: Upload file báo lỗi hoặc không có gì xảy ra

**Kiểm tra:**

1. **Folder uploads có tồn tại?**
   ```powershell
   # Check folder
   dir static\uploads
   
   # Nếu không có, tạo:
   mkdir static\uploads
   ```

2. **File quá lớn (> 5MB)?**
   - Check file size trước khi upload
   - Error: "File quá lớn (tối đa 5MB)"

3. **File type không được support?**
   - Images: jpg, jpeg, png, gif, bmp, webp, svg
   - Archives: zip, rar, 7z
   - Các loại khác sẽ bị reject

4. **Browser Console có lỗi?**
   - F12 → Console
   - Check network errors
   - Check socket.io emit response

---

### 6. Không thể đăng nhập

#### Vấn đề: Username/password đúng nhưng không login được

**Giải pháp:**

1. **Database chưa được khởi tạo**
   ```powershell
   python init_db.py
   ```

2. **Check database có users không**
   ```powershell
   python -c "from app import app, db; from models import User; app.app_context().push(); print(User.query.all())"
   ```

3. **Clear browser cookies**
   - Ctrl+Shift+Delete
   - Clear cookies for localhost

4. **Try default accounts:**
   - Admin: `admin` / `admin123`
   - User: `user1` / `password1`

---

### 7. Admin không thể sửa user info

#### Vấn đề: Click "Lưu" nhưng không update

**Kiểm tra:**

1. **Browser Console** (F12)
   - Check AJAX errors
   - Network tab → check POST request

2. **Database permissions**
   ```powershell
   # Delete và tạo lại database
   del chat.db
   python init_db.py
   ```

3. **Username đã tồn tại?**
   - Không thể đổi thành username đã có

4. **Có đăng nhập với admin không?**
   - User thường không có quyền

---

### 8. Thông báo chấm đỏ không hiện

#### Vấn đề: Tin nhắn mới nhưng không có 🔴 trên tab

**Lý do bình thường:**

1. **Tab đang active** → Không hiển thị notification
   - Phải switch sang tab khác

2. **Tin nhắn của chính mình** → Không notification
   - Chỉ notify khi người khác gửi

3. **Test đúng cách:**
   ```
   1. Mở 2 tabs, login 2 users khác nhau
   2. Tab 1: user1, Tab 2: user2
   3. Switch sang tab khác (không phải tab chat)
   4. Từ tab 1, gửi tin nhắn
   5. Tab 2 sẽ hiện 🔴
   ```

---

### 9. Auto-delete không chạy

#### Vấn đề: Tin nhắn/file cũ không tự động xóa

**Lý do:**

1. **Chưa login với admin**
   - Auto-delete chỉ chạy khi admin login

2. **Chưa đủ thời gian**
   - Messages: > 30 days
   - Files: > 7 days

3. **Đã chạy rồi (hôm nay)**
   - Chỉ chạy 1 lần mỗi ngày

**Test auto-delete:**

```python
# Test script: test_cleanup.py
from app import app, db
from models import Message, File, User
from datetime import datetime, timedelta

with app.app_context():
    # Tạo tin nhắn cũ (35 ngày trước)
    user = User.query.first()
    old_msg = Message(
        user_id=user.id,
        content="Test old message",
        timestamp=datetime.utcnow() - timedelta(days=35)
    )
    db.session.add(old_msg)
    db.session.commit()
    
    print(f"Created old message: {old_msg.id}")
    print("Now login with admin to trigger cleanup")
```

---

### 10. Tiếng Việt/Nhật hiển thị sai

#### Vấn đề: Ký tự bị vỡ, hiển thị □□□

**Giải pháp:**

1. **Check file encoding**
   - Tất cả files phải UTF-8
   - VSCode: bottom right → UTF-8

2. **Browser encoding**
   - F12 → Console
   - document.characterSet (phải là "UTF-8")

3. **Test với văn bản sample:**
   ```
   Tiếng Việt: Xin chào, đây là tiếng Việt có dấu
   日本語: こんにちは、日本語のテストです
   ```

---

### 11. CSS/JS không load

#### Vấn đề: Giao diện xấu, không có màu sắc

**Giải pháp:**

1. **Hard refresh browser**
   ```
   Ctrl + Shift + R  (hoặc Ctrl + F5)
   ```

2. **Check static files tồn tại**
   ```powershell
   dir static\css\style.css
   dir static\js\chat.js
   dir static\js\admin.js
   ```

3. **Check Flask serving static files**
   - Truy cập: http://localhost:5000/static/css/style.css
   - Nếu 404 → vấn đề với Flask routing

4. **Clear browser cache**
   - Ctrl + Shift + Delete
   - Clear cached images and files

---

### 12. Performance chậm

#### Vấn đề: App chậm, lag khi nhiều messages

**Optimization:**

1. **Limit messages load**
   ```python
   # Trong app.py, route /chat
   # Hiện tại: load 100 messages
   # Giảm xuống nếu cần:
   messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
   ```

2. **Database index**
   ```python
   # Đã có index trên timestamp
   # Check trong models.py:
   timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
   ```

3. **Clean old data thường xuyên**
   - Admin login mỗi ngày để trigger cleanup

4. **Upgrade to PostgreSQL** (production)
   - SQLite không tốt cho concurrent writes

---

## 🆘 Emergency Reset

Nếu mọi thứ bị lỗi và không biết sửa thế nào:

```powershell
# 1. Stop server
Ctrl + C

# 2. Backup (nếu cần)
copy chat.db chat.db.backup
xcopy /E /I static\uploads static\uploads.backup

# 3. Complete reset
del chat.db
rmdir /S /Q static\uploads
mkdir static\uploads
echo. > static\uploads\.gitkeep

# 4. Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 5. Reinitialize
python init_db.py

# 6. Restart
python app.py
```

---

## 📞 Getting Help

Nếu vẫn gặp vấn đề:

1. **Check logs**
   - Terminal output khi chạy `python app.py`
   - Browser Console (F12)

2. **Test với clean environment**
   ```powershell
   # Tạo venv mới
   python -m venv venv_test
   .\venv_test\Scripts\Activate
   pip install -r requirements.txt
   python init_db.py
   python app.py
   ```

3. **Run test script**
   ```powershell
   python test_setup.py
   ```

4. **Check versions**
   ```powershell
   python --version
   pip list
   ```

---

## ✅ Prevention Tips

### Để tránh vấn đề:

1. **Always use virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

2. **Regular backups**
   ```powershell
   # Backup database
   copy chat.db backups\chat_%date%.db
   ```

3. **Keep dependencies updated**
   ```powershell
   pip list --outdated
   pip install --upgrade <package>
   ```

4. **Monitor logs**
   - Check terminal output thường xuyên
   - Note any warnings

5. **Test after changes**
   - Sau khi sửa code, test lại tất cả features

---

**Good luck! 🍀**
