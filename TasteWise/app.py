from __future__ import annotations

import streamlit as st

from data_manager import append_interaction, load_dishes
from recommender import recommend_dishes
from utils.explanation import format_reasons


st.set_page_config(
    page_title="TasteWise 五味食堂推荐",
    page_icon="🍜",
    layout="wide",
)

st.title("🍜 TasteWise")
st.caption("基于酸、甜、苦、辣、咸五味偏好的高校食堂菜品推荐系统")

try:
    dishes = load_dishes()
except Exception as exc:
    st.error(f"菜品数据读取失败：{exc}")
    st.stop()

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

with st.sidebar:
    st.header("👤 用户信息")
    user_id = st.text_input(
        "用户 ID",
        value="demo_user",
        help="用于记录点赞、点踩和收藏行为。",
    ).strip() or "demo_user"

    st.header("🔎 推荐设置")
    canteens = ["全部"] + sorted(dishes["canteen"].dropna().unique().tolist())
    selected_canteen = st.selectbox("食堂", canteens)

    min_data_price = float(dishes["price"].min())
    max_data_price = float(dishes["price"].max())
    price_range = st.slider(
        "价格范围（元）",
        min_value=min_data_price,
        max_value=max_data_price,
        value=(min_data_price, max_data_price),
        step=1.0,
    )

    algorithm = st.selectbox(
        "推荐算法",
        ["加权欧氏距离", "余弦相似度"],
        help="第一种更强调口味数值接近；第二种更强调五味偏好方向相似。",
    )

st.subheader("1️⃣ 设置你的五味偏好")
st.write("评分范围：1 = 非常不喜欢，5 = 非常喜欢")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    acid = st.slider("🍋 酸", 1, 5, 3)
with col2:
    sweet = st.slider("🍬 甜", 1, 5, 3)
with col3:
    bitter = st.slider("🌿 苦", 1, 5, 1)
with col4:
    spicy = st.slider("🌶️ 辣", 1, 5, 3)
with col5:
    salty = st.slider("🧂 咸", 1, 5, 3)

with st.expander("高级设置：五味重要性权重"):
    st.caption("权重越大，系统越重视该味道是否匹配。")
    w1, w2, w3, w4, w5 = st.columns(5)
    with w1:
        acid_w = st.slider("酸权重", 1, 5, 1)
    with w2:
        sweet_w = st.slider("甜权重", 1, 5, 1)
    with w3:
        bitter_w = st.slider("苦权重", 1, 5, 1)
    with w4:
        spicy_w = st.slider("辣权重", 1, 5, 2)
    with w5:
        salty_w = st.slider("咸权重", 1, 5, 1)

if st.button("🚀 开始智能推荐", type="primary", use_container_width=True):
    user_profile = [acid, sweet, bitter, spicy, salty]
    weights = [acid_w, sweet_w, bitter_w, spicy_w, salty_w]

    canteen_filter = None if selected_canteen == "全部" else selected_canteen

    recommendations = recommend_dishes(
        user_profile=user_profile,
        dishes=dishes,
        top_k=5,
        algorithm=algorithm,
        weights=weights,
        canteen=canteen_filter,
        min_price=price_range[0],
        max_price=price_range[1],
    )

    st.session_state.user_profile = user_profile
    st.session_state.recommendations = recommendations

st.divider()
st.subheader("2️⃣ 推荐结果")

recommendations = st.session_state.recommendations

if recommendations is None:
    st.info("请先设置五味偏好，然后点击“开始智能推荐”。")
elif recommendations.empty:
    st.warning("当前筛选条件下没有可推荐菜品，请放宽食堂或价格范围。")
else:
    for rank, (_, dish) in enumerate(recommendations.iterrows(), start=1):
        with st.container(border=True):
            left, right = st.columns([4, 1])

            with left:
                st.markdown(f"### {rank}. {dish['name']}")
                st.write(
                    f"🏫 {dish['canteen']} · 🪟 {dish['window']} · "
                    f"💰 {dish['price']:.0f} 元"
                )
                st.progress(int(round(dish["match_score"])))
                st.markdown(f"**综合匹配度：{dish['match_score']:.1f}%**")
                st.caption(format_reasons(dish["reasons"]))

            with right:
                dish_id = int(dish["dish_id"])

                if st.button("👍 喜欢", key=f"like_{dish_id}", use_container_width=True):
                    append_interaction(user_id, dish_id, "like")
                    st.success("已记录喜欢")

                if st.button("👎 不喜欢", key=f"dislike_{dish_id}", use_container_width=True):
                    append_interaction(user_id, dish_id, "dislike")
                    st.warning("已记录不喜欢")

                if st.button("⭐ 收藏", key=f"favorite_{dish_id}", use_container_width=True):
                    append_interaction(user_id, dish_id, "favorite")
                    st.success("已收藏")

st.divider()
st.caption(
    "当前版本为开源 MVP：五味画像 + Top-K 推荐 + 食堂/价格筛选 + 推荐理由 + 用户反馈记录。"
)
