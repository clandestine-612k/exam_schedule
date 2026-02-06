import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from planner.generator import generate_plan
from planner.validator import validate_plan
from planner.parser import flatten_plan
from db.database import get_db

# ------------------- HELPERS -------------------

def get_week_dates(anchor_date):
    d = datetime.fromisoformat(anchor_date)
    start = d - timedelta(days=d.weekday())  # Monday
    return [(start + timedelta(days=i)).date().isoformat() for i in range(7)]

def calculate_streak(df, active_date):
    """
    Current streak:
    - consecutive fully-completed days ending at active_date

    Best streak:
    - max consecutive fully-completed days anywhere
    """

    if df.empty:
        return 0, 0

    # Day-wise completion status
    day_status = (
        df.groupby("date")["completed"]
        .apply(lambda x: x.all())
        .sort_index()
    )

    # ---------- BEST STREAK ----------
    best_streak = 0
    running = 0

    for done in day_status.values:
        if done:
            running += 1
            best_streak = max(best_streak, running)
        else:
            running = 0

    # ---------- CURRENT STREAK (ANCHOR TO active_date) ----------
    current_streak = 0

    # Only consider dates <= active_date
    relevant_days = day_status[day_status.index <= active_date]

    for done in reversed(relevant_days.values):
        if done:
            current_streak += 1
        else:
            break

    return current_streak, best_streak




st.set_page_config(page_title="Exam Planner", layout="wide")
st.title("📘 Your Personalized Study Planner for Competitive Exams")

# ------------------- LOAD PLAN METADATA -------------------

conn = get_db()
meta = dict(conn.execute("SELECT key, value FROM plan_meta").fetchall())
conn.close()

# ------------------- INPUTS -------------------

exam_options = ["NEET-PG", "UPSC CSE", "GATE CS", "CAT", "SSC","NEET-UG"]
default_exam = meta.get("exam", exam_options[0])

exam = st.selectbox(
    "Select Exam",
    exam_options,
    index=exam_options.index(default_exam)
)


default_days = int(meta.get("days", 180))

days_left = st.number_input(
    "Days left",
    min_value=1,
    max_value=365,
    value=default_days
)

default_hours = int(meta.get("hours", 8))

hours_per_day = st.number_input(
    "Study hours/day",
    min_value=1,
    max_value=16,
    value=default_hours
)


if st.button("Generate Study Plan"):
    with st.spinner("Generating your personalized plan..."):
        try:
            raw = generate_plan(exam, days_left, hours_per_day)
            #st.code(raw)
            plan = validate_plan(raw, days_left, hours_per_day)
            rows = flatten_plan(plan)

            conn = get_db()
            
            conn.execute("DELETE FROM tasks")
            conn.execute("DELETE FROM plan_meta")

            conn.execute(
                "INSERT INTO plan_meta (key, value) VALUES (?, ?)",
                ("exam", exam)
            )
            conn.execute(
                "INSERT INTO plan_meta (key, value) VALUES (?, ?)",
                ("days", str(days_left))
            )
            conn.execute(
                "INSERT INTO plan_meta (key, value) VALUES (?, ?)",
                ("hours", str(hours_per_day))
            )

            conn.executemany(
                "INSERT INTO tasks (date, subject, topic, hours, completed) VALUES (?,?,?,?,?)",
                [(r["date"], r["subject"], r["topic"], r["hours"], 0) for r in rows]
            )
            conn.commit()
            conn.close()

            st.success("Study plan generated successfully!")
            st.session_state.pop("active_date", None)

        except Exception as e:
            st.error(f"Plan generation failed: {e}")

st.divider()

# ------------------- DAILY TASKS -------------------

st.header("📅 Daily Tasks")

conn = get_db()
df_all = pd.read_sql("SELECT * FROM tasks ORDER BY date ASC", conn)
conn.close()

if df_all.empty:
    st.info("No study plan found. Please generate a plan.")
    st.stop()

all_dates = sorted(df_all["date"].unique())

# ✅ SAFE active_date initialization
if "active_date" not in st.session_state or st.session_state["active_date"] not in all_dates:
    incomplete = df_all[df_all["completed"] == 0]
    st.session_state["active_date"] = (
        incomplete.iloc[0]["date"] if not incomplete.empty else all_dates[0]
    )

active_date = st.session_state["active_date"]
idx = all_dates.index(active_date)

# Navigation
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅ Previous") and idx > 0:
        st.session_state["active_date"] = all_dates[idx - 1]
        st.rerun()

with col3:
    if st.button("Next ➡") and idx < len(all_dates) - 1:
        st.session_state["active_date"] = all_dates[idx + 1]
        st.rerun()

st.subheader(f"Tasks for {active_date}")
df_today = df_all[df_all["date"] == active_date]

updates = []
completed_count = 0

for _, row in df_today.iterrows():
    checked = st.checkbox(
        f"{row.subject} – {row.topic} ({row.hours}h)",
        value=bool(row.completed),
        key=f"task_{row.id}"
    )

    if checked:
        completed_count += 1

    if checked != bool(row.completed):
        updates.append((int(checked), row.id))

if updates:
    conn = get_db()
    conn.executemany("UPDATE tasks SET completed = ? WHERE id = ?", updates)
    conn.commit()
    conn.close()

progress = completed_count / len(df_today)
st.progress(progress)

if progress == 1.0:
    st.success("All tasks completed for this day 🎉")

st.divider()

# ------------------- WEEK VIEW -------------------

st.header("🗓️ Week View")

week_dates = get_week_dates(active_date)
week_df = df_all[df_all["date"].isin(week_dates)]

cols = st.columns(7)

for i, day in enumerate(week_dates):
    day_df = week_df[week_df["date"] == day]

    with cols[i]:
        st.markdown(f"**{day}**")

        if day == active_date:
            st.markdown("🟦 **Selected**")

        if day_df.empty:
            st.caption("No tasks")
            continue

        total = len(day_df)
        done = day_df["completed"].sum()
        percent = int((done / total) * 100)

        st.progress(done / total)

        if percent == 100:
            st.success("Done")
        elif percent == 0:
            st.warning("Not started")
        else:
            st.info(f"{percent}%")

        if st.button("Open", key=f"open_{day}"):
            st.session_state["active_date"] = day
            st.rerun()

st.divider()

# ------------------- STATISTICS -------------------

st.header("📊 Overall Progress")

conn = get_db()
df_all = pd.read_sql("SELECT * FROM tasks ORDER BY date ASC", conn)
conn.close()

if df_all.empty:
    st.info("No progress data available yet.")
    st.stop()

current_streak, best_streak = calculate_streak(df_all, st.session_state["active_date"])

col1, col2, col3 = st.columns(3)

with col1:
    overall_percent = round((df_all["completed"].sum() / len(df_all)) * 100, 2)
    st.metric("Overall Completion", f"{overall_percent}%")

with col2:
    st.metric("🔥 Current Streak", f"{current_streak} days")

with col3:
    st.metric("🏆 Best Streak", f"{best_streak} days")

st.subheader("Subject-wise Completion")

subject_stats = (
    df_all.groupby("subject")["completed"]
    .mean()
    .reset_index()
)

subject_stats["completed"] *= 100
st.bar_chart(subject_stats, x="subject", y="completed")
