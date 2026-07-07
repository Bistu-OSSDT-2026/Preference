# TasteWise

TasteWise 是一个面向高校食堂场景的五味偏好菜品推荐系统。用户输入自己对酸、甜、苦、辣、咸的喜好程度后，系统会结合食堂、价格范围和推荐算法，从菜品数据中生成 Top-K 推荐结果，并展示匹配度与推荐理由。

本项目定位为课程实践中的开源软件 MVP，重点不是追求功能数量或复杂技术栈，而是保证一个核心使用流程能够完整运行，并通过 GitHub Issue、分支、Pull Request、Review 和 Release 体验真实的小组协作过程。

## 项目目标

TasteWise 面向有选择困难、希望快速找到合口味菜品的校园食堂用户。

当前版本解决的问题：

- 用户不知道今天吃什么时，可以根据五味偏好获得推荐
- 用户可以按食堂和预算过滤候选菜品
- 系统可以解释为什么推荐某道菜
- 用户的喜欢、不喜欢、收藏行为可以被记录，为后续个性化优化做准备

## 当前版本范围

本版本优先保证以下核心流程可运行：

```text
用户设置五味偏好
→ 选择食堂、价格范围和推荐算法
→ 系统读取菜品数据
→ 计算菜品匹配度
→ 展示推荐结果和推荐理由
→ 用户记录喜欢、不喜欢或收藏反馈
```

当前已实现：

- Streamlit 网页界面
- 五味偏好滑块输入
- 五味权重高级设置
- 食堂筛选
- 价格筛选
- 推荐数量设置
- 加权欧氏距离推荐
- 余弦相似度推荐
- 推荐理由生成
- 用户反馈记录
- CSV 数据读取和字段校验
- 简单数据访问层，便于后续替换数据库

当前暂不实现：

- 用户注册和登录
- 多人实时协作
- 云端数据库
- 菜品图片上传
- 管理后台
- 自动学习用户长期画像

## 快速开始

### 1. 进入项目目录

```powershell
cd TasteWise
```

### 2. 创建并激活虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止脚本执行，可以先运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

然后再次激活虚拟环境。

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 启动项目

```powershell
streamlit run app.py
```

启动成功后，浏览器通常会自动打开本地页面。也可以手动访问：

```text
http://127.0.0.1:8501
```

## 运行测试

```powershell
pytest -q
```

测试内容主要覆盖：

- 精确匹配时匹配度为 100%
- 推荐结果按 Top-K 返回
- 价格筛选逻辑正确

## 项目结构

```text
TasteWise/
├── app.py                 # Streamlit 页面入口
├── data_manager.py        # 数据读取、字段校验和用户反馈写入
├── recommender.py         # 推荐主逻辑
├── requirements.txt       # 项目依赖
├── README.md              # 项目说明
├── LICENSE                # 开源许可证
├── data/
│   ├── dishes.csv         # 菜品数据
│   ├── users.csv          # 用户数据预留
│   └── interactions.csv   # 用户反馈记录
├── utils/
│   ├── __init__.py
│   ├── similarity.py      # 匹配度和相似度计算
│   └── explanation.py     # 推荐理由生成
└── tests/
    ├── conftest.py
    └── test_recommender.py
```

## 数据格式

### 菜品数据

`data/dishes.csv` 是当前系统的核心数据源。

| 字段 | 类型 | 说明 |
|---|---|---|
| dish_id | int | 菜品唯一 ID |
| name | str | 菜品名称 |
| canteen | str | 所属食堂 |
| window | str | 所属窗口 |
| price | number | 价格，单位为元 |
| acid | int | 酸味评分，范围 1-5 |
| sweet | int | 甜味评分，范围 1-5 |
| bitter | int | 苦味评分，范围 1-5 |
| spicy | int | 辣味评分，范围 1-5 |
| salty | int | 咸味评分，范围 1-5 |

新增菜品时，应保持字段名不变，并保证五味评分位于 1 到 5 之间。

### 用户反馈数据

`data/interactions.csv` 用于记录用户反馈行为。

| 字段 | 类型 | 说明 |
|---|---|---|
| user_id | str | 用户 ID |
| dish_id | int | 菜品 ID |
| action | str | 用户行为，支持 `like`、`dislike`、`favorite` |
| timestamp | str | 记录时间 |

## 推荐算法

### 加权欧氏距离

用户五味画像：

```text
u = [酸, 甜, 苦, 辣, 咸]
```

菜品五味画像：

```text
d = [酸, 甜, 苦, 辣, 咸]
```

加权距离：

```text
distance = sqrt(sum(weight_i * (u_i - d_i)^2))
```

系统会根据 1-5 评分的理论最大距离，把距离归一化为 0-100 的匹配度。分数越高，表示菜品越接近用户偏好。

### 余弦相似度

```text
similarity = (u · d) / (||u|| * ||d||)
```

