import numpy as np
import pandas as pd

from recommender import recommend_dishes
from utils.similarity import weighted_euclidean_score


def test_exact_match_gets_100():
    user = np.array([5, 1, 1, 5, 4], dtype=float)
    dish = np.array([5, 1, 1, 5, 4], dtype=float)
    weights = np.ones(5, dtype=float)

    score = weighted_euclidean_score(user, dish, weights)

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


def test_hometown_profile_affects_score_without_keywords():
    dishes = pd.DataFrame(
        [
            {
                "dish_id": 1,
                "name": "A",
                "canteen": "一食堂",
                "window": "窗口1",
                "price": 10,
                "acid": 3,
                "sweet": 4,
                "bitter": 1,
                "spicy": 1,
                "salty": 3,
            },
            {
                "dish_id": 2,
                "name": "B",
                "canteen": "一食堂",
                "window": "窗口2",
                "price": 10,
                "acid": 2,
                "sweet": 1,
                "bitter": 1,
                "spicy": 5,
                "salty": 4,
            },
        ]
    )

    base = recommend_dishes(
        user_profile=[3, 3, 1, 3, 3],
        dishes=dishes,
        top_k=2,
    )
    regional = recommend_dishes(
        user_profile=[3, 3, 1, 3, 3],
        dishes=dishes,
        top_k=2,
        hometown="川渝地区",
    )

    base_scores = dict(zip(base["dish_id"], base["match_score"]))
    regional_scores = dict(zip(regional["dish_id"], regional["match_score"]))

    assert regional_scores[2] > base_scores[2]
    assert regional_scores[1] < base_scores[1]
