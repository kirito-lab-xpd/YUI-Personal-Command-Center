
import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_data(filename):
    """Load a JSON list safely from the YUI project folder."""
    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def show_status():
    tasks = load_data("tasks.json")
    subjects = load_data("subjects.json")
    goals = load_data("study_goals.json")
    workouts = load_data("fitness.json")
    notes = load_data("notes.json")

    completed_tasks = sum(
        1 for item in tasks
        if isinstance(item, dict) and item.get("completed")
    )

    completed_goals = sum(
        1 for item in goals
        if isinstance(item, dict) and item.get("completed")
    )

    print("\n========== YUI STATUS ==========")
    print(f"Tasks:       {completed_tasks}/{len(tasks)} completed")
    print(f"Subjects:    {len(subjects)}")
    print(f"Study goals: {completed_goals}/{len(goals)} completed")
    print(f"Workouts:    {len(workouts)}")
    print(f"Notes:       {len(notes)}")
    print("================================")


def _display_study_goals(goals):
    valid_goals = [
        (index, goal)
        for index, goal in enumerate(goals)
        if isinstance(goal, dict)
    ]

    if not valid_goals:
        print("No study goals yet.")
        return valid_goals

    print("\n========== STUDY GOALS ==========")
    for number, (_, goal) in enumerate(valid_goals, 1):
        status = "Completed" if goal.get("completed") else "Pending"
        print(
            f"{number}. [{status}] "
            f"{goal.get('subject', 'Unknown')} - "
            f"{goal.get('goal', 'Untitled goal')}"
        )
    print("=================================")
    return valid_goals


