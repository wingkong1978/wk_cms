import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_security import Security, SQLAlchemyUserDatastore
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
admin = Admin(name='Flask-CMS', template_mode='bootstrap4')
mail = Mail()
csrf = CSRFProtect()
security = Security()

# 用户数据存储
user_datastore = None

def init_db():
    """确保数据库表已创建"""
    try:
        # 检查数据库连接
        db.engine.connect()
        
        # 检查users表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # 如果users表不存在，则创建所有表
        if 'users' not in inspector.get_table_names():
            db.create_all()
            print("数据库表已成功创建!")
        
    except Exception as e:
        print(f"数据库初始化错误: {str(e)}")
        # 如果出错，尝试创建所有表
        try:
            db.create_all()
            print("数据库表已成功创建!")
        except Exception as e:
            print(f"无法创建数据库表: {str(e)}")

def create_app(config=None, register_admin=True):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置应用
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        
        # Flask-Security配置
        SECURITY_PASSWORD_SALT=os.environ.get('SECURITY_PASSWORD_SALT', 'secure_salt'),
        SECURITY_PASSWORD_HASH='pbkdf2_sha256',
        SECURITY_REGISTERABLE=True,
        SECURITY_CONFIRMABLE=False,
        SECURITY_RECOVERABLE=True,
        SECURITY_CHANGEABLE=True,
        SECURITY_TRACKABLE=True,
        SECURITY_EMAIL_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@flask-cms.com'),
        SECURITY_SEND_REGISTER_EMAIL=False,
        SECURITY_SEND_PASSWORD_CHANGE_EMAIL=False,
        SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL=False,
        
        # 邮件配置
        MAIL_SERVER=os.environ.get('MAIL_SERVER', 'localhost'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', 25)),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true',
        MAIL_USE_SSL=os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true',
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@flask-cms.com')
    )
    
    # 如果提供了配置对象，则应用它
    if config:
        app.config.from_object(config)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    admin.init_app(app)
    
    # 初始化数据库
    with app.app_context():
        init_db()
    
    # 初始化Flask-Security
    from application.models.user import User, Role, Permission
    from application.forms import ExtendedRegisterForm
    global user_datastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    
    # 监听Flask-Security注册事件
    def user_registered_sighandler(app, user, confirm_token, form_data):
        """当用户注册时，保存用户名"""
        if isinstance(form_data, dict) and 'username' in form_data:
            user.username = form_data['username']
            db.session.add(user)
            db.session.commit()

    # 连接Flask-Security信号
    from flask_security import user_registered
    user_registered.connect(user_registered_sighandler)
    
    security.init_app(app, user_datastore,
                     register_form=ExtendedRegisterForm,
                     confirm_register_form=ExtendedRegisterForm,
                     register_user_template='security/register_user.html')
    
    # 注册回调函数，在注册过程中保存username字段
    @security.context_processor
    def security_context_processor():
        return {}
    
    # 注册蓝图
    from application.controllers.main import main_bp
    from application.controllers.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    # 注册管理后台视图
    if register_admin:
        from application.controllers.admin import register_admin_views
        register_admin_views()
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 添加命令
    register_commands(app)
    
    return app

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def page_not_found(e):
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return {'error': 'Internal server error'}, 500

def register_commands(app):
    """注册Flask命令"""
    @app.cli.command('init-db')
    def initialize_db():
        """初始化数据库表结构"""
        with app.app_context():
            db.create_all()
            print('数据库表结构初始化成功!')
    
    @app.cli.command('create-roles')
    def create_roles():
        """创建初始角色和权限"""
        from application.models.user import Role, Permission
        
        # 创建基本权限
        permissions = {
            'view_content': '查看内容',
            'create_content': '创建内容',
            'edit_content': '编辑内容',
            'delete_content': '删除内容',
            'approve_content': '审核内容',
            'manage_users': '管理用户',
            'manage_roles': '管理角色'
        }
        
        # 创建角色并分配权限
        roles = {
            'admin': {
                'description': '管理员',
                'permissions': list(permissions.keys())
            },
            'editor': {
                'description': '编辑',
                'permissions': ['view_content', 'create_content', 'edit_content', 'delete_content', 'approve_content']
            },
            'author': {
                'description': '作者',
                'permissions': ['view_content', 'create_content', 'edit_content']
            },
            'viewer': {
                'description': '访客',
                'permissions': ['view_content']
            }
        }
        
        # 创建权限
        created_permissions = {}
        for name, description in permissions.items():
            permission = Permission.query.filter_by(name=name).first()
            if not permission:
                permission = Permission(name=name, description=description)
                db.session.add(permission)
            created_permissions[name] = permission
        
        # 创建角色
        for name, data in roles.items():
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name, description=data['description'])
                db.session.add(role)
                
            # 分配权限
            role.permissions = [created_permissions[perm] for perm in data['permissions']]
        
        db.session.commit()
        print('初始角色和权限创建成功!')

    @app.cli.command('create-admin')
    def create_admin():
        """创建管理员用户"""
        from application.models.user import User, Role
        import uuid
        
        admin_email = 'admin@flask-cms.com'
        admin_password = 'admin123'  # 生产环境应使用更复杂的密码
        
        # 检查用户是否已存在
        admin = User.query.filter_by(email=admin_email).first()
        if admin:
            print(f'管理员用户 {admin_email} 已存在')
            return
        
        # 获取admin角色
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print('未找到admin角色，请先运行 create-roles 命令')
            return
        
        # 创建管理员用户
        admin = User(
            username='admin',
            email=admin_email,
            password=admin_password,
            active=True,
            fs_uniquifier=uuid.uuid4().hex
        )
        admin.roles = [admin_role]
        
        db.session.add(admin)
        db.session.commit()
        
        print(f'管理员用户创建成功! 邮箱: {admin_email}, 密码: {admin_password}') 