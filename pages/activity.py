import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Activity",
    page_icon="🏃",
    layout="centered"
)

st.title("Exercise Activity")

EXERCISES = ["yoga", "meditation", "bike", "run", "walk", "strength"]

exercise_choice = st.selectbox("Select exercise type", EXERCISES)

extra_options = {}
if exercise_choice in ["bike", "run"]:
    st.subheader("Route details")
    extra_options["bike_run"] = st.checkbox("Bike Run")
    extra_options["piesberg_loop"] = st.checkbox("Piesberg Loop")
    extra_options["piesberg_stairs"] = st.checkbox("Piesberg Stairs")

st.subheader("Session Details")

duration = st.number_input("Duration (minutes)", min_value=0, step=1)
timestamp = st.time_input("Time of session", value=datetime.now().time())
wellbeing = st.slider("Wellbeing: dying to fit", 0, 10, 5)

if st.button("Save Activity"):
    st.success("Activity saved")
