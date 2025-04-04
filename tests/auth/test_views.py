import pytest
from flask import url_for
from flask_security import url_for_security
from flask_security.utils import login_user, logout_user

def test_profile_page_access(app, client, admin_user):
    """测试个人资料页面访问控制"""
    with app.app_context():
        # 未登录用户应该被重定向到登录页面
        response = client.get(url_for('auth.profile'), follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location
        
        # 登录用户应该可以访问
        login_user(admin_user)
        response = client.get(url_for('auth.profile'))
        assert response.status_code == 200
        assert '个人资料' in response.data.decode('utf-8')
        logout_user()

def test_user_list_access(app, client, admin_user, editor_user):
    """测试用户列表页面的访问控制"""
    with app.app_context():
        # 未登录用户应该被重定向到登录页面
        response = client.get(url_for('auth.user_list'), follow_redirects=False)
        assert response.status_code == 302

        # 编辑用户不应该有权限访问用户列表
        login_user(editor_user)
        response = client.get(url_for('auth.user_list'), follow_redirects=True)
        assert response.status_code == 403  # 应该返回403 Forbidden
        assert 'Forbidden' in response.data.decode('utf-8')

        # 管理员应该可以访问用户列表
        login_user(admin_user)
        response = client.get(url_for('auth.user_list'), follow_redirects=True)
        assert response.status_code == 200
        assert '用户管理' in response.data.decode('utf-8')

def test_login_view(app, client):
    """测试登录视图"""
    with app.app_context():
        # 获取登录页面
        response = client.get(url_for_security('login'))
        assert response.status_code == 200
        assert '登录' in response.data.decode('utf-8')
        
        # 获取CSRF令牌
        csrf_token = response.data.decode('utf-8').split('name="csrf_token"')[1].split('value="')[1].split('"')[0]
        
        # 测试登录表单
        response = client.post(url_for_security('login'), data={
            'email': 'admin@example.com',
            'password': 'password',
            'remember': 'y',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert response.status_code == 200

def test_register_view(app, client):
    """测试注册视图"""
    with app.app_context():
        # 导入 url_for_security
        from flask_security import url_for_security
        
        # 获取注册页面
        response = client.get(url_for_security('register'))
        assert response.status_code == 200
        assert '注册' in response.data.decode('utf-8')
        
        # 获取CSRF令牌
        csrf_token = response.data.decode('utf-8').split('name="csrf_token"')[1].split('value="')[1].split('"')[0]
        
        # 测试注册表单
        form_data = {
            'email': 'newuser@example.com',
            'password': 'password',
            'password_confirm': 'password',
            'username': 'newuser',
            'csrf_token': csrf_token
        }
        print("\nSubmitting form data:", form_data)
        
        # 调试信息：打印 Flask-Security 注册路径
        register_url = url_for_security('register')
        print(f"\nRegister URL: {register_url}")
        
        response = client.post(register_url, data=form_data, follow_redirects=True)
        print("\nResponse status:", response.status_code)
        print("\nResponse content:", response.data.decode('utf-8'))
        
        # 捕获内部服务器错误的详细信息
        if response.status_code == 500:
            import traceback
            import sys
            print("\nTraceback from the most recent exception:")
            try:
                print(traceback.format_exception(*sys.exc_info()))
            except:
                print("无法获取异常信息")
        
        assert response.status_code == 200
        
        # 验证用户是否被创建
        from application.models.user import User
        user = User.query.filter_by(email='newuser@example.com').first()
        if user is None:
            # 打印所有用户以进行调试
            all_users = User.query.all()
            print("\nAll users in database:")
            for u in all_users:
                print(f"User: {u.username}, Email: {u.email}")
            
            # 打印表单验证错误
            from application.forms import ExtendedRegisterForm
            form = ExtendedRegisterForm(data=form_data)
            if not form.validate():
                print("\nForm validation errors:")
                for field, errors in form.errors.items():
                    print(f"{field}: {', '.join(errors)}")
        
        assert user is not None, "User was not created"
        assert user.username == 'newuser', "Username was not saved correctly" 