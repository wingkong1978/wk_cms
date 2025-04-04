from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_security import current_user
from application import db, admin
from application.models.user import User, Role, Permission

# 基础管理视图（需要认证）
class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('admin'))
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=url_for(admin.endpoint, **kwargs)))

# 用户管理视图
class UserModelView(AuthenticatedModelView):
    can_create = True
    can_edit = True
    can_delete = True
    column_exclude_list = ['password']
    column_searchable_list = ['username', 'email']
    column_filters = ['active', 'created_at', 'roles']
    form_excluded_columns = ['password', 'fs_uniquifier', 'created_at', 'updated_at', 
                           'confirmed_at', 'last_login_at', 'current_login_at', 
                           'last_login_ip', 'current_login_ip', 'login_count']
    column_labels = {
        'username': '用户名',
        'email': '邮箱',
        'active': '状态',
        'created_at': '注册时间',
        'roles': '角色'
    }
    
    def on_model_change(self, form, model, is_created):
        """在用户创建时自动生成唯一标识符"""
        if is_created:
            import uuid
            model.fs_uniquifier = uuid.uuid4().hex

# 角色管理视图
class RoleModelView(AuthenticatedModelView):
    can_create = True
    can_edit = True
    can_delete = True
    column_searchable_list = ['name', 'description']
    column_labels = {
        'name': '角色名称',
        'description': '描述',
        'permissions': '权限',
        'users': '用户'
    }

# 权限管理视图
class PermissionModelView(AuthenticatedModelView):
    can_create = True
    can_edit = True
    can_delete = True
    column_searchable_list = ['name', 'description']
    column_labels = {
        'name': '权限名称',
        'description': '描述',
        'roles': '角色'
    }

# 注册管理视图
def register_admin_views():
    """注册管理后台视图"""
    admin.add_view(UserModelView(User, db.session, name='用户管理'))
    admin.add_view(RoleModelView(Role, db.session, name='角色管理'))
    admin.add_view(PermissionModelView(Permission, db.session, name='权限管理')) 