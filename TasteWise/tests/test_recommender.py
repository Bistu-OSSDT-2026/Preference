import pandas as pd

from recommender import recommend_dishes
from utils.similarity import weighted_euclidean_score

import numpy as np


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
