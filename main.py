import json
import os
from app.core.fitness import fitness, load_fitness
from app.notes import notes, load_notes, save_notes
from app.assistant import assistant

# ==============================
# FILE PATHS
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TASK_FILE = os.path.join(BASE_DIR, "tasks.json")
SUBJECT_FILE = os.path.join(BASE_DIR, "subjects.json")
GOAL_FILE = os.path.join(BASE_DIR, "study_goals.json")


# ==============================
# TASK STORAGE
# ==============================

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []

    try:
        with open(TASK_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return []


def save_tasks(tasks):
    os.makedirs(BASE_DIR, exist_ok=True)

    with open(TASK_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


# ==============================
# SUBJECT STORAGE
# ==============================

def load_subjects():
    if not os.path.exists(SUBJECT_FILE):
        return []

    try:
        with open(SUBJECT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return []


def save_subjects(subjects):
    os.makedirs(BASE_DIR, exist_ok=True)

    with open(SUBJECT_FILE, "w", encoding="utf-8") as file:
        json.dump(subjects, file, indent=4)


# ==============================
# STUDY GOAL STORAGE
# ==============================

def load_goals():
    if not os.path.exists(GOAL_FILE):
        return []

    try:
        with open(GOAL_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return []


def save_goals(goals):
    os.makedirs(BASE_DIR, exist_ok=True)

    with open(GOAL_FILE, "w", encoding="utf-8") as file:
        json.dump(goals, file, indent=4)


# ==============================
# TASK MODULE
# ==============================

def tasks():
    while True:

        print("\n--- TASKS ---")
        print("1. Add a task")
        print("2. View tasks")
        print("3. Complete a task")
        print("4. Delete a task")
        print("5. Back")

        choice = input("\nChoose: ").strip()

        # ADD TASK
        if choice == "1":

            task = input("Enter your task: ").strip()

            if not task:
                print("Task cannot be empty.")
                continue

            current_tasks = load_tasks()

            current_tasks.append({
                "title": task,
                "completed": False
            })

            save_tasks(current_tasks)

            print("Task saved!")

        # VIEW TASKS
        elif choice == "2":

            current_tasks = load_tasks()

            if not current_tasks:
                print("\nNo tasks yet.")
                continue

            print("\nYour tasks:")

            for number, task in enumerate(current_tasks, 1):

                if not isinstance(task, dict):
                    continue

                status = "Completed" if task.get("completed") else "Pending"

                print(
                    f"{number}. [{status}] "
                    f"{task.get('title', 'Untitled task')}"
                )

        # COMPLETE TASK
        elif choice == "3":

            current_tasks = load_tasks()

            if not current_tasks:
                print("\nNo tasks to complete.")
                continue

            print("\nYour tasks:")

            for number, task in enumerate(current_tasks, 1):

                if not isinstance(task, dict):
                    continue

                status = "Completed" if task.get("completed") else "Pending"

                print(
                    f"{number}. [{status}] "
                    f"{task.get('title', 'Untitled task')}"
                )

            try:

                number = int(input("\nEnter task number: "))

                if 1 <= number <= len(current_tasks):

                    task = current_tasks[number - 1]

                    if task.get("completed"):
                        print("This task is already completed.")

                    else:
                        task["completed"] = True

                        save_tasks(current_tasks)

                        print("Task completed!")

                else:
                    print("Invalid task number.")

            except ValueError:
                print("Please enter a number.")

        # DELETE TASK
        elif choice == "4":

            current_tasks = load_tasks()

            if not current_tasks:
                print("\nNo tasks to delete.")
                continue

            print("\nYour tasks:")

            for number, task in enumerate(current_tasks, 1):

                if not isinstance(task, dict):
                    continue

                status = "Completed" if task.get("completed") else "Pending"

                print(
                    f"{number}. [{status}] "
                    f"{task.get('title', 'Untitled task')}"
                )

            try:

                number = int(
                    input("\nEnter task number to delete: ")
                )

                if 1 <= number <= len(current_tasks):

                    deleted = current_tasks.pop(number - 1)

                    save_tasks(current_tasks)

                    print(
                        f"Deleted: "
                        f"{deleted.get('title', 'Untitled task')}"
                    )

                else:
                    print("Invalid task number.")

            except ValueError:
                print("Please enter a number.")

        # BACK
        elif choice == "5":
            return

        else:
            print("Invalid option.")


# ==============================
# STUDY MODULE
# ==============================

def manage_subjects():
    while True:

        print("\n--- SUBJECTS ---")
        print("1. Add a subject")
        print("2. View subjects")
        print("3. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":

            subject = input("Enter subject: ").strip()

            if not subject:
                print("Subject cannot be empty.")
                continue

            subjects = load_subjects()
            existing_subjects = {
                item.strip().lower()
                for item in subjects
                if isinstance(item, str)
            }

            if subject.lower() in existing_subjects:
                print("This subject already exists.")
                continue

            subjects.append(subject)
            save_subjects(subjects)

            print("Subject saved!")

        elif choice == "2":

            subjects = load_subjects()

            if not subjects:
                print("\nNo subjects yet.")
                continue

            print("\nYour subjects:")

            for number, subject in enumerate(subjects, 1):
                if isinstance(subject, str):
                    print(f"{number}. {subject}")

        elif choice == "3":
            return

        else:
            print("Invalid option.")


def study():
    while True:

        print("\n--- STUDY ---")
        print("1. Subjects")
        print("2. Add study goal")
        print("3. View study goals")
        print("4. Complete study goal")
        print("5. Delete study goal")
        print("6. Back")

        choice = input("\nChoose: ").strip()

        # SUBJECTS
        if choice == "1":
            manage_subjects()

        # ADD STUDY GOAL
        elif choice == "2":

            subjects = load_subjects()

            if not subjects:
                print("\nAdd a subject first.")
                continue

            print("\nSubjects:")

            for number, subject in enumerate(subjects, 1):
                if isinstance(subject, str):
                    print(f"{number}. {subject}")

            try:

                subject_number = int(
                    input("\nChoose subject number: ")
                )

                if not 1 <= subject_number <= len(subjects):
                    print("Invalid subject number.")
                    continue

                subject = subjects[subject_number - 1]

                goal = input("Enter study goal: ").strip()

                if not goal:
                    print("Goal cannot be empty.")
                    continue

                goals = load_goals()

                goals.append({
                    "subject": subject,
                    "goal": goal,
                    "completed": False
                })

                save_goals(goals)

                print("Study goal saved!")

            except ValueError:
                print("Please enter a number.")

        # VIEW STUDY GOALS
        elif choice == "3":

            goals = load_goals()

            if not goals:
                print("\nNo study goals yet.")
                continue

            print("\nYour study goals:")

            for number, goal in enumerate(goals, 1):

                status = (
                    "Completed"
                    if goal.get("completed")
                    else "Pending"
                )

                print(
                    f"{number}. [{status}] "
                    f"{goal.get('subject', 'Unknown')} → "
                    f"{goal.get('goal', 'Untitled goal')}"
                )

        # COMPLETE STUDY GOAL
        elif choice == "4":

            goals = load_goals()

            if not goals:
                print("\nNo study goals to complete.")
                continue

            print("\nYour study goals:")

            for number, goal in enumerate(goals, 1):

                status = (
                    "Completed"
                    if goal.get("completed")
                    else "Pending"
                )

                print(
                    f"{number}. [{status}] "
                    f"{goal.get('subject', 'Unknown')} → "
                    f"{goal.get('goal', 'Untitled goal')}"
                )

            try:

                number = int(
                    input("\nEnter goal number: ")
                )

                if 1 <= number <= len(goals):

                    if goals[number - 1].get("completed"):
                        print("This goal is already completed.")

                    else:
                        goals[number - 1]["completed"] = True

                        save_goals(goals)

                        print("Study goal completed!")

                else:
                    print("Invalid goal number.")

            except ValueError:
                print("Please enter a number.")

        # DELETE STUDY GOAL
        elif choice == "5":

            goals = load_goals()

            if not goals:
                print("\nNo study goals to delete.")
                continue

            print("\nYour study goals:")

            for number, goal in enumerate(goals, 1):

                print(
                    f"{number}. "
                    f"{goal.get('subject', 'Unknown')} → "
                    f"{goal.get('goal', 'Untitled goal')}"
                )

            try:

                number = int(
                    input("\nEnter goal number to delete: ")
                )

                if 1 <= number <= len(goals):

                    deleted = goals.pop(number - 1)

                    save_goals(goals)

                    print(
                        f"Deleted: "
                        f"{deleted.get('goal', 'Untitled goal')}"
                    )

                else:
                    print("Invalid goal number.")

            except ValueError:
                print("Please enter a number.")

        # BACK
        elif choice == "6":
            return

        else:
            print("Invalid option.")
 
 # ==============================
# FOCUS TIMER
# ==============================

def focus_timer():
    import time

    print("\n==============================")
    print("        YUI FOCUS TIMER")
    print("==============================")

    try:
        minutes = int(input("Enter focus time in minutes: "))

        if minutes <= 0:
            print("Please enter a positive number.")
            return

        seconds = minutes * 60

        print(f"\nFocus session started: {minutes} minute(s)")
        print("Stay focused. YUI is timing you...\n")

        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            print(f"\rTime remaining: {mins:02d}:{secs:02d}", end="")
            time.sleep(1)
            seconds -= 1

        print("\n\nFocus session complete!")

    except ValueError:
        print("Please enter a valid number.")
# ==============================
# DASHBOARD
# ==============================

def dashboard():
    while True:
        print("\n--- DASHBOARD ---")
        print("1. Show overview")
        print("2. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            task_count = len(load_tasks())
            subject_count = len(load_subjects())
            goal_count = len(load_goals())

            workout_data = load_fitness()
            workout_count = len(workout_data)
            note_count = len(load_notes()) 
            print(f"Notes saved:       {note_count}")

            total_minutes = sum(
                workout.get("duration", 0)
                for workout in workout_data
                if isinstance(workout, dict)
                and isinstance(workout.get("duration", 0), (int, float))
            )

            print("\n========== YUI OVERVIEW ==========")
            print(f"Tasks:             {task_count}")
            print(f"Subjects:          {subject_count}")
            print(f"Study goals:       {goal_count}")
            print(f"Workouts logged:   {workout_count}")
            print(f"Training time:     {total_minutes} minutes")
            print("==================================")

        elif choice == "2":
            return

        else:
            print("Invalid option.")


# ==============================
# MAIN MENU
# ==============================

def main():

    while True:

        print("\n==============================")
        print("          YUI")
        print("   PERSONAL COMMAND CENTER")
        print("==============================")

        print("1. Dashboard")
        print("2. Focus Timer")
        print("3. Tasks")
        print("4. Study")
        print("5. Fitness")
        print("6. Notes")
        print("7. Assistant")
        print("8. Shorts Creator")
        print("9. Exit")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            dashboard()

        elif choice == "2":
            focus_timer()

        elif choice == "3":
            tasks()

        elif choice == "4":
            study()

        elif choice == "5":
           fitness()

        elif choice == "6":
            notes()

        elif choice == "7":
            assistant(load_goals, save_goals, load_subjects)

        elif choice == "8":
            from business.shorts.shorts_creator import create_short

            create_short()

        elif choice == "9":
            print("\nYUI shutting down...")
            break

        else:
            print("\nInvalid option.")


# ==============================
# START YUI
# ==============================

if __name__ == "__main__":
    main()




