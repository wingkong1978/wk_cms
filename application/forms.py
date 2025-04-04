from flask_security.forms import RegisterForm, StringField, Required, unique_user_email
from wtforms.validators import DataRequired, Length, Regexp, Email, ValidationError
from flask_security.utils import hash_password, get_message
from flask_security.forms import get_form_field_label
from flask import current_app

class ExtendedRegisterForm(RegisterForm):
    """扩展Flask-Security注册表单，添加username字段"""
    username = StringField(
        '用户名', 
        validators=[
            DataRequired('用户名不能为空'),
            Length(min=3, max=80, message='用户名长度必须在3-80个字符之间'),
            Regexp('^[A-Za-z0-9_-]+$', message='用户名只能包含字母、数字、下划线和连字符')
        ]
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired('邮箱不能为空'),
            Email('邮箱格式不正确'),
            unique_user_email
        ]
    )
    
    def validate_username(self, field):
        """验证用户名是否唯一"""
        from application.models.user import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')

    def validate(self, extra_validators=None):
        """验证表单"""
        return super().validate(extra_validators=extra_validators)
        
    def to_dict(self, only_user=None):
        """扩展to_dict方法以包含username字段
        
        only_user参数是Flask-Security传递的，用于获取仅与用户模型相关的字段
        """
        data = super().to_dict(only_user=only_user)
        data['username'] = self.username.data
        return data 