# GitHub StarHub 热点项目详情

## 1. 项目概述

GitHub StarHub 是一个用于抓取、分析和展示 GitHub项目数据的应用。它能够定期抓取 GitHub 上的热门项目，并对数据进行可视化分析，包括编程语言分布、星标数量分布和项目创建时间分布等。项目分为前后端两部分，后端负责数据抓取、存储和API服务，前端负责数据展示和用户交互。

## 2. 项目功能

*   **GitHub 项目数据抓取**: 定期从 GitHub页面抓取热门项目数据，支持每日和每周趋势数据。
*   **数据存储**: 将抓取到的项目数据存储到 MySQL 数据库中，确保数据持久化。
*   **数据分析与可视化**: 提供多种数据分析图表，包括：
    *   编程语言分布图：展示不同编程语言在热门项目中的占比。
    *   星标数量分布图：分析项目星标数量的分布情况。
    *   项目创建时间分布图：揭示项目创建时间的趋势。
*   **执行记录**: 详细记录每次数据抓取的执行时间、类型、状态、完成时间、总数、星标、更新和耗时等信息，便于监控和审计。
*   **项目详情展示**: 通过交互式弹窗展示单个项目的详细信息，包括项目名称、作者、描述、语言、星标数、捕获时间、URL等。
*   **响应式布局**: 前端界面采用响应式设计，适应不同屏幕尺寸的设备，提供良好的用户体验。

## 3. 技术架构

本项目采用前后端分离的架构，后端提供数据接口和定时任务，前端负责用户界面展示。

### 3.1 后端架构

后端主要由数据抓取模块、数据库管理模块、API服务模块和定时任务调度模块组成。

*   **数据抓取**: `github_trending.py` 负责从 GitHub Trending 页面抓取数据。
*   **数据库**: `db.py` 和 `models.py` 负责数据库的连接、操作和数据模型的定义，使用 MySQL 作为数据库。
*   **API服务**: `api.py` 基于 Flask 框架提供 RESTful API 接口，供前端调用获取数据。
*   **定时任务**: `scheduler.py` 使用 APScheduler 库实现定时抓取 GitHub Trending 数据。
*   **数据可视化**: `visualizer.py` 负责生成数据分析图表。

### 3.2 前端架构

前端基于 Vue.js 框架构建，采用组件化开发，通过 Vue Router 进行路由管理，并使用 Element UI 提供丰富的界面组件。

*   **核心框架**: Vue.js，用于构建用户界面。
*   **UI 组件库**: Element UI，提供美观且功能丰富的 UI 组件，加速开发。
*   **路由管理**: Vue Router，实现单页面应用（SPA）的路由跳转和视图切换。
*   **数据可视化**: 集成 ECharts 等图表库，用于渲染数据分析图表。
*   **组件化**: 页面由多个可复用组件构成，提高代码复用性和可维护性。

## 4. 技术栈

### 后端

*   **语言**: Python
*   **Web 框架**: Flask
*   **数据库**: MySQL
*   **数据抓取**: 自定义脚本
*   **定时任务**: APScheduler
*   **数据可视化**: Matplotlib/Seaborn

### 前端

*   **框架**: Vue.js
*   **UI 组件库**: Element UI
*   **路由**: Vue Router
*   **图表**: ECharts

## 5. 项目代码结构

```
. # 项目根目录
├── README.md
├── api.py                 # 后端API接口定义，提供数据服务
├── db.py                  # 数据库连接和基本操作封装
├── github_trending.py     # GitHub Trending 数据抓取核心逻辑
├── main.py                # 后端主入口文件，启动 Flask 应用
├── models.py              # 数据库模型定义，ORM映射
├── scheduler.py           # 定时任务调度器，负责数据抓取任务的定时执行
├── visualizer.py          # 数据可视化脚本，生成分析图表
├── requirements.txt       # 后端项目依赖列表
├── data/                  # 存储抓取到的原始数据和可视化结果
│   └── visualizations/    # 存储生成的图表图片 (已清理，但结构保留)
└── frontend/              # 前端项目目录
    ├── public/            # 静态资源文件，如 favicon.ico, index.html
    ├── src/               # 前端源码目录
    │   ├── App.vue        # 主应用组件，定义整体布局和导航
    │   ├── main.js        # 前端应用入口文件，初始化 Vue 实例和插件
    │   ├── router/        # Vue Router 路由配置，定义页面路径和组件映射
    │   │   └── index.js
    │   ├── components/    # 可复用组件目录
    │   │   └── ProjectDetailDialog.vue # 项目详情弹窗组件
    │   └── views/         # 页面组件目录，每个文件对应一个主要视图
    │       ├── DataAnalysis.vue # 数据分析页面
    │       ├── ExecutionRecords.vue # 执行记录页面
    │       ├── Settings.vue # 系统设置页面
    │       └── TrendingProjects.vue # 热门项目页面
    ├── package.json       # 前端项目依赖和脚本信息
    ├── package-lock.json  # 锁定前端依赖版本
    └── vue.config.js      # Vue CLI 配置文件，用于自定义 webpack 配置等
```

## 6. 安装与运行

### 6.1 后端

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **初始化数据库**:
    *   在 `db.py` 文件中配置您的 MySQL 数据库连接信息。
*   首次运行或需要重置数据库时，请确保 MySQL 服务已启动，并执行以下命令创建数据库表结构：
        ```bash
        python db.py
        ```
3.  **运行后端服务**:
    ```bash
    python main.py
    ```
    或者运行定时任务（如果需要后台自动抓取数据）：
    ```bash
    python scheduler.py
    ```

### 6.2 前端

1.  **进入前端目录**:
    ```bash
    cd frontend
    ```
2.  **安装依赖**:
    ```bash
    npm install
    ```
3.  **运行前端应用**:
    ```bash
    npm run serve
    ```

## 7. 贡献

欢迎任何形式的贡献！如果您有任何建议或发现 Bug，请随时提出 Issue 或提交 Pull Request。

## 8. 许可证

本项目采用 MIT 许可证。

---

© 2025 GitHub StarHub. All rights reserved. Designed by Key.ZZZZZZ
