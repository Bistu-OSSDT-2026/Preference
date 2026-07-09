from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from data_manager import DATA_DIR, DISHES_PATH, INTERACTIONS_PATH


# ── Schema 常量 ──────────────────────────────────────────────────────────────

DISH_COLUMNS = [
    "dish_id", "name", "canteen", "window", "price",
    "acid", "sweet", "bitter", "spicy", "salty",
]
USER_COLUMNS = [
    "user_id", "username",
    "acid", "sweet", "bitter", "spicy", "salty",
]
INTERACTION_COLUMNS = ["user_id", "dish_id", "action", "timestamp"]

NUMERIC_DISH_COLS = [
    "dish_id", "price", "acid", "sweet", "bitter", "spicy", "salty",
]
NUMERIC_USER_COLS = ["acid", "sweet", "bitter", "spicy", "salty"]

TASTE_COLS = ["acid", "sweet", "bitter", "spicy", "salty"]
VALID_ACTIONS = {"like", "dislike", "favorite"}

USERS_PATH = DATA_DIR / "users.csv"

TEMPLATE_DIR = DATA_DIR / "import_templates"


# ── 数据校验器 ────────────────────────────────────────────────────────────────

class DataValidator:
    """校验待导入 CSV 数据的字段完整性和取值范围。

    所有校验方法均为静态方法，不依赖文件系统。
    """

    # ── 通用工具 ──────────────────────────────────────────────────────────

    @staticmethod
    def _check_missing_columns(
        df: pd.DataFrame,
        expected: list[str],
        label: str,
    ) -> list[str]:
        missing = set(expected) - set(df.columns)
        if missing:
            return [f"[{label}] 缺少字段：{sorted(missing)}"]
        return []

    @staticmethod
    def _check_numeric(
        df: pd.DataFrame,
        columns: list[str],
        label: str,
    ) -> list[str]:
        issues: list[str] = []
        for col in columns:
            if col not in df.columns:
                continue
            try:
                pd.to_numeric(df[col], errors="raise")
            except (ValueError, TypeError) as exc:
                issues.append(f"[{label}] 字段 {col} 包含非数值内容：{exc}")
        return issues

    @staticmethod
    def _check_taste_range(
        df: pd.DataFrame,
        label: str,
    ) -> list[str]:
        issues: list[str] = []
        for col in TASTE_COLS:
            if col not in df.columns:
                continue
            vals = pd.to_numeric(df[col], errors="coerce")
            mask_out_of_range = (vals < 1) | (vals > 5)
            if mask_out_of_range.any():
                bad_indices = df.index[mask_out_of_range].tolist()
                issues.append(
                    f"[{label}] {col} 取值超出 1~5 范围"
                    f"（行 {bad_indices[:6]}…）"
                )
        return issues

    # ── 菜品校验 ──────────────────────────────────────────────────────────

    @staticmethod
    def validate_dishes(df: pd.DataFrame) -> list[str]:
        """校验菜品 DataFrame，返回问题列表。「无问题 → 空列表」"""
        issues: list[str] = []

        issues += DataValidator._check_missing_columns(df, DISH_COLUMNS, "菜品")
        issues += DataValidator._check_numeric(df, NUMERIC_DISH_COLS, "菜品")

        if "dish_id" in df.columns:
            if df["dish_id"].isna().any():
                issues.append("[菜品] dish_id 存在空值")
            if df["dish_id"].duplicated().any():
                dupes = df.loc[df["dish_id"].duplicated(), "dish_id"].tolist()
                issues.append(f"[菜品] dish_id 重复：{dupes}")

        if "name" in df.columns and df["name"].isna().any():
            issues.append("[菜品] name 存在空值")

        if "price" in df.columns:
            prices = pd.to_numeric(df["price"], errors="coerce")
            if (prices <= 0).any():
                issues.append("[菜品] price 存在 ≤0 的值")

        issues += DataValidator._check_taste_range(df, "菜品")

        return issues

    # ── 用户校验 ──────────────────────────────────────────────────────────

    @staticmethod
    def validate_users(df: pd.DataFrame) -> list[str]:
        """校验用户 DataFrame，返回问题列表。"""
        issues: list[str] = []

        issues += DataValidator._check_missing_columns(df, USER_COLUMNS, "用户")

        if "user_id" in df.columns:
            if df["user_id"].isna().any():
                issues.append("[用户] user_id 存在空值")
            if df["user_id"].duplicated().any():
                dupes = df.loc[df["user_id"].duplicated(), "user_id"].tolist()
                issues.append(f"[用户] user_id 重复：{dupes}")

        if "username" in df.columns and df["username"].isna().any():
            issues.append("[用户] username 存在空值")

        issues += DataValidator._check_numeric(df, NUMERIC_USER_COLS, "用户")
        issues += DataValidator._check_taste_range(df, "用户")

        return issues

    # ── 交互记录校验 ──────────────────────────────────────────────────────

    @staticmethod
    def validate_interactions(df: pd.DataFrame) -> list[str]:
        """校验交互记录 DataFrame，返回问题列表。"""
        issues: list[str] = []

        issues += DataValidator._check_missing_columns(
            df, INTERACTION_COLUMNS, "交互",
        )

        if "action" in df.columns:
            invalid = set(df["action"].dropna().unique()) - VALID_ACTIONS
            if invalid:
                issues.append(
                    f"[交互] 非法 action 值：{invalid}"
                    f"（仅允许 {sorted(VALID_ACTIONS)}）",
                )

        if "dish_id" in df.columns:
            try:
                pd.to_numeric(df["dish_id"], errors="raise")
            except (ValueError, TypeError) as exc:
                issues.append(f"[交互] dish_id 包含非数值内容：{exc}")

        return issues


