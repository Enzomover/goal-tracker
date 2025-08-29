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

# --- Remove non-digit characters and parse ---
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

# Goal Amount input with commas
goal_amount_input = st.sidebar.text_input(
    "Target Amount ($)", format_number(st.session_state.goal_amount)
)
st.session_state.goal_amount = parse_input(goal_amount_input)

# Current Amount input with commas
current_amount_input = st.sidebar.text_input(
    "Current Progress ($)", format_number(st.session_state.current_amount)
)
st.session_state.current_amount = parse_input(current_amount_input)

# --- Save button ---
if st.sidebar.button("💾 Save Progress"):
    save_data({
        "goal_name": st.session_state.goal_name,
        "goal_amount": st.session_state.goal_amount,
        "current_amount": st.session_state.current_amount
    })
    st.sidebar.success("Progress saved!")

# --- Calculate Progress ---
progress = min((st.session_state.current_amount / st.session_state.goal_amount) * 100, 100) if st.session_state.goal_amount > 0 else 0

# --- Display Main Dashboard ---
st.subheader(f"Tracking: {st.session_state.goal_name}")
st.write(f"**Target Goal:** ${format_number(st.session_state.goal_amount)}")
st.write(f"**Current Progress:** ${format_n_
