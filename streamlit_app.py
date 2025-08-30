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
        "growth_percent": 5,
        "transactions": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def format_number(n):
    return f"{n:,.2f}"

def parse_input(value):
    try:
        return float(re.sub(r"[^\d.]", "", value))
    except:
        return 0

# --- Load data ---
data = load_data()

# --- Custom CSS for polished look ---
st.markdown("""
<style>
    .main {background-color:#0E1117;}
    .stApp {background-color:#0E1117;}
    div[data-testid="stHeader"] {background: rgba(0,0,0,0);}
    h1, h2, h3, h4, h5, h6, p, label, span {color:#E8EAF6 !important;}
    .card {
        background-color:#1A1C23;
        padding:20px;
        border-radius:12px;
        box-shadow:0 4px 10px rgba(0,0,0,0.3);
        margin-bottom:20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Goal & Finance Tracker (2025 Edition)")

# --- Tabs ---
tab1, tab2 = st.tabs(["🎯 Goal Tracker", "💵 Finance Tracker"])

# --- Goal Tracker ---
with tab1:
