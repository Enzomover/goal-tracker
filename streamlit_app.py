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

# --- Modern 2025 Look Styling ---
st.set_page_config(
    page_title="🎯 Goal & Finance Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
body {background-color: #F3F4F6; font-family: 'Inter', sans-serif;
