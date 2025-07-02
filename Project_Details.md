
# GitHub 热门项目跟踪系统

这是一个用于跟踪和分析GitHub热门项目的系统，包含后端爬虫和数据分析功能，以及基于Vue的前端界面。系统可以自动抓取GitHub每日和每周热门项目，生成数据分析报告，并通过Web界面直观展示。

## 系统功能

- 抓取 GitHub 每日和每周热门项目数据
- 自动保存项目数据到 JSON 文件
- 分析项目数据，包括语言分布、星标数等统计信息
- 生成可视化报告，包括语言分布图、星标分布图和项目创建时间分布图
- 支持定时任务，可以按计划自动抓取数据
- 提供Web界面展示执行记录、数据分析结果和热门项目列表
- 支持通过Web界面手动触发抓取任务和设置自动计划任务

## 安装

1. 克隆或下载本项目
2. 安装依赖库：

```bash
pip install -r requirements.txt
```

## 使用方法

### 运行一次抓取

```bash
python main.py --mode once
```

### 按周期抓取

```bash
# 只抓取日榜
python main.py --mode once --period daily

# 只抓取周榜
python main.py --mode once --period weekly
```

### 定时运行

```bash
# 使用默认时间（每天8:00抓取日榜，每周一9:00抓取周榜）
python main.py --mode schedule

# 自定义抓取时间
python main.py --mode schedule --daily-time "10:00" --weekly-time "11:00"
```

## 数据和可视化

- 抓取的数据保存在 `data` 目录下的 JSON 文件中
- 可视化报告保存在 `data/visualizations` 目录下

## 项目结构

- `github_trending.py`: GitHub 趋势项目抓取核心类
- `visualizer.py`: 数据可视化模块
- `scheduler.py`: 定时任务调度器
- `main.py`: 主程序，整合所有功能
- `requirements.txt`: 项目依赖库列表

## 技术栈

*   **数据库**: MySQL

## 注意事项

- GitHub API 有请求频率限制，建议添加个人 Token 以提高限制
- 在 `github_trending.py` 文件中的 `__init__` 方法中添加您的 GitHub Token：

```python
self.headers["Authorization"] = "token YOUR_GITHUB_TOKEN"
```
 **生成个人访问令牌**：
        *   访问 GitHub 个人设置 -> Developer settings -> Personal access tokens -> Tokens (classic)。
        *   点击“Generate new token”或“Generate new token (classic)”。
        *   为 Token 命名（例如：`GitHub StarHub Token`），并授予必要的权限（至少需要 `public_repo` 或 `repo` 权限，具体取决于您需要访问的仓库类型）。
        *   生成后，请务必复制您的 Token，因为它只会显示一次。

## 自定义

您可以根据需要修改以下参数：

- 在 `github_trending.py` 中修改 `per_page` 参数以调整每次抓取的项目数量
- 在 `visualizer.py` 中修改可视化图表的样式和大小
- 在 `main.py` 中修改定时任务的时间设置