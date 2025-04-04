from datetime import datetime
from flask_security import UserMixin, RoleMixin
from application import db

# 用户-角色关联表（多对多）
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

# 角色-权限关联表（多对多）
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)

class Permission(db.Model, RoleMixin):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class Role(db.Model, RoleMixin):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # 角色-权限关联（多对多）
    permissions = db.relationship('Permission', secondary=role_permissions,
                            backref=db.backref('roles', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model, UserMixin):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255))  # Flask-Security-Too会处理密码哈希
    active = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用户身份验证相关字段
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer, default=0)
    
    # 用户-角色关联（多对多）
    roles = db.relationship('Role', secondary=user_roles,
                          backref=db.backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def has_role(self, role):
        """检查用户是否拥有指定角色"""
        if isinstance(role, str):
            return role in [r.name for r in self.roles]
        return super(User, self).has_role(role)
    
    def has_permission(self, permission):
        """检查用户是否拥有指定权限"""
        if isinstance(permission, str):
            for role in self.roles:
                if permission in [p.name for p in role.permissions]:
                    return True
            return False
        return any(permission in role.permissions for role in self.roles) 