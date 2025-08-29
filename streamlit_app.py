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
        "current_amount": 5000,
        "transactions": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def format_number(n):
    return f"{n:,}"

def parse_input(value):
    try:
        return float(re.sub(r"[^\d.]", "", value))
    except:
        return 0

# --- Load data ---
data = load_data()

st.title("🎯 Goal & Finance Tracker")

# --- Goal Tracker ---
st.header("Goal Tracker")
goal_name = st.text_input("Goal Name", data["goal_name"])
goal_amount_input = st.text_input("Target Amount ($)", format_number(data["goal_amount"]))
goal_amount = parse_input(goal_amount_input)
current_amount_input = st.text_input("Current Progress ($)", format_number(data["current_amount"]))
current_amount = parse_input(current_amount_input)

# Update current_amount based on transactions
current_amount_from_transactions = sum(t['amount'] if t['type']=='Income' else -t['amount'] for t in data["transactions"])
current_amount += current_amount_from_transactions

progress = min((current_amount / goal_amount) * 100, 100) if goal_amount > 0 else 0

st.subheader(f"Tracking: {goal_name}")
st.write(f"**Target Goal:** ${format_number(goal_amount)}")
st.write(f"**Current Progress:** ${format_number(current_amount)}")
st.write(f"**Completion:** {progress:.2f}%")
st.progress(progress / 100)

# Motivational message
if progress >= 100:
    st.success("🎉 Goal reached!")
elif progress >= 75:
    st.info("🔥 Almost there!")
elif progress >= 50:
    st.warning("💪 Halfway done!")
else:
    st.write("🚀 Keep going!")

# --- Transactions Section ---
st.header("Income & Expenses T
