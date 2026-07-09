from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DISHES_PATH = DATA_DIR / "dishes.csv"
INTERACTIONS_PATH = DATA_DIR / "interactions.csv"


def load_dishes() -> pd.DataFrame:
    if not DISHES_PATH.exists():
        raise FileNotFoundError(f"找不到菜品数据：{DISHES_PATH}")

    dishes = pd.read_csv(DISHES_PATH, encoding="utf-8")

    numeric_columns = [
        "dish_id",
        "price",
        "acid",
        "sweet",
        "bitter",
        "spicy",
        "salty",
    ]
    for column in numeric_columns:
        dishes[column] = pd.to_numeric(dishes[column], errors="raise")

    return dishes


def append_interaction(user_id: str, dish_id: int, action: str) -> None:
    allowed_actions = {"like", "dislike", "favorite"}
    if action not in allowed_actions:
        raise ValueError(f"不支持的行为：{action}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

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

    write_header = not INTERACTIONS_PATH.exists() or INTERACTIONS_PATH.stat().st_size == 0
    row.to_csv(
        INTERACTIONS_PATH,
        mode="a",
        header=write_header,
        index=False,
        encoding="utf-8",
    )
