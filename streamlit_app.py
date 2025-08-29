import streamlit as st
import json
import os
import re
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
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

# ------------------- Growth Inputs -------------------
growth_monthly_input = st.text_input("Expected Monthly Growth (%)", "0")
growth_yearly_input = st.text_input("Expected Yearly Growth (%)", "0")
growth_monthly = parse_input(growth_monthly_input) / 100
growth_yearly = parse_input(growth_yearly_input) / 100

months_to_project = st.number_input("Months to project", min_value=1, value=12)

# ------------------- Dual-color Progress Bar -------------------
projected_monthly = current_amount * ((1 + growth_monthly) ** months_to_project)

current = min(current_amount, goal_amount)
growth_proj = min(projected_monthly, goal_amount)
remaining = max(goal_amount - growth_proj, 0)

fig_bar = go.Figure(go.Bar(
    x=[current, growth_proj - current, remaining],
    y=["Progress"],
    orientation='h',
    marker_color=["#636EFA", "#00CC96", "#E5ECF6"],
    hovertext=["Current Contribution", "Projected Growth", "Remaining"],
    hoverinfo="text+x"
))
fig_bar.update_layout(
    barmode='stack',
    showlegend=False,
    xaxis=dict(title="Goal Progress ($)", range=[0, goal_amount]),
    height=80,
    margin=dict(l=20, r=20, t=20, b=20)
)
st.subheader("Goal Progress")
st.plotly_chart(fig_bar, use_container_width=True)

# ------------------- Simplified Growth Chart -------------------
months = list(range(1, months_to_project+1))
monthly_growth = [current_amount * ((1 + growth_monthly) ** m) for m in months]
yearly_growth = [current_amount * ((1 + growth_yearly) ** (m / 12)) for m in months]

fig_growth = go.Figure()
fig_growth.add_trace(go.Scatter(
    x=months, y=monthly_growth, mode='lines+markers', name="Monthly Growth", line=dict(color="#636EFA")
))
fig_growth.add_trace(go.Scatter(
    x=months, y=yearly_growth, mode='lines+markers', name="Yearly Growth", line=dict(color="#00CC96")
))
fig_growth.add_trace(go.Scatter(
    x=[1, months_to_project], y=[goal_amount, goal_amount], mode='lines', name="Goal Target", line=dict(color="red", dash="dash")
))
fig_growth.update_layout(
    title="Projected Goal Growth",
    xaxis_title="Month",
    yaxis_title="Value ($)",
    height=350,
    margin=dict(l=40, r=20, t=50, b=40)
)
st.subheader("Growth Projection")
st.plotly_chart(fig_growth, use_container_width=True)
st.write(f"Projected after {months_to_project} month(s): ${format_number(monthly_growth[-1])}")

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

