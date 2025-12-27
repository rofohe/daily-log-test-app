# --------------------------------------------------
# activity_page.py
# --------------------------------------------------

import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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
# Function to get Google Sheet worksheet
# --------------------------------------------------
def get_worksheet():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1JHcRPvNsl7og23GT-0AKNmoyD8BwFPP0UB_myJsvBcg"
    ws = client.open_by_url(SHEET_URL).worksheet("activity_db")
    return ws

# Optional: test worksheet connection at page load
try:
    worksheet = get_worksheet()
    st.write("Connected worksheet:", worksheet.title)
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")

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
duration = st.number_input("Duration (minutes)", min_value=0, step=1, format="%d")
timestamp = st.time_input("Time of session", value=datetime.now().time())
wellbeing = st.slider("Wellbeing: dying to fit", min_value=0, max_value=10, value=5)

# --------------------------------------------------
# Submit button
# --------------------------------------------------
if st.button("Save Activity"):
    st.write("Button clicked!")  # Debug: confirms button triggers

    # Collect data
    entry = {
        "exercise": exercise_choice,
        "extras": {k: v for k, v in extra_options.items() if v},
        "duration": duration,
        "timestamp": timestamp.strftime("%H:%M:%S"),
        "wellbeing": wellbeing,
        "date": datetime.today().isoformat()
    }

    # Append to Google Sheet with fresh connection
    try:
        worksheet = get_worksheet()  # fresh connection on button click
        worksheet.append_row([
            entry["date"],
            entry["timestamp"],
            entry["exercise"],
            str(entry["extras"]),
            entry["duration"],
            entry["wellbeing"]
        ])
        st.success("Activity saved to Google Sheets!")
        st.write("Total rows in sheet:", worksheet.row_count)  # debug
    except Exception as e:
        st.error(f"Failed to save activity: {e}")

    # Show the submitted data in the app
    st.json(entry)
