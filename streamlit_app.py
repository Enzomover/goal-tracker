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
    t['amount'] if t['type'] == 'Income' else -t['amount'] for t in data["transactions"]
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

# --- Manage Transactions (expanders, inline edit/delete) ---
if data["transactions"]:
    st.header("Manage Transactions")

    # Iterate over a copy to safely remove items while looping
    for idx, t in enumerate(data["transactions"].copy()):
        with st.expander(f"{t['type']} | ${format_number(t['amount'])} | {t['category']} | {t['date']}"):
            new_type = st.selectbox("Transaction Type", ["Income", "Expense"],
                                    index=0 if t['type']=="Income" else 1, key=f"type_{idx}")
            new_amount = st.text_input("Amount ($)", format_number(t['amount']), key=f"amount_{idx}")
            new_category = st.text_input("Category", t['category'], key=f"category_{idx}")
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
                            "date": new_date.strftime("%Y-%m-%d")
                        }
                        save_data(data)
                        st.success("Transaction updated!")

            with col2:
                if st.button("Delete", key=f"delete_{idx}"):
                    # Remove transaction immediately
                    data["transactions"].pop(idx)
                    save_data(data)
                    st.success("Transaction deleted!")

# --- Display transactions table ---
if data["transactions"]:
    st.subheader("Transactions Log")
    df = pd.DataFrame(data["transactions"])
    df_display = df.copy()
    df_display['amount'] = df_display['amount'].apply(format_number)
    st.dataframe(df_display, use_container_width=True)

# --- Totals and percentages ---
total_income = sum(t['amount'] for t in data["transactions"] if t['type'] == "Income")
total_expense = sum(t['amount'] for t in data["transactions"] if t['type'] == "Expense")
saving_percent = (total_income - total_expense) / total_income * 100 if total_income > 0 else 0
expense_percent = (total_expense / total_income * 100) if total_income > 0 else 0

st.header("Summary")
st.write(f"**Total Income:** ${format_number(total_income)}")
st.write(f"**Total Expense:** ${format_number(total_expense)}")
st.write(f"**Saving %:** {saving_percent:.2f}%")
st.write(f"**Expense % of Income:** {expense_percent:.2f}%")

# --- Pie chart: Income vs Expense ---
fig_income_expense = px.pie(
    names=["Income", "Expense"],
    values=[total_income, total_expense],
    title="Income vs Expense",
    hole=0.4  # Donut chart
)
st.plotly_chart(fig_income_expense, use_container_width=True)

# --- Pie chart: Expenses by Category ---
expense_categories = [t for t in data["transactions"] if t['type']=="Expense"]
if expense_categories:
    df_expense_cat = pd.DataFrame(expense_categories)
    fig_expense_
