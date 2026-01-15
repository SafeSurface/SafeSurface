# SafeSurface 仓库拆分指南

本指南将帮助您将 SafeSurface 从 monorepo 架构迁移到多仓库架构。

## 📋 目标架构

- **SafeSurface** (主仓库) - 文档、架构说明
- **SafeSurface-Backend** (子仓库) - Python FastAPI 后端
- **SafeSurface-Web** (子仓库) - Next.js 前端

## 🚀 实施步骤

### 步骤 1: 在 GitHub 创建三个新仓库

1. **SafeSurface** - 主仓库
2. **SafeSurface-Backend** - 后端代码
3. **SafeSurface-Web** - 前端代码

> 💡 在 GitHub 上创建时,**不要**初始化 README/LICENSE/gitignore,保持空仓库

### 步骤 2: 准备后端仓库

```powershell
# 2.1 创建临时目录
cd e:/code
mkdir SafeSurface-Backend-temp
cd SafeSurface-Backend-temp

# 2.2 使用 git filter-repo 提取 apps/backend 的历史
# (如果保留 git 历史,推荐使用 git filter-repo)
# 安装: pip install git-filter-repo

# 或者简单方式:直接复制文件
cp -r ../SafeSurface/apps/backend/* ./

# 2.3 初始化新仓库
git init
git add .
git commit -m "feat: initial commit for SafeSurface backend"

# 2.4 添加远程仓库并推送
git remote add origin https://github.com/YOUR_USERNAME/SafeSurface-Backend.git
git branch -M main
git push -u origin main
```

### 步骤 3: 准备前端仓库

```powershell
# 3.1 创建临时目录
cd e:/code
mkdir SafeSurface-Web-temp
cd SafeSurface-Web-temp

# 3.2 复制前端代码
cp -r ../SafeSurface/apps/web/* ./

# 3.3 初始化新仓库
git init
git add .
git commit -m "feat: initial commit for SafeSurface frontend"

# 3.4 添加远程仓库并推送
git remote add origin https://github.com/YOUR_USERNAME/SafeSurface-Web.git
git branch -M main
git push -u origin main
```

### 步骤 4: 重构主仓库

```powershell
# 4.1 备份当前仓库
cd e:/code
cp -r SafeSurface SafeSurface-backup

# 4.2 清理 apps 目录
cd SafeSurface
rm -rf apps/backend apps/web

# 4.3 添加子模块
git submodule add https://github.com/YOUR_USERNAME/SafeSurface-Backend.git apps/backend
git submodule add https://github.com/YOUR_USERNAME/SafeSurface-Web.git apps/web

# 4.4 更新 .gitignore (如果需要)
# 添加子模块特定的忽略规则

# 4.5 提交更改
git add .
git commit -m "refactor: migrate to multi-repo architecture with git submodules"

# 4.6 推送到远程
git remote add origin https://github.com/YOUR_USERNAME/SafeSurface.git
git push -u origin main
```

### 步骤 5: 初始化子模块(其他开发者克隆时)

```powershell
# 方式 1: 克隆时包含子模块
git clone --recursive https://github.com/YOUR_USERNAME/SafeSurface.git

# 方式 2: 克隆后初始化子模块
git clone https://github.com/YOUR_USERNAME/SafeSurface.git
cd SafeSurface
git submodule init
git submodule update
```

## 📝 日常开发工作流

### 更新子模块

```powershell
# 进入主仓库
cd e:/code/SafeSurface

# 更新所有子模块到最新版本
git submodule update --remote --merge

# 或者只更新特定子模块
cd apps/backend
git pull origin main
```

### 在子模块中开发

```powershell
# 进入子模块目录
cd e:/code/SafeSurface/apps/backend

# 正常的 git 工作流
git checkout -b feature/new-api
# ... 进行修改 ...
git add .
git commit -m "feat: add new API endpoint"
git push origin feature/new-api

# 回到主仓库更新子模块引用
cd ../..
git add apps/backend
git commit -m "chore: update backend submodule"
git push
```

