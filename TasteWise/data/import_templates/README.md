# 数据采集模板

本目录包含用于收集新数据的 CSV 模板文件。每个模板文件仅包含表头，
可直接用 Excel、Google Sheets 或文本编辑器填写。

## 模板文件

| 文件 | 用途 |
|------|------|
| `dishes_template.csv` | 新增菜品数据 |
| `users_template.csv` | 新增用户数据 |
| `interactions_template.csv` | 新增交互记录 |

## 字段说明

### dishes_template.csv（菜品）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| dish_id | int | 菜品唯一 ID（不可与已有 ID 重复） | 201 |
| name | string | 菜品名称 | 宫保鸡丁 |
| canteen | string | 所属食堂 | 一食堂 |
| window | string | 窗口名称 | 川菜窗口 |
| price | float | 价格（元），必须 > 0 | 12 |
| acid | int | 酸味评分 1~5 | 2 |
| sweet | int | 甜味评分 1~5 | 3 |
| bitter | int | 苦味评分 1~5 | 1 |
| spicy | int | 辣味评分 1~5 | 4 |
| salty | int | 咸味评分 1~5 | 3 |

### users_template.csv（用户）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| user_id | string | 用户唯一标识 | user_zhangsan |
| username | string | 显示名称 | 张三 |
| acid ~ salty | int | 五味偏好 1~5 | 3 |

### interactions_template.csv（交互记录）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| user_id | string | 用户标识 | user_zhangsan |
| dish_id | int | 菜品 ID | 201 |
| action | string | like / dislike / favorite | like |
| timestamp | string | ISO 时间戳 | 2026-07-09T12:00:00 |

## 使用流程

1. 复制模板文件为新文件（如 `new_dishes.csv`）
2. 按表头格式填写数据
3. 使用 `data_importer.py` 导入：

```python
from data_importer import DataImporter

importer = DataImporter()

# 预览（dry-run）
report = importer.import_dishes("data/import_templates/new_dishes.csv", dry_run=True)
print(report["summary"])

# 正式导入
report = importer.import_dishes("data/import_templates/new_dishes.csv")
print(report["summary"])
```

或通过命令行：

```bash
# 预览
python data_importer.py preview data/import_templates/new_dishes.csv

# 导入
python data_importer.py import data/import_templates/new_dishes.csv
```
