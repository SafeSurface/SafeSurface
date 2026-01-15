# SafeSurface Web Frontend

基于 Next.js + React + TypeScript + Ant Design Pro 开发的 SafeSurface AI Agent 渗透测试平台前端。

## 技术栈

- **框架**: Next.js 14 (App Router)
- **UI库**: React 18
- **组件库**: Ant Design Pro 5.x
- **样式**: Tailwind CSS 3.x
- **语言**: TypeScript
- **包管理**: pnpm

## 快速开始

### 安装依赖

```bash
pnpm install
```

### 开发模式

```bash
pnpm dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看项目。

### 构建生产版本

```bash
pnpm build
pnpm start
```

## 页面结构

- `/` - 首页（自动重定向到 Welcome）
- `/welcome` - 欢迎页面
- `/login` - 登录页面
- `/dashboard` - 仪表盘（主控制台）

## 功能特性

### Welcome 页面
- 产品介绍
- 核心特性展示
- 统计数据展示
- 响应式设计

### Login 页面
- 用户登录表单
- 表单验证
- 社交登录选项（GitHub, Google）
- 找回密码功能

### Dashboard 页面
- 实时统计数据
- AI Agent 运行状态监控
- 扫描任务管理
- 漏洞统计
- 响应式侧边栏导航

## 主题配置

项目使用 Ant Design 暗黑主题，配色方案：
- 主色调: `#7c4dff` (紫色)
- 背景色: `#0a0a0a` (深黑)
- 卡片背景: `#1f1f1f` (灰黑)

## 项目结构

```
apps/web/
├── app/               # Next.js App Router
│   ├── dashboard/     # 仪表盘页面
│   ├── login/         # 登录页面
│   ├── welcome/       # 欢迎页面
│   ├── globals.css    # 全局样式
│   ├── layout.tsx     # 根布局
│   └── page.tsx       # 首页
├── public/            # 静态资源
├── next.config.js     # Next.js 配置
├── tailwind.config.ts # Tailwind 配置
├── tsconfig.json      # TypeScript 配置
└── package.json       # 项目依赖
```

## 开发规范

- 使用 TypeScript 严格模式
- 遵循 ESLint 规则
- 使用 Ant Design 组件优先
- Tailwind CSS 用于布局和间距
- 组件采用函数式 + Hooks

## 下一步开发

- [ ] 完善登录逻辑和认证
- [ ] 添加更多 Dashboard 功能
- [ ] 实现扫描任务创建和管理
- [ ] 添加漏洞详情页面
- [ ] 集成报告生成功能
- [ ] 添加实时 WebSocket 通信
- [ ] 优化移动端响应式体验

## License

© 2026 SafeSurface