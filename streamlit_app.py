import streamlit as st
import json
import os

# --- File to store data ---
DATA_FILE = "goal_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"goal_name": "Retirement Fund", "goal_amount": 50000, "current_amount": 5000}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- App ---
st.title("🎯 Goal Tracker with Comma Inputs")

data = load_data()

st.sidebar.header("Set Your Goal")
goal_name = st.sidebar.text_input("Goal Name", data["goal_name"])

# --- Text inputs with commas ---
def parse_number_input(value):
    try:
        return int(value.replace(",", ""))
    except:
        return 0

goal_amount_input = st.sidebar.text_input(
    "Target Amount ($)", f"{data['goal_amount']:,}"
)
goal_amount = parse_number_input(goal_amount_input)

current_amount_input = st.sidebar.text_input(
    "Current Progress ($)", f"{data['current_amount']:,}"
)
current_amount = parse_number_input(current_amount_input)

# --- Save button ---
if st.sidebar.button("💾 Save Progress"):
    save_data({
        "goal_name": goal_name,
        "goal_amount": goal_amount,
        "current_amount": current_amount
    })
    st.sidebar.success("Progress saved!")

# --- Calculate progress ---
progress = min((current_amount / goal_amount) * 100, 100) if goal_amount > 0 else 0

# --- Main display ---
st.subheader(f"Tracking: {goal_name}")
st.write(f"**Target Goal:** ${goal_amount:,}")
st.write(f"**Current Progress:** ${current_amount:,}")
st.write(f"**Completion:** {progress:.2f}%")
st.progress(progress / 100)

# --- Motivational message ---
if progress >= 100:
    st.success("🎉 Congratulations! You reached your goal!")
elif progress >= 75:
    st.info("🔥 Almost there, keep pushing!")
elif progress >= 50:
    st.warning("💪 Halfway done, great work!")
else:
    st.write("🚀 Just getting started—keep going!")
