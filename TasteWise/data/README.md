# TasteWise Data

本目录保存 TasteWise 推荐系统当前使用的数据文件。现阶段项目使用 CSV 作为轻量数据源，后续可以迁移到 SQLite、MySQL 或其他数据库。

## 文件说明

| 文件 | 说明 |
|---|---|
| `dishes.csv` | 菜品基础数据，是推荐算法的主要输入 |
| `users.csv` | 演示用户数据，为后续用户画像功能预留 |
| `interactions.csv` | 用户喜欢、不喜欢、收藏等反馈记录 |

## dishes.csv 字段

| 字段 | 说明 |
|---|---|
| `dish_id` | 菜品唯一 ID |
| `name` | 菜品名称 |
| `canteen` | 所属食堂 |
| `window` | 所属窗口或供应时段 |
| `price` | 价格，单位为元 |
| `acid` | 酸味评分，范围 1-5 |
| `sweet` | 甜味评分，范围 1-5 |
| `bitter` | 苦味评分，范围 1-5 |
| `spicy` | 辣味评分，范围 1-5 |
| `salty` | 咸味评分，范围 1-5 |

## 数据维护要求

- `dish_id` 应保持唯一。
- 五味评分应保持在 1 到 5 之间。
- `price` 应使用数字，不要添加货币符号。
- 新增字段前应同步更新 `data_manager.py` 的字段校验逻辑。
- 更新数据后建议至少运行一次推荐流程，确认页面可以正常显示结果。

## 后续数据库迁移建议

如果将 CSV 替换为数据库，建议优先建立以下表：

- `dishes`：菜品基础信息和五味评分
- `users`：用户基础信息和默认偏好
- `interactions`：用户反馈行为
- `daily_menu`：每日供应和库存信息
- `reviews`：用户评分和文字评价

迁移时可保持 `data_manager.py` 对外提供的 `load_dishes()` 和 `append_interaction()` 接口不变，减少页面层和推荐算法的改动。
