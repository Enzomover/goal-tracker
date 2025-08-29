import streamlit as st
import json
import os
import re

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

# --- Format numbers with commas ---
def format_number(n):
    return f"{n:,}"

# --- Parse input safely ---
def parse_input(value):
    try:
        return int(re.sub(r"[^\d]", "", value))
    except:
        return 0

# --- Initialize session state ---
if "goal_amount" not in st.session_state:
    st.session_state.goal_amount = load_data()["goal_amount"]
if "current_amount" not in st.session_state:
    st.session_state.current_amount = load_data()["current_amount"]
if "goal_name" not in st.session_state:
    st.session_state.goal_name = load_data()["goal_name"]

# --- App Title ---
st.title("🎯 Goal Tracker")

# --- Sidebar Inputs ---
st.sidebar.header("Set Your Goal")
st.session_state.goal_name = st.sidebar.text_input("Goal Name", st.session_state.goal_name)

# --- Input fields with commas ---
goal_amount_str = st.sidebar.text_input("Target Amount ($)", format_number(st.session_state.goal_amount))
current_amount_str = st.sidebar.text_input("Current Progress ($)", format_number(st.session_state.current_amount))

# --- Parse input safely ---
goal_amount = parse_input(goal_amount_str)
current_amount = parse_input(current_amount_str)

# --- Update session state ---
st.session_state.goal_amount = goal_amount
st.session_state.current_amount = current_amount

# --- Save button ---
if st.sidebar.button("💾 Save Progress"):
    save_data({
        "goal_name": st.session_state.goal_name,
        "goal_amount": st.session_state.goal_amount,
        "current_amount": st.session_state.current_amount
    })
    st.sidebar.success("Progress saved!")

# --- Calculate Progress safely ---
progress = (current_amount / goal_amount * 100) if goal_amount > 0 else 0
progress = min(progress, 100)

# --- Display Main Dashboard ---
st.subheader(f"Tracking: {st.session_state.goal_name}")
st.write(f"**Target Goal:** ${format_number(goal_amount)}")
st.write(f"**Current Progress:** ${format_number(current_amount)}")
st.write(f"**Completion:** {progress:.2f}%")

# --- Single Smooth Progress Bar ---
st.progress(progress / 100)

# --- Motivational Message ---
if progress >= 100:
    st.success("🎉 Congratulations! You reached your goal!")
elif progress >= 75:
    st.info("🔥 Almost there, keep pushing!")
elif progress >= 50:
    st.warning("💪 Halfway done, great work!")
else:
    st.write("🚀 Just getting started—keep going!")
