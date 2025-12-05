// Initialize Socket.IO
const socket = io();

// DOM Elements
const messagesArea = document.getElementById('messages-area');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const fileInput = document.getElementById('file-input');
const typingIndicator = document.getElementById('typing-indicator');
const pageTitle = document.getElementById('page-title');
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');

// State
let isTyping = false;
let typingTimeout = null;
let hasNewMessages = false;
let isPageVisible = true;
const originalTitle = 'Chat App';
const REACTION_EMOJIS = ['👍', '❤️', '😂', '😮', '😢'];

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('chat-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('chat-theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    themeIcon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
}

// Convert to Japan Time (JST = UTC+9)
function formatTimeJST(timestamp) {
    const date = new Date(timestamp);
    const jstDate = new Date(date.getTime() + (9 * 60 * 60 * 1000)); // Add 9 hours
    return jstDate.toLocaleTimeString('ja-JP', { 
        hour: '2-digit', 
        minute: '2-digit',
        timeZone: 'Asia/Tokyo'
    });
}

// Auto-scroll to bottom
function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Add message to chat
function addMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.user_id === CURRENT_USER_ID ? 'message-right' : 'message-left'}`;
    messageDiv.setAttribute('data-message-id', message.id);
    
    const isOwner = message.user_id === CURRENT_USER_ID;
    const editedLabel = message.edited_at ? '<span class="edited-label">(đã sửa)</span>' : '';
    const actionsHtml = isOwner ? `
        <div class="message-actions">
            <button class="btn-icon edit-msg" data-id="${message.id}" title="Sửa">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn-icon delete-msg" data-id="${message.id}" title="Xóa">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    ` : '';
    
    const reactions = parseReactions(message.reactions);
    const reactionsHtml = buildReactionsHtml(message.id, reactions);
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-author">${escapeHtml(message.username)}</div>
            <div class="message-text">${escapeHtml(message.content)} ${editedLabel}</div>
            ${reactionsHtml}
            <div class="message-footer">
                <div class="message-time">${formatTimeJST(message.timestamp)}</div>
                ${actionsHtml}
            </div>
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    attachMessageListeners(messageDiv);
    scrollToBottom();
    
    // Show notification if not current user and page not visible
    if (message.user_id !== CURRENT_USER_ID) {
        showNewMessageNotification();
    }
}

function parseReactions(reactionsStr) {
    try {
        return JSON.parse(reactionsStr || '{}');
    } catch {
        return {};
    }
}

function buildReactionsHtml(messageId, reactions) {
    if (!reactions || Object.keys(reactions).length === 0) {
        return `<div class="reactions" data-message-id="${messageId}">
            <button class="btn-reaction" data-emoji="👍">👍</button>
            <button class="btn-reaction" data-emoji="❤️">❤️</button>
            <button class="btn-reaction" data-emoji="😂">😂</button>
            <button class="btn-reaction" data-emoji="😮">😮</button>
            <button class="btn-reaction" data-emoji="😢">😢</button>
        </div>`;
    }
    
    let html = `<div class="reactions" data-message-id="${messageId}">`;
    
    // Show existing reactions with counts
    for (const [emoji, users] of Object.entries(reactions)) {
        const count = users.length;
        const isActive = users.includes(String(CURRENT_USER_ID)) ? 'active' : '';
        html += `<button class="btn-reaction ${isActive}" data-emoji="${emoji}">${emoji} ${count}</button>`;
    }
    
    // Add remaining reaction buttons
    REACTION_EMOJIS.forEach(emoji => {
        if (!reactions[emoji]) {
            html += `<button class="btn-reaction" data-emoji="${emoji}">${emoji}</button>`;
        }
    });
    
    html += '</div>';
    return html;
}

function attachMessageListeners(messageDiv) {
    // Edit button
    const editBtn = messageDiv.querySelector('.edit-msg');
    if (editBtn) {
        editBtn.addEventListener('click', function() {
            const msgId = this.dataset.id;
            const msgText = messageDiv.querySelector('.message-text').textContent.replace('(đã sửa)', '').trim();
            const newContent = prompt('Sửa tin nhắn:', msgText);
            if (newContent && newContent.trim()) {
                socket.emit('edit_message', {
                    message_id: parseInt(msgId),
                    content: newContent.trim()
                });
            }
        });
    }
    
    // Delete button
    const deleteBtn = messageDiv.querySelector('.delete-msg');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            const msgId = this.dataset.id;
            if (confirm('Bạn có chắc muốn xóa tin nhắn này?')) {
                socket.emit('delete_message', { message_id: parseInt(msgId) });
            }
        });
    }
    
    // Reaction buttons
    const reactionBtns = messageDiv.querySelectorAll('.btn-reaction');
    reactionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const msgId = messageDiv.dataset.messageId;
            const emoji = this.dataset.emoji;
            socket.emit('add_reaction', {
                message_id: parseInt(msgId),
                emoji: emoji
            });
        });
    });
}

