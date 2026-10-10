
import json
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FITNESS_FILE = os.path.join(BASE_DIR, "fitness.json")


def load_fitness():
    if not os.path.exists(FITNESS_FILE):
        return []

    try:
        with open(FITNESS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_fitness(data):
    with open(FITNESS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def fitness():
    while True:
        print("\n========== YUI FITNESS ==========")
        print("1. Log a workout")
        print("2. View workout history")
        print("3. Back")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            workout = input("Workout or activity: ").strip()

            if not workout:
                print("Please enter an activity.")
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

            data = load_fitness()
            data.append({
                "date": date.today().isoformat(),
                "activity": workout,
                "duration": duration,
                "notes": notes
            })

            save_fitness(data)
            print("Workout saved successfully!")

        elif choice == "2":
            data = load_fitness()

            if not data:
                print("\nNo workouts logged yet.")
            else:
                print("\n--- WORKOUT HISTORY ---")

                for number, item in enumerate(data, 1):
                    print(f"\n{number}. {item.get('activity', 'Unknown activity')}")
                    print(f"   Date: {item.get('date', 'Not recorded')}")

                    duration = item.get("duration")
                    if duration is not None:
                        print(f"   Duration: {duration} minutes")
                    else:
                        print("   Duration: Not recorded")

                    if item.get("notes"):
                        print(f"   Notes: {item['notes']}")

        elif choice == "3":
            return

        else:
            print("Invalid option.")