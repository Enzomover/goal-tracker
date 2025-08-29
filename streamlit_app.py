import streamlit as st
import json
import os
import re
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        return float(re.sub(r"[^\d.]", "", value))
    except:
        return 0

# --- Load data ---
data = load_data()

st.title("🎯 Goal & Finance Tracker")

# ------------------- GOAL TRACKER -------------------
st.header("Goal Tracker")

goal_name = st.text_input("Goal Name", data["goal_name"])
goal_amount_input = st.text_input("Target Amount ($)", format_number(data["goal_amount"]))
goal_amount = parse_input(goal_amount_input)
current_amount_input = st.text_input("Current Progress ($)", format_number(data.get("current_amount",0)))
current_amount = parse_input(current_amount_input)

# Save goal
if st.button("💾 Save Goal Progress"):
    data["goal_name"] = goal_name
    data["goal_amount"] = goal_amount
    data["current_amount"] = current_amount
    save_data(data)
    st.success("Goal progress saved!")

# Display current progress
progress = min((current_amount / goal_amount) * 100, 100) if goal_amount > 0 else 0
st.write(f"**Target Goal:** ${format_number(goal_amount)}")
st.write(f"**Current Progress:** ${format_number(current_amount)}")
st.write(f"**Completion:** {progress:.2f}%")

# ------------------- Growth Inputs -------------------
growth_monthly_input = st.text_input("Expected Monthly Growth (%)", "0")
growth_yearly_input = st.text_input("Expected Yearly Growth (%)", "0")
growth_monthly = parse_input(growth_monthly_input) / 100
growth_yearly = parse_input(growth_yearly_input) / 100

months_to_project = st.number_input("Months to project", min_value=1, value=12)
years_to_project = st.number_input("Years to project", min_value=1, value=5)

# ------------------- Dual-color Progress Bar -------------------
projected_monthly = current_amount * ((1 + growth_monthly) ** months_to_project)

current = min(current_amount, goal_amount)
growth_proj = min(projected_monthly, goal_amount)
remaining = max(goal_amount - max(current, growth_proj), 0)

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=[current],
    y=["Progress"],
    orientation='h',
    marker=dict(color="#636EFA"),
    name="Current Contribution"
))
fig_bar.add_trace(go.Bar(
    x=[growth_proj - current],
    y=["Progress"],
    orientation='h',
    marker=dict(color="#00CC96"),
    name="Projected Growth"
))
fig_bar.add_trace(go.Bar(
    x=[remaining],
    y=["Progress"],
    orientation='h',
    marker=dict(color="#E5ECF6"),
    name="Remaining"
))
fig_bar.update_layout(
    barmode='stack',
    showlegend=True,
    xaxis=dict(range=[0, goal_amount], title="Goal Progress ($)"),
    height=120
)
st.subheader("Goal Progress with Growth Projection")
st.plotly_chart(fig_bar, use_container_width=True)

# ------------------- Combined Growth Chart -------------------
monthly_values = [current_amount * ((1 + growth_monthly) ** m) for m in range(1, months_to_project+1)]
yearly_values = [current_amount * ((1 + growth_yearly) ** (m / 12)) for m in range(1, years_to_project*12 + 1)]

df_growth = pd.DataFrame({
    "Month": list(range(1, months_to_project+1)) + list(range(1, years_to_project*12+1)),
    "Monthly Growth": monthly_values + [None]*len(yearly_values),
    "Yearly Growth": [None]*len(monthly_values) + yearly_values,
    "Goal Target": [goal_amount]* (len(monthly_values) + len(yearly_values))
})

st.subheader("📊 Growth Projection Over Time")
st.line_chart(df_growth.set_index("Month"))
st.write(f"Projected after {months_to_project} month(s): ${format_number(monthly_values[-1])}")
st.write(f"Projected after {years_to_project} year(s): ${format_number(yearly_values[-1])}")

# ------------------- FINANCE TRACKER -------------------
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
            st.experimental_rerun()

# Manage Transactions (Auto-update)
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

            # Auto-update on change
            amt_val = parse_input(new_amount)
            updated_tx = {
                "type": new_type,
                "amount": amt_val,
                "category": new_category,
                "color": new_color,
                "date": new_date.strftime("%Y-%m-%d")
            }
            if updated_tx != t:
                data["transactions"][idx] = updated_tx
                save_data(data)
                st.experimental_rerun()

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
fig_income_ex
