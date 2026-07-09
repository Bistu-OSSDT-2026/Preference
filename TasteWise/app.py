from __future__ import annotations

import streamlit as st

from data_manager import (
    add_comment,
    append_interaction,
    get_comments,
    get_interacted_dish_ids,
    load_dishes,
    load_interactions,
    load_users,
    register_user,
    undo_last_interaction,
)
from recommender import recommend_dishes
from utils.explanation import format_reasons
from utils.hometown import HOMETOWN_PREFERENCES, hometown_options


TASTE_META = [
    ("acid", "酸", "明亮开胃", "#f59e0b", "🍋"),
    ("sweet", "甜", "柔和回甘", "#ec4899", "🍬"),
    ("bitter", "苦", "清爽解腻", "#16a34a", "🌿"),
    ("spicy", "辣", "热烈刺激", "#ef4444", "🌶️"),
    ("salty", "咸", "鲜香扎实", "#0ea5e9", "🧂"),
]

TASTE_DEFAULTS = {key: (1 if key == "bitter" else 3) for key, *_ in TASTE_META}


st.set_page_config(
    page_title="TasteWise 五味食堂推荐",
    page_icon="🍜",
    layout="wide",
)

# ────────── Custom CSS ──────────
st.markdown(
    """
    <style>
    :root {
        --tw-ink: #172033;
        --tw-muted: #65758b;
        --tw-line: #e5e7eb;
        --tw-surface: #ffffff;
        --tw-soft: #f7f5ef;
        --tw-primary: #d9480f;
        --tw-primary-dark: #9a3412;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(250, 204, 21, 0.18), transparent 28rem),
            linear-gradient(180deg, #fffaf0 0%, #f8fafc 46%, #eef2f7 100%);
        color: var(--tw-ink);
    }

    [data-testid="stSidebar"] {
        background: #fffaf0;
        border-right: 1px solid rgba(148, 163, 184, 0.28);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    .tw-hero {
        padding: 28px 30px;
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        background:
            linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(255, 247, 237, 0.88)),
            url("https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=1600&q=80");
        background-size: cover;
        background-position: center;
        box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
    }

    .tw-eyebrow {
        color: var(--tw-primary-dark);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 8px;
    }

    .tw-title {
        color: var(--tw-ink);
        font-size: 2.45rem;
        font-weight: 800;
        line-height: 1.12;
        margin: 0 0 12px;
    }

    .tw-subtitle {
        color: #334155;
        font-size: 1.02rem;
        line-height: 1.75;
        max-width: 680px;
        margin: 0;
    }

    .tw-metrics {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 22px;
        max-width: 620px;
    }

    .tw-metric {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.78);
        padding: 13px 14px;
    }

    .tw-metric strong {
        display: block;
        color: var(--tw-ink);
        font-size: 1.25rem;
        line-height: 1.2;
    }

    .tw-metric span {
        color: var(--tw-muted);
        font-size: 0.86rem;
    }

    .tw-section-title {
        color: var(--tw-ink);
        font-size: 1.3rem;
        font-weight: 760;
        margin: 1.6rem 0 0.35rem;
    }

    .tw-section-note {
        color: var(--tw-muted);
        margin-bottom: 1rem;
    }

    .tw-taste-card {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.74);
        padding: 14px 14px 6px;
        min-height: 164px;
    }

    .tw-taste-head {
        display: flex;
        gap: 9px;
        align-items: center;
        color: var(--tw-ink);
        font-weight: 760;
        margin-bottom: 2px;
    }

    .tw-taste-desc {
        color: var(--tw-muted);
        font-size: 0.84rem;
        margin-bottom: 9px;
    }

    .tw-dish-card {
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
        padding: 18px 18px 16px;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
        margin-bottom: 14px;
    }

    .tw-rank {
        color: var(--tw-primary-dark);
        font-weight: 800;
        font-size: 0.9rem;
    }

    .tw-dish-name {
        color: var(--tw-ink);
        font-size: 1.34rem;
        font-weight: 780;
        margin: 2px 0 8px;
    }

    .tw-dish-meta {
        color: var(--tw-muted);
        font-size: 0.94rem;
        margin-bottom: 10px;
    }

    .tw-score {
        display: inline-flex;
        align-items: baseline;
        gap: 4px;
        color: var(--tw-primary-dark);
        font-weight: 800;
        font-size: 1.4rem;
    }

    .tw-score small {
        color: var(--tw-muted);
        font-size: 0.82rem;
        font-weight: 600;
    }

    .tw-reasons {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-top: 8px;
    }

    .tw-footer {
        color: var(--tw-muted);
        font-size: 0.86rem;
        margin-top: 1.5rem;
    }

    .tw-login-box {
        max-width: 480px;
        margin: 6rem auto 2rem;
        text-align: center;
    }

    .tw-login-box h1 {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .tw-login-box p {
        color: var(--tw-muted);
        margin-bottom: 1.5rem;
    }

    .tw-login-box .test-hint {
        color: var(--tw-primary-dark);
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 8px;
        padding: 12px 14px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(148, 163, 184, 0.26);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 700;
    }

    .stProgress > div > div > div > div {
        background-color: var(--tw-primary);
    }

    @media (max-width: 760px) {
        .tw-hero { padding: 22px 20px; }
        .tw-title { font-size: 2rem; }
        .tw-metrics { grid-template-columns: 1fr; }
        .tw-login-box { margin-top: 3rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ────────── Login / Register Page ──────────

def render_login_page():
    st.markdown('<div class="tw-login-box">', unsafe_allow_html=True)
    st.markdown("<h1>🍜 TasteWise</h1>", unsafe_allow_html=True)
    st.markdown("<p>基于五味偏好的高校食堂菜品推荐系统</p>", unsafe_allow_html=True)

    st.markdown(
        '<div class="test-hint">🔑 测试账号无需密码，点击即可进入</div>',
        unsafe_allow_html=True,
    )

    if st.button("🚀  测试登录", type="primary", use_container_width=True):
        st.session_state.logged_in = True
        st.session_state.user_id = "demo_user"
        st.session_state.is_new_user = False
        st.rerun()

    st.markdown("---")

    with st.expander("使用已有账号 / 注册"):
        tab_login, tab_register = st.tabs(["登录", "注册"])

        with tab_login:
            login_id = st.text_input("输入用户 ID", key="login_id")
            if st.button("登录", use_container_width=True):
                users = load_users()
                if users.empty or login_id.strip() not in users["user_id"].values:
                    st.error(f"用户「{login_id}」不存在，请先注册")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_id = login_id.strip()
                    st.session_state.is_new_user = False
                    st.rerun()

        with tab_register:
            reg_id = st.text_input("设置用户 ID", key="reg_id",
                                   help="2-20个字符，字母/数字/下划线")
            reg_name = st.text_input("设置昵称", key="reg_name")
            if st.button("注册", use_container_width=True):
                uid = reg_id.strip()
                uname = reg_name.strip()
                if not uid:
                    st.error("用户 ID 不能为空")
                elif not uname:
                    st.error("昵称不能为空")
                elif register_user(uid, uname):
                    st.success(f"用户「{uid}」注册成功！")
                    st.session_state.logged_in = True
                    st.session_state.user_id = uid
                    st.session_state.is_new_user = True
                    st.rerun()
                else:
                    st.error(f"用户「{uid}」已存在，请直接登录")

    st.markdown("</div>", unsafe_allow_html=True)


# ────────── Initialize session state ──────────

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "is_new_user" not in st.session_state:
    st.session_state.is_new_user = False
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "recommendations_drinks" not in st.session_state:
    st.session_state.recommendations_drinks = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if not st.session_state.logged_in:
    render_login_page()
    st.stop()

# ────────── Main App (logged in) ──────────

user_id = st.session_state.user_id

try:
    dishes = load_dishes()
except Exception as exc:
    st.error(f"菜品数据读取失败：{exc}")
    st.stop()

# ── New user guidance ──
if st.session_state.is_new_user:
    st.info(
        "👋 欢迎使用 TasteWise！你的用户 ID 用于保存饮食记录和偏好，"
        "后续登录时输入同一 ID 可查看历史记录。"
    )
    st.session_state.is_new_user = False

min_data_price = float(dishes["price"].min())
max_data_price = float(dishes["price"].max())
canteen_count = dishes["canteen"].nunique()
window_count = dishes["window"].nunique()

# ────────── Sidebar ──────────

with st.sidebar:
    st.markdown(f"**当前用户：** {user_id}")
    if st.button("退出登录", use_container_width=True):
        for key in ["logged_in", "user_id", "recommendations",
                     "recommendations_drinks", "user_profile"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.header("推荐筛选")

    hometown = st.selectbox(
        "老家是哪里",
        hometown_options(),
        help="选择后，系统会轻微结合常见地域口味，让推荐更贴近你的家乡饮食习惯。",
    )
    st.caption(HOMETOWN_PREFERENCES[hometown].description)

    canteens = ["全部"] + sorted(dishes["canteen"].dropna().unique().tolist())
    selected_canteen = st.selectbox("食堂", canteens)

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
        help="加权欧氏距离更看重具体口味接近；余弦相似度更看重五味方向相似。",
    )

    top_k = st.slider("推荐数量", 3, 10, 5)

    exclude_eaten = st.checkbox(
        "排除已吃过的食谱",
        value=False,
        help="勾选后，推荐结果将排除你已交互过（喜欢/不喜欢/收藏）的菜品。",
    )

# ────────── Hero Section ──────────

st.markdown(
    f"""
    <section class="tw-hero">
        <div class="tw-eyebrow">TasteWise MVP</div>
        <h1 class="tw-title">按你的五味偏好，挑出今天更想吃的菜</h1>
        <p class="tw-subtitle">
            输入酸、甜、苦、辣、咸的偏好，系统会在食堂菜品中计算匹配度，
            同时保留用户反馈，方便后续接入更完整的数据库和个性化模型。
        </p>
        <div class="tw-metrics">
            <div class="tw-metric"><strong>{len(dishes)}</strong><span>道菜品</span></div>
            <div class="tw-metric"><strong>{canteen_count}</strong><span>个食堂</span></div>
            <div class="tw-metric"><strong>{window_count}</strong><span>类窗口</span></div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# ────────── Taste Preferences ──────────

st.markdown('<div class="tw-section-title">设置五味偏好</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="tw-section-note">评分 1 表示不喜欢，5 表示非常喜欢。默认值适合多数日常口味。</div>',
    unsafe_allow_html=True,
)

# Reset button
reset_col1, reset_col2 = st.columns([6, 1])
with reset_col2:
    if st.button("🔄 重置默认", use_container_width=True):
        st.session_state.taste_reset = True
        st.rerun()

should_reset = st.session_state.pop("taste_reset", False)

taste_values: dict[str, int] = {}
taste_cols = st.columns(5)
for col, (key, label, description, color, icon) in zip(taste_cols, TASTE_META):
    with col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="tw-taste-head"><span>{icon}</span><span>{label}</span></div>
                <div class="tw-taste-desc">{description}</div>
                """,
                unsafe_allow_html=True,
            )
            default_value = TASTE_DEFAULTS[key]
            current_value = default_value if should_reset else None
            taste_values[key] = st.slider(
                label,
                1,
                5,
                value=current_value if current_value is not None else default_value,
                label_visibility="collapsed",
                key=f"taste_{key}" if not should_reset else f"taste_{key}_reset",
            )

# ────────── Weights (algorithm-aware) ──────────

is_cosine = algorithm == "余弦相似度"
with st.expander("高级设置：五味重要性权重", expanded=False):
    if is_cosine:
        st.caption(
            "⚠️ 余弦相似度天然归一化，不支持权重调整。"
            "切换为「加权欧氏距离」后即可自定义权重。"
        )
    else:
        st.caption("权重越大，推荐时越重视该味道是否匹配。")

    weight_values: dict[str, int] = {}
    weight_cols = st.columns(5)
    for col, (key, label, _, _, _) in zip(weight_cols, TASTE_META):
        with col:
            default_weight = 2 if key == "spicy" else 1
            weight_values[key] = st.slider(
                f"{label}权重",
                1,
                5,
                default_weight,
                key=f"weight_{key}",
                disabled=is_cosine,
            )

# ────────── Generate Recommendations ──────────

st.markdown("")
if st.button("生成推荐", type="primary", use_container_width=True):
    user_profile = [taste_values[key] for key, *_ in TASTE_META]
    weights = [weight_values[key] for key, *_ in TASTE_META]
    canteen_filter = None if selected_canteen == "全部" else selected_canteen

    exclude_ids = get_interacted_dish_ids(user_id) if exclude_eaten else None

    # 按分类推荐（如果有 category 列）
    has_category = "category" in dishes.columns
    if has_category:
        main_dishes = dishes[dishes["category"] == "主食"].copy()
        drinks_snacks = dishes[dishes["category"].isin(["饮品", "小食"])].copy()
    else:
        main_dishes = dishes.copy()
        drinks_snacks = dishes.iloc[0:0].copy()  # empty

    recommendations = recommend_dishes(
        user_profile=user_profile,
        dishes=main_dishes,
        top_k=top_k,
        algorithm=algorithm,
        weights=weights,
        canteen=canteen_filter,
        min_price=price_range[0],
        max_price=price_range[1],
        exclude_recipe_ids=exclude_ids,
    )

    # 饮品小食推荐
    recommendations_drinks = recommend_dishes(
        user_profile=user_profile,
        dishes=drinks_snacks,
        top_k=top_k,
        algorithm=algorithm,
        weights=weights,
        canteen=canteen_filter,
        min_price=price_range[0],
        max_price=price_range[1],
        exclude_recipe_ids=exclude_ids,
        hometown=hometown,
    )

    st.session_state.user_profile = user_profile
    st.session_state.recommendations = recommendations
    st.session_state.recommendations_drinks = recommendations_drinks


# ────────── Render results helper ──────────

def render_recommendations(reco_df, empty_msg):
    if reco_df is None:
        st.info(empty_msg)
    elif reco_df.empty:
        st.warning("当前筛选条件下没有可推荐菜品，请放宽食堂或价格范围。")
    else:
        summary_cols = st.columns(3)
        summary_cols[0].metric("最高匹配度", f"{reco_df['match_score'].max():.1f}%")
        summary_cols[1].metric("平均价格", f"{reco_df['price'].mean():.0f} 元")
        summary_cols[2].metric("候选食堂", f"{reco_df['canteen'].nunique()} 个")

        for rank, (_, dish) in enumerate(reco_df.iterrows(), start=1):
            dish_id = int(dish["dish_id"])
            with st.container(border=True):
                left, right = st.columns([4, 1.15])

                with left:
                    st.markdown(
                        f"""
                        <div class="tw-rank">推荐 #{rank}</div>
                        <div class="tw-dish-name">{dish['name']}</div>
                        <div class="tw-dish-meta">
                            🏫 {dish['canteen']} · 🪟 {dish['window']} · 💰 {dish['price']:.0f} 元
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.progress(int(round(dish["match_score"])))
                    st.markdown(
                        f"""
                        <div class="tw-score">{dish['match_score']:.1f}% <small>综合匹配度</small></div>
                        <div class="tw-reasons">{format_reasons(dish["reasons"])}</div>
                        """,
                        unsafe_allow_html=True,
                    )

                with right:
                    if st.button("喜欢", key=f"like_{dish_id}", use_container_width=True):
                        append_interaction(user_id, dish_id, "like")
                        st.success("已记录")

                    if st.button("不喜欢", key=f"dislike_{dish_id}", use_container_width=True):
                        append_interaction(user_id, dish_id, "dislike")
                        st.warning("已记录")

                    if st.button("收藏", key=f"favorite_{dish_id}", use_container_width=True):
                        append_interaction(user_id, dish_id, "favorite")
                        st.success("已收藏")

                    if st.button("💬 评论", key=f"comment_btn_{dish_id}", use_container_width=True):
                        st.session_state[f"show_comments_{dish_id}"] = \
                            not st.session_state.get(f"show_comments_{dish_id}", False)

            # === 评论区：点击"评论"按钮后展开 ===
            if st.session_state.get(f"show_comments_{dish_id}", False):
                st.divider()
                st.markdown("**💬 评论**")
                comments_df = get_comments(dish_id)
                if comments_df.empty:
                    st.info("暂无评论，快来发表第一条评论吧！")
                else:
                    for _, c in comments_df.iterrows():
                        st.markdown(
                            f"**{c['user_id']}** · {c['timestamp']}  \n"
                            f"{c['comment']}"
                        )
                        st.divider()
                with st.form(key=f"comment_form_{dish_id}", clear_on_submit=True):
                    st.text_input(
                        "评论内容",
                        placeholder="说说你对这道菜的看法…",
                        label_visibility="collapsed",
                        key=f"ci_{dish_id}",
                    )
                    submitted = st.form_submit_button("💬 发送评论", use_container_width=True)
                    if submitted:
                        comment_val = st.session_state.get(f"ci_{dish_id}", "")
                        if comment_val.strip():
                            add_comment(user_id, dish_id, comment_val)
                            st.success("✅ 评论已发表！")
                        else:
                            st.error("评论不能为空")


# ────────── Recommendation Results ──────────

st.markdown('<div class="tw-section-title">🍚 主食推荐</div>', unsafe_allow_html=True)
render_recommendations(
    st.session_state.recommendations,
    "设置偏好后点击「生成推荐」，这里会展示最匹配的主食。",
)

st.markdown('<div class="tw-section-title">🥤 饮品小食</div>', unsafe_allow_html=True)
render_recommendations(
    st.session_state.recommendations_drinks,
    "设置偏好后点击「生成推荐」，这里会展示匹配的饮品和小食。",
)

# ────────── Dish List ──────────

with st.expander("📋 菜品列表"):
    dish_name_query = st.text_input("搜索菜品名称", placeholder="输入菜品名称筛选…")
    dish_cols = {
        "name": "名称",
        "canteen": "食堂",
        "window": "窗口",
        "price": "价格",
        "acid": "酸",
        "sweet": "甜",
        "bitter": "苦",
        "spicy": "辣",
        "salty": "咸",
    }
    if "category" in dishes.columns:
        # insert category after name
        dish_cols = {"name": "名称", "category": "分类", **{k: v for k, v in list(dish_cols.items())[1:]}}
    filtered_dishes = dishes.copy()
    if dish_name_query:
        filtered_dishes = filtered_dishes[
            filtered_dishes["name"].str.contains(dish_name_query, case=False, na=False)
        ]
    display_df = filtered_dishes[list(dish_cols.keys())].copy()
    display_df.rename(columns=dish_cols, inplace=True)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ────────── Diet History ──────────

with st.expander("📜 我的饮食记录"):
    history = load_interactions(user_id)
    if history.empty:
        st.info("暂无饮食记录。对推荐菜品点击「喜欢」「不喜欢」或「收藏」后，记录会出现在这里。")
    else:
        action_labels = {
            "like": "👍 喜欢",
            "dislike": "👎 不喜欢",
            "favorite": "⭐ 收藏",
        }
        display_history = history[["dish_name", "action", "timestamp"]].copy()
        display_history["action"] = display_history["action"].map(
            lambda a: action_labels.get(a, a)
        )
        display_history.rename(
            columns={
                "dish_name": "菜品名称",
                "action": "操作",
                "timestamp": "时间",
            },
            inplace=True,
        )
        st.dataframe(display_history, use_container_width=True, hide_index=True)

        if st.button("↩️ 撤销上一次操作", use_container_width=True):
            if undo_last_interaction(user_id):
                st.success("已撤销最近一次操作")
                st.rerun()
            else:
                st.info("没有可撤销的操作")

# ────────── Footer ──────────

st.markdown(
    '<div class="tw-footer">当前版本：五味画像、Top-K 推荐、食堂/价格筛选、推荐理由、'
    '用户反馈记录、菜品浏览、饮食历史、已吃排除、主食/饮品分类推荐。'
    '数据访问层已集中，便于后续替换 CSV 或接入数据库。</div>',
    unsafe_allow_html=True,
)
