import streamlit as st
import json
import os
import re

DATA_FILE = "finance_data.json"

# ---------------- Helpers ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "goal_name": "Retirement Fund",
        "goal_amount": 50000,
        "current_amount": 0,
        "growth_percent": 5.0
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def format_number(n):
    return f"{n:,.2f}"

def parse_input(value):
    try:
        return float(re.sub(r"[^\d.]", "", str(value)))
    except:
        return 0

# ---------------- Force Light Theme ----------------
st.markdown(
    """
    <style>
    body, .main, .stApp {
        background-color: #fafafa !important;
        color: #000000 !important;
    }
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    .stProgress > div > div {
        background-color: #e0e0e0 !important;
        border-radius: 20px;
    }
    .stCard {
        box-shadow: none !important;
    }
    [data-testid="stThemeToggle"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load Data ----------------
data = load_data()

st.title("🎯 Goal & Finance Tracker")

# ---------------- Goal Tracker Form ----------------
st.header("Goal Tracker")

with st.form("goal_form"):
    goal_name = st.text_input("Goal Name", data.get("goal_name", "My Goal"))
    goal_amount_input = st.text_input("Target Amount ($)", format_number(data.get("goal_amount", 0)))
    goal_amount = parse_input(goal_amount_input)

    current_amount_input = st.text_input("Current Progress ($)", format_number(data.get("current_amount", 0)))
    current_amount = parse_input(current_amount_input)

    growth_percent = st.number_input(
        "Expected Yearly Growth (%)", 
        min_value=0.0, 
        step=0.1, 
        value=float(data.get("growth_percent", 0))
    )

    submitted = st.form_submit_button("💾 Save Goal Progress")
    if submitted:
        data["goal_name"] = goal_name
        data["goal_amount"] = goal_amount
        data["current_amount"] = current_amount
        data["growth_percent"] = growth_percent
        save_data(data)
        st.success("Goal progress saved!")

# ---------------- Progress Calculations ----------------
goal_amount = data.get("goal_amount", 0)
current_amount = data.get("current_amount", 0)
growth_percent = data.get("growth_percent", 0)

progress = min((current_amount / goal_amount) * 100, 100) if goal_amount > 0 else 0
expected_growth_value = current_amount * (growth_percent / 100)
total_value = current_amount + expected_growth_value

# ---------------- Custom Progress Bar ----------------
st.subheader(f"📊 Tracking: {data['goal_name']}")

# Dynamic bar color based on progress
if progress >= 100:
    bar_color = "#4CAF50"  # Green
elif progress >= 75:
    bar_color = "#FFC107"  # Amber
elif progress >= 50:
    bar_color = "#2196F3"  # Blue
else:
    bar_color = "#F44336"  # Red

st.markdown(
    f"""
    <div style="width:100%; background:#ddd; border-radius:30px; padding:3px; margin:15px 0;">
        <div style="width:{progress}%; background:{bar_color};
                    height:28px; border-radius:30px; text-align:center; 
                    color:white; font-weight:bold; line-height:28px;">
            {progress:.2f}%  —  ${format_number(current_amount)}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Growth + Totals ----------------
st.write(f"**Target Goal:** ${format_number(goal_amount)}")
st.write(f"**Current Contributions:** ${format_number(current_amount)}")
st.write(f"**Expected Yearly Growth:** {growth_percent:.2f}% → ${format_number(expected_growth_value)}")
st.write(f"**Total Value (with growth):** ${format_number(total_value)}")

# Progress feedback
if progress >= 100:
    st.success("🎉 Goal reached!")
elif progress >= 75:
    st.info("🔥 Almost there!")
elif progress >= 50:
    st.warning("💪 Halfway done!")
else:
    st.write("🚀 Keep going!")
