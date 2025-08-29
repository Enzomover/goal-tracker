import streamlit as st

# --- Goal Tracker App ---
st.set_page_config(page_title="Goal Tracker", layout="centered")

st.title("🎯 Goal Tracker with Growth Projection")

# --- User Inputs ---
goal_name = st.text_input("Goal Name", "My Investment Goal")
goal_amount = st.number_input("Goal Amount ($)", min_value=1, value=10000, step=100)

current_amount = st.number_input("Current Contribution ($)", min_value=0.0, value=1000.0, step=100.0)

monthly_growth_rate = st.number_input("Monthly Growth Rate (%)", min_value=0.0, value=1.0, step=0.1) / 100
months_to_project = st.number_input("Months to Project", min_value=0, value=12, step=1)

yearly_growth_rate = st.number_input("Yearly Growth Rate (%)", min_value=0.0, value=5.0, step=0.1) / 100
years_to_project = st.number_input("Years to Project", min_value=0, value=2, step=1)

# --- Growth Calculation ---
projected_amount = current_amount

# Apply monthly growth
if months_to_project > 0:
    projected_amount *= (1 + monthly_growth_rate) ** months_to_project

# Apply yearly growth
if years_to_project > 0:
    projected_amount *= (1 + yearly_growth_rate) ** years_to_project

projected_growth = max(0, projected_amount - current_amount)

# --- Progress Bar Logic ---
blue_percent = (current_amount / goal_amount) * 100 if goal_amount > 0 else 0
total_with_growth = min(current_amount + projected_growth, goal_amount)
green_percent = (total_with_growth / goal_amount) * 100 - blue_percent if goal_amount > 0 else 0

# Clamp values between 0 and 100
blue_percent = max(0, min(blue_percent, 100))
green_percent = max(0, min(green_percent, 100))
total_percent = min(blue_percent + green_percent, 100)

# --- Display Progress Bar ---
st.subheader(f"{goal_name} Progress")

progress_bar_html = f"""
<div style="position: relative; width: 100%; height: 40px; background-color: #E5ECF6;
            border-radius: 20px; overflow: hidden; display: flex;">
    <!-- Blue: Contribution -->
    <div style="flex: {blue_percent}; background-color: #636EFA;"></div>
    
    <!-- Green: Projected Growth -->
    <div style="flex: {green_percent}; background-color: #00CC96;"></div>
    
    <!-- Empty Space -->
    <div style="flex: {100 - (blue_percent + green_percent)};"></div>
    
    <!-- Text -->
    <div style="position: absolute; width: 100%; text-align: center; top: 50%;
                transform: translateY(-50%); font-weight: bold; color: black;">
        {total_percent:.1f}% of Goal
    </div>
</div>
"""
st.markdown(progress_bar_html, unsafe_allow_html=True)

# --- Legend ---
st.markdown(
    """
    <div style="margin-top: 10px; display: flex; gap: 20px;">
        <div style="display: flex; align-items: center; gap: 5px;">
            <div style="width: 20px; height: 20px; background-color: #636EFA; border-radius: 4px;"></div>
            <span>Contributions</span>
        </div>
        <div style="display: flex; align-items: center; gap: 5px;">
            <div style="width: 20px; height: 20px; background-color: #00CC96; border-radius: 4px;"></div>
            <span>Projected Growth</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Extra Info ---
st.write(f"💰 Current Contributions: **${current_amount:,.2f}**")
st.write(f"📈 Projected Growth: **${projected_growth:,.2f}**")
st.write(f"🎯 Goal Amount: **${goal_amount:,.2f}**")
st.write(f"✅ Total with Growth: **${min(projected_amount, goal_amount):,.2f}**")
