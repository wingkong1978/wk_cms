import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from application import create_app, db
from application.models.user import User, Role, Permission

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    }, register_admin=False)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_user_model(app):
    """测试用户模型"""
    with app.app_context():
        # 创建测试用户
        user = User(
            username='testuser',
            email='test@example.com',
            password='password',
            active=True,
            fs_uniquifier='test-uniquifier'
        )
        db.session.add(user)
        db.session.commit()
        
        # 测试用户属性
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.active is True

def test_role_model(app):
    """测试角色模型"""
    with app.app_context():
        # 创建测试角色
        role = Role(name='testrole', description='Test Role')
        db.session.add(role)
        db.session.commit()
        
        # 测试角色属性
        assert role.name == 'testrole'
        assert role.description == 'Test Role'

def test_permission_model(app):
    """测试权限模型"""
    with app.app_context():
        # 创建测试权限
        permission = Permission(name='test_permission', description='Test Permission')
        db.session.add(permission)
        db.session.commit()
        
        # 测试权限属性
        assert permission.name == 'test_permission'
        assert permission.description == 'Test Permission'

def test_user_role_relationship(app):
    """测试用户-角色关系"""
    with app.app_context():
        # 创建测试权限
        permission = Permission(name='test_permission', description='Test Permission')
        db.session.add(permission)
        
        # 创建测试角色
        role = Role(name='testrole', description='Test Role')
        role.permissions = [permission]
        db.session.add(role)
        
        # 创建测试用户
        user = User(
            username='testuser',
            email='test@example.com',
            password='password',
            active=True,
            fs_uniquifier='test-uniquifier'
        )
        user.roles = [role]
        db.session.add(user)
        db.session.commit()
        
        # 检查用户-角色关系
        fetched_user = User.query.filter_by(username='testuser').first()
        assert len(fetched_user.roles) == 1
        assert fetched_user.roles[0].name == 'testrole'
        
        # 测试has_role方法
        assert fetched_user.has_role('testrole') is True
        assert fetched_user.has_role('admin') is False

def test_role_permission_relationship(app):
    """测试角色-权限关系"""
    with app.app_context():
        # 创建测试权限
        permission1 = Permission(name='perm1', description='Permission 1')
        permission2 = Permission(name='perm2', description='Permission 2')
        db.session.add_all([permission1, permission2])
        
        # 创建测试角色
        role = Role(name='role_with_perms', description='Role with Permissions')
        role.permissions = [permission1, permission2]
        db.session.add(role)
        db.session.commit()
        
        # 检查角色-权限关系
        fetched_role = Role.query.filter_by(name='role_with_perms').first()
        permission_names = [p.name for p in fetched_role.permissions]
        assert 'perm1' in permission_names
        assert 'perm2' in permission_names

def test_user_permissions(app):
    """测试用户权限检查"""
    with app.app_context():
        # 创建测试权限
        perm_view = Permission(name='view', description='View Permission')
        perm_edit = Permission(name='edit', description='Edit Permission')
        perm_delete = Permission(name='delete', description='Delete Permission')
        db.session.add_all([perm_view, perm_edit, perm_delete])
        
        # 创建测试角色
        admin_role = Role(name='admin_test', description='Admin Test')
        admin_role.permissions = [perm_view, perm_edit, perm_delete]
        
        editor_role = Role(name='editor_test', description='Editor Test')
        editor_role.permissions = [perm_view, perm_edit]
        
        viewer_role = Role(name='viewer_test', description='Viewer Test')
        viewer_role.permissions = [perm_view]
        
        db.session.add_all([admin_role, editor_role, viewer_role])
        
        # 创建测试用户
        admin_user = User(
            username='admin_test', 
            email='admin_test@example.com',
            password='password', 
            active=True, 
            fs_uniquifier='admin_test-id'
        )
        admin_user.roles = [admin_role]
        
        editor_user = User(
            username='editor_test', 
            email='editor_test@example.com',
            password='password', 
            active=True, 
            fs_uniquifier='editor_test-id'
        )
        editor_user.roles = [editor_role]
        
        viewer_user = User(
            username='viewer_test', 
            email='viewer_test@example.com',
            password='password', 
            active=True, 
            fs_uniquifier='viewer_test-id'
        )
        viewer_user.roles = [viewer_role]
        
        db.session.add_all([admin_user, editor_user, viewer_user])
        db.session.commit()
        
        # 获取用户
        admin = User.query.filter_by(username='admin_test').first()
        editor = User.query.filter_by(username='editor_test').first()
        viewer = User.query.filter_by(username='viewer_test').first()
        
        # 管理员权限测试
        assert admin.has_permission('view') is True
        assert admin.has_permission('edit') is True
        assert admin.has_permission('delete') is True
        
        # 编辑权限测试
        assert editor.has_permission('view') is True
        assert editor.has_permission('edit') is True
        assert editor.has_permission('delete') is False
        
        # 访客权限测试
        assert viewer.has_permission('view') is True
        assert viewer.has_permission('edit') is False
        assert viewer.has_permission('delete') is False 