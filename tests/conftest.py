import pytest
import tempfile
import os
from application import create_app, db
from application.models.user import User, Role, Permission

@pytest.fixture(scope='function')
def app():
    """创建测试应用"""
    # 创建临时文件作为测试数据库
    db_fd, db_path = tempfile.mkstemp()
    db_uri = f'sqlite:///{db_path}'
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri,
        'WTF_CSRF_ENABLED': False,
        'SECURITY_PASSWORD_HASH': 'plaintext',  # 测试中使用明文密码
        'SECURITY_PASSWORD_SALT': 'testing-salt',
        'SECURITY_CONFIRMABLE': False,  # 测试不需要确认邮件
        'SECURITY_REGISTERABLE': True,  # 允许注册
        'SECURITY_SEND_REGISTER_EMAIL': False  # 不发送注册邮件
    }, register_admin=False)
    
    # 创建应用上下文
    with app.app_context():
        # 确保使用正确的应用上下文创建表
        db.drop_all()  # 先删除所有表
        db.create_all()  # 重新创建所有表
        
        # 创建基本权限
        permissions = {
            'view_content': '查看内容',
            'create_content': '创建内容',
            'edit_content': '编辑内容'
        }
        
        created_permissions = {}
        for name, description in permissions.items():
            # 检查权限是否已存在
            permission = Permission.query.filter_by(name=name).first()
            if not permission:
                permission = Permission(name=name, description=description)
                db.session.add(permission)
            created_permissions[name] = permission
        
        # 创建角色
        roles = {
            'admin': {
                'description': '管理员',
                'permissions': ['view_content', 'create_content', 'edit_content']
            },
            'editor': {
                'description': '编辑',
                'permissions': ['view_content', 'edit_content']
            },
            'viewer': {
                'description': '访客',
                'permissions': ['view_content']
            }
        }
        
        created_roles = {}
        for name, data in roles.items():
            # 检查角色是否已存在
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name, description=data['description'])
                db.session.add(role)
                
            # 分配权限
            role.permissions = [created_permissions[perm] for perm in data['permissions']]
            created_roles[name] = role
        
        # 创建测试用户
        users = {
            'admin': {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'password',
                'active': True,
                'fs_uniquifier': 'admin-uniquifier',
                'role': 'admin'
            },
            'editor': {
                'username': 'editor',
                'email': 'editor@example.com',
                'password': 'password',
                'active': True,
                'fs_uniquifier': 'editor-uniquifier',
                'role': 'editor'
            },
            'viewer': {
                'username': 'viewer',
                'email': 'viewer@example.com',
                'password': 'password',
                'active': True,
                'fs_uniquifier': 'viewer-uniquifier',
                'role': 'viewer'
            }
        }
        
        for key, data in users.items():
            # 检查用户是否已存在
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                user = User(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    active=data['active'],
                    fs_uniquifier=data['fs_uniquifier']
                )
                user.roles = [created_roles[data['role']]]
                db.session.add(user)
        
        # 确保所有变更都提交到数据库
        db.session.commit()
        
        yield app
        
        # 清理数据库
        db.session.remove()
        db.drop_all()
        
        # 关闭临时文件
        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture(scope='function')
def client(app):
    """测试客户端"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """CLI测试运行器"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def admin_user(app):
    """管理员用户"""
    with app.app_context():
        return User.query.filter_by(username='admin').first()

@pytest.fixture(scope='function')
def editor_user(app):
    """编辑用户"""
    with app.app_context():
        return User.query.filter_by(username='editor').first()

@pytest.fixture(scope='function')
def viewer_user(app):
    """访客用户"""
    with app.app_context():
        return User.query.filter_by(username='viewer').first() 