// Add file to chat
function addFile(file) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${file.user_id === CURRENT_USER_ID ? 'message-right' : 'message-left'}`;
    messageDiv.setAttribute('data-file-id', file.id);
    
    const isOwner = file.user_id === CURRENT_USER_ID;
    const deleteBtn = isOwner ? `
        <button class="btn-icon delete-file" data-id="${file.id}" title="Xóa">
            <i class="bi bi-trash"></i>
        </button>
    ` : '';
    
    let fileContent = '';
    if (file.file_type === 'image') {
        fileContent = `
            <div class="message-file">
                <a href="/uploads/${file.filename}" target="_blank">
                    <img src="/uploads/${file.filename}" alt="${escapeHtml(file.original_filename)}" class="uploaded-image">
                </a>
                <div class="file-name">${escapeHtml(file.original_filename)}</div>
            </div>
        `;
    } else {
        const fileSizeKB = (file.file_size / 1024).toFixed(1);
        fileContent = `
            <div class="message-file">
                <a href="/uploads/${file.filename}" download="${escapeHtml(file.original_filename)}" class="file-download">
                    <i class="bi bi-file-earmark-zip"></i>
                    <span>${escapeHtml(file.original_filename)}</span>
                    <small>(${fileSizeKB} KB)</small>
                </a>
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-author">${escapeHtml(file.username)}</div>
            ${fileContent}
            <div class="message-footer">
                <div class="message-time">${formatTimeJST(file.upload_time)}</div>
                ${deleteBtn}
            </div>
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    
    // Attach delete listener
    const delBtn = messageDiv.querySelector('.delete-file');
    if (delBtn) {
        delBtn.addEventListener('click', function() {
            const fileId = this.dataset.id;
            if (confirm('Bạn có chắc muốn xóa file này?')) {
                socket.emit('delete_file', { file_id: parseInt(fileId) });
            }
        });
    }
    
    scrollToBottom();
    
    // Show notification if not current user
    if (file.user_id !== CURRENT_USER_ID) {
        showNewMessageNotification();
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Show new message notification in title
function showNewMessageNotification() {
    if (!isPageVisible) {
        hasNewMessages = true;
        updatePageTitle();
    }
}

// Update page title with notification
function updatePageTitle() {
    if (hasNewMessages && !isPageVisible) {
        pageTitle.textContent = '🔴 Tin nhắn mới - ' + originalTitle;
    } else {
        pageTitle.textContent = originalTitle;
    }
}

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        socket.emit('send_message', { message: message });
        messageInput.value = '';
        stopTyping();
    }
}

// Handle typing indicator
function handleTyping() {
    if (!isTyping) {
        isTyping = true;
        socket.emit('typing', { is_typing: true });
    }
    
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        stopTyping();
    }, 2000);
}

function stopTyping() {
    if (isTyping) {
        isTyping = false;
        socket.emit('typing', { is_typing: false });
    }
}

// Handle file upload
function handleFileUpload(file) {
    if (!file) return;
    
    // Check file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('File quá lớn! Kích thước tối đa là 5MB.');
        return;
    }
    
    // Check file type
    const fileName = file.name.toLowerCase();
    const isImage = /\.(jpg|jpeg|png|gif|bmp|webp|svg)$/i.test(fileName);
    const isArchive = /\.(zip|rar|7z)$/i.test(fileName);
    
    if (!isImage && !isArchive) {
        alert('Chỉ cho phép upload ảnh hoặc file nén (.zip, .rar, .7z)');
        return;
    }
    
    // Read file and convert to base64
    const reader = new FileReader();
    reader.onload = function(e) {
        const fileType = isImage ? 'image' : 'file';
        socket.emit('upload_file', {
            file: e.target.result,
            filename: file.name,
            file_type: fileType
        }, (response) => {
            if (response && !response.success) {
                alert('Lỗi upload: ' + response.message);
            }
        });
    };
    reader.readAsDataURL(file);
}

// Event Listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    } else {
        handleTyping();
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
        e.target.value = ''; // Reset input
    }
});

themeToggle.addEventListener('click', toggleTheme);

// Page visibility change
document.addEventListener('visibilitychange', () => {
    isPageVisible = !document.hidden;
    if (isPageVisible) {
        hasNewMessages = false;
        updatePageTitle();
    }
});

// Socket.IO Events
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

socket.on('new_message', (message) => {
    addMessage(message);
});

socket.on('new_file', (file) => {
    addFile(file);
});

socket.on('message_deleted', (data) => {
    const msgDiv = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (msgDiv) {
        msgDiv.remove();
    }
});

socket.on('message_edited', (message) => {
    const msgDiv = document.querySelector(`[data-message-id="${message.id}"]`);
    if (msgDiv) {
        msgDiv.remove();
        addMessage(message);
    }
});

socket.on('file_deleted', (data) => {
    const fileDiv = document.querySelector(`[data-file-id="${data.file_id}"]`);
    if (fileDiv) {
        fileDiv.remove();
    }
});

socket.on('reaction_updated', (data) => {
    const msgDiv = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (msgDiv) {
        const reactionsDiv = msgDiv.querySelector('.reactions');
        if (reactionsDiv) {
            reactionsDiv.outerHTML = buildReactionsHtml(data.message_id, data.reactions);
            attachMessageListeners(msgDiv);
        }
    }
});

socket.on('user_typing', (data) => {
    if (data.user_id !== CURRENT_USER_ID) {
        typingIndicator.querySelector('.typing-user').textContent = data.username;
        typingIndicator.style.display = data.is_typing ? 'block' : 'none';
    }
});

socket.on('user_connected', (data) => {
    console.log(`${data.username} connected`);
});

socket.on('user_disconnected', (data) => {
    console.log(`${data.username} disconnected`);
});

// Initialize
initTheme();
scrollToBottom();

// Paste event for images
messageInput.addEventListener('paste', (e) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            e.preventDefault();
            const blob = items[i].getAsFile();
            handleFileUpload(blob);
            break;
        }
    }
});
