import streamlit as st
import json
import os
import re
from datetime import datetime

# --- File to store data ---
DATA_FILE = "finance_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "goal_name": "Retirement Fund",
        "goal_amount": 50000,
        "current_amount": 0,
        "growth_percent": 5,
        "transactions": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def format_number(n):
    return f"${n:,.2f}"

def parse_input(value):
    try:
        return float(re.sub(r"[^\d.]", "", value))
    except:
        return 0

# --- Load data ---
data = load_data()

# --- Custom CSS for polished look ---
st.markdown("""
<style>
    .main {background-color:#0E1117;}
    .stApp {background-color:#0E1117;}
    div[data-testid="stHeader"] {background: rgba(0,0,0,0);}
    h1, h2, h3, h4, h5, h6, p, label, span {color:#E8EAF6 !important;}
    .card {
        background-color:#1A1C23;
        padding:20px;
        border-radius:12px;
        box-shadow:0 4px 10px rgba(0,0,0,0.3);
        margin-bottom:20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Goal & Finance Tracker (2025 Edition)")

# --- Tabs ---
tab1, tab2 = st.tabs(["🎯 Goal Tracker", "💵 Finance Tracker"])

# =========================
# 🎯 GOAL TRACKER TAB
# =========================
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Set Your Goal")

    data["goal_name"] = st.text_input("Goal Name", value=data["goal_name"])
    data["goal_amount"] = parse_input(st.text_input("Goal Amount ($)", value=str(data["goal_amount"])))
    data["growth_percent"] = st.number_input("Expected Yearly Growth (%)", min_value=0.0, step=0.1, value=float(data["growth_percent"]))

    # Calculate progress
    current_total = data["current_amount"]
    goal = data["goal_amount"]
    progress = min(current_total / goal * 100, 100) if goal > 0 else 0

    # --- Custom Progress Bar ---
    progress_html = f"""
    <div style='width: 100%; background: #333; border-radius: 25px;'>
      <div style='width: {progress:.2f}%;
                  background: linear-gradient(90deg, #2196F3, #21CBF3);
                  height: 25px;
                  border-radius: 25px;
                  box-shadow: 0px 0px 10px #21CBF3;'>
      </div>
    </div>
    <p style='margin-top:8px; font-weight:bold;'>{progress:.2f}% Completed</p>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

    st.markdown(f"💰 Current Balance: **{format_number(current_total)}**")
    st.markdown(f"🎯 Goal: **{format_number(goal)}**")
    st.markdown(f"📈 Growth Projection: **{data['growth_percent']}% yearly**")

    st.markdown("</div>", unsafe_allow_html=True)

    save_data(data)

# =========================
# 💵 FINANCE TRACKER TAB
# =========================
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Manage Transactions")

    col1, col2 = st.columns(2)
    with col1:
        amount = st.text_input("Amount ($)")
    with col2:
        tx_type = st.selectbox("Type", ["Income", "Expense"])

    if st.button("➕ Add Transaction"):
        amt = parse_input(amount)
        if amt > 0:
            if tx_type == "Income":
                data["current_amount"] += amt
            else:
                data["current_amount"] -= amt

            data["transactions"].append({
                "amount": amt if tx_type == "Income" else -amt,
                "type": tx_type,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_data(data)
            st.success("Transaction added!")

    st.markdown("### 📜 Transaction Log")
    if data["transactions"]:
        for tx in reversed(data["transactions"][-10:]):  # show last 10
            color = "🟢" if tx["amount"] > 0 else "🔴"
            st.write(f"{color} {tx['date']} | {tx['type']} | {format_number(tx['amount'])}")
    else:
        st.info("No transactions yet.")

    st.markdown("</div>", unsafe_allow_html=True)
