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
        json.dump(data,
