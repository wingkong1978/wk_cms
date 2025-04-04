// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化Bootstrap提示工具
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 密码强度验证
    var passwordField = document.querySelector('input[type="password"]');
    if (passwordField) {
        passwordField.addEventListener('keyup', function() {
            validatePassword(this.value);
        });
    }
    
    // 表单验证
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// 密码强度验证函数
function validatePassword(password) {
    var strength = 0;
    var strengthBar = document.getElementById('password-strength');
    
    if (!strengthBar) return;
    
    // 长度检查
    if (password.length >= 8) strength += 1;
    
    // 包含字母和数字
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 1;
    if (/\d/.test(password)) strength += 1;
    
    // 包含特殊字符
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
    
    // 更新强度条
    switch(strength) {
        case 0:
            strengthBar.className = 'progress-bar bg-danger';
            strengthBar.style.width = '25%';
            strengthBar.textContent = '非常弱';
            break;
        case 1:
            strengthBar.className = 'progress-bar bg-warning';
            strengthBar.style.width = '50%';
            strengthBar.textContent = '弱';
            break;
        case 2:
            strengthBar.className = 'progress-bar bg-info';
            strengthBar.style.width = '75%';
            strengthBar.textContent = '中等';
            break;
        case 3:
            strengthBar.className = 'progress-bar bg-primary';
            strengthBar.style.width = '85%';
            strengthBar.textContent = '强';
            break;
        case 4:
            strengthBar.className = 'progress-bar bg-success';
            strengthBar.style.width = '100%';
            strengthBar.textContent = '非常强';
            break;
    }
} 