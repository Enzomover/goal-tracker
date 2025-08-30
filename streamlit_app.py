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
        "Expected Growth Rate (% p
