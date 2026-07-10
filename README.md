# TasteWise

TasteWise 是一个 **专为本校食堂设计的菜品推荐系统**。与美团等外卖软件不同，外卖平台只收录商业餐厅，不包含高校基本伙食堂；TasteWise 则覆盖一食堂、二食堂的全部基本伙周菜谱和风味窗口菜品，帮助学生解决"今天吃什么"的选择困难。

用户输入自己对酸、甜、苦、辣、咸五味的偏好后，系统会结合食堂、价格和推荐算法筛选菜品，并给出匹配度与推荐理由。

当前版本使用 Streamlit 构建网页界面，使用 CSV 文件保存菜品数据和用户反馈。项目已经抽出简单的数据访问层，后续可以更方便地把 CSV 替换为 SQLite、MySQL、PostgreSQL 或后端 API。

## 主要功能

- 五味偏好输入：通过滑块设置酸、甜、苦、辣、咸偏好
- 权重控制：可调整不同味道在推荐中的重要性
- 食堂筛选：按不同食堂过滤候选菜品
- 价格筛选：按预算范围过滤菜品
- 推荐算法：支持加权欧氏距离和余弦相似度
- 推荐结果：展示 Top-K 菜品、匹配度、食堂窗口、价格和推荐理由
- 用户反馈：记录喜欢、不喜欢、收藏行为
- 数据层封装：通过 `CsvDataStore` 统一读取菜品和写入反馈，便于后续更换数据库

## 页面预览

启动后访问本地页面：

```text
http://127.0.0.1:8501
```

页面包含：

- 顶部产品介绍和数据概览
- 左侧用户信息、食堂、价格和算法筛选
- 中间五味偏好设置
- 下方推荐结果卡片和反馈按钮

## 项目结构

```text
TasteWise/
├── app.py                 # Streamlit 网页入口
├── data_manager.py        # 数据读取、校验和反馈写入
├── recommender.py         # 推荐主逻辑
├── requirements.txt       # Python 依赖
├── README.md              # 项目说明
├── LICENSE
├── data/
│   ├── dishes.csv         # 菜品数据
│   ├── users.csv          # 用户数据预留
│   └── interactions.csv   # 用户反馈记录
├── utils/
│   ├── __init__.py
│   ├── similarity.py      # 相似度和匹配度计算
│   └── explanation.py     # 推荐理由生成
└── tests/
    ├── conftest.py
    └── test_recommender.py
```

## 快速开始

### 方法一：一键启动（推荐 ⭐）

**Windows (cmd)** — 双击或执行：
```batch
cd TasteWise
start.bat
```

**Windows (PowerShell):**
```powershell
cd TasteWise
.\start.ps1
```
> 如果提示"无法加载文件"，先执行：`Set-ExecutionPolicy -Scope Process Bypass`

**macOS / Linux:**
```bash
cd TasteWise
chmod +x start.sh
./start.sh
```

启动脚本会自动完成：✅ 检测 Python → ✅ 创建虚拟环境 → ✅ 安装依赖 → ✅ 启动应用。

启动成功后，终端会输出：
```
Local URL: http://localhost:8501
```

浏览器会自动打开这个地址，那就是 TasteWise 的界面。

### 方法二：手动分步启动

```powershell
# 1. 进入项目目录
cd TasteWise

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
#    Windows (cmd):  .venv\Scripts\activate.bat
#    Windows (PS):   .\.venv\Scripts\Activate.ps1
#    Mac/Linux:      source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动应用
streamlit run app.py
```

启动成功后，浏览器通常会自动打开页面。如果没有自动打开，可以手动访问：

```text
http://127.0.0.1:8501
```

### 停止应用

在终端中按 `Ctrl + C`，或直接关闭启动脚本的窗口。

## 运行测试

```powershell
pytest -q
```

测试主要覆盖推荐算法、Top-K 返回结果和价格筛选逻辑。

## 数据说明

### 菜品数据

`data/dishes.csv` 是当前推荐系统的核心数据源。

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

新增菜品时，请保证字段名不变，五味评分保持在 1 到 5 之间。

### 用户反馈数据

`data/interactions.csv` 用于记录用户行为。

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

系统会把距离归一化为 0 到 100 的匹配度。分数越高，代表菜品五味画像越接近用户偏好。

### 余弦相似度

```text
similarity = (u · d) / (||u|| * ||d||)
```

余弦相似度更关注用户偏好和菜品画像的整体方向是否相似。

## 为后续数据库改造做准备

当前项目的数据入口集中在 `data_manager.py`：

- `CsvDataStore.load_dishes()`：读取并校验菜品数据
- `CsvDataStore.append_interaction()`：写入用户反馈
- `load_dishes()` 和 `append_interaction()`：供页面层调用的兼容函数

如果后续要迁移到数据库，建议新增一个数据源类，例如：

```python
class SqlDataStore:
    def load_dishes(self):
        ...

    def append_interaction(self, user_id, dish_id, action):
        ...
```

然后把 `data_store = CsvDataStore()` 替换成新的实现。这样 `app.py` 和 `recommender.py` 基本不需要改动。

建议的数据库表：

- `dishes`：保存菜品基础信息和五味评分
- `users`：保存用户信息
- `interactions`：保存喜欢、不喜欢、收藏等反馈行为
- `user_profiles`：保存用户长期五味偏好画像

## 后续路线

- V0.2：加入菜品图片和五味雷达图
- V0.3：根据用户反馈自动更新用户画像
- V0.4：加入协同过滤或热门菜品召回
- V0.5：接入 SQLite 或 MySQL
- V0.6：商家登录与菜谱自助管理（进行中）
- V1.0：形成混合推荐系统和完整后端 API，支持食堂窗口自主运营

## License

本项目基于 **MIT License** 开源。

你可以在遵守以下条件的前提下，自由地使用、修改、分发本软件：

- **使用**：可以用于个人学习、教学或商业项目
- **修改**：可以根据需要修改源代码
- **分发**：可以重新分发原始或修改后的版本
- **署名**：分发时需保留原始的版权声明和许可声明

完整许可文本请参见根目录的 [`LICENSE`](LICENSE) 文件。

> MIT 是一种宽松的开源许可证，只要求保留版权和许可声明，不限制后续的使用和分发方式。
