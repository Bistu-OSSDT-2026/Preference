from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from utils.explanation import generate_reasons
from utils.hometown import (
    apply_hometown_to_profile,
    get_hometown_preference,
    hometown_keyword_bonus,
    hometown_reason,
)
from utils.similarity import cosine_match_score, weighted_euclidean_score

TASTE_COLUMNS = ["acid", "sweet", "bitter", "spicy", "salty"]
HOMETOWN_SCORE_WEIGHT = 0.25


def _validate_profile(values: Sequence[float], name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)

    if arr.shape != (5,):
        raise ValueError(f"{name} 必须正好包含 5 个值：酸、甜、苦、辣、咸。")

    if np.any(arr < 1) or np.any(arr > 5):
        raise ValueError(f"{name} 中所有值必须位于 1 到 5 之间。")

    return arr


def recommend_dishes(
    user_profile: Sequence[float],
    dishes: pd.DataFrame,
    top_k: int = 5,
    algorithm: str = "加权欧氏距离",
    weights: Iterable[float] | None = None,
    canteen: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    exclude_recipe_ids: set[int] | None = None,
    hometown: str | None = None,
) -> pd.DataFrame:
    """
    根据用户五味偏好返回 Top-K 菜品。

    参数
    ----
    user_profile:
        [酸, 甜, 苦, 辣, 咸]，每项取值 1~5。
    dishes:
        菜品 DataFrame。
    algorithm:
        "加权欧氏距离" 或 "余弦相似度"。
    weights:
        五味重要性权重，仅对加权欧氏距离直接生效。
    hometown:
        用户家乡或地域口味，用于轻微调整五味画像并补充地域菜品线索。
    """
    user = _validate_profile(user_profile, "user_profile")
    scoring_user = apply_hometown_to_profile(user, hometown)
    hometown_preference = get_hometown_preference(hometown)
    hometown_profile = (
        np.asarray(hometown_preference.taste_profile, dtype=float)
        if hometown_preference is not None
        else None
    )

    required = {"dish_id", "name", "canteen", "window", "price", *TASTE_COLUMNS}
    missing = required - set(dishes.columns)
    if missing:
        raise ValueError(f"菜品数据缺少字段：{sorted(missing)}")

    filtered = dishes.copy()

    if canteen:
        filtered = filtered[filtered["canteen"] == canteen]

    if min_price is not None:
        filtered = filtered[filtered["price"] >= float(min_price)]

    if max_price is not None:
        filtered = filtered[filtered["price"] <= float(max_price)]

    if exclude_recipe_ids:
        filtered = filtered[~filtered["dish_id"].isin(exclude_recipe_ids)]

    if filtered.empty:
        return filtered.assign(match_score=pd.Series(dtype=float))

    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    if weights is None:
        weight_arr = np.ones(5, dtype=float)
    else:
        weight_arr = np.asarray(list(weights), dtype=float)
        if weight_arr.shape != (5,):
            raise ValueError("weights 必须正好包含 5 个值。")
        if np.any(weight_arr <= 0):
            raise ValueError("weights 中所有值必须大于 0。")

    scores: list[float] = []
    reasons: list[list[str]] = []

    for _, dish in filtered.iterrows():
        dish_profile = _validate_profile(
            dish[TASTE_COLUMNS].to_numpy(dtype=float),
            f"菜品 {dish['name']} 的五味画像",
        )

        if algorithm == "加权欧氏距离":
            score = weighted_euclidean_score(user, dish_profile, weight_arr)
            if hometown_profile is not None:
                hometown_score = weighted_euclidean_score(
                    hometown_profile,
                    dish_profile,
                    weight_arr,
                )
                score = (
                    score * (1.0 - HOMETOWN_SCORE_WEIGHT)
                    + hometown_score * HOMETOWN_SCORE_WEIGHT
                )
        elif algorithm == "余弦相似度":
            score = cosine_match_score(user, dish_profile)
            if hometown_profile is not None:
                hometown_score = cosine_match_score(hometown_profile, dish_profile)
                score = (
                    score * (1.0 - HOMETOWN_SCORE_WEIGHT)
                    + hometown_score * HOMETOWN_SCORE_WEIGHT
                )
        else:
            raise ValueError(f"不支持的算法：{algorithm}")

        score = min(100.0, score + hometown_keyword_bonus(dish, hometown))
        scores.append(score)

        dish_reasons = generate_reasons(scoring_user, dish_profile)
        region_reason = hometown_reason(dish, hometown)
        if region_reason:
            dish_reasons = [region_reason, *dish_reasons]
        reasons.append(dish_reasons[:3])

    result = filtered.copy()
    result["match_score"] = scores
    result["reasons"] = reasons

    return (
        result.sort_values(
            by=["match_score", "dish_id"],
            ascending=[False, True],
        )
        .head(top_k)
        .reset_index(drop=True)
    )
