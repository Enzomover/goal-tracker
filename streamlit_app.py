import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- Connect to Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Your Google Sheet name
SHEET_NAME = "GoalTracker"
sheet = client.open(SHEET_NAME).sheet1

# --- Load Data ---
data = sheet.get_all_records()
if data:
    goal_name = data[0]["goal_name"]
    goal_amount = int(data[0]["goal_amount"])
    current_amount = int(data[0]["current_amount"])
else:
    goal_name, goal_amount, current_amount = "Retirement Fund", 50000, 5000
    sheet.append_row([goal_name, goal_amount, current_amount])

# --- UI ---
st.title("🎯 Goal Tracker")

st.sidebar.header("Set Your Goal")
goal_name = st.sidebar.text_input("Goal Name", goal_name)
goal_amount = st.sidebar.number_input("Target Amount ($)", min_value=1, value=goal_amount, step=100)
current_amount = st.sidebar.number_input("Current Progress ($)", min_value=0, value=current_amount, step=100)

if st.sidebar.button("💾 Save Progress"):
    sheet.update("A2", [[goal_name, goal_amount, current_amount]])
    st.sidebar.success("Progress saved!")

# --- Progress ---
progress = min((current_amount / goal_amount) * 100, 100)
st.subheader(f"Tracking: {goal_name}")
st.write(f"**Target Goal:** ${goal_amount:,.2f}")
st.write(f"**Current Progress:** ${current_amount:,.2f}")
st.write(f"**Completion:** {progress:.2f}%")
st.progress(progress / 100)

# --- Motivational Message ---
if progress >= 100:
    st.success("🎉 Congratulations! You reached your goal!")
elif progress >= 75:
    st.info("🔥 Almost there, keep pushing!")
elif progress >= 50:
    st.warning("💪 Halfway done, great work!")
else:
    st.write("🚀 Just getting started—keep going!")
