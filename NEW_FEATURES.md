# 🆕 CÁC TÍNH NĂNG MỚI

## Đã thêm vào ứng dụng Chat

### 1. ✏️ Xóa và Sửa Tin Nhắn

**Xóa tin nhắn:**
- Mỗi tin nhắn có nút "🗑️" (chỉ hiện khi hover)
- Chỉ người gửi hoặc Admin mới có thể xóa
- Click nút xóa → xác nhận → tin nhắn biến mất real-time

**Sửa tin nhắn:**
- Mỗi tin nhắn có nút "✏️" (chỉ hiện khi hover)
- Chỉ người gửi mới có thể sửa
- Click nút sửa → nhập nội dung mới → tin nhắn cập nhật với label "(đã sửa)"

### 2. 🗑️ Xóa Ảnh/File

- Mỗi file/ảnh có nút "🗑️" 
- Chỉ người upload hoặc Admin mới có thể xóa
- Xóa cả file vật lý và database record
- Cập nhật real-time cho tất cả users

### 3. 🌓 Dark Mode (Theme Trắng/Đen)

**Chuyển đổi theme:**
- Click nút 🌙/☀️ trên header
- Tự động lưu preference vào localStorage
- Theme được giữ nguyên khi reload trang

**2 Themes:**
- **Light Mode**: Nền trắng, dễ nhìn ban ngày
- **Dark Mode**: Nền đen, dễ chịu ban đêm, giảm mỏi mắt

### 4. 🇯🇵 Hiển Thị Japan Time (JST)

**Thời gian:**
- Tất cả timestamps hiển thị theo giờ Nhật (JST = UTC+9)
- Format: HH:MM theo chuẩn Nhật Bản
- Ví dụ: 14:30, 09:15

**Cách hoạt động:**
- Backend lưu UTC
- Frontend tự động convert sang JST
- Đảm bảo đồng bộ với timezone Nhật

### 5. 👍 Reactions (5 Icons Cơ Bản)

**5 Emoji giống Microsoft Teams:**
- 👍 Like
- ❤️ Love
- 😂 Laugh
- 😮 Surprised
- 😢 Sad

**Cách dùng:**
- Hover vào tin nhắn → hiện 5 emoji
- Click emoji để react
- Click lại để bỏ reaction
- Hiển thị số lượng người react
- Reaction của bạn được highlight

---

## Cập Nhật Database

Nếu bạn đã có database cũ (`chat.db`), chạy lệnh sau để thêm các trường mới:

```powershell
python upgrade_db.py
```

Hoặc xóa database và tạo mới:

```powershell
del chat.db
python init_db.py
```

---

## Shortcuts

### Keyboard Shortcuts:
- `Enter`: Gửi tin nhắn
- `Ctrl+V`: Paste ảnh từ clipboard

### Mouse Shortcuts:
- Hover tin nhắn: Hiện nút xóa/sửa và reactions
- Click emoji: Thêm/bỏ reaction
- Click ảnh: Xem full size
- Right click → Save: Tải file

---

## Technical Details

### New Database Columns:
- `messages.edited_at`: DateTime - Thời gian sửa tin nhắn cuối
- `messages.reactions`: TEXT (JSON) - Lưu reactions

### New Socket.IO Events:
- `delete_message`: Xóa tin nhắn
- `edit_message`: Sửa tin nhắn
- `delete_file`: Xóa file
- `add_reaction`: Thêm/bỏ reaction
- `message_deleted`: Broadcast khi tin nhắn bị xóa
- `message_edited`: Broadcast khi tin nhắn được sửa
- `file_deleted`: Broadcast khi file bị xóa
- `reaction_updated`: Broadcast khi có reaction mới

### Theme System:
- CSS Variables cho dynamic theming
- LocalStorage để lưu preference
- Real-time theme switching không reload

### Time Conversion:
- Server: UTC
- Client: Auto convert to JST (UTC+9)
- Format: Japanese standard (HH:MM)

---

## Screenshots

### Light Mode
- Giao diện sáng, tươi
- Tin nhắn trái: nền trắng
- Tin nhắn phải: gradient tím

### Dark Mode
- Giao diện tối, mắt dễ chịu
- Tin nhắn trái: nền xám đậm
- Tin nhắn phải: gradient tím (giống light)

### Reactions
- Hover → hiện 5 emoji
- Click → thêm reaction
- Hiển thị count và highlight

---

## Compatibility

- ✅ Chrome, Edge, Firefox (latest)
- ✅ Mobile responsive
- ✅ Touch-friendly reactions
- ✅ All timezones → JST conversion

---

**Enjoy the new features!** 🎉
