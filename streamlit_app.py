import streamlit as st
import json
import os
import re
from datetime import datetime
import pandas as pd
import plotly.express as px

# --- Safe page config ---
try:
    st.set_page_config(
        page_title="🎯 Goal & Finance Tracker",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except AttributeError:
    pass  # Older Streamlit versions do not support set_page_config

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
        "monthly_contribution": 0.0,
        "yearly_contribution": 0.0,
        "growth_rate": 5.0,
        "years_to_project": 10,
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

# --- Page Header ---
st.markdown("""
# 🎯 Goal & Finance Tracker
Modern dashboard with goal projection, finance tracking, and interactive charts.
""", unsafe_allow_html=True)

# --- GOAL TRACKER ---
st.subheader("🏦 Goal Tracker")
goal_col1, goal_col2 = st.columns([2,1])

# --- Left column: Inputs ---
with goal_col1:
    st.text_input("Goal Name", value=data.get("goal_name", "Retirement Fund"), key="goal_name")
    st.text_input("Target Amount ($)", value=format_number(data.get("goal_amount", 50000)), key="goal_amount")
    st.text_input("Current Progress ($)", value=format_number(data.get("current_amount", 0)), key="current_amount")
    st.number_input(
        "Monthly Contribution ($)", 
        min_value=0.0, 
        value=data.get("monthly_contribution", 0.0), 
        step=100.0, 
        key="monthly_contribution"
    )
    st.number_input(
        "Yearly Contribution ($)", 
        min_value=0.0, 
        value=data.get("yearly_contribution", 0.0), 
        step=500.0, 
        key="yearly_contribution"
    )
    st.number_input(
        "Expected Growth Rate (% per year)", 
        min_value=0.0, 
        value=data.get("growth_rate", 5.0), 
        step=0.1, 
        key="growth_rate"
    )
    st.number_input(
        "Years to Project", 
        min_value=0, 
        value=data.get("years_to_project", 10), 
        step=1, 
        key="years_to_project"
    )

# --- Right column: Display ---
with goal_col2:
    display_goal_name = st.session_state.get("goal_name", data.get("goal_name", "Retirement Fund"))
    display_goal_amount = parse_input(st.session_state.get("goal_amount", data.get("goal_amount", 50000)))
    display_current_amount = parse_input(st.session_state.get("current_amount", data.get("current_amount", 0)))
    monthly_contribution = st.session_state.monthly_contribution
    yearly_contribution = st.session_state.yearly_contribution
    growth_rate = st.session_state.growth_rate
    years_to_project = st.session_state.years_to_project

    # --- Calculations ---
    months = years_to_project * 12
    monthly_growth_rate = (1 + growth_rate / 100) ** (1/12) - 1
    future_value = display_current_amount
    for _ in range(months):
        future_value = (future_value + monthly_contribution + yearly_contribution / 12) * (1 + monthly_growth_rate)

    total_contrib = (monthly_contribution * 12 + yearly_contribution) * years_to_project
    contrib_percent = (total_contrib / display_goal_amount * 100) if display_goal_amount > 0 else 0
    growth_percent = ((future_value - display_current_amount - total_contrib) / display_goal_amount * 100) if display_goal_amount > 0 else 0
    total_percent = min((future_value / display_goal_amount) * 100, 100) if display_goal_amount > 0 else 0

    # --- Display Goal Info ---
    st.subheader(display_goal_name)
    st.write(f"Target Goal: **${format_number(display_goal_amount)}**")
    st.write(f"Current Amount: **${format_number(display_current_amount)}**")
    st.write(f"Contribution %: **{contrib_percent:.2f}%**")
    st.write(f"Growth %: **{growth_percent:.2f}%**")
    st.write(f"Total % toward goal: **{total_percent:.2f}%**")
    st.write(f"Total Projected Amount: **${format_number(future_value)}**")
    
    # --- Progress bar ---
    st.progress(total_percent / 100)
    
    # --- Status emoji ---
    if total_percent >= 100:
        st.success("🎉 Goal reached!")
    elif total_percent >= 75:
        st.info("🔥 Almost there!")
    elif total_percent >= 50:
        st.warning("💪 Halfway done!")
    else:
        st.write("🚀 Keep going!")

# --- Save Goal ---
if st.button("💾 Save Goal Progress"):
    data.update({
        "goal_name": st.session_state.goal_name,
        "goal_amount": parse_input(st.session_state.goal_amount),
        "current_amount": parse_input(st.session_state.current_amount),
        "monthly_contribution": st.session_state.monthly_contribution,
        "yearly_contribution": st.session_state.yearly_contribution,
        "growth_rate": st.session_state.growth_rate,
        "years_to_project": st.session_state.years_to_project
    })
    save_data(data)
    st.success("Goal progress saved!")

# --- FINANCE TRACKER ---
st.subheader("💵 Finance Tracker")
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
        if amt > 0 and t_category:
            data["transactions"].append({
                "type": t_type,
                "amount": amt,
                "category": t_category,
                "color": t_color,
                "date": t_date.strftime("%Y-%m-%d")
            })
            save_data(data)
            st.success(f"{t_type} added!")

# --- Display Transactions ---
if data["transactions"]:
    st.subheader("📋 Transactions")
    for t in data["transactions"]:
        st.markdown(f"{t['type']} | ${format_number(t['amount'])} | {t['category']} | {t['date']} | Color: {t['color']}")

# --- Summary & Charts ---
total_income = sum(t['amount'] for t in data["transactions"] if t['type'] == "Income")
total_expense = sum(t['amount'] for t in data["transactions"] if t['type'] == "Expense")
saving_per_

