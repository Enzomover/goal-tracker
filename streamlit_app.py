import streamlit as st

st.title("🎯 Goal Tracker (Phone Test Version)")

# --- Inputs ---
goal_name = st.text_input("Goal Name", "Retirement Fund")
goal_amount = st.number_input("Target Amount ($)", min_value=1, value=50000, step=100)
current_amount = st.number_input("Current Progress ($)", min_value=0, value=5000, step=100)

# --- Progress Calculation ---
progress = min((current_amount / goal_amount) * 100, 100)

# --- Display ---
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
