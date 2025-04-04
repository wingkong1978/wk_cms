#!/usr/bin/env python
"""
应用启动脚本
"""
from application import create_app, db, init_db

app = create_app()

# 确保在应用启动前初始化数据库
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 