# ── 数据导入器 ────────────────────────────────────────────────────────────────

class DataImporter:
    """将外部 CSV 数据导入并合并到现有数据库中。

    使用示例::

        importer = DataImporter()
        report = importer.import_dishes("new_dishes.csv")
        print(report["summary"])  # 新增 / 跳过 / 错误统计
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self.data_dir = data_dir or DATA_DIR
        self.backup_dir = self.data_dir / "backups"
        self.validator = DataValidator()

    # ── 备份 ──────────────────────────────────────────────────────────────

    def _backup(self, target: Path) -> Path:
        """在目标文件所在目录创建带时间戳的备份。

        Returns:
            备份文件路径。
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{target.stem}_{ts}{target.suffix}"
        backup_path = self.backup_dir / backup_name
        if target.exists():
            shutil.copy2(target, backup_path)
        return backup_path

    # ── 通用合并逻辑 ──────────────────────────────────────────────────────

    @staticmethod
    def _merge_dataframes(
        existing: pd.DataFrame,
        incoming: pd.DataFrame,
        key: str,
        overwrite: bool,
    ) -> tuple[pd.DataFrame, int, int, int]:
        """合并两个 DataFrame。

        Args:
            existing: 现有数据。
            incoming: 待导入数据。
            key: 去重主键列名。
            overwrite: True=覆盖已有记录，False=跳过已有记录。

        Returns:
            (merged_df, added_count, skipped_count, overwritten_count)
        """
        if existing.empty:
            return incoming.copy(), len(incoming), 0, 0

        if incoming.empty:
            return existing.copy(), 0, 0, 0

        existing_keys = set(existing[key].dropna())
        incoming_keys = incoming[key].dropna()

        dup_mask = incoming_keys.isin(existing_keys)

        if overwrite:
            dup_keys = set(incoming_keys[dup_mask])
            merged = existing[~existing[key].isin(dup_keys)].copy()
            merged = pd.concat([merged, incoming], ignore_index=True)
            added = len(incoming) - dup_mask.sum()
            skipped = 0
            overwritten = dup_mask.sum()
        else:
            new_rows = incoming[~dup_mask].copy()
            merged = pd.concat([existing, new_rows], ignore_index=True)
            added = len(new_rows)
            skipped = dup_mask.sum()
            overwritten = 0

        return merged, added, skipped, overwritten

    # ── 导入菜品 ──────────────────────────────────────────────────────────

    def import_dishes(
        self,
        source_path: str | Path,
        *,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """从 CSV 文件导入菜品并合并到 dishes.csv。

        Args:
            source_path: 待导入的 CSV 文件路径。
            overwrite: True 用新数据覆盖已有 dish_id 的记录。
            dry_run: True 只校验和预览，不实际写入。

        Returns:
            报告字典：
            {
                "success": bool,
                "summary": str,
                "added": int,
                "skipped": int,
                "overwritten": int,
                "errors": list[str],
            }
        """
        source_path = Path(source_path)
        report: dict = {
            "success": False,
            "summary": "",
            "added": 0,
            "skipped": 0,
            "overwritten": 0,
            "errors": [],
        }

        # 1. 读取新数据
        try:
            incoming = pd.read_csv(source_path, encoding="utf-8")
        except Exception as exc:
            report["errors"].append(f"读取文件失败：{exc}")
            report["summary"] = f"❌ 读取 {source_path.name} 失败"
            return report

        if incoming.empty:
            report["errors"].append("导入文件为空")
            report["summary"] = "⚠️ 导入文件为空，未执行任何操作"
            return report

        # 2. 校验
        validation_errors = self.validator.validate_dishes(incoming)
        if validation_errors:
            report["errors"].extend(validation_errors)
            report["summary"] = (
                f"❌ 数据校验失败，发现 {len(validation_errors)} 个问题"
            )
            return report

        # 3. 读取现有数据
        existing = pd.DataFrame()
        if DISHES_PATH.exists():
            existing = pd.read_csv(DISHES_PATH, encoding="utf-8")

        # 4. 合并
        merged, added, skipped, overwritten_val = self._merge_dataframes(
            existing, incoming, key="dish_id", overwrite=overwrite,
        )

        report["added"] = added
        report["skipped"] = skipped
        report["overwritten"] = overwritten_val

        # 5. 写入
        if dry_run:
            report["success"] = True
            parts = [f"🔍 预览：将新增 {added} 条菜品"]
            if overwritten_val:
                parts.append(f"覆盖 {overwritten_val} 条")
            if skipped:
                parts.append(f"跳过 {skipped} 条（已存在）")
            report["summary"] = "；".join(parts)
            return report

        self._backup(DISHES_PATH)
        merged.to_csv(DISHES_PATH, index=False, encoding="utf-8")

        report["success"] = True
        parts = [f"✅ 新增 {added} 条菜品"]
        if overwritten_val:
            parts.append(f"覆盖 {overwritten_val} 条")
        if skipped:
            parts.append(f"跳过 {skipped} 条（已存在）")
        report["summary"] = "；".join(parts)
        return report

    # ── 导入用户 ──────────────────────────────────────────────────────────

    def import_users(
        self,
        source_path: str | Path,
        *,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """从 CSV 文件导入用户并合并到 users.csv。

        Args:
            source_path: 待导入的 CSV 文件路径。
            overwrite: True 用新数据覆盖已有 user_id 的记录。
            dry_run: True 只校验和预览，不实际写入。

        Returns:
            报告字典，结构同 import_dishes。
        """
        source_path = Path(source_path)
        report: dict = {
            "success": False,
            "summary": "",
            "added": 0,
            "skipped": 0,
            "overwritten": 0,
            "errors": [],
        }

        # 1. 读取新数据
        try:
            incoming = pd.read_csv(source_path, encoding="utf-8")
        except Exception as exc:
            report["errors"].append(f"读取文件失败：{exc}")
            report["summary"] = f"❌ 读取 {source_path.name} 失败"
            return report

        if incoming.empty:
            report["errors"].append("导入文件为空")
            report["summary"] = "⚠️ 导入文件为空，未执行任何操作"
            return report

        # 2. 校验
        validation_errors = self.validator.validate_users(incoming)
        if validation_errors:
            report["errors"].extend(validation_errors)
            report["summary"] = (
                f"❌ 数据校验失败，发现 {len(validation_errors)} 个问题"
            )
            return report

        # 3. 读取现有数据
        existing = pd.DataFrame()
        if USERS_PATH.exists():
            existing = pd.read_csv(USERS_PATH, encoding="utf-8")

        # 4. 合并
        merged, added, skipped, overwritten_val = self._merge_dataframes(
            existing, incoming, key="user_id", overwrite=overwrite,
        )

        report["added"] = added
        report["skipped"] = skipped
        report["overwritten"] = overwritten_val

        # 5. 写入
        if dry_run:
            report["success"] = True
            parts = [f"🔍 预览：将新增 {added} 个用户"]
            if overwritten_val:
                parts.append(f"覆盖 {overwritten_val} 个")
            if skipped:
                parts.append(f"跳过 {skipped} 个（已存在）")
            report["summary"] = "；".join(parts)
            return report

        self._backup(USERS_PATH)
        merged.to_csv(USERS_PATH, index=False, encoding="utf-8")

        report["success"] = True
        parts = [f"✅ 新增 {added} 个用户"]
        if overwritten_val:
            parts.append(f"覆盖 {overwritten_val} 个")
        if skipped:
            parts.append(f"跳过 {skipped} 个（已存在）")
        report["summary"] = "；".join(parts)
        return report

    # ── 导入交互记录 ──────────────────────────────────────────────────────

    def import_interactions(
        self,
        source_path: str | Path,
        *,
        dry_run: bool = False,
    ) -> dict:
        """从 CSV 文件导入交互记录并追加到 interactions.csv。

        交互记录采用**追加模式**（不做去重），因为同一用户可多次
        对同一菜品执行不同操作。

        Args:
            source_path: 待导入的 CSV 文件路径。
            dry_run: True 只校验和预览，不实际写入。

        Returns:
            报告字典。
        """
        source_path = Path(source_path)
        report: dict = {
            "success": False,
            "summary": "",
            "added": 0,
            "skipped": 0,
            "overwritten": 0,
            "errors": [],
        }

        # 1. 读取新数据
        try:
            incoming = pd.read_csv(source_path, encoding="utf-8")
        except Exception as exc:
            report["errors"].append(f"读取文件失败：{exc}")
            report["summary"] = f"❌ 读取 {source_path.name} 失败"
            return report

        if incoming.empty:
            report["errors"].append("导入文件为空")
            report["summary"] = "⚠️ 导入文件为空，未执行任何操作"
            return report

        # 2. 校验
        validation_errors = self.validator.validate_interactions(incoming)
        if validation_errors:
            report["errors"].extend(validation_errors)
            report["summary"] = (
                f"❌ 数据校验失败，发现 {len(validation_errors)} 个问题"
            )
            return report

        # 3. 读取现有数据
        existing = pd.DataFrame()
        if INTERACTIONS_PATH.exists():
            try:
                existing = pd.read_csv(INTERACTIONS_PATH, encoding="utf-8")
            except Exception:
                pass

        report["added"] = len(incoming)

        # 4. 写入（追加模式）
        if dry_run:
            report["success"] = True
            report["summary"] = f"🔍 预览：将追加 {len(incoming)} 条交互记录"
            return report

        self._backup(INTERACTIONS_PATH)
        merged = pd.concat([existing, incoming], ignore_index=True)
        merged.to_csv(INTERACTIONS_PATH, index=False, encoding="utf-8")

        report["success"] = True
        report["summary"] = f"✅ 已追加 {len(incoming)} 条交互记录"
        return report

    # ── 批量导入 ──────────────────────────────────────────────────────────

    def import_all(
        self,
        dishes_path: Optional[str | Path] = None,
        users_path: Optional[str | Path] = None,
        interactions_path: Optional[str | Path] = None,
        *,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> dict[str, dict]:
        """一次调用导入多种数据。

        Returns:
            {"dishes": {...}, "users": {...}, "interactions": {...}}
            未提供路径的类型返回 None。
        """
        results: dict[str, dict] = {}
        if dishes_path is not None:
            results["dishes"] = self.import_dishes(
                dishes_path, overwrite=overwrite, dry_run=dry_run,
            )
        if users_path is not None:
            results["users"] = self.import_users(
                users_path, overwrite=overwrite, dry_run=dry_run,
            )
        if interactions_path is not None:
            results["interactions"] = self.import_interactions(
                interactions_path, dry_run=dry_run,
            )
        return results


# ── 模板生成工具 ──────────────────────────────────────────────────────────────

def generate_templates(output_dir: Optional[Path] = None) -> dict[str, Path]:
    """生成数据采集模板 CSV 文件（仅表头，用于数据收集）。

    Args:
        output_dir: 模板输出目录，默认为 data/import_templates/。

    Returns:
        {"dishes": Path, "users": Path, "interactions": Path}
    """
    output_dir = Path(output_dir) if output_dir else TEMPLATE_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    created: dict[str, Path] = {}

    dishes_template = output_dir / "dishes_template.csv"
    pd.DataFrame(columns=DISH_COLUMNS).to_csv(
        dishes_template, index=False, encoding="utf-8",
    )
    created["dishes"] = dishes_template

    users_template = output_dir / "users_template.csv"
    pd.DataFrame(columns=USER_COLUMNS).to_csv(
        users_template, index=False, encoding="utf-8",
    )
    created["users"] = users_template

    interactions_template = output_dir / "interactions_template.csv"
    pd.DataFrame(columns=INTERACTION_COLUMNS).to_csv(
        interactions_template, index=False, encoding="utf-8",
    )
    created["interactions"] = interactions_template

    return created


# ── CLI 入口 ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python data_importer.py <command> [args]")
        print("  generate-templates    生成数据采集模板 CSV")
        print("  preview <path>        预览导入（dry-run），自动识别类型")
        print("  import <path>         导入合并，自动识别类型")
        sys.exit(0)

    command = sys.argv[1]
    importer = DataImporter()

    if command == "generate-templates":
        paths = generate_templates()
        for kind, path in paths.items():
            print(f"  ✅ {kind}: {path}")
        print("模板生成完毕。")

    elif command in ("preview", "import"):
        if len(sys.argv) < 3:
            print("请指定待导入的 CSV 文件路径")
            sys.exit(1)
        source = Path(sys.argv[2])
        dry = command == "preview"

        name = source.stem.lower()
        if "dish" in name:
            report = importer.import_dishes(source, dry_run=dry)
        elif "user" in name:
            report = importer.import_users(source, dry_run=dry)
        elif "interact" in name:
            report = importer.import_interactions(source, dry_run=dry)
        else:
            print(f"无法自动识别文件类型，请确保文件名包含 dish/user/interact")
            print(f"文件名：{source.name}")
            sys.exit(1)

        print(report["summary"])
        if report["errors"]:
            print("校验错误：")
            for err in report["errors"]:
                print(f"  - {err}")
    else:
        print(f"未知命令：{command}")
        sys.exit(1)
