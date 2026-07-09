from __future__ import annotations

from typing import Iterable

import numpy as np


TASTE_NAMES = ["酸味", "甜味", "苦味", "辣味", "咸味"]


def generate_reasons(
    user_profile: np.ndarray,
    dish_profile: np.ndarray,
) -> list[str]:
    """
    从“偏好是否接近”和“用户是否特别喜欢某味”两个角度生成解释。
    """
    reasons: list[str] = []
    differences = np.abs(user_profile - dish_profile)

    # 优先解释用户高偏好（4~5分）且菜品匹配的味道。
    preferred_indices = np.argsort(-user_profile)
    for index in preferred_indices:
        if user_profile[index] >= 4 and differences[index] <= 1:
            reasons.append(
                f"{TASTE_NAMES[index]}与你的高偏好接近"
            )

    # 如果理由不足，再补充总体最接近的味道。
    close_indices = np.argsort(differences)
    for index in close_indices:
        text = f"{TASTE_NAMES[index]}匹配度较高"
        if differences[index] <= 1 and text not in reasons:
            reasons.append(text)
        if len(reasons) >= 3:
            break

    if not reasons:
        reasons.append("综合五味画像与当前候选菜品相比更接近")

    return reasons[:3]


def format_reasons(reasons: Iterable[str]) -> str:
    return "推荐理由：" + "；".join(f"✓ {reason}" for reason in reasons)
