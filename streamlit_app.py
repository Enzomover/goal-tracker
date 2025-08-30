# ---------------- Custom Progress Bar ----------------
st.subheader(f"📊 Tracking: {data['goal_name']}")

# Dynamic bar color based on progress
if progress >= 100:
    bar_color = "#4CAF50"  # Green
elif progress >= 75:
    bar_color = "#FFC107"  # Amber
elif progress >= 50:
    bar_color = "#2196F3"  # Blue
else:
    bar_color = "#F44336"  # Red

st.markdown(
    f"""
    <div style="width:100%; background:#ddd; border-radius:30px; padding:3px; margin:15px 0;">
        <div style="width:{progress}%; background:{bar_color};
                    height:28px; border-radius:30px; text-align:center; 
                    color:white; font-weight:bold; line-height:28px;">
            {progress:.2f}%  —  ${format_number(current_amount)}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