### 提交子模块的更改

```powershell
# 1. 先在子模块中提交
cd apps/backend
git add .
git commit -m "fix: resolve issue"
git push

# 2. 回到主仓库更新引用
cd ../..
git add apps/backend
git commit -m "chore: update backend to latest commit"
git push
```

## 🔄 替代方案:不使用 Git Submodules

如果您觉得 Git Submodules 太复杂,可以考虑:

### 方案 A: 完全独立的仓库

```
e:/code/
├── SafeSurface/          (文档仓库)
├── SafeSurface-Backend/  (后端仓库)
└── SafeSurface-Web/      (前端仓库)
```

**优点:**
- ✅ 完全独立,互不影响
- ✅ CI/CD 更简单
- ✅ 没有子模块的复杂性

**缺点:**
- ❌ 需要分别克隆三个仓库
- ❌ 文档和代码分离

### 方案 B: pnpm/npm workspaces (推荐用于前端)

如果前端有多个包,可以继续使用 monorepo,但将后端独立:

```
SafeSurface-Frontend/ (monorepo)
├── packages/
│   ├── web/
│   ├── ui-components/
│   └── shared/

SafeSurface-Backend/ (独立仓库)
```

### 方案 C: Git Subtree

类似 submodule 但更简单,不推荐新手使用。

## 📦 配置文件调整

### 主仓库 README.md

\`\`\`markdown
# SafeSurface

Web 应用安全扫描平台

## 仓库结构

- **Frontend**: [SafeSurface-Web](https://github.com/YOUR_USERNAME/SafeSurface-Web)
- **Backend**: [SafeSurface-Backend](https://github.com/YOUR_USERNAME/SafeSurface-Backend)

## 快速开始

\`\`\`bash
# 克隆包含子模块
git clone --recursive https://github.com/YOUR_USERNAME/SafeSurface.git

# 启动后端
cd apps/backend
pip install -r requirements.txt
python start.py

# 启动前端
cd apps/web
pnpm install
pnpm dev
\`\`\`
\`\`\`

### 后端仓库 README.md

\`\`\`markdown
# SafeSurface Backend

Python FastAPI 后端服务

## 技术栈

- FastAPI
- SQLAlchemy (Async)
- PostgreSQL
- Redis
- Celery

## 安装

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## 运行

\`\`\`bash
python start.py
\`\`\`

API 文档: http://localhost:8000/docs
\`\`\`

### 前端仓库 README.md

\`\`\`markdown
# SafeSurface Web

Next.js 前端应用

## 技术栈

- Next.js 14
- React 18
- Ant Design 5
- TailwindCSS

## 安装

\`\`\`bash
pnpm install
\`\`\`

## 运行

\`\`\`bash
pnpm dev
\`\`\`

访问: http://localhost:3000
\`\`\`

## ⚠️ 注意事项

1. **Git 历史保留**: 如果需要保留完整的 git 历史,使用 `git filter-repo` 而不是简单的 `cp`
2. **环境变量**: 确保每个仓库都有自己的 `.env.example` 文件
3. **CI/CD**: 需要为每个仓库单独配置 GitHub Actions
4. **依赖管理**: 后端和前端现在完全独立,无法共享依赖
5. **版本管理**: 建议使用语义化版本号(SemVer)标记各仓库的发布

## 🎯 推荐方案

根据您的情况,我推荐:

**如果团队较小,开发频繁**: 使用 **Git Submodules** (本指南的主要方案)
- 可以在一个工作区同时开发前后端
- 主仓库可以控制子仓库的版本
- 适合紧密耦合的项目

**如果前后端独立部署**: 使用 **完全独立的仓库** (方案 A)
- 各自独立开发和部署
- CI/CD 更简单
- 适合松耦合的项目

## 📚 额外资源

- [Git Submodules 官方文档](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [git-filter-repo 文档](https://github.com/newren/git-filter-repo)
- [Monorepo vs Multi-repo](https://github.com/joelparkerhenderson/monorepo-vs-polyrepo)

---

创建日期: 2026-01-15
