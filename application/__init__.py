import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
admin = Admin(name='Flask-CMS', template_mode='bootstrap4')

def create_app(config=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置应用
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    # 如果提供了配置对象，则应用它
    if config:
        app.config.from_object(config)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    
    # 注册蓝图
    from application.controllers.main import main_bp
    app.register_blueprint(main_bp)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def page_not_found(e):
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return {'error': 'Internal server error'}, 500 