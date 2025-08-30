import streamlit as st
import json
import os
import re
from datetime import datetime
import pandas as pd
import plotly.express as px

# --- File to store data ---
DATA_FILE = "finance_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "goals": [],  # list of goals
        "transactions": []
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

# --- Load data ---
data = load_data()

st.title("🎯 Goal & Finance Tracker")

# --- ADD NEW GOAL ---
st.header("➕ Add New Goal")
with st.form("new_goal_form"):
    goal_name = st.text_input("Goal Name")
    goal_amount_input = st.text_input("Target Amount ($)")
    current_amount_input = st.text_input("Current Amount ($)")
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, step=100.0)
    yearly_contribution = st.number_input("Yearly Contribution ($)", min_value=0.0, step=500.0)
    growth_rate = st.number_input("Expected Growth Rate (% per year)", min_value=0.0, step=0.1, value=5.0)
    years_to_project = st.number_input("Years to Project", min_value=0, step=1, value=10)
    submitted_goal = st.form_submit_button("Add Goal")

    if submitted_goal:
        if goal_name and parse_input(goal_amount_input) > 0:
            data['goals'].append({
                "goal_name": goal_name,
                "goal_amount": parse_input(goal_amount_input),
                "current_amount": parse_input(current_amount_input),
                "monthly_contribution": monthly_contribution,
                "yearly_contribution": yearly_contribution,
                "growth_rate": growth_rate,
                "years_to_project": years_to_project
            })
            save_data(data)
            st.success(f"Goal '{goal_name}' added!")

# --- DISPLAY ALL GOALS ---
if data.get("goals"):
    st.header("🏦 Goals Overview")
    for idx, goal in enumerate(data["goals"]):
        st.subheader(f"{goal['goal_name']}")

        # --- Calculations (monthly compounding) ---
        goal_amount = goal['goal_amount']
        current_amount = goal['current_amount']
        monthly_contribution = goal['monthly_contribution']
        yearly_contribution = goal['yearly_contribution']
        growth_rate = goal['growth_rate']
        years_to_project = goal['years_to_project']

        months = years_to_project * 12
        monthly_growth_rate = (1 + growth_rate/100)**(1/12) - 1
        future_value = current_amount
        for _ in range(months):
            future_value = (future_value + monthly_contribution + yearly_contribution/12) * (1 + monthly_growth_rate)

        total_contrib = (monthly_contribution*12 + yearly_contribution) * years_to_project
        contrib_percent = (total_contrib / goal_amount * 100) if goal_amount > 0 else 0
        growth_percent = ((future_value - current_amount - total_contrib)/goal_amount*100) if goal_amount > 0 else 0
        total_percent = min((future_value / goal_amount)*100, 100) if goal_amount > 0 else 0

        # --- Display Goal Info ---
        st.write(f"🎯 Target Goal: **${format_number(goal_amount)}**")
        st.write(f"💰 Current Amount: **${format_number(current_amount)}**")
        st.write(f"📘 Contribution %: **{contrib_percent:.2f}%**")
        st.write(f"💹 Growth %: **{growth_percent:.2f}%**")
        st.write(f"🎯 Total % toward goal: **{total_percent:.2f}%**")
        st.progress(total_percent / 100)
        st.write(f"💰 Total Projected Amount: **${format_number(future_value)}**")

        # --- DELETE GOAL BUTTON ---
        if st.button(f"Delete '{goal['goal_name']}'", key=f"delete_goal_{idx}"):
            data["goals"].pop(idx)
            save_data(data)
            st.experimental_rerun()

# --- FINANCE TRACKER (unchanged) ---
st.header("Finance Tracker")

with st.form(key="transaction_form"):
    t_type = st.selectbox("Transaction Type", ["Income", "Expense"])
    t_amount = st.text_input("Amount ($)")
    t_category = st.text_input("Category (e.g., Food, Salary, Bills)")
    t_color = st.color_picker("Choose a color for this transaction", "#636EFA")
    t_date = st.date_input("Transaction Date")
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        amount = parse_input(t_amount)
        if amount > 0 and t_category:
            data["transactions"].append({
                "type": t_type,
                "amount": amount,
                "category": t_category,
                "color": t_color,
                "date": t_date.strftime("%Y-%m-%d")
            })
            save_data(data)
            st.success(f"{t_type} added!")
        else:
            st.error("Please enter a valid amount and category.")

# Remaining code for managing transactions, summaries, and charts stays exactly as in your original master code
