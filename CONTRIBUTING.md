# Contributing to TasteWise

感谢你参与 TasteWise 项目。本项目是一个课程实践型开源项目，目标是在有限时间内完成一个真实、可运行、可协作的小型软件项目。

## 协作流程

建议所有改动都围绕 GitHub Issue 展开：

```text
查看或创建 Issue
→ 认领任务
→ 创建开发分支
→ 完成本地修改
→ 运行必要检查
→ 提交 Pull Request
→ 其他成员 Review
→ 修改问题
→ 合并并关闭 Issue
```

## 开始开发

1. 从最新 `master` 创建分支。
2. 每个分支只处理一个相对独立的任务。
3. 修改前先阅读相关 Issue，确认完成标准。
4. 修改后运行项目或相关测试，确认核心流程可用。
5. 编写代码时参考 [`CODE_STYLE.md`](CODE_STYLE.md)，保持命名、数据格式和测试习惯一致。

## 分支命名

推荐使用以下格式：

```text
feature/short-description
fix/short-description
docs/short-description
test/short-description
```

示例：

```text
feature/database-schema
fix/empty-recommendations
docs/update-readme
test/recommender-cases
```

## 提交信息

提交信息应简短说明改动目的：

```text
docs: add contributing guide
feat: add dish search filter
fix: handle empty data file
test: add recommender tests
```

## Pull Request 要求

提交 PR 时请说明：

- 本次改动解决了什么问题
- 关联的 Issue 编号
- 做了哪些主要修改
- 如何验证改动

PR 合并前建议至少由一名其他成员检查。

## Review 重点

Review 时重点关注：

- 是否完成 Issue 要求
- 是否能够正常运行
- 是否影响已有功能
- 文档和代码是否容易理解
- 是否需要补充测试或说明

## 本地运行

进入项目目录：

```powershell
cd TasteWise
```

安装依赖：

```powershell
pip install -r requirements.txt
```

启动应用：

```powershell
streamlit run app.py
```

运行测试：

```powershell
pytest -q
```

也可以从仓库根目录运行开发检查脚本：

```powershell
.\scripts\check.ps1
```

如果只修改推荐算法，可以先运行更快的推荐测试：

```powershell
.\scripts\check.ps1 -RecommenderOnly
```

如果系统找不到 `python`，可以显式指定解释器路径：

```powershell
.\scripts\check.ps1 -Python .\TasteWise\.venv\Scripts\python.exe
```

## 发布前检查

发布版本前请确认：

- 核心推荐流程可以运行
- README 与实际项目一致
- 数据文件格式正确
- 主要测试通过
- Release Notes 说明了功能、使用方法和已知问题

---

## 团队成员贡献

> 以下按 GitHub 用户名首字母排序，列出每位成员在本项目中的主要贡献。

### 9dlc1 (dengl)

| 贡献 | 类型 | 说明 |
|------|------|------|
| 项目初始化 | 🏗️ 架构 | 创建 TasteWise 项目骨架、初始菜品数据集、初始 README |
| 贡献指南 | 📖 文档 | 编写 `CONTRIBUTING.md`，规范分支命名、提交信息、PR 流程 |
| Issue 模板 | 📖 文档 | 添加 Feature 和 Bug Report 的 GitHub Issue 模板 |
| 数据文档 | 📖 文档 | 编写 `data/README.md`，说明 CSV 文件用途和字段含义 |
| 故乡感知推荐 (v1) | 🧠 算法 | 首次实现基于用户家乡口味的推荐模块，融合到评分体系 |
| 故乡感知推荐 (v2) | 🧠 算法 | 重构并合并到 master，增加区域关键词加分、推荐理由、测试覆盖 |

### brainreason (Geng Chen)

| 贡献 | 类型 | 说明 |
|------|------|------|
| 技术栈文档 | 📖 文档 | 编写 `TECH_SPEC.md`，记录架构、算法、数据模型、技术决策 |
| PRD 文档 | 📖 文档 | 编写 `PRD.md` 产品需求文档，定义 MVP 范围和功能规格 |
| README 重写 | 📖 文档 | 重写 `TasteWise/README.md`，补充环境配置、流程说明、问题排查 |
| 根目录 README | 📖 文档 | 同步启动步骤到根目录 `README.md`，方便用户直接查看 |
| AGENTS.md | 📖 文档 | 编写 AI 助手工作规范，定义协作流程和安全规范 |
| 一键启动脚本 | ⚙️ 工具 | 添加 `start.bat` / `start.ps1`，简化环境搭建和启动 |
| 食谱列表与历史 | 🖥️ 功能 | 添加菜品列表浏览、搜索筛选、饮食历史记录、已吃排除功能 |
| 登录注册系统 | 🔐 功能 | 实现测试登录、用户注册、会话管理、退出登录 |
| 分类推荐 | 🧠 算法 | 新增主食/饮品小食分类推荐，优化推荐结果展示 |
| 数据清洗 | 🧹 数据 | 修复 7 项菜品数据错误（乱码、残缺名称、错别字） |
| 撤销操作 | ↩️ 功能 | 支持撤销最近一次喜欢/不喜欢/收藏操作 |
| UI 增强 | 🎨 前端 | 算法自动禁用权重、口味重置按钮、菜品分类列显示 |
| License 完善 | 📖 文档 | 添加根目录 LICENSE 文件，扩展 README License 说明 |
| 合并与流程管理 | 🔀 协作 | 负责多次 PR 合并、AGENTS.md 流程修正 |

### heyang070105

| 贡献 | 类型 | 说明 |
|------|------|------|
| 数据收集与合并工具 | ⚙️ 工具 | 编写 `data_importer.py`，支持外部 CSV 数据校验、去重合并、自动备份 |
| 数据采集模板 | 📖 文档 | 生成三种数据类型的 CSV 导入模板（菜品/用户/交互记录） |
| CLI 入口 | ⚙️ 工具 | 提供命令行接口：`generate-templates`、`preview`、`import` |
| 测试覆盖 | 🧪 测试 | 编写 30+ 个 pytest 测试用例，覆盖校验、导入、边界情况 |

### Wgoenyfan

| 贡献 | 类型 | 说明 |
|------|------|------|
| 启动脚本优化 | ⚙️ 工具 | 修复 bat 中 `\a` 转义为响铃符导致的闪退问题，改用 `if not errorlevel 1` 语法 |
| PowerShell 增强 | ⚙️ 工具 | 增加彩色输出和错误处理，创建 `_check_deps.py` 依赖检查脚本 |
| 菜品评论系统 | 💬 功能 | 为菜品添加评论功能，支持发布评论和切换显示/隐藏评论 |

### zpx3284

| 贡献 | 类型 | 说明 |
|------|------|------|
| MVP 核心代码 | 🏗️ 架构 | 实现 TasteWise MVP 全量核心代码：Streamlit 界面、推荐引擎、数据管理 |
| 推荐算法 | 🧠 算法 | 实现加权欧氏距离和余弦相似度两种算法，支持五味权重配置 |
| 推荐理由 | 📝 功能 | 基于偏好接近度自动生成可解释推荐理由 |
| 菜品数据 | 📊 数据 | 采集 656 道真实高校食堂菜品五味画像数据 |
| 单元测试 | 🧪 测试 | 编写核心测试，覆盖精确匹配、Top-K 返回、价格筛选 |
| 推荐历史记忆 | 💾 功能 | 新增推荐历史自动保存与恢复：每次推荐自动存档，登录时恢复上次偏好 |
