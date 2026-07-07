# 🍜 TasteWise

基于用户对 **酸、甜、苦、辣、咸** 五味喜爱程度的高校食堂菜品推荐系统。

## 功能

- 五味偏好滑块输入
- 五味重要性权重
- 加权欧氏距离推荐
- 余弦相似度推荐
- Top 5 菜品推荐
- 食堂筛选
- 价格筛选
- 0~100% 匹配度
- 可解释推荐理由
- 喜欢 / 不喜欢 / 收藏反馈记录

## 项目结构

```text
TasteWise/
├── app.py
├── recommender.py
├── data_manager.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── data/
│   ├── dishes.csv
│   ├── users.csv
│   └── interactions.csv
├── utils/
│   ├── __init__.py
│   ├── similarity.py
│   └── explanation.py
└── tests/
    └── test_recommender.py
```

## 运行方法

### 1. 进入项目目录

```powershell
cd TasteWise
```

### 2. 创建虚拟环境（推荐）

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

浏览器通常会自动打开本地页面。

## 运行测试

```powershell
pytest -q
```

## 数据格式

`data/dishes.csv` 的核心字段：

| 字段 | 说明 |
|---|---|
| dish_id | 菜品 ID |
| name | 菜名 |
| canteen | 食堂 |
| window | 窗口 |
| price | 价格 |
| acid | 酸度 1~5 |
| sweet | 甜度 1~5 |
| bitter | 苦度 1~5 |
| spicy | 辣度 1~5 |
| salty | 咸度 1~5 |

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

再根据 1~5 评分的理论最大距离归一化为 0~100 匹配度。

### 余弦相似度

```text
similarity = (u · d) / (||u|| * ||d||)
```

适合比较用户与菜品五味向量的整体方向。

## 下一步路线

- V0.2：五味雷达图、菜品图片
- V0.3：根据点赞/点踩自动更新用户画像
- V0.4：协同过滤
- V1.0：混合推荐系统与数据库后端

## License

MIT
