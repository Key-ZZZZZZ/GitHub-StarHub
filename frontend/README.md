# GitHub 热门项目跟踪系统前端

这是一个基于Vue 3开发的GitHub热门项目跟踪系统前端，用于展示每日和每周的GitHub热门项目数据，支持手动执行数据抓取任务和设置自动计划任务。

## 功能特点

- 执行记录：查看历史执行记录，手动触发每日/每周热点项目抓取，设置自动计划任务
- 数据分析：通过图表直观展示GitHub热门项目的语言分布、星标数量和创建时间分布
- 热门项目：查看详细的热门项目列表，支持按语言筛选和关键词搜索
- 系统设置：配置计划任务执行时间和数据存储策略

## 技术栈

- Vue 3：前端框架
- Element Plus：UI组件库
- ECharts：数据可视化图表库
- Axios：HTTP请求库

## 安装与运行

### 前置条件

- Node.js 12.x 或更高版本
- npm 6.x 或更高版本

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式运行

```bash
npm run serve
```

### 构建生产版本

```bash
npm run build
```

## 与后端API交互

前端默认连接到 `http://localhost:5001` 的后端API服务。主要API接口包括：

- `/api/execution-history`：获取执行历史记录
- `/api/run-daily`：手动触发每日任务
- `/api/run-weekly`：手动触发每周任务
- `/api/scheduler-status`：获取调度器状态
- `/api/start-scheduler`：启动计划任务
- `/api/stop-scheduler`：停止计划任务

## 项目结构

```
frontend/
├── public/             # 静态资源
├── src/                # 源代码
│   ├── components/     # 公共组件
│   ├── router/         # 路由配置
│   ├── views/          # 页面组件
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
└── package.json        # 项目配置
```

## 使用说明

1. 确保后端API服务已启动（运行在5001端口）
2. 启动前端开发服务器
3. 在浏览器中访问 `http://localhost:8080`
4. 使用左侧导航菜单访问不同功能模块

## 注意事项

- 前端需要与后端API配合使用，确保后端服务正常运行
- 默认API地址为 `http://localhost:5001`，如需修改请更新相关API调用代码