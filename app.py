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
    df = pd.read_csv(url)

    # CLEAN COLUMN NAMES (FIXES YOUR ERROR)
    df.columns = df.columns.str.strip().str.lower()

    return df

df = load_data()

# =========================
# REQUIRED COLUMNS CHECK
# =========================
required_cols = [
    "id",
    "loan_freq",
    "total_interest_amount",
    "monthly_payment",
    "achievement",
    "volentary_saving",
    "fee_charge",
    "benefit_gain",
    "no_new_members_by"
]

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"❌ Missing columns in CSV: {missing}")
    st.stop()

# =========================
# CLEAN DATA TYPES (SAFE)
# =========================
for col in required_cols:
    if col != "id":
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# =========================
# NORMALIZATION FUNCTION
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
    normalize(df["benefit_gain"]) * 5 +
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
# FORMAT DATA
# =========================
df["loan_freq"] = df["loan_freq"].astype(int)
df["no_new_members_by"] = df["no_new_members_by"].astype(int)
df["rank"] = df["rank"].astype(int)

float_cols = [
    "total_interest_amount",
    "monthly_payment",
    "achievement",
    "volentary_saving",
    "fee_charge",
    "benefit_gain",
    "score"
]

for col in float_cols:
    df[col] = df[col].round(2)

# =========================
# FORMAT STYLE
# =========================
format_style = {
    "loan_freq": "{:.0f}",
    "no_new_members_by": "{:.0f}",
    "rank": "{:.0f}",
    "total_interest_amount": "{:.2f}",
    "monthly_payment": "{:.2f}",
    "achievement": "{:.2f}",
    "volentary_saving": "{:.2f}",
    "fee_charge": "{:.2f}",
    "benefit_gain": "{:.2f}",
    "score": "{:.2f}"
}

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
    df.head(10).style.format(format_style).background_gradient(cmap="Greens"),
    use_container_width=True
)

# =========================
# FULL TABLE
# =========================
st.subheader("📊 All Members Performance")

st.dataframe(
    df.style.format(format_style),
    use_container_width=True
)

# =========================
# SEARCH
# =========================
st.subheader("🔍 Search Member")

member_id = st.text_input("Enter Member ID")

if member_id:
    result = df[df["id"].astype(str) == member_id.strip()]
    if not result.empty:
        st.success("✅ Member Found")
        st.dataframe(result.style.format(format_style), use_container_width=True)
    else:
        st.error("❌ Member not found")

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
    "Bronze": "orange",
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
