#!/usr/bin/env python
"""
Flask应用管理脚本
提供命令行工具用于管理应用，如数据库迁移等
"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from application import create_app, db

app = create_app()
manager = Manager(app)

# 添加数据库迁移命令
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run() 