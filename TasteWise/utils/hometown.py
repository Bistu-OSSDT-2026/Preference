from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


TASTE_VECTOR_LENGTH = 5


@dataclass(frozen=True)
class HometownPreference:
    label: str
    description: str
    taste_profile: tuple[float, float, float, float, float]
    keywords: tuple[str, ...]


HOMETOWN_PREFERENCES: dict[str, HometownPreference] = {
    "不限定": HometownPreference(
        label="不限定",
        description="只按你手动设置的五味偏好推荐。",
        taste_profile=(3, 3, 1, 3, 3),
        keywords=(),
    ),
    "川渝地区": HometownPreference(
        label="川渝地区",
        description="偏麻辣、重口、下饭。",
        taste_profile=(2, 1.5, 1, 5, 4.5),
        keywords=("川", "渝", "麻辣", "水煮", "回锅", "担担", "辣子", "重庆"),
    ),
    "湖南 / 江西": HometownPreference(
        label="湖南 / 江西",
        description="偏鲜辣、咸香、烟火气。",
        taste_profile=(2, 1.5, 1, 5, 4.5),
        keywords=("湘", "赣", "剁椒", "小炒", "辣椒", "农家"),
    ),
    "江浙沪": HometownPreference(
        label="江浙沪",
        description="偏清鲜、微甜、口味柔和。",
        taste_profile=(2.5, 4, 1, 1.5, 3),
        keywords=("糖醋", "红烧", "东坡", "苏", "杭", "上海", "甜"),
    ),
    "广东 / 福建": HometownPreference(
        label="广东 / 福建",
        description="偏清淡、鲜甜、汤品和蒸煮。",
        taste_profile=(1.5, 3.5, 1, 1.2, 2.5),
        keywords=("粤", "闽", "清蒸", "汤", "烧腊", "叉烧", "卤"),
    ),
    "东北地区": HometownPreference(
        label="东北地区",
        description="偏咸香、酸甜、分量扎实。",
        taste_profile=(3.5, 3.5, 1, 1.5, 4),
        keywords=("东北", "锅包", "地三鲜", "酸菜", "炖", "饺"),
    ),
    "西北 / 新疆": HometownPreference(
        label="西北 / 新疆",
        description="偏咸香、孜然、面食和牛羊肉。",
        taste_profile=(1.5, 1.5, 1, 3, 4.5),
        keywords=("西北", "新疆", "兰州", "牛肉面", "孜然", "羊", "清真", "面"),
    ),
    "华北 / 山东": HometownPreference(
        label="华北 / 山东",
        description="偏咸鲜、家常、面食和酱香。",
        taste_profile=(2, 2, 1, 2, 4),
        keywords=("鲁", "山东", "炸酱", "葱爆", "酱", "面", "饼"),
    ),
    "云贵地区": HometownPreference(
        label="云贵地区",
        description="偏酸辣、鲜香、风味突出。",
        taste_profile=(4.5, 1.5, 1, 4.5, 4),
        keywords=("云南", "贵州", "酸汤", "酸辣", "米线", "菌", "糊辣"),
    ),
}


def hometown_options() -> list[str]:
    return list(HOMETOWN_PREFERENCES.keys())


def get_hometown_preference(hometown: str | None) -> HometownPreference | None:
    if not hometown or hometown == "不限定":
        return None
    return HOMETOWN_PREFERENCES.get(hometown)


def apply_hometown_to_profile(
    user_profile: np.ndarray,
    hometown: str | None,
    influence: float = 0.25,
) -> np.ndarray:
    preference = get_hometown_preference(hometown)
    if preference is None:
        return user_profile

    influence = float(np.clip(influence, 0.0, 1.0))
    hometown_profile = np.asarray(preference.taste_profile, dtype=float)
    if hometown_profile.shape != (TASTE_VECTOR_LENGTH,):
        return user_profile

    blended = user_profile * (1.0 - influence) + hometown_profile * influence
    return np.clip(blended, 1.0, 5.0)


def hometown_keyword_bonus(dish: pd.Series, hometown: str | None) -> float:
    preference = get_hometown_preference(hometown)
    if preference is None or not preference.keywords:
        return 0.0

    searchable = " ".join(
        str(dish.get(column, ""))
        for column in ("name", "canteen", "window")
    )
    return 4.0 if any(keyword in searchable for keyword in preference.keywords) else 0.0


def hometown_reason(dish: pd.Series, hometown: str | None) -> str | None:
    preference = get_hometown_preference(hometown)
    if preference is None:
        return None

    bonus = hometown_keyword_bonus(dish, hometown)
    if bonus > 0:
        return f"包含更贴近{preference.label}口味的菜品线索"
    return f"五味画像已结合{preference.label}常见口味微调"