def assistant(load_goals, save_goals, load_subjects):
    print("\n================================")
    print("       YUI AI ASSISTANT")
    print("================================")
    print("YUI Assistant v1 is ready.")
    print("Type 'help' to see available commands.")

    while True:
        command = input("\nYou > ").strip().lower()
        aliases = {
            "show my tasks": "tasks",
            "list my tasks": "tasks",
            "how many tasks": "tasks",
            "show my notes": "notes",
            "how many notes": "notes",
            "what time is it": "time",
            "what's the time": "time",
            "today's date": "date",
            "show my progress": "status",
            "show my status": "status",
            "add goal": "add study goal",
            "create study goal": "add study goal",
            "new study goal": "add study goal",
            "show my study goals": "study goals",
            "list study goals": "study goals",
            "view study goals": "study goals",
            "finish study goal": "complete study goal",
            "complete goal": "complete study goal",
            "workout history": "fitness",
            "motivate me": "motivate",
            "help me": "help",
        }

        command = aliases.get(command, command)

        if command in ("exit", "quit", "back"):
            print("YUI Assistant shutting down. See you!")
            return

        elif command == "help":
            print("\nAvailable commands:")
            print("  help       - Show commands")
            print("  time       - Show current time")
            print("  date       - Show today's date")
            print("  status     - Summarize your YUI data")
            print("  tasks      - List your tasks")
            print("  complete task - Mark a pending task complete")
            print("  study      - Summarize subjects and goals")
            print("  add study goal - Add a goal for an existing subject")
            print("  study goals - List goals and their status")
            print("  complete study goal - Mark a goal completed")
            print("  log workout - Save a workout")
            print("  fitness    - Count logged workouts")
            print("  add note   - Save a note")
            print("  search notes - Search saved notes")
            print("  notes      - Count saved notes")
            print("  motivate   - Get a motivational message")
            print("  exit       - Return to the main menu")

        elif command == "time":
            print("Current time:", datetime.now().strftime("%I:%M %p"))

        elif command == "date":
            print("Today's date:", datetime.now().strftime("%d %B %Y"))

        elif command in ("status", "dashboard"):
            show_status()
        
        elif command in ("complete task", "finish task", "mark task complete"):
            tasks = load_data("tasks.json")

            pending = [
                task for task in tasks
                if isinstance(task, dict) and not task.get("completed", False)
            ]

            if not pending:
                print("You have no pending tasks!")
                continue

            print("\n--- PENDING TASKS ---")
            for number, task in enumerate(pending, 1):
                print(f"{number}. {task.get('title', 'Untitled task')}")

            try:
                number = int(input("Which task number did you complete? "))

                if not 1 <= number <= len(pending):
                    print("Invalid task number.")
                    continue

                selected = pending[number - 1]
                selected["completed"] = True

                path = os.path.join(BASE_DIR, "tasks.json")

                with open(path, "w", encoding="utf-8") as file:
                    json.dump(tasks, file, indent=4, ensure_ascii=False)

                print(f"Task completed: {selected.get('title', 'Untitled task')}!")

            except ValueError:
                print("Please enter a valid number.")
            except OSError as error:
                print(f"Could not save the task: {error}")

        elif command == "tasks":
            tasks_data = load_data("tasks.json")

            if not tasks_data:
                print("You have no tasks yet.")
                continue

            print("\n========== YOUR TASKS ==========")

            for number, task in enumerate(tasks_data, 1):
                if not isinstance(task, dict):
                    continue

                title = task.get("title", "Untitled task")
                status = (
                    "Completed"
                    if task.get("completed", False)
                    else "Pending"
                )

                print(f"{number}. [{status}] {title}")

            print("================================")
        elif command in ("tasks", "show tasks", "list tasks"):
            tasks_data = load_data("tasks.json")

            if not tasks_data:
                print("You have no tasks yet.")
                continue

            print("\n========== YOUR TASKS ==========")

            for number, task in enumerate(tasks_data, 1):
                if not isinstance(task, dict):
                    continue

                title = task.get("title", "Untitled task")
                status = (
                    "Completed"
                    if task.get("completed", False)
                    else "Pending"
                )

                print(f"{number}. [{status}] {title}")

            print("================================")

        elif command == "study":
            subjects = load_subjects()
            goals = load_goals()
            print(f"You have {len(subjects)} subjects and {len(goals)} study goals.")

        elif command == "add study goal":
            subjects = [
                subject for subject in load_subjects()
                if isinstance(subject, str) and subject.strip()
            ]

            if not subjects:
                print("Add a subject in Study before creating a study goal.")
                continue

            print("\n--- SUBJECTS ---")
            for number, subject in enumerate(subjects, 1):
                print(f"{number}. {subject}")

            try:
                number = int(input("Choose a subject number: "))
            except ValueError:
                print("Please enter a valid subject number.")
                continue

            if not 1 <= number <= len(subjects):
                print("Invalid subject number.")
                continue

            goal_text = input("Enter study goal: ").strip()
            if not goal_text:
                print("Study goal cannot be empty.")
                continue

            goals = load_goals()
            goals.append({
                "subject": subjects[number - 1],
                "goal": goal_text,
                "completed": False
            })

            try:
                save_goals(goals)
                print("Study goal saved!")
            except OSError as error:
                print(f"Could not save study goal: {error}")

        elif command == "study goals":
            _display_study_goals(load_goals())

        elif command == "complete study goal":
            goals = load_goals()
            valid_goals = _display_study_goals(goals)

            if not valid_goals:
                continue

            try:
                number = int(input("Enter study goal number to complete: "))
            except ValueError:
                print("Please enter a valid study goal number.")
                continue

            if not 1 <= number <= len(valid_goals):
                print("Invalid study goal number.")
                continue

            _, selected_goal = valid_goals[number - 1]
            if selected_goal.get("completed"):
                print("This study goal is already completed.")
                continue

            selected_goal["completed"] = True
            try:
                save_goals(goals)
                print("Study goal completed!")
            except OSError as error:
                print(f"Could not save study goal: {error}")
        
        elif command in ("log workout", "add workout", "record workout"):
            activity = input("Workout or activity: ").strip()

            if not activity:
                print("Activity cannot be empty.")
                continue

            try:
                duration = int(input("Duration in minutes: "))
                if duration <= 0:
                    print("Duration must be greater than zero.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue

            notes = input("Notes (optional): ").strip()

            workouts = load_data("fitness.json")
            workouts.append({
                "date": datetime.now().date().isoformat(),
                "activity": activity,
                "duration": duration,
                "notes": notes
            })

            path = os.path.join(BASE_DIR, "fitness.json")

            try:
                with open(path, "w", encoding="utf-8") as file:
                    json.dump(workouts, file, indent=4, ensure_ascii=False)

                print(f"Workout saved: {activity} ({duration} minutes)")

            except OSError as error:
                print(f"Could not save workout: {error}")

        elif command == "fitness":
            workouts = load_data("fitness.json")
            print(f"You have logged {len(workouts)} workouts.")
        
        elif command in ("add note", "create note", "save note", "new note"):
            title = input("Note title: ").strip()

            if not title:
                print("Note title cannot be empty.")
                continue

            content = input("Note content: ").strip()

            if not content:
                print("Note content cannot be empty.")
                continue

            notes_data = load_data("notes.json")
            notes_data.append({
                "title": title,
                "content": content,
                "date": datetime.now().date().isoformat()
            })

            path = os.path.join(BASE_DIR, "notes.json")

            try:
                with open(path, "w", encoding="utf-8") as file:
                    json.dump(
                        notes_data, file,
                        indent=4, ensure_ascii=False
                    )

                print(f"Note saved: {title}")

            except OSError as error:
                print(f"Could not save note: {error}")
        
        elif command in ("search notes", "find notes", "find note"):
            notes_data = load_data("notes.json")
            query = input("Search notes for: ").strip().lower()

            if not query:
                print("Enter a search term.")
                continue

            matches = [
                item for item in notes_data
                if isinstance(item, dict)
                and (
                    query in item.get("title", "").lower()
                    or query in item.get("content", "").lower()
                )
            ]

            if matches:
                print("\n--- MATCHING NOTES ---")
                for number, item in enumerate(matches, 1):
                    print(f"\n{number}. {item.get('title', 'Untitled')}")
                    print(f"Date: {item.get('date', 'Not recorded')}")
                    print(item.get("content", ""))
            else:
                print("No matching notes found.")

        elif command == "notes":
            notes = load_data("notes.json")
            print(f"You have {len(notes)} saved notes.")

        elif command == "motivate":
            print("Small steps every day create big results. Keep building YUI!")

        elif not command:
            continue

        else:
            print("I don't recognize that command yet.")
            print("Type 'help' to see what I can do.")

        print("\nNote: This version works offline using commands.")
        print("An AI model is not connected yet.")
