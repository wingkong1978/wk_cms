#!/usr/bin/env python
"""
应用初始化脚本 - 执行此脚本将初始化数据库并创建基础数据
"""
from application import create_app, db, init_db
import click

@click.command()
def init():
    """初始化应用程序"""
    click.echo("开始初始化应用程序...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 初始化数据库表
        click.echo("初始化数据库表结构...")
        db.drop_all()  # 谨慎使用！这会删除所有现有数据
        db.create_all()
        click.echo("数据库表结构创建成功!")
        
        # 创建基础角色和权限
        click.echo("创建基础角色和权限...")
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
        
        created_permissions = {}
        for name, description in permissions.items():
            permission = Permission(name=name, description=description)
            db.session.add(permission)
            created_permissions[name] = permission
        
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
        
        for name, data in roles.items():
            role = Role(name=name, description=data['description'])
            role.permissions = [created_permissions[perm] for perm in data['permissions']]
            db.session.add(role)
        
        db.session.commit()
        click.echo("角色和权限创建成功!")
        
        # 创建管理员用户
        click.echo("创建管理员用户...")
        from application.models.user import User
        import uuid
        
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin',
            email='admin@flask-cms.com',
            password='admin123',  # 生产环境应使用更复杂的密码
            active=True,
            fs_uniquifier=uuid.uuid4().hex
        )
        admin.roles = [admin_role]
        
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f"管理员用户创建成功! 邮箱: admin@flask-cms.com, 密码: admin123")
        click.echo("应用程序初始化完成!")

if __name__ == '__main__':
    init() 