import streamlit as st
import json
import os
import re

DATA_FILE = "goal_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"goal_name": "Retirement Fund", "goal_amount": 50000, "current_amount": 5000}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def format_number(n):
    return f"{n:,}"

def parse_input(value):
    try:
        return int(re.sub(r"[^\d]", "", value))
    except:
        return 0

st.title("🎯 Goal Tracker")

data = load_data()

# Sidebar
st.sidebar.header("Set Your Goal")
goal_name = st.sidebar.text_input("Goal Name", data["goal_name"])

# --- Inputs with automatic commas ---
goal_amount_input = st.sidebar.text_input("Target Amount ($)", format_number(data["goal_amount"]))
goal_amount = parse_input(goal_amount_input)

current_amount_input = st.sidebar.text_input("Current Progress ($)", format_number(data["current_amount"]))
current_amount = parse_input(current_amount_input)

# Save button
if st.sidebar.button("💾 Save Progress"):
    save_data({
        "goal_name": goal_name,
        "goal_amount": goal_amount,
        "current_amount": current_amount
    })
    st.sidebar.success("Progress saved!")

# --- Calculate progress safely ---
progress = (current_amount / goal_amount * 100) if goal_amount > 0 else 0
progress = min(progress, 100)

# --- Display ---
st.subheader(f"Tracking: {goal_name}")
st.write(f"**Target Goal:** ${format_number(goal_amount)}")
st.write(f"**Current Progress:** ${format_number(current_amount)}")
st.write(f"**Completion:** {progress:.2f}%")
st.progress(progress / 100)

# Motivational messages
if progress >= 100:
    st.success("🎉 Congratulations! You reached your goal!")
elif progress >= 75:
    st.info("🔥 Almost there, keep pushing!")
elif progress >= 50:
    st.warning("💪 Halfway done, great work!")
else:
    st.write("🚀 Just getting started—keep going!")
