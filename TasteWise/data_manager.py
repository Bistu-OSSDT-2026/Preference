from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DISHES_PATH = DATA_DIR / "dishes.csv"
INTERACTIONS_PATH = DATA_DIR / "interactions.csv"
USERS_PATH = DATA_DIR / "users.csv"
COMMENTS_PATH = DATA_DIR / "comments.csv"
REQUIRED_DISH_COLUMNS = {
    "dish_id",
    "name",
    "canteen",
    "window",
    "price",
    "acid",
    "sweet",
    "bitter",
    "spicy",
    "salty",
}
NUMERIC_DISH_COLUMNS = [
    "dish_id",
    "price",
    "acid",
    "sweet",
    "bitter",
    "spicy",
    "salty",
]


class CsvDataStore:
    """Small data-access layer so CSV storage can later be replaced cleanly."""

    def __init__(
        self,
        dishes_path: Path = DISHES_PATH,
        interactions_path: Path = INTERACTIONS_PATH,
    ) -> None:
        self.dishes_path = dishes_path
        self.interactions_path = interactions_path

    def load_dishes(self) -> pd.DataFrame:
        if not self.dishes_path.exists():
            raise FileNotFoundError(f"找不到菜品数据：{self.dishes_path}")

        dishes = pd.read_csv(self.dishes_path, encoding="utf-8")
        missing = REQUIRED_DISH_COLUMNS - set(dishes.columns)
        if missing:
            raise ValueError(f"菜品数据缺少字段：{sorted(missing)}")

        for column in NUMERIC_DISH_COLUMNS:
            dishes[column] = pd.to_numeric(dishes[column], errors="raise")

        return dishes

    def append_interaction(self, user_id: str, dish_id: int, action: str) -> None:
        allowed_actions = {"like", "dislike", "favorite"}
        if action not in allowed_actions:
            raise ValueError(f"不支持的行为：{action}")

        self.interactions_path.parent.mkdir(parents=True, exist_ok=True)

        row = pd.DataFrame(
            [
                {
                    "user_id": user_id,
                    "dish_id": int(dish_id),
                    "action": action,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                }
            ]
        )

        write_header = (
            not self.interactions_path.exists()
            or self.interactions_path.stat().st_size == 0
        )
        row.to_csv(
            self.interactions_path,
            mode="a",
            header=write_header,
            index=False,
            encoding="utf-8",
        )


def load_interactions(user_id: str) -> pd.DataFrame:
    """读取 interactions.csv，筛选指定用户，联表菜品名称，按时间倒序返回。"""
    if not INTERACTIONS_PATH.exists():
        return pd.DataFrame()

    interactions = pd.read_csv(INTERACTIONS_PATH, encoding="utf-8")

    if interactions.empty:
        return interactions

    required_cols = {"user_id", "dish_id", "action", "timestamp"}
    missing = required_cols - set(interactions.columns)
    if missing:
        raise ValueError(f"交互数据缺少字段：{sorted(missing)}")

    user_data = interactions[interactions["user_id"] == user_id].copy()
    if user_data.empty:
        return user_data

    user_data["dish_id"] = pd.to_numeric(user_data["dish_id"], errors="raise")

    dishes = load_dishes()
    merged = user_data.merge(
        dishes[["dish_id", "name"]], on="dish_id", how="left"
    )
    merged.rename(columns={"name": "dish_name"}, inplace=True)

    return merged.sort_values("timestamp", ascending=False).reset_index(drop=True)


def get_interacted_dish_ids(user_id: str) -> set[int]:
    """返回用户已交互过的 dish_id 集合。"""
    if not INTERACTIONS_PATH.exists():
        return set()

    interactions = pd.read_csv(INTERACTIONS_PATH, encoding="utf-8")

    if interactions.empty:
        return set()

    required_cols = {"user_id", "dish_id"}
    missing = required_cols - set(interactions.columns)
    if missing:
        raise ValueError(f"交互数据缺少字段：{sorted(missing)}")

    user_data = interactions[interactions["user_id"] == user_id]
    dish_ids = pd.to_numeric(user_data["dish_id"], errors="coerce").dropna()
    return set(int(dish_id) for dish_id in dish_ids.unique())


def load_users() -> pd.DataFrame:
    """读取 users.csv，返回所有用户数据。"""
    if not USERS_PATH.exists():
        return pd.DataFrame()

    users = pd.read_csv(USERS_PATH, encoding="utf-8")
    return users


def register_user(user_id: str, username: str) -> bool:
    """注册新用户，写入 users.csv。返回 True 表示成功，False 表示用户已存在。"""
    existing = load_users()
    if not existing.empty and user_id in existing["user_id"].values:
        return False

    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = pd.DataFrame(
        [{"user_id": user_id, "username": username}]
    )

    write_header = (
        not USERS_PATH.exists() or USERS_PATH.stat().st_size == 0
    )
    row.to_csv(
        USERS_PATH,
        mode="a",
        header=write_header,
        index=False,
        encoding="utf-8",
    )
    return True


