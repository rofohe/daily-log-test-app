import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# ------------------------
# Page config
# ------------------------
st.set_page_config(
    page_title="Daily Log",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Daily Log")

# ------------------------
# Google Sheets connection
# ------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

gc = gspread.authorize(credentials)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1JHcRPvNsl7og23GT-0AKNmoyD8BwFPP0UB_myJsvBcg"
worksheet = gc.open_by_url(SHEET_URL).worksheet("database")

# ------------------------
# Load existing data
# ------------------------
records = worksheet.get_all_records()
df = pd.DataFrame(records)

if not df.empty:
    df["date"] = pd.to_datetime(df["date"]).dt.date

# ------------------------
# Streak calculation
# ------------------------
def calculate_streak(dates):
    if not dates:
        return 0

    unique_dates = sorted(set(dates), reverse=True)
    streak = 0
    current_day = datetime.today().date()

    for d in unique_dates:
        if d == current_day:
            streak += 1
            current_day -= timedelta(days=1)
        elif d == current_day - timedelta(days=1):
            current_day -= timedelta(days=1)
            streak += 1
        else:
            break

    return streak

streak = calculate_streak(df["date"].tolist() if not df.empty else [])

st.metric("🔥 Current streak (days)", streak)

st.divider()

# ------------------------
# Input form
# ------------------------
with st.form("daily_log_form", clear_on_submit=True):

    st.subheader("Activities")

    activities_options = [
        "Workout",
        "Walk",
        "Stretching / Mobility",
        "Meditation",
        "Reading",
        "Journaling",
        "Healthy Eating",
        "Early Sleep"
    ]

    selected_activities = st.multiselect(
        "Which activities did you do today?",
        activities_options
    )

    st.subheader("Body metrics")

    weight = st.number_input("Weight", min_value=0.0, step=0.1)
    waist = st.number_input("Waist circumference", min_value=0.0, step=0.1)

    st.subheader("Wellbeing")

    wellbeing = st.slider("Overall wellbeing (0–10)", 0, 10, 5)

    st.subheader("Reflection")

    reflection = st.text_area(
        "Anything you'd like to reflect on today?",
        height=120
    )

    submitted = st.form_submit_button("Save entry")

# ------------------------
# Save entry
# ------------------------
if submitted:
    today = datetime.now()

    # Prevent duplicate daily entries
    if not df.empty and today.date() in df["date"].values:
        st.warning("You already logged an entry for today.")
    else:
        row = [
            today.isoformat(),
            today.date().isoformat(),
            today.strftime("%A"),
            ", ".join(selected_activities),
            weight,
            waist,
            wellbeing,
            reflection
        ]

        worksheet.append_row(row)

        st.success("✅ Entry saved!")
        st.rerun()

# ------------------------
# Show recent entries
# ------------------------
st.divider()
st.subheader("📊 Recent entries")

if not df.empty:
    st.dataframe(
        df.sort_values("date", ascending=False).head(7),
        use_container_width=True
    )
else:
    st.info("No entries yet.")
