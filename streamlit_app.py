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
    return f"{n:,}"

def parse_input(value):
    try:
        return float(re.sub(r"[^\d.]", "", str(value)))
    except:
        return 0

# --- Load data ---
data = load_data()

st.title("🎯 Goal & Finance Tracker")

# --- GOAL TRACKER ---
st.header("Goal Tracker")

goal_name = st.text_input("Goal Name", data["goal_name"])
goal_amount_input = st.text_input("Target Amount ($)", format_number(data["goal_amount"]))
goal_amount = parse_input(goal_amount_input)
current_amount_input = st.text_input("Current Progress ($)", format_number(data.get("current_amount",0)))
current_amount = parse_input(current_amount_input)

# Save button
if st.button("💾 Save Goal Progress"):
    data["goal_name"] = goal_name
    data["goal_amount"] = goal_amount
    data["current_amount"] = current_amount
    save_data(data)
    st.success("Goal progress saved!")

# --- Simple Progress Bar ---
progress = min(current_amount / goal_amount, 1.0) if goal_amount > 0 else 0
st.subheader(f"Tracking: {goal_name}")
st.write(f"**Target Goal:** ${format_number(goal_amount)}")
st.write(f"**Current Progress:** ${format_number(current_amount)}")
st.write(f"**Completion:** {progress*100:.2f}%")

st.progress(progress)

if progress >= 1:
    st.success("🎉 Goal reached!")
elif progress >= 0.75:
    st.info("🔥 Almost there!")
elif progress >= 0.5:
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

# Display transaction log with color swatch
if data["transactions"]:
    st.subheader("Transactions Log")
    for t in data["transactions"]:
        color_box = f"<span style='display:inline-block;width:20px;height:20px;background-color:{t.get('color','#636EFA')};margin-right:10px;border-radius:3px;'></span>"
        st.markdown(f"{color_box} **{t['type']}** | ${format_number(t['amount'])} | {t['category']} | {t['date']}", unsafe_allow_html=True)

# Totals and percentages
total_income = sum(t['amount'] for t in data["transactions"] if t['type'] == "Income")
total_expense = sum(t['amount'] for t in data["transactions"] if t['type'] == "Expense")
saving_percent = (total_income - total_expense) / total_income * 100 if total_income > 0 else 0
expense_percent = (total_expense / total_income * 100) if total_income > 0 else 0

st.header("Summary")
st.write(f"**Total Income:** ${format_number(total_income)}")
st.write(f"**Total Expense:** ${format_number(total_expense)}")
st.write(f"**Saving %:** {saving_percent:.2f}%")
st.write(f"**Expense % of Income:** {expense_percent:.2f}%")

# Pie chart: Income vs Expense
fig_income_expense = px.pie(
    names=["Income", "Expense"],
    values=[total_income, total_expense],
    title="Income vs Expense",
    hole=0.4
)
st.plotly_chart(fig_income_expense, use_container_width=True)

# Pie chart: Expenses by transaction with individual colors
expense_transactions = [t for t in data["transactions"] if t['type']=="Expense"]
if expense_transactions:
    df_expense = pd.DataFrame(expense_transactions)
    df_expense['label'] = df_expense.apply(
        lambda row: f"{row['category']} (${format_number(row['amount'])})", axis=1
    )

    fig_expense_tx = px.pie(
        df_expense,
        names='label',
        values='amount',
        title="Expenses by Transaction",
        hole=0.4
    )

    fig_expense_tx.update_traces(
        marker=dict(colors=df_expense['color'].tolist()),
        hoverinfo='label+percent+value',
        textinfo='percent+label',
        pull=[0.05]*len(df_expense)
    )

    st.plotly_chart(fig_expense_tx, use_container_width=True)
