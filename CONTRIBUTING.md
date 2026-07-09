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

## 发布前检查

发布版本前请确认：

- 核心推荐流程可以运行
- README 与实际项目一致
- 数据文件格式正确
- 主要测试通过
- Release Notes 说明了功能、使用方法和已知问题