def undo_last_interaction(user_id: str) -> bool:
    """撤销用户最后一次交互记录。返回 True 表示成功，False 表示无记录可撤销。"""
    if not INTERACTIONS_PATH.exists():
        return False

    df = pd.read_csv(INTERACTIONS_PATH, encoding="utf-8")
    if df.empty:
        return False

    user_rows = df[df["user_id"] == user_id]
    if user_rows.empty:
        return False

    # 删除该用户最后一条记录（按原文件顺序的最后一条）
    last_idx = user_rows.index[-1]
    df = df.drop(index=last_idx).reset_index(drop=True)

    df.to_csv(INTERACTIONS_PATH, index=False, encoding="utf-8")
    return True


data_store = CsvDataStore()


def load_dishes() -> pd.DataFrame:
    return data_store.load_dishes()


def append_interaction(user_id: str, dish_id: int, action: str) -> None:
    data_store.append_interaction(user_id, dish_id, action)


def add_comment(user_id: str, dish_id: int, comment_text: str) -> None:
    """添加一条菜品评论"""
    if not comment_text.strip():
        raise ValueError("评论内容不能为空")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    row = pd.DataFrame(
        [
            {
                "user_id": user_id,
                "dish_id": int(dish_id),
                "comment": comment_text.strip(),
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
        ]
    )

    write_header = not COMMENTS_PATH.exists() or COMMENTS_PATH.stat().st_size == 0
    row.to_csv(
        COMMENTS_PATH,
        mode="a",
        header=write_header,
        index=False,
        encoding="utf-8",
    )


def get_comments(dish_id: int) -> pd.DataFrame:
    """获取某道菜品的所有评论，按时间倒序排列"""
    if not COMMENTS_PATH.exists():
        return pd.DataFrame(columns=["user_id", "dish_id", "comment", "timestamp"])

    comments = pd.read_csv(COMMENTS_PATH, encoding="utf-8")
    comments = comments[comments["dish_id"] == dish_id].copy()
    if comments.empty:
        return comments

    comments.sort_values("timestamp", ascending=False, inplace=True)
    return comments


# ────────── Recommendation History ──────────

RECOMMENDATION_HISTORY_PATH = DATA_DIR / "recommendation_history.csv"


def save_recommendation_session(
    user_id: str,
    taste_profile: dict[str, int],
    weights: dict[str, int],
    algorithm: str,
    canteen_filter: str | None,
    price_min: float,
    price_max: float,
    top_results: pd.DataFrame,
) -> str:
    """保存一次推荐会话到 CSV，返回 session_id。"""
    import json
    import uuid

    session_id = uuid.uuid4().hex[:12]

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    row = pd.DataFrame(
        [
            {
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "taste_profile": json.dumps(taste_profile, ensure_ascii=False),
                "weights": json.dumps(weights, ensure_ascii=False),
                "algorithm": algorithm,
                "canteen_filter": canteen_filter or "",
                "price_min": price_min,
                "price_max": price_max,
                "top_dish_ids": json.dumps(
                    top_results["dish_id"].tolist(), ensure_ascii=False
                ),
                "top_match_scores": json.dumps(
                    [round(s, 1) for s in top_results["match_score"].tolist()],
                    ensure_ascii=False,
                ),
            }
        ]
    )

    write_header = (
        not RECOMMENDATION_HISTORY_PATH.exists()
        or RECOMMENDATION_HISTORY_PATH.stat().st_size == 0
    )
    row.to_csv(
        RECOMMENDATION_HISTORY_PATH,
        mode="a",
        header=write_header,
        index=False,
        encoding="utf-8",
    )

    return session_id


def load_recommendation_history(user_id: str) -> pd.DataFrame:
    """读取指定用户的推荐历史，按时间倒序排列。"""
    import json

    if not RECOMMENDATION_HISTORY_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(RECOMMENDATION_HISTORY_PATH, encoding="utf-8")
    if df.empty:
        return df

    user_history = df[df["user_id"] == user_id].copy()
    if user_history.empty:
        return user_history

    # Parse JSON columns
    for col in ("taste_profile", "weights", "top_dish_ids", "top_match_scores"):
        if col in user_history.columns:
            user_history[col] = user_history[col].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x
            )

    # Join dish names
    dishes = load_dishes()
    dish_name_map = dict(zip(dishes["dish_id"], dishes["name"]))

    def resolve_names(dish_ids):
        return [dish_name_map.get(int(did), f"菜品#{did}") for did in dish_ids]

    user_history["top_dish_names"] = user_history["top_dish_ids"].apply(resolve_names)

    return user_history.sort_values("timestamp", ascending=False).reset_index(drop=True)


def get_last_session(user_id: str) -> dict | None:
    """获取用户最近一次推荐会话的设置，用于自动恢复偏好。返回 None 表示无历史。"""
    history = load_recommendation_history(user_id)
    if history.empty:
        return None

    last = history.iloc[0]
    return {
        "taste_profile": last["taste_profile"],
        "weights": last["weights"],
        "algorithm": last["algorithm"],
        "canteen_filter": last["canteen_filter"] or None,
        "price_min": last["price_min"],
        "price_max": last["price_max"],
    }
