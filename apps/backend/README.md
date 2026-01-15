# SafeSurface Backend

SafeSurface 后端服务，包含 FastAPI 应用和 Celery 后台任务处理。

## 技术栈

- **FastAPI** - 现代化的 Python Web 框架
- **Celery** - 分布式任务队列
- **SQLAlchemy** - ORM
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和消息队列

## 开发

### 安装依赖

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和 Redis 连接
```

### 启动 API 服务

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动 Worker

```bash
# 启动 Celery Worker
celery -A api.worker.celery_app worker --loglevel=info

# 启动 Celery Beat (定时任务)
celery -A api.worker.celery_app beat --loglevel=info
```

### API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── api/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 统一配置管理
│   ├── api/                 # API 路由
│   │   ├── deps.py          # 依赖注入
│   │   └── v1/              # API v1
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── tasks.py
│   │       └── health.py
│   ├── core/                # 核心功能
│   │   └── security.py      # 认证/授权
│   ├── models/              # 数据模型
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   └── user.py
│   ├── services/            # 业务逻辑
│   │   └── user.py
│   ├── db/                  # 数据库
│   │   ├── base.py
│   │   └── session.py
│   └── worker/              # 后台任务（子模块）
│       ├── celery_app.py    # Celery 配置
│       ├── tasks/           # 任务定义
│       │   ├── security.py
│       │   └── report.py
│       └── utils/           # 工具函数
│           └── logger.py
├── pyproject.toml
├── requirements.txt
└── README.md
```
