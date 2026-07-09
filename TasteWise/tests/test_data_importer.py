from pathlib import Path
import tempfile

import pandas as pd
import pytest

from data_importer import (
    DataImporter,
    DataValidator,
    DISH_COLUMNS,
    INTERACTION_COLUMNS,
    USER_COLUMNS,
    generate_templates,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 测试夹具
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def tmp_data_dir():
    """创建临时数据目录，测试结束后自动清理。"""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def importer(tmp_data_dir):
    """返回指向临时目录的 DataImporter 实例。"""
    return DataImporter(data_dir=tmp_data_dir)


@pytest.fixture
def sample_dishes_df():
    """3 条合法菜品数据。"""
    return pd.DataFrame([
        {
            "dish_id": 101, "name": "宫保鸡丁", "canteen": "一食堂",
            "window": "川菜窗口", "price": 12,
            "acid": 2, "sweet": 3, "bitter": 1, "spicy": 4, "salty": 3,
        },
        {
            "dish_id": 102, "name": "清蒸鲈鱼", "canteen": "二食堂",
            "window": "粤菜窗口", "price": 18,
            "acid": 1, "sweet": 1, "bitter": 1, "spicy": 1, "salty": 3,
        },
        {
            "dish_id": 103, "name": "红烧肉", "canteen": "一食堂",
            "window": "本帮窗口", "price": 15,
            "acid": 1, "sweet": 4, "bitter": 1, "spicy": 1, "salty": 4,
        },
    ])


@pytest.fixture
def sample_users_df():
    """2 条合法用户数据。"""
    return pd.DataFrame([
        {
            "user_id": "user_a", "username": "张三",
            "acid": 3, "sweet": 4, "bitter": 1, "spicy": 5, "salty": 3,
        },
        {
            "user_id": "user_b", "username": "李四",
            "acid": 1, "sweet": 5, "bitter": 2, "spicy": 1, "salty": 2,
        },
    ])


@pytest.fixture
def sample_interactions_df():
    """2 条合法交互记录。"""
    return pd.DataFrame([
        {
            "user_id": "user_a", "dish_id": 101,
            "action": "like", "timestamp": "2026-07-09T12:00:00",
        },
        {
            "user_id": "user_b", "dish_id": 102,
            "action": "favorite", "timestamp": "2026-07-09T12:30:00",
        },
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# DataValidator — 菜品校验
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateDishes:
    """菜品数据校验测试。"""

    def test_valid_dishes_pass(self, sample_dishes_df):
        errors = DataValidator.validate_dishes(sample_dishes_df)
        assert errors == []

    def test_missing_columns(self):
        df = pd.DataFrame([{"dish_id": 1, "name": "test"}])
        errors = DataValidator.validate_dishes(df)
        assert any("缺少字段" in e for e in errors)

    def test_duplicate_dish_id(self):
        df = pd.DataFrame([
            {"dish_id": 1, "name": "A", "canteen": "X", "window": "W",
             "price": 10, "acid": 1, "sweet": 1, "bitter": 1,
             "spicy": 1, "salty": 1},
            {"dish_id": 1, "name": "B", "canteen": "X", "window": "W",
             "price": 10, "acid": 1, "sweet": 1, "bitter": 1,
             "spicy": 1, "salty": 1},
        ])
        errors = DataValidator.validate_dishes(df)
        assert any("dish_id 重复" in e for e in errors)

    def test_missing_dish_id(self):
        df = pd.DataFrame([
            {"dish_id": None, "name": "A", "canteen": "X", "window": "W",
             "price": 10, "acid": 1, "sweet": 1, "bitter": 1,
             "spicy": 1, "salty": 1},
        ])
        errors = DataValidator.validate_dishes(df)
        assert any("dish_id 存在空值" in e for e in errors)

    def test_missing_name(self):
        df = pd.DataFrame([
            {"dish_id": 1, "name": None, "canteen": "X", "window": "W",
             "price": 10, "acid": 1, "sweet": 1, "bitter": 1,
             "spicy": 1, "salty": 1},
        ])
        errors = DataValidator.validate_dishes(df)
        assert any("name 存在空值" in e for e in errors)

    def test_price_zero_or_negative(self):
        df = pd.DataFrame([
            {"dish_id": 1, "name": "A", "canteen": "X", "window": "W",
             "price": 0, "acid": 1, "sweet": 1, "bitter": 1,
             "spicy": 1, "salty": 1},
        ])
        errors = DataValidator.validate_dishes(df)
        assert any("≤0" in e for e in errors)

    def test_taste_out_of_range(self):
        df = pd.DataFrame([
            {"dish_id": 1, "name": "A", "canteen": "X", "window": "W",
             "price": 10, "acid": 6, "sweet": 1, "bitter": 1,
             "spicy": 1, "salty": 1},
        ])
        errors = DataValidator.validate_dishes(df)
        assert any("1~5" in e for e in errors)

    def test_non_numeric_dish_id(self):
        df = pd.DataFrame([
            {"dish_id": "abc", "name": "A", "canteen": "X", "window": "W",
             "price": 10, "acid": 1, "sweet": 1, "bitter": 1,
             "spicy": 1, "salty": 1},
        ])
        errors = DataValidator.validate_dishes(df)
        assert any("非数值" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════════
# DataValidator — 用户校验
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateUsers:
    """用户数据校验测试。"""

    def test_valid_users_pass(self, sample_users_df):
        errors = DataValidator.validate_users(sample_users_df)
        assert errors == []

    def test_missing_user_id(self):
        df = pd.DataFrame([{
            "user_id": None, "username": "test",
            "acid": 1, "sweet": 1, "bitter": 1, "spicy": 1, "salty": 1,
        }])
        errors = DataValidator.validate_users(df)
        assert any("user_id 存在空值" in e for e in errors)

    def test_duplicate_user_id(self):
        df = pd.DataFrame([
            {"user_id": "u1", "username": "A",
             "acid": 1, "sweet": 1, "bitter": 1, "spicy": 1, "salty": 1},
            {"user_id": "u1", "username": "B",
             "acid": 1, "sweet": 1, "bitter": 1, "spicy": 1, "salty": 1},
        ])
        errors = DataValidator.validate_users(df)
        assert any("user_id 重复" in e for e in errors)

    def test_taste_out_of_range_user(self):
        df = pd.DataFrame([{
            "user_id": "u1", "username": "test",
            "acid": 0, "sweet": 1, "bitter": 1, "spicy": 1, "salty": 1,
        }])
        errors = DataValidator.validate_users(df)
        assert any("1~5" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════════
# DataValidator — 交互校验
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateInteractions:
    """交互记录校验测试。"""

    def test_valid_interactions_pass(self, sample_interactions_df):
        errors = DataValidator.validate_interactions(sample_interactions_df)
        assert errors == []

    def test_invalid_action(self):
        df = pd.DataFrame([{
            "user_id": "u1", "dish_id": 1,
            "action": "invalid_action", "timestamp": "2026-07-09T12:00:00",
        }])
        errors = DataValidator.validate_interactions(df)
        assert any("非法 action" in e for e in errors)

    def test_non_numeric_dish_id_in_interaction(self):
        df = pd.DataFrame([{
            "user_id": "u1", "dish_id": "not_a_number",
            "action": "like", "timestamp": "2026-07-09T12:00:00",
        }])
        errors = DataValidator.validate_interactions(df)
        assert any("非数值" in e for e in errors)

    def test_missing_columns_interactions(self):
        df = pd.DataFrame([{"user_id": "u1", "dish_id": 1}])
        errors = DataValidator.validate_interactions(df)
        assert any("缺少字段" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════════
# DataImporter — 菜品导入
# ═══════════════════════════════════════════════════════════════════════════════

class TestImportDishes:
    """菜品导入合并测试。"""

    def test_import_new_dishes(
        self, importer, sample_dishes_df, tmp_data_dir,
    ):
        src = tmp_data_dir / "new_dishes.csv"
        sample_dishes_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_dishes(src)
        assert report["success"] is True
        assert report["added"] == 3
        assert report["skipped"] == 0

        dishes_path = tmp_data_dir / "dishes.csv"
        assert dishes_path.exists()
        saved = pd.read_csv(dishes_path, encoding="utf-8")
        assert len(saved) == 3

    def test_dry_run_does_not_write(
        self, importer, sample_dishes_df, tmp_data_dir,
    ):
        src = tmp_data_dir / "new_dishes.csv"
        sample_dishes_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_dishes(src, dry_run=True)
        assert report["success"] is True
        assert "预览" in report["summary"]

        dishes_path = tmp_data_dir / "dishes.csv"
        assert not dishes_path.exists()

    def test_skip_existing_dish_ids(
        self, importer, sample_dishes_df, tmp_data_dir,
    ):
        existing = tmp_data_dir / "dishes.csv"
        sample_dishes_df.iloc[:1].to_csv(existing, index=False, encoding="utf-8")

        src = tmp_data_dir / "new_dishes.csv"
        sample_dishes_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_dishes(src, overwrite=False)
        assert report["success"] is True
        assert report["added"] == 2
        assert report["skipped"] == 1

    def test_overwrite_existing_dish_ids(
        self, importer, sample_dishes_df, tmp_data_dir,
    ):
        existing = tmp_data_dir / "dishes.csv"
        old = pd.DataFrame([{
            "dish_id": 101, "name": "旧菜名", "canteen": "一食堂",
            "window": "旧窗口", "price": 5,
            "acid": 1, "sweet": 1, "bitter": 1, "spicy": 1, "salty": 1,
        }])
        old.to_csv(existing, index=False, encoding="utf-8")

        src = tmp_data_dir / "new_dishes.csv"
        sample_dishes_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_dishes(src, overwrite=True)
        assert report["success"] is True
        assert report["added"] == 2
        assert report["overwritten"] == 1

        saved = pd.read_csv(existing, encoding="utf-8")
        row = saved[saved["dish_id"] == 101]
        assert row["name"].values[0] == "宫保鸡丁"

    def test_validation_failure_returns_errors(
        self, importer, tmp_data_dir,
    ):
        bad_df = pd.DataFrame([{"dish_id": 1, "name": "test"}])
        src = tmp_data_dir / "bad_dishes.csv"
        bad_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_dishes(src)
        assert report["success"] is False
        assert len(report["errors"]) > 0

    def test_empty_file(self, importer, tmp_data_dir):
        src = tmp_data_dir / "empty.csv"
        pd.DataFrame(columns=DISH_COLUMNS).to_csv(src, index=False, encoding="utf-8")

        report = importer.import_dishes(src)
        assert report["success"] is False
        assert "为空" in report["summary"]

    def test_backup_created(self, importer, sample_dishes_df, tmp_data_dir):
        existing = tmp_data_dir / "dishes.csv"
        sample_dishes_df.iloc[:1].to_csv(existing, index=False, encoding="utf-8")

        src = tmp_data_dir / "new_dishes.csv"
        sample_dishes_df.to_csv(src, index=False, encoding="utf-8")

        importer.import_dishes(src)

        backup_dir = tmp_data_dir / "backups"
        assert backup_dir.exists()
        backups = list(backup_dir.glob("dishes_*.csv"))
        assert len(backups) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# DataImporter — 用户导入
# ═══════════════════════════════════════════════════════════════════════════════

class TestImportUsers:
    """用户导入合并测试。"""

    def test_import_new_users(
        self, importer, sample_users_df, tmp_data_dir,
    ):
        src = tmp_data_dir / "new_users.csv"
        sample_users_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_users(src)
        assert report["success"] is True
        assert report["added"] == 2

        users_path = tmp_data_dir / "users.csv"
        saved = pd.read_csv(users_path, encoding="utf-8")
        assert len(saved) == 2

    def test_skip_existing_user_ids(
        self, importer, sample_users_df, tmp_data_dir,
    ):
        existing = tmp_data_dir / "users.csv"
        sample_users_df.iloc[:1].to_csv(existing, index=False, encoding="utf-8")

        src = tmp_data_dir / "new_users.csv"
        sample_users_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_users(src, overwrite=False)
        assert report["added"] == 1
        assert report["skipped"] == 1

    def test_overwrite_existing_user(
        self, importer, sample_users_df, tmp_data_dir,
    ):
        existing = tmp_data_dir / "users.csv"
        old = pd.DataFrame([{
            "user_id": "user_a", "username": "旧名字",
            "acid": 1, "sweet": 1, "bitter": 1, "spicy": 1, "salty": 1,
        }])
        old.to_csv(existing, index=False, encoding="utf-8")

        src = tmp_data_dir / "new_users.csv"
        sample_users_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_users(src, overwrite=True)
        assert report["overwritten"] == 1
        saved = pd.read_csv(existing, encoding="utf-8")
        assert saved[saved["user_id"] == "user_a"]["username"].values[0] == "张三"

    def test_dry_run_users(self, importer, sample_users_df, tmp_data_dir):
        src = tmp_data_dir / "new_users.csv"
        sample_users_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_users(src, dry_run=True)
        assert "预览" in report["summary"]
        assert not (tmp_data_dir / "users.csv").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# DataImporter — 交互导入
# ═══════════════════════════════════════════════════════════════════════════════

class TestImportInteractions:
    """交互记录导入测试。"""

    def test_import_new_interactions(
        self, importer, sample_interactions_df, tmp_data_dir,
    ):
        src = tmp_data_dir / "new_interactions.csv"
        sample_interactions_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_interactions(src)
        assert report["success"] is True
        assert report["added"] == 2

        int_path = tmp_data_dir / "interactions.csv"
        saved = pd.read_csv(int_path, encoding="utf-8")
        assert len(saved) == 2

    def test_append_mode_accumulates(
        self, importer, sample_interactions_df, tmp_data_dir,
    ):
        src = tmp_data_dir / "batch1.csv"
        sample_interactions_df.iloc[:1].to_csv(src, index=False, encoding="utf-8")
        importer.import_interactions(src)

        src2 = tmp_data_dir / "batch2.csv"
        sample_interactions_df.iloc[1:].to_csv(src2, index=False, encoding="utf-8")
        report = importer.import_interactions(src2)

        assert report["added"] == 1
        int_path = tmp_data_dir / "interactions.csv"
        saved = pd.read_csv(int_path, encoding="utf-8")
        assert len(saved) == 2

    def test_dry_run_interactions(
        self, importer, sample_interactions_df, tmp_data_dir,
    ):
        src = tmp_data_dir / "new_interactions.csv"
        sample_interactions_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_interactions(src, dry_run=True)
        assert "预览" in report["summary"]
        assert not (tmp_data_dir / "interactions.csv").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# DataImporter — 批量导入
# ═══════════════════════════════════════════════════════════════════════════════

class TestImportAll:
    """批量导入测试。"""

    def test_import_all_three(
        self, importer, sample_dishes_df, sample_users_df,
        sample_interactions_df, tmp_data_dir,
    ):
        dishes_src = tmp_data_dir / "new_dishes.csv"
        users_src = tmp_data_dir / "new_users.csv"
        int_src = tmp_data_dir / "new_interactions.csv"
        sample_dishes_df.to_csv(dishes_src, index=False, encoding="utf-8")
        sample_users_df.to_csv(users_src, index=False, encoding="utf-8")
        sample_interactions_df.to_csv(int_src, index=False, encoding="utf-8")

        results = importer.import_all(
            dishes_path=dishes_src,
            users_path=users_src,
            interactions_path=int_src,
        )

        assert results["dishes"]["success"] is True
        assert results["dishes"]["added"] == 3
        assert results["users"]["success"] is True
        assert results["users"]["added"] == 2
        assert results["interactions"]["success"] is True
        assert results["interactions"]["added"] == 2

    def test_import_all_partial(
        self, importer, sample_dishes_df, tmp_data_dir,
    ):
        """只导入部分类型时，其余不出现在结果中。"""
        dishes_src = tmp_data_dir / "new_dishes.csv"
        sample_dishes_df.to_csv(dishes_src, index=False, encoding="utf-8")

        results = importer.import_all(dishes_path=dishes_src)

        assert results["dishes"]["success"] is True
        assert "users" not in results
        assert "interactions" not in results

    def test_import_all_dry_run(
        self, importer, sample_dishes_df, sample_users_df, tmp_data_dir,
    ):
        dishes_src = tmp_data_dir / "new_dishes.csv"
        users_src = tmp_data_dir / "new_users.csv"
        sample_dishes_df.to_csv(dishes_src, index=False, encoding="utf-8")
        sample_users_df.to_csv(users_src, index=False, encoding="utf-8")

        results = importer.import_all(
            dishes_path=dishes_src,
            users_path=users_src,
            dry_run=True,
        )

        for key in results:
            assert "预览" in results[key]["summary"]

        assert not (tmp_data_dir / "dishes.csv").exists()
        assert not (tmp_data_dir / "users.csv").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# DataImporter — 边界情况
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """边界情况测试。"""

    def test_nonexistent_file(self, importer, tmp_data_dir):
        src = tmp_data_dir / "does_not_exist.csv"
        report = importer.import_dishes(src)
        assert report["success"] is False
        assert "读取" in report["summary"]

    def test_import_to_empty_existing(
        self, importer, sample_dishes_df, tmp_data_dir,
    ):
        """已有文件为空时正常导入。"""
        existing = tmp_data_dir / "dishes.csv"
        existing.write_text("", encoding="utf-8")

        src = tmp_data_dir / "new_dishes.csv"
        sample_dishes_df.to_csv(src, index=False, encoding="utf-8")

        report = importer.import_dishes(src)
        assert report["success"] is True
        assert report["added"] == 3

    def test_full_dishes_row(self):
        """确保 DISH_COLUMNS 常量与预期一致。"""
        assert "dish_id" in DISH_COLUMNS
        assert "name" in DISH_COLUMNS
        assert "canteen" in DISH_COLUMNS
        assert "window" in DISH_COLUMNS
        assert "price" in DISH_COLUMNS
        assert "acid" in DISH_COLUMNS
        assert "sweet" in DISH_COLUMNS
        assert "bitter" in DISH_COLUMNS
        assert "spicy" in DISH_COLUMNS
        assert "salty" in DISH_COLUMNS
        assert len(DISH_COLUMNS) == 10


# ═══════════════════════════════════════════════════════════════════════════════
# 模板生成
# ═══════════════════════════════════════════════════════════════════════════════

class TestGenerateTemplates:
    """模板生成测试。"""

    def test_generate_all_templates(self, tmp_data_dir):
        paths = generate_templates(output_dir=tmp_data_dir)

        assert "dishes" in paths
        assert "users" in paths
        assert "interactions" in paths

        for path in paths.values():
            assert path.exists()
            df = pd.read_csv(path, encoding="utf-8")
            assert len(df) == 0  # 仅表头，无数据行

    def test_dishes_template_columns(self, tmp_data_dir):
        paths = generate_templates(output_dir=tmp_data_dir)
        df = pd.read_csv(paths["dishes"], encoding="utf-8")
        assert list(df.columns) == DISH_COLUMNS

    def test_users_template_columns(self, tmp_data_dir):
        paths = generate_templates(output_dir=tmp_data_dir)
        df = pd.read_csv(paths["users"], encoding="utf-8")
        assert list(df.columns) == USER_COLUMNS

    def test_interactions_template_columns(self, tmp_data_dir):
        paths = generate_templates(output_dir=tmp_data_dir)
        df = pd.read_csv(paths["interactions"], encoding="utf-8")
        assert list(df.columns) == INTERACTION_COLUMNS
