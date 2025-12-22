import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta


#st.write("Loaded secrets:", list(st.secrets.keys()))

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Daily Log",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Daily Log")

# --------------------------------------------------
# Google Sheets connection
# --------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

gc = gspread.authorize(credentials)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1JHcRPvNsl7og23GT-0AKNmoyD8BwFPP0UB_myJsvBcg"
worksheet = gc.open_by_url(SHEET_URL).worksheet("database")

# --------------------------------------------------
# Load existing data
# --------------------------------------------------
records = worksheet.get_all_records()
df = pd.DataFrame(records)

if not df.empty:
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["activities"] = df["activities"].fillna("")

# --------------------------------------------------
# Activity configuration
# --------------------------------------------------
activities_options = [
    "Sleep",
    "Hygiene",
    "Diet",
    "Family & House",
    "Sobriety",
    "Productivity",
    "Self-actualisation"
]

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def calculate_daily_streak(dates):
    if not dates:
        return 0

    dates = sorted(set(dates), reverse=True)
    streak = 0
    current = datetime.today().date()

    for d in dates:
        if d == current:
            streak += 1
            current -= timedelta(days=1)
        else:
            break

    return streak


def activity_streaks(df):
    if df.empty:
        return {}

    streaks = {}

    for activity in activities_options:
        dates = df[df["activities"].str.contains(activity, na=False)]["date"].tolist()
        if not dates:
            continue

        dates = sorted(set(dates), reverse=True)
        streak = 0
        current = dates[0]

        for d in dates:
            if d == current:
                streak += 1
                current -= timedelta(days=1)
            else:
                break

        if streak >= 3:
            streaks[activity] = streak

    return streaks


def reflection_wordcount_stats(df, current_reflection):
    current_wc = len(current_reflection.split())

    if df.empty or "reflection" not in df.columns:
        return current_wc, None

    last_reflection = str(df.sort_values("date").iloc[-1]["reflection"])
    last_wc = len(last_reflection.split())

    return current_wc, last_wc

# --------------------------------------------------
# Streak metric
# --------------------------------------------------
daily_streak = calculate_daily_streak(df["date"].tolist() if not df.empty else [])
st.metric("🔥 Daily entry streak", f"{daily_streak} days")

st.divider()

# --------------------------------------------------
# Input form
# --------------------------------------------------
with st.form("daily_log_form", clear_on_submit=True):

    st.subheader("Activities")

    cols = st.columns(len(activities_options))
    activity_values = {}

    for col, activity in zip(cols, activities_options):
        with col:
            activity_values[activity] = st.checkbox(activity)

    st.subheader("Body metrics")

    weight = st.number_input("Weight", min_value=0.0, step=0.1)

    waist_in = st.number_input(
        "Waist (in)",
        min_value=1.0,
        max_value=2.0,
        step=0.01
    )

    waist_out = st.number_input(
        "Waist (out)",
        min_value=1.0,
        max_value=2.0,
        step=0.01
    )

    st.subheader("Wellbeing")

    wellbeing = st.slider("Overall wellbeing (0–10)", 0, 10, 5)

    st.subheader("Reflection")

    reflection = st.text_area(
        "Write freely about today",
        height=140
    )

    submitted = st.form_submit_button("Save entry")

# --------------------------------------------------
# Save entry
# --------------------------------------------------
if submitted:
    now = datetime.now()
    today = now.date()

    if not df.empty and today in df["date"].values:
        st.warning("You already logged an entry for today.")
    else:
        selected_activities = [
            name for name, checked in activity_values.items() if checked
        ]

        row = [
            now.isoformat(),
            today.isoformat(),
            now.strftime("%A"),
            ", ".join(selected_activities),
            weight,
            waist_in,
            waist_out,
            wellbeing,
            reflection
        ]

        worksheet.append_row(row)
        st.success("✅ Entry saved")
        st.rerun()

# --------------------------------------------------
# Summary section
# --------------------------------------------------
st.divider()
st.subheader("📊 Daily Summary")

# Activity streaks
streaks = activity_streaks(df)

if streaks:
    st.markdown("**Activity streaks (≥ 3 days):**")
    for activity, days in streaks.items():
        st.write(f"🔥 {activity}: {days} days")
else:
    st.write("No activity streaks of 3+ days yet.")

# Reflection stats
current_wc, last_wc = reflection_wordcount_stats(df, reflection)

if last_wc is not None:
    diff = current_wc - last_wc
    if diff > 0:
        st.success(f"Reflection word count: {current_wc} words (⬆️ +{diff} vs last entry)")
    elif diff < 0:
        st.info(f"Reflection word count: {current_wc} words (⬇️ {abs(diff)} vs last entry)")
    else:
        st.write(f"Reflection word count: {current_wc} words (same as last entry)")
else:
    st.write(f"Reflection word count: {current_wc} words")

# --------------------------------------------------
# Recent entries
# --------------------------------------------------
st.divider()
st.subheader("📅 Recent entries")

if not df.empty:
    st.dataframe(
        df.sort_values("date", ascending=False).head(7),
        use_container_width=True
    )
else:
    st.info("No entries yet.")
