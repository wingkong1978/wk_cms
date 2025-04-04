from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_security import login_required, current_user, roles_required
from application import user_datastore, db
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 权限检查装饰器
def permission_required(permission):
    """检查用户是否拥有指定权限的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not current_user.has_permission(permission):
                flash('您没有权限执行此操作', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 扩展Flask-Security视图
@auth_bp.route('/profile')
@login_required
def profile():
    """用户个人资料页面"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/user_list')
@login_required
@roles_required('admin')  # 只允许管理员访问
def user_list():
    """用户列表页面 - 仅管理员可访问"""
    from application.models.user import User
    users = User.query.all()
    return render_template('auth/user_list.html', users=users)

# 组合权限装饰器示例
def admin_permission_required(f):
    """需要管理员权限的装饰器"""
    return permission_required('manage_users')(f)

def content_creator_permission_required(f):
    """需要内容创建权限的装饰器"""
    return permission_required('create_content')(f)

def content_editor_permission_required(f):
    """需要内容编辑权限的装饰器"""
    return permission_required('edit_content')(f)

def content_approver_permission_required(f):
    """需要内容审核权限的装饰器"""
    return permission_required('approve_content')(f) 