# --------------------------------------------------
# activity_page.py
# --------------------------------------------------

import streamlit as st
from datetime import datetime

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Exercise Activity",
    page_icon="🏃",
    layout="centered"
)

st.title("Exercise Activity")

# --------------------------------------------------
# Exercise selection
# --------------------------------------------------
EXERCISES = ["yoga", "meditation", "bike", "run", "walk", "strength"]

exercise_choice = st.selectbox("Select exercise type", EXERCISES)

# Conditional extra questions
extra_options = {}
if exercise_choice in ["bike", "run"]:
    st.subheader("Optional details")
    extra_options["bike_run"] = st.checkbox("Bike Run")
    extra_options["piesberg_loop"] = st.checkbox("Piesberg Loop")
    extra_options["piesberg_stairs"] = st.checkbox("Piesberg Stairs")

# --------------------------------------------------
# Metrics inputs
# --------------------------------------------------
st.subheader("Session Details")

duration = st.number_input(
    "Duration (minutes)", min_value=0, step=1, format="%d"
)

timestamp = st.time_input(
    "Time of session", value=datetime.now().time()
)

wellbeing = st.slider(
    "Wellbeing: dying to fit", min_value=0, max_value=10, value=5
)

# --------------------------------------------------
# Submit button
# --------------------------------------------------
if st.button("Save Activity"):
    # Collect data
    entry = {
        "exercise": exercise_choice,
        "extras": {k: v for k, v in extra_options.items() if v},
        "duration": duration,
        "timestamp": timestamp.strftime("%H:%M:%S"),
        "wellbeing": wellbeing,
        "date": datetime.today().isoformat()
    }

    # Here you would typically append to Google Sheets or database
    # For now, just show confirmation
    st.success("Activity saved!")
    st.json(entry)
