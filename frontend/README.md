# 工作追踪器前端

这是一个使用React + TypeScript + TailwindCSS构建的简单工作列表应用。

## 功能特性

- 🎯 展示工作列表
- 🔍 按职位名称、公司名称、工作地点搜索
- 📱 响应式设计，支持移动端和桌面端
- ⚡ 快速加载和搜索

## 技术栈

- **React 19** - 现代化的React框架
- **TypeScript** - 类型安全的JavaScript
- **TailwindCSS** - 实用优先的CSS框架
- **Vite** - 快速的构建工具

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

前端服务将在 `http://localhost:3000` 启动（默认为5173但我们已调整至3000）

### 构建生产版本

```bash
npm run build
```

## API集成

应用集成了后端的`getAllJobs` API，支持以下查询参数：

- `title` - 职位名称
- `company` - 公司名称  
- `location` - 工作地点

## 项目结构

```
src/
├── components/          # React组件
│   ├── JobCard.tsx     # 工作卡片组件
│   └── SearchForm.tsx  # 搜索表单组件
├── services/            # API服务
│   └── jobService.ts   # 工作相关API调用
├── types/               # TypeScript类型定义
│   └── Job.ts          # 工作实体类型
├── App.tsx             # 主应用组件
├── main.tsx            # 应用入口点
└── index.css           # 全局样式
```

## 注意事项

- 确保后端服务在 http://localhost:8080 运行
- 后端需要支持CORS跨域请求
- API路径为 `/api/jobs`
