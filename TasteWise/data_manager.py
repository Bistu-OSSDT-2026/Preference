from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DISHES_PATH = DATA_DIR / "dishes.csv"
INTERACTIONS_PATH = DATA_DIR / "interactions.csv"
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


data_store = CsvDataStore()


def load_dishes() -> pd.DataFrame:
    return data_store.load_dishes()


def append_interaction(user_id: str, dish_id: int, action: str) -> None:
    data_store.append_interaction(user_id, dish_id, action)
