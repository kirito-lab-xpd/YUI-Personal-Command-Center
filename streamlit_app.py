"""YUI's isolated, session-only browser demo."""

from copy import deepcopy
from datetime import date, timedelta

import streamlit as st


st.set_page_config(
    page_title="YUI | Personal Command Center",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAMPLE_DATA = {
    "tasks": [
        {"title": "Plan the week", "completed": False},
        {"title": "Review project notes", "completed": True},
        {"title": "Organize study materials", "completed": False},
        {"title": "Take a screen break", "completed": True},
    ],
    "subjects": ["Computer Science", "Design"],
    "goals": [
        {
            "subject": "Computer Science",
            "goal": "Review data structures",
            "completed": True,
        },
        {
            "subject": "Computer Science",
            "goal": "Practice algorithm problems",
            "completed": False,
        },
        {
            "subject": "Design",
            "goal": "Study color systems",
            "completed": False,
        },
    ],
    "workouts": [
        {
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "activity": "Walk",
            "duration": 30,
            "notes": "Easy recovery session",
        },
        {
            "date": (date.today() - timedelta(days=3)).isoformat(),
            "activity": "Strength training",
            "duration": 45,
            "notes": "Full-body session",
        },
    ],
    "notes": [
        {
            "title": "Weekly intention",
            "content": "Make steady progress and leave room to recharge.",
            "date": date.today().isoformat(),
        },
        {
            "title": "Study reminder",
            "content": "Use short practice sessions and review mistakes.",
            "date": date.today().isoformat(),
        },
    ],
}


def get_demo_data():
    if "yui_demo_data" not in st.session_state:
        st.session_state.yui_demo_data = deepcopy(SAMPLE_DATA)
    return st.session_state.yui_demo_data


def set_section(section):
    st.session_state.demo_section = section


def set_completed(collection, index, widget_key):
    get_demo_data()[collection][index]["completed"] = st.session_state[widget_key]


def render_task_list(tasks, editable=False):
    if not tasks:
        st.caption("Nothing here yet. Add an item to get started.")
        return

    for index, task in enumerate(tasks):
        if editable:
            widget_key = f"task_done_{index}_{task['title']}"
            st.checkbox(
                task["title"],
                value=bool(task.get("completed")),
                key=widget_key,
                on_change=set_completed,
                args=("tasks", index, widget_key),
            )
        else:
            status = "Complete" if task.get("completed") else "In progress"
            st.markdown(
                f"- {'✅' if task.get('completed') else '◯'} "
                f"**{task['title']}** · {status}"
            )


def render_dashboard(data):
    st.title("Welcome back")
    st.caption(f"Your personal command center · {date.today():%A, %B %d, %Y}")

    task_count = len(data["tasks"])
    completed_tasks = sum(bool(task.get("completed")) for task in data["tasks"])
    completed_goals = sum(bool(goal.get("completed")) for goal in data["goals"])
    workout_minutes = sum(workout["duration"] for workout in data["workouts"])

    cards = st.columns(4)
    cards[0].metric("Tasks", task_count, f"{completed_tasks} completed")
    cards[1].metric(
        "Study",
        len(data["subjects"]),
        f"{len(data['goals'])} goals · {completed_goals} complete",
    )
    cards[2].metric(
        "Fitness",
        len(data["workouts"]),
        f"{workout_minutes} total minutes",
    )
    cards[3].metric("Notes", len(data["notes"]), "Saved in this demo session")

    left, right = st.columns((1.4, 1))
    with left:
        st.subheader("Recent tasks")
        render_task_list(data["tasks"][-5:][::-1])
    with right:
        st.subheader("Study progress")
        goal_total = len(data["goals"])
        progress = completed_goals / goal_total if goal_total else 0
        st.progress(progress, text=f"{completed_goals} of {goal_total} goals complete")
        for goal in data["goals"][:4]:
            marker = "✅" if goal.get("completed") else "◯"
            st.markdown(f"{marker} **{goal['subject']}** · {goal['goal']}")

    st.subheader("Quick actions")
    quick_actions = st.columns(4)
    for column, label, section in zip(
        quick_actions,
        ("Add a task", "Study goals", "Log a workout", "Create a note"),
        ("Tasks", "Study", "Fitness", "Notes"),
    ):
        column.button(
            label,
            key=f"quick_{section}",
            use_container_width=True,
            on_click=set_section,
            args=(section,),
        )

    if data["workouts"]:
        latest = data["workouts"][-1]
        st.caption(
            f"Latest workout: {latest['activity']} · {latest['duration']} min "
            f"· {latest['date']}"
        )


def render_tasks(data):
    st.title("Tasks")
    st.caption("Task changes are temporary and stay in this browser session.")
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("New task", placeholder="What would you like to do?")
        submitted = st.form_submit_button("Add task", type="primary")
    if submitted:
        if title.strip():
            data["tasks"].append({"title": title.strip(), "completed": False})
            st.success("Task added to this demo session.")
        else:
            st.warning("Enter a task before adding it.")

    st.subheader("Your tasks")
    render_task_list(data["tasks"], editable=True)


def render_study(data):
    st.title("Study")
    st.caption("Explore sample subjects and update study goals for this session.")
    if data["subjects"]:
        st.write("**Subjects:** " + " · ".join(data["subjects"]))
    else:
        st.info("Add a subject to begin tracking study goals.")

    if data["subjects"]:
        with st.form("add_goal_form", clear_on_submit=True):
            subject = st.selectbox("Subject", data["subjects"])
            goal_text = st.text_input("New study goal")
            submitted = st.form_submit_button("Add goal", type="primary")
        if submitted:
            if goal_text.strip():
                data["goals"].append(
                    {
                        "subject": subject,
                        "goal": goal_text.strip(),
                        "completed": False,
                    }
                )
                st.success("Study goal added to this demo session.")
            else:
                st.warning("Enter a study goal before adding it.")

    st.subheader("Study goals")
    if not data["goals"]:
        st.caption("No goals yet. Add one above.")
    for index, goal in enumerate(data["goals"]):
        widget_key = f"goal_done_{index}_{goal['goal']}"
        st.checkbox(
            f"{goal['subject']} · {goal['goal']}",
            value=bool(goal.get("completed")),
            key=widget_key,
            on_change=set_completed,
            args=("goals", index, widget_key),
        )


def render_fitness(data):
    st.title("Fitness")
    workout_minutes = sum(workout["duration"] for workout in data["workouts"])
    total, minutes = st.columns(2)
    total.metric("Workouts logged", len(data["workouts"]))
    minutes.metric("Total minutes", workout_minutes)

    with st.form("add_workout_form", clear_on_submit=True):
        activity = st.text_input("Activity", placeholder="e.g. Walk, cycling")
        duration = st.number_input("Duration (minutes)", min_value=1, value=30)
        workout_date = st.date_input("Date", value=date.today())
        notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("Log workout", type="primary")
    if submitted:
        if activity.strip():
            data["workouts"].append(
                {
                    "date": workout_date.isoformat(),
                    "activity": activity.strip(),
                    "duration": int(duration),
                    "notes": notes.strip(),
                }
            )
            st.success("Workout added to this demo session.")
        else:
            st.warning("Enter an activity before logging a workout.")

    st.subheader("Workout history")
    if not data["workouts"]:
        st.caption("No workouts yet. Log one above.")
    for workout in reversed(data["workouts"]):
        st.markdown(
            f"**{workout['activity']}** · {workout['duration']} min "
            f"· {workout['date']}"
        )
        if workout.get("notes"):
            st.caption(workout["notes"])


def render_notes(data):
    st.title("Notes")
    st.caption("Notes created here are session-only sample data.")
    query = st.text_input("Search notes", placeholder="Search titles and content")
    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Title")
        content = st.text_area("Note")
        submitted = st.form_submit_button("Create note", type="primary")
    if submitted:
        if title.strip() and content.strip():
            data["notes"].append(
                {
                    "title": title.strip(),
                    "content": content.strip(),
                    "date": date.today().isoformat(),
                }
            )
            st.success("Note added to this demo session.")
        else:
            st.warning("Both a title and note are required.")

    st.subheader("Saved notes")
    matches = [
        note
        for note in data["notes"]
        if query.casefold() in note["title"].casefold()
        or query.casefold() in note["content"].casefold()
    ]
    if not matches:
        st.caption("No matching notes.")
    for note in reversed(matches):
        with st.expander(f"{note['title']} · {note['date']}"):
            st.write(note["content"])


def render_assistant(data):
    st.title("Assistant")
    st.caption("A lightweight offline demo—no external AI model is connected.")
    with st.form("assistant_form"):
        command = st.text_input(
            "Try a command",
            placeholder="help, status, tasks, study, or motivate",
        )
        submitted = st.form_submit_button("Run command", type="primary")
    if not submitted:
        st.info("Commands are read-only and use only this session's sample data.")
        return

    normalized = command.strip().casefold()
    if normalized == "help":
        response = "Available commands: help, status, tasks, study, motivate."
    elif normalized == "status":
        response = (
            f"{len(data['tasks'])} tasks, {len(data['goals'])} study goals, "
            f"{len(data['workouts'])} workouts, and {len(data['notes'])} notes "
            "in this demo session."
        )
    elif normalized == "tasks":
        pending = sum(not task.get("completed") for task in data["tasks"])
        response = f"You have {pending} pending tasks in this demo."
    elif normalized == "study":
        completed = sum(bool(goal.get("completed")) for goal in data["goals"])
        response = f"{completed} of {len(data['goals'])} study goals are complete."
    elif normalized == "motivate":
        response = "Small steps add up. Choose one useful next action and begin."
    else:
        response = "I don't recognize that offline command. Type 'help' for options."
    st.success(response)


def main():
    data = get_demo_data()
    sections = ("Dashboard", "Tasks", "Study", "Fitness", "Notes", "Assistant")

    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        .stApp { background: #0d0b12; color: #f5f3fa; }
        [data-testid="stSidebar"] { background: #121019; border-right: 1px solid #282331; }
        [data-testid="stHeader"] { background: rgba(13, 11, 18, 0.92); }
        [data-testid="stMetric"] {
            background: #17141f; border: 1px solid #2c2637;
            border-radius: 14px; padding: 16px 18px;
        }
        [data-testid="stMetricValue"] { color: #f5f3fa; }
        [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"] { color: #aaa3b5; }
        h1, h2, h3 { color: #f5f3fa; }
        .stButton > button[kind="primary"], .stFormSubmitButton > button {
            background: #8b5cf6; color: white; border: 0; border-radius: 9px;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            border-color: #a681ff; color: white; background: #6d28d9;
        }
        div[data-testid="stProgress"] > div > div { background: #8b5cf6; }
        [data-testid="stExpander"] { background: #17141f; border-color: #2c2637; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.markdown("# ✦ YUI")
        st.caption("PERSONAL COMMAND CENTER")
        st.markdown("---")
        st.radio("Workspace", sections, key="demo_section", label_visibility="collapsed")
        st.markdown("---")
        st.caption("● DEMO MODE")
        st.caption("Sample data · temporary changes")
        if st.button("Reset sample data", use_container_width=True):
            st.session_state.yui_demo_data = deepcopy(SAMPLE_DATA)
            st.rerun()

    st.info(
        "DEMO DATA ONLY · This browser demo uses clearly labeled sample data. "
        "Changes are temporary to this session. It never reads or changes your "
        "desktop JSON files."
    )

    section = st.session_state.demo_section
    renderers = {
        "Dashboard": render_dashboard,
        "Tasks": render_tasks,
        "Study": render_study,
        "Fitness": render_fitness,
        "Notes": render_notes,
        "Assistant": render_assistant,
    }
    renderers[section](data)


if __name__ == "__main__":
    main()
