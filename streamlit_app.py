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
        "goal_name": "Retirement Fund",
        "goal_amount": 50000,
        "current_amount": 0,
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

# --- GOAL TRACKER (Manual + Growth Projection) ---
st.header("Goal Tracker")

goal_name = st.text_input("Goal Name", data.get("goal_name", "Retirement Fund"))
goal_amount_input = st.text_input("Target Amount ($)", format_number(data.get("goal_amount", 50000)))
goal_amount = parse_input(goal_amount_input)
current_amount_input = st.text_input("Current Progress ($)", format_number(data.get("current_amount", 0)))
current_amount = parse_input(current_amount_input)

# Projection inputs
monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=0.0, step=100.0)
yearly_contribution = st.number_input("Yearly Contribution ($)", min_value=0.0, value=0.0, step=500.0)
growth_rate = st.number_input("Expected Growth Rate (% per year)", min_value=0.0, value=5.0, step=0.1)
years_to_project = st.number_input("Years to Project", min_value=0, value=10, step=1)

# Save button
if st.button("💾 Save Goal Progress"):
    data.update({
        "goal_name": goal_name,
        "goal_amount": goal_amount,
        "current_amount": current_amount,
        "monthly_contribution": monthly_contribution,
        "yearly_contribution": yearly_contribution,
        "growth_rate": growth_rate,
        "years_to_project": years_to_project
    })
    save_data(data)
    st.success("Goal progress saved!")

# --- Calculations ---
total_contrib = (monthly_contribution * 12 + yearly_contribution) * years_to_project

future_value = current_amount
for _ in range(years_to_project):
    future_value = (future_value + monthly_contribution * 12 + yearly_contribution) * (1 + growth_rate/100)

contrib_percent = (total_contrib / goal_amount * 100) if goal_amount > 0 else 0
growth_percent = ((future_value - current_amount - total_contrib) / goal_amount * 100) if goal_amount > 0 else 0
total_percent = min((future_value / goal_amount) * 100, 100) if goal_amount > 0 else 0

# --- Display ---
st.subheader(f"Tracking: {goal_name}")
st.write(f"**Target Goal:** ${format_number(goal_amount)}")
st.write(f"**Current Amount:** ${format_number(current_amount)}")
st.write(f"📘 Contribution % toward goal: **{contrib_percent:.2f}%**")
st.write(f"💹 Growth % toward goal: **{growth_percent:.2f}%**")
st.write(f"🎯 Total % toward goal: **{total_percent:.2f}%**")

# Progress bar
st.progress(total_percent / 100)

# Total projected amount in dollars
total_projected_amount = future_value  # includes current + contributions + growth
st.write(f"💰 **Total Projected Amount:** ${format_number(total_projected_amount)}")

if total_percent >= 100:
    st.success("🎉 Goal reached!")
elif total_percent >= 75:
    st.info("🔥 Almost there!")
elif total_percent >= 50:
    st.warning("💪 Halfway done!")
else:
    st.write("🚀 Keep going!")

# --- FINANCE TRACKER ---
st.header("Finance Tracker")

# Add Transaction
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

# Manage Transactions
if data["transactions"]:
    st.header("Manage Transactions")
    for idx, t in enumerate(data["transactions"].copy()):
        with st.expander(f"{t['type']} | ${format_number(t['amount'])} | {t['category']} | {t['date']}"):
            new_type = st.selectbox("Transaction Type", ["Income", "Expense"],
                                    index=0 if t['type']=="Income" else 1, key=f"type_{idx}")
            new_amount = st.text_input("Amount ($)", format_number(t['amount']), key=f"amount_{idx}")
            new_category = st.text_input("Category", t['category'], key=f"category_{idx}")
            new_color = st.color_picker("Choose color", t.get('color', "#636EFA"), key=f"color_{idx}")
            new_date = st.date_input("Transaction Date",
                                     datetime.strptime(t['date'].split()[0], "%Y-%m-%d"),
                                     key=f"date_{idx}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{idx}"):
                    amt_val = parse_input(new_amount)
                    if amt_val > 0 and new_category:
                        data["transactions"][idx] = {
                            "type": new_type,
                            "amount": amt_val,
                            "category": new_category,
                            "color": new_color,
                            "date": new_date.strftime("%Y-%m-%d")
                        }
                        save_data(data)
                        st.success("Transaction updated!")

            with col2:
                if st.button("Delete", key=f"delete_{idx}"):
                    data["transactions"].pop(idx)
                    save_data(data)
                    st.success("Transaction deleted!")

# Display transaction log
if data["transactions"]:
    st.subheader("Transactions Log")
    for t in data["transactions"]:
        color_box = f"<span style='display:inline-block;width:20px;height:20px;background-color:{t.get('color_
