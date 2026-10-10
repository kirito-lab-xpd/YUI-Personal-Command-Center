
import json
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES_FILE = os.path.join(BASE_DIR, "notes.json")


def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_notes(data):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def notes():
    while True:
        print("\n========== YUI NOTES ==========")
        print("1. Add a note")
        print("2. View notes")
        print("3. Search notes")
        print("4. Edit a note")
        print("5. Delete a note")
        print("6. Back")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            title = input("Note title: ").strip()

            if not title:
                print("Title cannot be empty.")
                continue

            content = input("Write your note: ").strip()

            if not content:
                print("Note content cannot be empty.")
                continue

            data = load_notes()
            data.append({
                "title": title,
                "content": content,
                "date": date.today().isoformat()
            })

            save_notes(data)
            print("Note saved successfully!")

        elif choice == "2":
            data = load_notes()

            if not data:
                print("\nNo notes saved yet.")
                continue

            print("\n--- YOUR NOTES ---")

            for number, item in enumerate(data, 1):
                if not isinstance(item, dict):
                    continue

                print(f"\n{number}. {item.get('title', 'Untitled')}")
                print(f"   Date: {item.get('date', 'Not recorded')}")
                print(f"   {item.get('content', '')}")
            
        elif choice == "3":
            data = load_notes()
            query = input("Search title or content: ").strip().lower()

            if not query:
                print("Please enter a search term.")
                continue

            matches = [
                item for item in data
                if isinstance(item, dict)
                and (
                    query in item.get("title", "").lower()
                    or query in item.get("content", "").lower()
                )
            ]

            if matches:
                print("\n--- SEARCH RESULTS ---")
                for number, item in enumerate(matches, 1):
                    print(f"\n{number}. {item.get('title', 'Untitled')}")
                    print(item.get("content", ""))
            else:
                print("No matching notes found.") 

        
        elif choice == "4":
            data = load_notes()

            if not data:
                print("\nNo notes to edit.")
                continue

            print("\n--- SELECT A NOTE TO EDIT ---")
            for number, item in enumerate(data, 1):
                if isinstance(item, dict):
                    print(f"{number}. {item.get('title', 'Untitled')}")

            try:
                number = int(input("Enter note number: "))

                if not 1 <= number <= len(data):
                    print("Invalid note number.")
                    continue

                item = data[number - 1]

                if not isinstance(item, dict):
                    print("This note cannot be edited.")
                    continue

                print("Press Enter to keep the existing value.")

                new_title = input(
                    f"Title [{item.get('title', '')}]: "
                ).strip()

                new_content = input(
                    f"Content [{item.get('content', '')}]: "
                ).strip()

                if new_title:
                    item["title"] = new_title

                if new_content:
                    item["content"] = new_content

                save_notes(data)
                print("Note updated successfully!")

            except ValueError:
                print("Please enter a valid number.")
            
        elif choice == "5":
            data = load_notes()

            if not data:
                print("\nNo notes to delete.")
                continue

            print("\n--- DELETE A NOTE ---")

            for number, item in enumerate(data, 1):
                if isinstance(item, dict):
                    print(f"{number}. {item.get('title', 'Untitled')}")

            try:
                number = int(input("\nEnter note number to delete: "))

                if 1 <= number <= len(data):
                    removed = data[number - 1]

                    if not isinstance(removed, dict):
                        print("Invalid note entry.")
                        continue

                    confirm = input(
                        f"Delete '{removed.get('title', 'Untitled')}'? (y/n): "
                    ).strip().lower()

                    if confirm == "y":
                        data.pop(number - 1)
                        save_notes(data)
                        print("Note deleted successfully!")
                    else:
                        print("Deletion cancelled.")

                else:
                    print("Invalid note number.")

            except ValueError:
                print("Please enter a valid number.")

        elif choice == "6":
            return

        else:
            print("Invalid option.")
