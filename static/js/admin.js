// Admin panel functionality

let currentEditingUserId = null;
let currentUsernameValue = '';
const passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));

// Edit button click
document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const userId = this.dataset.userId;
        const row = document.getElementById(`user-row-${userId}`);
        
        // Show edit mode
        currentEditingUserId = userId;
        currentUsernameValue = row.querySelector('.username-display').textContent;
        
        row.querySelector('.username-display').classList.add('d-none');
        row.querySelector('.username-input').classList.remove('d-none');
        row.querySelector('.edit-btn').classList.add('d-none');
        row.querySelector('.save-btn').classList.remove('d-none');
        row.querySelector('.cancel-btn').classList.remove('d-none');
    });
});

// Cancel button click
document.querySelectorAll('.cancel-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const userId = this.dataset.userId;
        const row = document.getElementById(`user-row-${userId}`);
        
        // Restore original value
        row.querySelector('.username-input').value = currentUsernameValue;
        
        // Hide edit mode
        row.querySelector('.username-display').classList.remove('d-none');
        row.querySelector('.username-input').classList.add('d-none');
        row.querySelector('.edit-btn').classList.remove('d-none');
        row.querySelector('.save-btn').classList.add('d-none');
        row.querySelector('.cancel-btn').classList.add('d-none');
        
        currentEditingUserId = null;
    });
});

// Save button click
document.querySelectorAll('.save-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const userId = this.dataset.userId;
        passwordModal.show();
        
        // Store current user id for password modal
        document.getElementById('save-password-btn').dataset.userId = userId;
    });
});

// Save password button in modal
document.getElementById('save-password-btn').addEventListener('click', function() {
    const userId = this.dataset.userId;
    const row = document.getElementById(`user-row-${userId}`);
    const newUsername = row.querySelector('.username-input').value.trim();
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Validate
    if (!newUsername) {
        alert('Tên đăng nhập không được để trống!');
        return;
    }
    
    if (newPassword && newPassword !== confirmPassword) {
        alert('Mật khẩu xác nhận không khớp!');
        return;
    }
    
    // Send update request
    const updateData = {
        username: newUsername
    };
    
    if (newPassword) {
        updateData.password = newPassword;
    }
    
    fetch(`/admin/update_user/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update display
            row.querySelector('.username-display').textContent = newUsername;
            row.querySelector('.username-display').classList.remove('d-none');
            row.querySelector('.username-input').classList.add('d-none');
            row.querySelector('.edit-btn').classList.remove('d-none');
            row.querySelector('.save-btn').classList.add('d-none');
            row.querySelector('.cancel-btn').classList.add('d-none');
            
            // Clear modal
            document.getElementById('new-password').value = '';
            document.getElementById('confirm-password').value = '';
            passwordModal.hide();
            
            // Show success message
            showAlert('success', data.message);
        } else {
            showAlert('danger', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Có lỗi xảy ra khi cập nhật!');
    });
});

// Show alert function
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const cardBody = document.querySelector('.card-body');
    cardBody.insertBefore(alertDiv, cardBody.firstChild);
    
    // Auto dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Clear modal when closed
document.getElementById('passwordModal').addEventListener('hidden.bs.modal', function() {
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-password').value = '';
});
