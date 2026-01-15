# SafeSurface 仓库拆分 - 快速指南

## 🎯 目标

将当前的 monorepo 拆分为三个独立的 GitHub 仓库:
- `SafeSurface` - 主仓库(包含文档)
- `SafeSurface-Backend` - 后端代码
- `SafeSurface-Web` - 前端代码

## ⚡ 快速开始(推荐)

### 使用自动化脚本

```powershell
# 在 SafeSurface 目录下执行
cd e:/code/SafeSurface

# 运行拆分脚本
.\scripts\split-repos.ps1 -GithubUsername "YOUR_GITHUB_USERNAME"
```

脚本会:
1. ✅ 创建 `SafeSurface-Backend-temp` 和 `SafeSurface-Web-temp` 目录
2. ✅ 复制代码并初始化 Git 仓库
3. ✅ 配置远程仓库地址
4. ℹ️ 显示后续操作命令

### 然后按照脚本提示:

1. **在 GitHub 创建两个空仓库** (不要初始化任何文件):
   - `SafeSurface-Backend`
   - `SafeSurface-Web`

2. **推送后端代码**:
```powershell
cd e:/code/SafeSurface-Backend-temp
git push -u origin main
```

3. **推送前端代码**:
```powershell
cd e:/code/SafeSurface-Web-temp
git push -u origin main
```

4. **更新主仓库**:
```powershell
cd e:/code/SafeSurface

# 删除旧的 apps 目录
git rm -rf apps/backend apps/web
git commit -m "refactor: remove apps directories before adding submodules"

# 添加子模块
git submodule add https://github.com/YOUR_USERNAME/SafeSurface-Backend.git apps/backend
git submodule add https://github.com/YOUR_USERNAME/SafeSurface-Web.git apps/web

# 提交并推送
git add .
git commit -m "refactor: migrate to multi-repo architecture"
git push
```

## 🔄 其他开发者如何使用

### 首次克隆

```powershell
# 方式 1: 包含子模块
git clone --recursive https://github.com/YOUR_USERNAME/SafeSurface.git

# 方式 2: 先克隆后初始化
git clone https://github.com/YOUR_USERNAME/SafeSurface.git
cd SafeSurface
git submodule update --init --recursive
```

### 更新子模块

```powershell
# 更新所有子模块到最新版本
git submodule update --remote --merge

# 或者进入子模块手动更新
cd apps/backend
git pull origin main
```

### 在子模块中开发

```powershell
# 1. 进入子模块
cd apps/backend

# 2. 创建分支并开发
git checkout -b feature/new-feature
# ... 修改代码 ...
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 3. 回到主仓库更新引用
cd ../..
git add apps/backend
git commit -m "chore: update backend submodule"
git push
```

## 🛠️ 手动操作(不使用脚本)

如果不想使用脚本,可以查看 [SPLIT_GUIDE.md](./SPLIT_GUIDE.md) 获取详细的手动操作步骤。

## ⚠️ 注意事项

1. **备份**: 操作前建议备份整个 SafeSurface 目录
2. **环境变量**: 确保每个仓库都有 `.env.example` 文件
3. **CI/CD**: 需要为每个仓库单独配置
4. **依赖**: 前后端现在完全独立

## 📊 对比:Monorepo vs Multi-repo

| 特性 | Monorepo (当前) | Multi-repo (拆分后) |
|------|----------------|---------------------|
| 代码管理 | 统一管理 | 分别管理 |
| 版本控制 | 单一版本 | 各自版本 |
| CI/CD | 统一配置 | 分别配置 |
| 部署 | 一起部署 | 独立部署 |
| 团队协作 | 容易冲突 | 减少冲突 |
| 学习曲线 | 简单 | 需要了解 submodules |

## 🤔 推荐方案

**如果您的情况是:**
- ✅ 前后端需要独立部署
- ✅ 不同团队维护前后端
- ✅ 发布周期不同

**建议:** 使用 Multi-repo (Git Submodules)

**如果您的情况是:**
- ✅ 前后端紧密耦合
- ✅ 同一团队维护
- ✅ 同时部署

**建议:** 保持 Monorepo

## 📚 相关文档

- [完整拆分指南](./SPLIT_GUIDE.md)
- [Git Submodules 文档](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
