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
    url = "https://raw.githubusercontent.com/Walfaanaa/EGSA2025_performance/main/EGSA2025_performance.xlsx"
    
    try:
        df = pd.read_excel(url, engine="openpyxl")  # ✅ FIXED
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

    # Clean column names
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
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# =========================
# CLEAN DATA TYPES
# =========================
for col in required_cols:
    if col != "id":
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# =========================
# NORMALIZATION FUNCTION
# =========================
def normalize(col):
    max_val = col.max()
    if max_val == 0:
        return pd.Series(0, index=col.index)
    return col / max_val

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
df["rank"] = df["score"].rank(method="first", ascending=False).astype(int)

# =========================
# REWARD SYSTEM
# =========================
total = len(df)

def get_reward(rank):
    if rank <= int(total * 0.1):
        return "Gold"
    elif rank <= int(total * 0.3):
        return "Silver"
    elif rank <= int(total * 0.6):
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
int_cols = ["loan_freq", "no_new_members_by", "rank"]
float_cols = [
    "total_interest_amount",
    "monthly_payment",
    "achievement",
    "volentary_saving",
    "fee_charge",
    "benefit_gain",
    "score"
]

for col in int_cols:
    df[col] = df[col].astype(int)

for col in float_cols:
    df[col] = df[col].round(2)

# =========================
# SUMMARY METRICS
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
    df.head(10),
    use_container_width=True
)

# =========================
# PERFORMANCE INSIGHT
# =========================
st.subheader("📈 Performance Insight")

top_member = df.iloc[0]
st.info(f"Top Performer ID: {top_member['id']} | Score: {top_member['score']:.2f}")

# =========================
# FULL TABLE
# =========================
st.subheader("📊 All Members Performance")

st.dataframe(df, use_container_width=True)

# =========================
# SEARCH FUNCTION
# =========================
st.subheader("🔍 Search Member")

member_id = st.text_input("Enter Member ID")

if member_id:
    result = df[df["id"].astype(str) == member_id.strip()]
    if not result.empty:
        st.success("✅ Member Found")
        st.dataframe(result, use_container_width=True)
    else:
        st.error("❌ Member not found")

# =========================
# PIE CHART
# =========================
st.subheader("🎯 Reward Distribution")

reward_counts = df["reward"].value_counts()

fig, ax = plt.subplots()

ax.pie(
    reward_counts.values,
    labels=reward_counts.index,
    autopct="%1.1f%%",
    startangle=90
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

# =========================
# REWARD MONEY ALLOCATION (FIXED RATIO 4:2:1)
# =========================
st.subheader("💰 Reward Allocation (Top 3 - Fixed Ratio)")

# Input total reward amount
total_reward = st.number_input("Enter Total Reward Amount", min_value=0.0, value=00000.0)

# Get top 3 performers
top3 = df.nsmallest(3, "rank").copy()

# Define ratio
weights = [4, 2, 1]

# Total weight
total_weight = sum(weights)

# Allocate rewards
top3["allocated_reward"] = [
    (w / total_weight) * total_reward for w in weights
]

# Round values
top3["allocated_reward"] = top3["allocated_reward"].round(2)

# Display result
st.write("### 🏅 The three top achiever for Reward in this year are : ")
st.dataframe(top3[["id", "score", "rank", "allocated_reward"]], use_container_width=True)
