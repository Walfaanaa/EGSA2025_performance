import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="EGSA Performance", layout="wide")

st.title("🏆 EGSA Member Performance Dashboard")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Walfaanaa/EGSA2025_performance/main/EGSA2025_performance.csv"
    return pd.read_csv(url)

df = load_data()

# =========================
# CLEAN DATA
# =========================
df = df.fillna(0)

# =========================
# NORMALIZATION
# =========================
def normalize(col):
    max_val = col.max()
    return col / max_val if max_val != 0 else 0

# =========================
# SCORE CALCULATION
# =========================
df["score"] = (
    normalize(df["loan_freq"]) * 15 +
    normalize(df["total_interest_amount"]) * 15 +
    normalize(df["monthly_payment"]) * 15 +
    normalize(df["achievement"]) * 15 +
    normalize(df["volentary_saving"]) * 10 +
    normalize(df["fee_charge"]) * 5 +
    normalize(df["Benefit_gain"]) * 5 +
    normalize(df["no_new_members_by"]) * 20
)

# =========================
# RANKING
# =========================
df["rank"] = df["score"].rank(ascending=False, method="dense").astype(int)

# =========================
# REWARD SYSTEM
# =========================
total = len(df)

def get_reward(rank):
    if rank <= total * 0.1:
        return "Gold"
    elif rank <= total * 0.3:
        return "Silver"
    elif rank <= total * 0.6:
        return "Bronze"
    else:
        return "Needs Improvement"

df["reward"] = df["rank"].apply(get_reward)

# =========================
# SORT
# =========================
df = df.sort_values(by="rank")

# =========================
# FORMAT DATA (IMPORTANT)
# =========================

# Integer columns
df["loan_freq"] = df["loan_freq"].astype(int)
df["no_new_members_by"] = df["no_new_members_by"].astype(int)
df["rank"] = df["rank"].astype(int)

# Round float columns
float_cols = [
    "total_interest_amount",
    "monthly_payment",
    "achievement",
    "volentary_saving",
    "fee_charge",
    "Benefit_gain",
    "score"
]

for col in float_cols:
    if col in df.columns:
        df[col] = df[col].round(2)

# =========================
# SUMMARY
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Total Members", len(df))
col2.metric("Top Score", f"{df['score'].max():.2f}")
col3.metric("Average Score", f"{df['score'].mean():.2f}")

# =========================
# TOP 10
# =========================
st.subheader("🏆 Top 10 Performers")
st.dataframe(
    df.head(10).style.background_gradient(cmap="Greens"),
    use_container_width=True
)

# =========================
# ALL DATA
# =========================
st.subheader("📊 All Members Performance")

st.dataframe(
    df.style.format({
        "loan_freq": "{:.0f}",
        "no_new_members_by": "{:.0f}",
        "rank": "{:.0f}",
        "score": "{:.2f}"
    }),
    use_container_width=True
)

# =========================
# SEARCH
# =========================
st.subheader("🔍 Search Member")

member_id = st.text_input("Enter Member ID")

if member_id:
    result = df[df["id"].astype(str) == member_id]
    if not result.empty:
        st.success("Member Found")
        st.dataframe(result, use_container_width=True)
    else:
        st.error("Member not found")

# =========================
# PIE CHART
# =========================
st.subheader("🎯 Reward Distribution")

reward_counts = df["reward"].value_counts()

labels = reward_counts.index
sizes = reward_counts.values

color_map = {
    "Gold": "green",
    "Silver": "blue",
    "Bronze": "yellow",
    "Needs Improvement": "red"
}

colors = [color_map[label] for label in labels]

fig, ax = plt.subplots()

ax.pie(
    sizes,
    labels=labels,
    autopct="%1.1f%%",
    startangle=90,
    colors=colors
)

ax.axis("equal")

st.pyplot(fig)

# =========================
# DOWNLOAD
# =========================
st.download_button(
    label="📥 Download Results",
    data=df.to_csv(index=False),
    file_name="egsa_performance.csv",
    mime="text/csv"
)
