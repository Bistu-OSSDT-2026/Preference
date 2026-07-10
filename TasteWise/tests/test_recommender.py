import numpy as np
import pandas as pd
import pytest

from recommender import recommend_dishes
from utils.similarity import cosine_match_score, weighted_euclidean_score


def test_exact_match_gets_100():
    user = np.array([5, 1, 1, 5, 4], dtype=float)
    dish = np.array([5, 1, 1, 5, 4], dtype=float)
    weights = np.ones(5, dtype=float)

    score = weighted_euclidean_score(user, dish, weights)

    assert score == 100.0


def test_cosine_exact_direction_gets_100():
    user = np.array([2, 1, 1, 5, 4], dtype=float)
    dish = np.array([4, 2, 2, 10, 8], dtype=float)

    score = cosine_match_score(user, dish)

    assert score == 100.0


def test_recommend_returns_top_k():
    dishes = pd.DataFrame(
        [
            {
                "dish_id": 1,
                "name": "A",
                "canteen": "一食堂",
                "window": "窗口1",
                "price": 8,
                "acid": 5,
                "sweet": 1,
                "bitter": 1,
                "spicy": 5,
                "salty": 4,
            },
            {
                "dish_id": 2,
                "name": "B",
                "canteen": "一食堂",
                "window": "窗口2",
                "price": 9,
                "acid": 4,
                "sweet": 1,
                "bitter": 1,
                "spicy": 5,
                "salty": 4,
            },
            {
                "dish_id": 3,
                "name": "C",
                "canteen": "二食堂",
                "window": "窗口3",
                "price": 10,
                "acid": 1,
                "sweet": 5,
                "bitter": 4,
                "spicy": 1,
                "salty": 1,
            },
        ]
    )

    result = recommend_dishes(
        user_profile=[5, 1, 1, 5, 4],
        dishes=dishes,
        top_k=2,
    )

    assert len(result) == 2
    assert result.iloc[0]["name"] == "A"


def test_price_filter():
    dishes = pd.DataFrame(
        [
            {
                "dish_id": 1,
                "name": "便宜菜",
                "canteen": "一食堂",
                "window": "窗口1",
                "price": 6,
                "acid": 3,
                "sweet": 3,
                "bitter": 1,
                "spicy": 3,
                "salty": 3,
            },
            {
                "dish_id": 2,
                "name": "较贵菜",
                "canteen": "一食堂",
                "window": "窗口2",
                "price": 20,
                "acid": 3,
                "sweet": 3,
                "bitter": 1,
                "spicy": 3,
                "salty": 3,
            },
        ]
    )

    result = recommend_dishes(
        user_profile=[3, 3, 1, 3, 3],
        dishes=dishes,
        min_price=0,
        max_price=10,
    )

    assert result["name"].tolist() == ["便宜菜"]


def test_cosine_similarity_can_rank_by_taste_direction():
    dishes = pd.DataFrame(
        [
            {
                "dish_id": 1,
                "name": "整体方向相似",
                "canteen": "一食堂",
                "window": "窗口1",
                "price": 10,
                "acid": 2,
                "sweet": 1,
                "bitter": 1,
                "spicy": 5,
                "salty": 4,
            },
            {
                "dish_id": 2,
                "name": "整体方向不同",
                "canteen": "一食堂",
                "window": "窗口2",
                "price": 10,
                "acid": 5,
                "sweet": 5,
                "bitter": 4,
                "spicy": 1,
                "salty": 1,
            },
        ]
    )

    result = recommend_dishes(
        user_profile=[3, 1, 1, 5, 4],
        dishes=dishes,
        top_k=2,
        algorithm="余弦相似度",
    )

    assert result.iloc[0]["name"] == "整体方向相似"


def test_weighted_euclidean_weights_can_change_ranking():
    dishes = pd.DataFrame(
        [
            {
                "dish_id": 1,
                "name": "辣味更接近",
                "canteen": "一食堂",
                "window": "窗口1",
                "price": 10,
                "acid": 1,
                "sweet": 1,
                "bitter": 1,
                "spicy": 5,
                "salty": 1,
            },
            {
                "dish_id": 2,
                "name": "整体更均衡",
                "canteen": "一食堂",
                "window": "窗口2",
                "price": 10,
                "acid": 3,
                "sweet": 3,
                "bitter": 1,
                "spicy": 3,
                "salty": 3,
            },
        ]
    )

    base = recommend_dishes(
        user_profile=[3, 3, 1, 5, 3],
        dishes=dishes,
        top_k=2,
        algorithm="加权欧氏距离",
    )
    spicy_weighted = recommend_dishes(
        user_profile=[3, 3, 1, 5, 3],
        dishes=dishes,
        top_k=2,
        algorithm="加权欧氏距离",
        weights=[1, 1, 1, 6, 1],
    )

    assert base.iloc[0]["name"] == "整体更均衡"
    assert spicy_weighted.iloc[0]["name"] == "辣味更接近"


def test_unsupported_algorithm_raises_clear_error():
    dishes = pd.DataFrame(
        [
            {
                "dish_id": 1,
                "name": "测试菜",
                "canteen": "一食堂",
                "window": "窗口1",
                "price": 10,
                "acid": 3,
                "sweet": 3,
                "bitter": 1,
                "spicy": 3,
                "salty": 3,
            },
        ]
    )

    with pytest.raises(ValueError, match="不支持的算法"):
        recommend_dishes(
            user_profile=[3, 3, 1, 3, 3],
            dishes=dishes,
            algorithm="未知算法",
        )


def test_hometown_preference_can_influence_ranking():
    dishes = pd.DataFrame(
        [
            {
                "dish_id": 1,
                "name": "清甜鸡饭",
                "canteen": "一食堂",
                "window": "家常窗口",
                "price": 10,
                "acid": 3,
                "sweet": 4,
                "bitter": 1,
                "spicy": 2,
                "salty": 3,
            },
            {
                "dish_id": 2,
                "name": "麻辣小炒肉",
                "canteen": "二食堂",
                "window": "湘菜窗口",
                "price": 12,
                "acid": 2,
                "sweet": 1,
                "bitter": 1,
                "spicy": 5,
                "salty": 4,
            },
        ]
    )

    result = recommend_dishes(
        user_profile=[3, 3, 1, 3, 3],
        dishes=dishes,
        top_k=2,
        hometown="湖南 / 江西",
    )

    assert result.iloc[0]["name"] == "麻辣小炒肉"
    reason_text = "；".join(result.iloc[0]["reasons"])
    assert "家乡" in reason_text or "湖南" in reason_text
