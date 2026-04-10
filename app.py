import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="EGSA Performance", layout="wide")

st.title("🏆 EGSA Member Performance Dashboard")

# =========================
# LOAD DATA FROM GITHUB
# =========================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Walfaanaa/EGSA2025_performance/main/EGSA2025_performance.csv"
    return pd.read_csv(url)

df = load_data()

# =========================
# HANDLE EMPTY VALUES
# =========================
df = df.fillna(0)

# =========================
# SAFE DIVISION
# =========================
def safe_div(a, b):
    return a / b if b != 0 else 0

# =========================
# SCORE CALCULATION
# =========================
df["score"] = (
    safe_div(df["loan_freq"], df["loan_freq"].max()) * 20 +
    safe_div(df["total_interest_amount"], df["total_interest_amount"].max()) * 15 +
    safe_div(df["monthly_payment"], df["monthly_payment"].max()) * 15 +
    safe_div(df["achievement"], df["achievement"].max()) * 15 +
    safe_div(df["volentary_saving"], df["volentary_saving"].max()) * 10 +
    safe_div(df["fee_charge"], df["fee_charge"].max()) * 5 +
    safe_div(df["no_new_members_by"], df["no_new_members_by"].max()) * 20
)

# =========================
# RANKING
# =========================
df["rank"] = df["score"].rank(ascending=False, method="dense")

# =========================
# REWARD SYSTEM
# =========================
total = len(df)

def get_reward_by_rank(rank):
    if rank <= total * 0.1:
        return "🥇 Gold"
    elif rank <= total * 0.3:
        return "🥈 Silver"
    elif rank <= total * 0.6:
        return "🥉 Bronze"
    else:
        return "Needs Improvement"

df["reward"] = df["rank"].apply(get_reward_by_rank)

# =========================
# SORT DATA
# =========================
df = df.sort_values(by="rank")

# =========================
# DASHBOARD SUMMARY
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Total Members", len(df))
col2.metric("Top Score", round(df["score"].max(), 2))
col3.metric("Average Score", round(df["score"].mean(), 2))

# =========================
# TOP PERFORMERS
# =========================
st.subheader("🏆 Top 10 Performers")
st.dataframe(df.head(10), use_container_width=True)

# =========================
# FULL DATA TABLE
# =========================
st.subheader("📊 All Members Performance")
st.dataframe(df, use_container_width=True)

# =========================
# SEARCH MEMBER
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
# DOWNLOAD OPTION
# =========================
st.download_button(
    label="📥 Download Results",
    data=df.to_csv(index=False),
    file_name="egsa_performance.csv",
    mime="text/csv"
)
