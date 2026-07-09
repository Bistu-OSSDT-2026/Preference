from __future__ import annotations

import numpy as np


def weighted_euclidean_score(
    user: np.ndarray,
    dish: np.ndarray,
    weights: np.ndarray,
) -> float:
    """
    加权欧氏距离转 0~100 匹配度。

    五味评分范围固定为 1~5，因此每一维最大差值为 4。
    使用同样的权重计算理论最大距离，再进行归一化。
    """
    distance = np.sqrt(np.sum(weights * (user - dish) ** 2))
    max_distance = np.sqrt(np.sum(weights * (4.0 ** 2)))

    if max_distance == 0:
        return 100.0

    score = (1.0 - distance / max_distance) * 100.0
    return float(np.clip(score, 0.0, 100.0))


def cosine_match_score(user: np.ndarray, dish: np.ndarray) -> float:
    """
    余弦相似度转 0~100 分。
    对本项目 1~5 的正数五味向量，相似度通常位于 0~1。
    """
    denominator = np.linalg.norm(user) * np.linalg.norm(dish)

    if denominator == 0:
        return 0.0

    similarity = float(np.dot(user, dish) / denominator)
    return float(np.clip(similarity * 100.0, 0.0, 100.0))
