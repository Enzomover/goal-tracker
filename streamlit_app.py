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
        "goals": [],
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

st.set_page_config(
    page_title="🎯 Multi-Goal Finance Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Multi-Goal Finance Tracker")

# --- Add New Goal ---
st.header("➕ Add New Goal")
with st.form("new_goal_form"):
    new_goal_name = st.text_input("Goal Name")
    new_goal_amount = st.text_input("Target Amount ($)")
    new_current_amount = st.text_input("Current Amount ($)")
    new_monthly = st.number_input("Monthly Contribution ($)", min_value=0.0, step=100.0)
    new_yearly = st.number_input("Yearly Contribution ($)", min_value=0.0, step=500.0)
    new_growth = st.number_input("Expected Growth Rate (% per year)", min_value=0.0, step=0.1, value=5.0)
    new_years = st.number_input("Years to Project", min_value=0, step=1, value=10)
    submitted_goal = st.form_submit_button("Add Goal")

    if submitted_goal:
        if new_goal_name and parse_input(new_goal_amount) > 0:
            data['goals'].append({
                "goal_name": new_goal_name,
                "goal_amount": parse_input(new_goal_amount),
                "current_amount": parse_input(new_current_amount),
                "monthly_contribution": new_monthly,
                "yearly_contribution": new_yearly,
                "growth_rate": new_growth,
                "years_to_project": new_years
            })
            save_data(data)
            st.success(f"Goal '{new_goal_name}' added!")

# --- Display All Goals ---
if data['goals']:
    st.header("🏦 Goals Overview")
    for idx, goal in enumerate(data['goals']):
        st.subheader(f"{goal['goal_name']}")

        # --- Monthly compounding calculation ---
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
        contrib_percent = (total_contrib / goal_amount * 100) if goal_amount>0 else 0
        growth_percent = ((future_value - current_amount - total_contrib)/goal_amount*100) if goal_amount>0 else 0
        total_percent = min((future_value/goal_amount)*100,100) if goal_amount>0 else 0

        # --- Display Goal Info ---
        st.write(f"🎯 Target Goal: **${format_number(goal_amount)}**")
        st.write(f"💰 Current Amount: **${format_number(current_amount)}**")
        st.write(f"📘 Contribution %: **{contrib_percent:.2f}%**")
        st.write(f"💹 Growth %: **{growth_percent:.2f}%**")
        st.write(f"🎯 Total % toward goal: **{total_percent:.2f}%**")
        st.progress(total_percent / 100)
        st.write(f"💰 Total Projected Amount: **${format_number(future_value)}**")

        # --- Update or Delete Goal ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Delete '{goal['goal_name']}'", key=f"delete_{idx}"):
                data['goals'].pop(idx)
                save_data(data)
                st.experimental_rerun()

# --- FINANCE TRACKER ---
st.header("💵 Finance Tracker")
with st.form(key="transaction_form"):
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col1: t_type = st.selectbox("Type", ["Income", "Expense"])
    with col2: t_amount = st.text_input("Amount ($)")
    with col3: t_category = st.text_input("Category")
    with col4: t_color = st.color_picker("Color", "#636EFA")
    t_date = st.date_input("Date")
    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        amt = parse_input(t_amount)
        if amt>0 and t_category:
            data["transactions"].append({
                "type": t_type,
                "amount": amt,
                "category": t_category,
                "color": t_color,
                "date": t_date.strftime("%Y-%m-%d")
            })
            save_data(data)
            st.success(f"{t_type} added!")

# --- Transactions Summary ---
if data["transactions"]:
    st.subheader("📋 Transactions")
    for t in data["transactions"]:
        st.write(f"{t['type']} | ${format_number(t['amount'])} | {t['category']} | {t['date']} | Color: {t['color']}")

total_income = sum(t['amount'] for t in data["transactions"] if t['type']=="Income")
total_expense = sum(t['amount'] for t in data["transactions"] if t['type']=="Expense")
saving_percent = (total_income - total_expense)/total_income*100 if total_income>0 else 0
expense_percent = (total_expense/total_income*100) if total_income>0 else 0

st.header("📊 Summary")
col_income, col_expense = st.columns(2)
with col_income:
    st.metric("Total Income", f"${format_number(total_income)}")
    st.metric("Total Savings %", f"{saving_percent:.2f}%")
with col_expense:
    st.metric("Total Expense", f"${format_number(total_expense)}")
    st.metric("Expense % of Income", f"{expense_percent:.2f}%")

# Pie charts
fig_income_expense = px.pie(
    names=["Income","Expense"],
    values=[total_income,total_expense],
    title="Income vs Expense",
    hole=0.4
)
st.plotly_chart(fig_income_expense, use_container_width=True)

expense_transactions = [t for t in data["transactions"] if t['type']=="Expense"]
if expense_transactions:
    df_exp = pd.DataFrame(expense_transactions).reset_index(drop=True)
    df_exp['label'] = df_exp.apply(lambda r: f"{r['category']} (${format_number(r['amount'])})", axis=1)
    fig_exp_tx = px.pie(
        df_exp,
        names='label',
        values='amount',
        title="Expenses by Transaction",
        hole=0.4
    )
    fig_exp_tx.update_traces(
        marker=dict(colors=df_exp['color']),
        hoverinfo='label+percent+value',
        textinfo='percent+label',
        pull=[0.05]*len(df_exp)
    )
    st.plotly_chart(fig_exp_tx, use_container_width=True)
