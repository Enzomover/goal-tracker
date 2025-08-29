import streamlit as st
import json
import os
import re
from datetime import datetime
import pandas as pd

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
current_amount_from_transactions = sum(
    t['amount'] if t['type']=='Income' else -t['amount'] for t in data["transactions"]
)
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

# --- Add new transaction ---
st.header("Add Transaction")
with st.form(key="transaction_form"):
    t_type = st.selectbox("Transaction Type", ["Income", "Expense"])
    t_amount = st.text_input("Amount ($)")
    t_category = st.text_input("Category (e.g., Food, Salary, Bills)")
    t_date = st.date_input("Transaction Date")
    submitted = st.form_submit_button("Add Transaction")
    
    if submitted:
        amount = parse_input(t_amount)
        if amount > 0 and t_category:
            data["transactions"].append({
                "type": t_type,
                "amount": amount,
                "category": t_category,
                "date": t_date.strftime("%Y-%m-%d")
            })
            save_data(data)
            st.success(f"{t_type} added!")
        else:
            st.error("Please enter a valid amount and category.")

# --- Edit/Delete transactions safely ---
if data["transactions"]:
    st.header("Manage Transactions")
    
    trans_list = [
        f"{i+1}: {t['type']} | ${format_number(t['amount'])} | {t['category']} | {t['date']}" 
        for i, t in enumerate(data["transactions"])
    ]
    
    selected_idx = st.selectbox(
        "Select a transaction to edit or delete",
        range(len(trans_list)),
        format_func=lambda x: trans_list[x]
    )
    
    t = data["transactions"][selected_idx]
    
    new_type = st.selectbox("Transaction Type", ["Income", "Expense"], index=0 if t['type']=="Income" else 1)
    new_amount = st.text_input("Amount ($)", format_number(t['amount']))
    new_category = st.text_input("Category", t['category'])
    new_date = st.date_input("Transaction Date", datetime.strptime(t['date'].split()[0], "%Y-%m-%d"))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update Transaction"):
            amt_val = parse_input(new_amount)
            if amt_val > 0_
