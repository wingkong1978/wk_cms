# Flask-CMS

一个基于Flask构建的轻量级内容管理系统。

## 功能特点

- 用户认证与权限管理
- 内容管理（文章、分类、标签）
- 后台管理界面
- RESTful API支持
- 响应式前端设计

## 技术栈

- **后端**: Flask, SQLAlchemy, Alembic
- **数据库**: PostgreSQL (可选 MySQL 或 SQLite)
- **缓存**: Redis
- **前端**: HTML5, CSS3, JavaScript
- **部署**: Docker, Gunicorn

## 快速开始

### 使用Docker

```bash
# 克隆仓库
git clone https://github.com/yourusername/flask-cms.git
cd flask-cms

# 启动服务
docker-compose up -d
```

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/yourusername/flask-cms.git
cd flask-cms

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env  # 编辑.env文件设置环境变量

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 运行开发服务器
flask run
```

## 项目结构

```
/application         # 主应用目录
   /controllers      # 控制器层
   /models           # 数据模型层
   /templates        # 视图模板
   /static           # 静态资源
   /services         # 服务层
/doc                 # 文档目录
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件 