余弦相似度更关注用户偏好和菜品画像的整体方向是否相似。

## 数据库改造准备

当前项目默认使用 CSV 文件，但数据访问已经集中在 `data_manager.py` 中：

- `CsvDataStore.load_dishes()`：读取并校验菜品数据
- `CsvDataStore.append_interaction()`：写入用户反馈
- `load_dishes()`：页面层读取菜品的兼容入口
- `append_interaction()`：页面层写入反馈的兼容入口

后续如果迁移到 SQLite、MySQL、PostgreSQL 或后端 API，可以新增一个数据源类：

```python
class SqlDataStore:
    def load_dishes(self):
        ...

    def append_interaction(self, user_id, dish_id, action):
        ...
```

然后将：

```python
data_store = CsvDataStore()
```

替换为新的实现即可。这样 `app.py` 和 `recommender.py` 不需要大规模改动。

建议的数据库表：

- `dishes`：菜品基础信息和五味评分
- `users`：用户基础信息
- `interactions`：喜欢、不喜欢、收藏等反馈行为
- `user_profiles`：用户长期五味偏好画像

## 小组协作流程

本项目建议按照课程实践的 12 个开发课时组织协作。实际开发中各阶段可以交叉进行，不需要机械地按顺序完成。

### 第 1 课时：确定项目目标和版本范围

小组应先明确：

- 项目面向什么用户
- 项目解决什么问题
- 用户如何完成核心使用流程
- 当前版本完成哪些内容
- 当前版本暂不完成哪些内容

本项目当前版本的核心目标是：让用户能够输入五味偏好，并获得可解释的食堂菜品推荐。

### 第 2 课时：建立仓库和协作约定

建议完成：

- 建立 GitHub 公开仓库
- 编写 README
- 添加开源许可证
- 确定项目负责人
- 确定基本协作方式

本项目采用的基本流程：

```text
查看或创建 Issue
→ 认领任务
→ 创建开发分支
→ 完成修改和本地检查
→ 提交 Pull Request
→ 其他成员 Review
→ 修改后合并
```

### 第 3 课时：完成项目设计

并行开发前，小组应尽量统一以下内容：

- 核心用户操作流程
- 项目目录结构
- 模块划分
- 数据格式
- 页面布局
- 依赖版本

TasteWise 当前主要模块为：

- `app.py`：负责页面展示和用户交互
- `data_manager.py`：负责数据读取和反馈写入
- `recommender.py`：负责推荐结果计算
- `utils/`：负责相似度计算和推荐理由生成

### 第 4 课时：拆分 Issue

Issue 可以用于记录：

- 新功能
- 开发任务
- 测试任务
- 文档工作
- Bug 修复
- 发布准备

一个 Issue 应尽量说明：

- 要完成什么
- 完成后的结果是什么
- 负责人是谁

### 第 5-8 课时：开发并提交 Pull Request

成员认领任务后，建议围绕 Issue 开发：

```text
Issue → 开发分支 → 完成开发 → 本地检查 → 提交 PR
```

开发过程中可以使用 AI 工具，但提交者需要理解并负责自己的代码和文档改动。

### 第 6-9 课时：进行 PR Review

PR 提交后，应由其他成员检查：

- 是否完成 Issue 要求
- 是否可以正常运行
- 结果是否符合预期
- 是否影响已有功能

建议流程：

```text
提交 PR → Review → 提出问题 → 修改 → 再检查 → 合并
```

### 第 7-10 课时：测试并处理真实问题

建议至少完成：

- 一种自动化检查，例如 GitHub Actions 或本地测试命令
- 一次真实 Bug 的发现、记录、修复和验证流程

Bug 处理流程：

```text
建立 Issue → 修复 → 提交 PR → 验证 → 关闭 Issue
```

### 第 11-12 课时：收尾并发布版本

实践后期应停止继续增加新功能，集中完成：

- 测试
- Bug 修复
- README 和项目文档完善
- Release 准备

发布前检查：

- 核心流程是否可运行
- README 是否正确
- 自动化检查是否通过
- 项目状态是否一致

建议发布版本号：

```text
v0.1.0
```

Release Notes 建议说明：

- 本版本功能
- 使用方法
- 已知问题

## 分支和提交建议

建议分支命名：

```text
feature/issue-number-short-description
fix/issue-number-short-description
docs/issue-number-short-description
```

示例：

```text
docs/update-readme
feature/recommendation-filter
fix/price-filter
```

建议提交信息简洁说明改动：

```text
docs: update project README
feat: add canteen filter
fix: handle empty recommendation result
```

## 后续路线

- V0.2：加入菜品图片和五味雷达图
- V0.3：根据用户反馈自动更新用户画像
- V0.4：加入协同过滤或热门菜品召回
- V0.5：接入 SQLite 或 MySQL
- V1.0：形成混合推荐系统和完整后端 API

## License

MIT
