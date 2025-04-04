#!/usr/bin/env python
"""
迁移重置脚本 - 用于重置数据库迁移环境
警告：此脚本会删除所有表并重新初始化迁移环境
"""
from application import create_app, db
import click
import os
import shutil

@click.command()
@click.option('--force', is_flag=True, help='强制执行，不询问确认')
def reset_migrations(force):
    """重置数据库迁移环境"""
    if not force:
        click.confirm('此操作将删除数据库中的所有数据，确定要继续吗?', abort=True)
    
    click.echo("开始重置迁移环境...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 1. 删除迁移文件夹
        migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')
        if os.path.exists(migrations_dir):
            click.echo("删除现有迁移文件夹...")
            shutil.rmtree(migrations_dir)
            click.echo("迁移文件夹已删除")
        
        # 2. 删除所有表
        click.echo("删除数据库中的所有表...")
        try:
            db.drop_all()
            
            # 特别处理 alembic_version 表
            db.engine.execute("DROP TABLE IF EXISTS alembic_version")
            click.echo("所有表已删除")
        except Exception as e:
            click.echo(f"删除表时出错: {str(e)}")
            try:
                # 使用SQLAlchemy 1.4+的新方法
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
                    conn.commit()
                click.echo("alembic_version表已删除")
            except Exception as e2:
                click.echo(f"删除alembic_version表时出错: {str(e2)}")
        
        # 3. 初始化迁移
        click.echo("初始化新的迁移环境...")
        try:
            import subprocess
            
            # 使用subprocess运行命令而不是直接调用函数
            subprocess.check_call(['flask', 'db', 'init'])
            subprocess.check_call(['flask', 'db', 'migrate', '-m', '初始迁移'])
            
            click.echo("迁移环境初始化成功")
        except Exception as e:
            click.echo(f"初始化迁移时出错: {str(e)}")
            click.echo("尝试使用manage.py初始化迁移...")
            try:
                subprocess.check_call(['python', 'manage.py', 'db', 'init'])
                subprocess.check_call(['python', 'manage.py', 'db', 'migrate', '-m', '初始迁移'])
                click.echo("使用manage.py初始化迁移成功")
            except Exception as e2:
                click.echo(f"使用manage.py初始化迁移失败: {str(e2)}")
        
        # 4. 创建表
        click.echo("创建数据库表...")
        try:
            import subprocess
            subprocess.check_call(['flask', 'db', 'upgrade'])
            click.echo("数据库表创建成功")
        except Exception as e:
            click.echo(f"创建表时出错: {str(e)}")
            try:
                subprocess.check_call(['python', 'manage.py', 'db', 'upgrade'])
                click.echo("使用manage.py创建表成功")
            except Exception as e2:
                click.echo(f"使用manage.py创建表失败: {str(e2)}")
        
        # 5. 创建基础数据
        click.echo("创建基础数据...")
        try:
            # 创建角色和权限
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
            
            # 创建管理员用户
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
            
            click.echo("基础数据创建成功")
        except Exception as e:
            click.echo(f"创建基础数据时出错: {str(e)}")
    
    click.echo("迁移环境重置完成!")

if __name__ == '__main__':
    reset_migrations() 