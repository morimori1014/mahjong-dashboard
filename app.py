
import streamlit as st
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib

st.set_page_config(
    page_title="麻雀戦略・統計ダッシュボード",
    page_icon="🀄",  # 好きな絵文字とかにできる
)
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# =========================
# 🀄 タイトル
# =========================
st.title("🀄 麻雀戦略・統計ダッシュボード")
st.write("和了率・放銃率の変化から戦略の良し悪しを評価します（EV + 有意性）")

# =========================
# 📌 入力エリア
# =========================
st.header("📊 入力")

col1, col2 = st.columns(2)

with col1:
    win1 = st.number_input("和了率（改善前 %）", value=21.0)
    deal1 = st.number_input("放銃率（改善前 %）", value=12.0)
    n1 = st.number_input("局数（改善前）", value=5000)

with col2:
    win2 = st.number_input("和了率（改善後 %）", value=20.0)
    deal2 = st.number_input("放銃率（改善後 %）", value=11.0)
    n2 = st.number_input("局数（改善後）", value=500)

# =========================
# ⚙️ パラメータ
# =========================
st.header("⚙️ 評価設定")

alpha = st.slider("有意水準 α", 0.01, 0.2, 0.05, 0.01)

w_win = st.slider(
    "和了率の重み",
    min_value=0.1,
    max_value=5.0,
    value=3.3,
    step=0.1
)

w_deal = st.slider(
    "放銃率の重み",
    min_value=0.1,
    max_value=5.0,
    value=1.5,
    step=0.1
)

# =========================
# 🧠 計算
# =========================
if st.button("📈 評価する"):

    # -------------------------
    # EV評価（簡易モデル）
    # -------------------------
    ev_diff = (win2 - win1) * w_win + (deal1 - deal2) * w_deal

    # 標準誤差（簡易近似）
    se = np.sqrt(
        (win1 * (100 - win1) / n1 + win2 * (100 - win2) / n2) * w_win**2 +
        (deal1 * (100 - deal1) / n1 + deal2 * (100 - deal2) / n2) * w_deal**2
    )

    z = ev_diff / se if se > 0 else 0
    p_two = stats.norm.sf(abs(z)) * 2
    p_one = p_two / 2

    # =========================
    # 📊 結果表示
    # =========================
    st.subheader("📊 評価結果")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("EV変化", f"{ev_diff:.3f}")

    with col2:
        st.metric("Z値", f"{z:.3f}")

    with col3:
        st.metric("p値（片側）", f"{p_one:.4f}")

    # =========================
    # 判定
    # =========================
    st.subheader("🧠 判定")

    if p_one <= alpha:
        st.success(f"有意（α={alpha}で改善は統計的に確認されました）")
    else:
        st.warning(f"非有意（α={alpha}ではまだ確証なし）")

    if ev_diff > 0:
        st.info("EV評価：改善傾向")
    else:
        st.error("EV評価：悪化傾向")

    # =========================
    # 📈 可視化
    # =========================
    st.subheader("📈 ビジュアル比較")

    labels = ["Win Rate", "Deal-in Rate"]
    before = [win1, deal1]
    after = [win2, deal2]

    x = np.arange(len(labels))

    fig, ax = plt.subplots()
    ax.bar(x - 0.2, before, 0.4, label="before")
    ax.bar(x + 0.2, after, 0.4, label="after")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("%")
    ax.legend()

    st.pyplot(fig)

    # =========================
    # 解釈
    # =========================
    st.subheader("🀄 解釈")

    st.write(f"""
    - 和了率変化：{win2 - win1:+.2f}%
    - 放銃率変化：{deal2 - deal1:+.2f}%
    - EVスコア：{ev_diff:.3f}
    - p値（片側）：{p_one:.4f}

    👉 この戦略は **{'採用候補' if ev_diff > 0 else '見直し候補'}** です
    """)
