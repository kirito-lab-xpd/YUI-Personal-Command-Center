import json
import math
import time
import tkinter as tk
from datetime import date, datetime
from pathlib import Path
from tkinter import messagebox, ttk

import main as storage
from app.core import fitness as fitness_storage
from app import notes as notes_storage


DATA_PATHS = {
    "tasks": Path(storage.TASK_FILE),
    "subjects": Path(storage.SUBJECT_FILE),
    "goals": Path(storage.GOAL_FILE),
    "workouts": Path(fitness_storage.FITNESS_FILE),
    "notes": Path(notes_storage.NOTES_FILE),
}
LOADERS = {
    "tasks": storage.load_tasks,
    "subjects": storage.load_subjects,
    "goals": storage.load_goals,
    "workouts": fitness_storage.load_fitness,
    "notes": notes_storage.load_notes,
}
SAVERS = {
    "tasks": storage.save_tasks,
    "subjects": storage.save_subjects,
    "goals": storage.save_goals,
    "workouts": fitness_storage.save_fitness,
    "notes": notes_storage.save_notes,
}

BG = "#0D0B12"
SIDEBAR = "#100D17"
PANEL = "#17141F"
PANEL_ALT = "#211C2B"
TEXT = "#F7F5FC"
MUTED = "#AAA4B6"
PURPLE = "#8B5CF6"
PURPLE_HOVER = "#9A70FF"
VIOLET = "#6D28D9"
OUTLINE = "#2B2537"
class StorageError(Exception):
    pass


def load_collection(name):
    path = DATA_PATHS[name]
    if not path.exists():
        return LOADERS[name]()

    try:
        with open(path, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        raise StorageError(
            f"Could not read {path.name}: {error}. The file was left unchanged."
        ) from error

    if not isinstance(raw_data, list):
        raise StorageError(
            f"{path.name} must contain a JSON list. The file was left unchanged."
        )
    return LOADERS[name]()


def save_collection(name, data):
    path = DATA_PATHS[name]
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except (json.JSONDecodeError, OSError) as error:
            raise StorageError(
                f"Could not safely update {path.name}: {error}. "
                "The existing file was left unchanged."
            ) from error
        if not isinstance(existing_data, list):
            raise StorageError(
                f"Could not safely update {path.name}: expected a JSON list. "
                "The existing file was left unchanged."
            )
    try:
        SAVERS[name](data)
    except OSError as error:
        raise StorageError(f"Could not save {path.name}: {error}") from error


def display_task(task):
    if isinstance(task, str):
        return task, "Pending"
    if isinstance(task, dict):
        return (
            str(task.get("title", "Untitled task")),
            "Completed" if task.get("completed", False) else "Pending",
        )
    return "Invalid task record", "Unavailable"


class YuiApp:
    NAVIGATION = (
        ("Dashboard", "◆"),
        ("Tasks", "✓"),
        ("Study", "▤"),
        ("Focus Timer", "◷"),
        ("Fitness", "✦"),
        ("Notes", "▧"),
        ("Assistant", "✧"),
        ("Settings", "⚙"),
    )

    def __init__(self, root):
        self.root = root
        self.root.title("YUI | Personal Command Center")
        self.root.geometry("1280x820")
        self.root.minsize(820, 500)
        self.root.configure(bg=BG)
        self.current_page = "Dashboard"
        self.nav_buttons = {}
        self.timer_after_id = None
        self.timer_deadline = None
        self.timer_remaining = 0
        self.timer_running = False
        self.timer_status_text = "Ready when you are."
        self.timer_minutes = tk.StringVar(master=root, value="25")
        self._configure_styles()
        self._build_shell()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.show_page("Dashboard")

    def _close(self):
        if self.timer_after_id is not None:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.root.destroy()

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "TFrame", background=BG
        )
        style.configure(
            "Panel.TFrame", background=PANEL, borderwidth=1,
            relief="solid", bordercolor=OUTLINE
        )
        style.configure(
            "TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10)
        )
        style.configure(
            "Title.TLabel", background=BG, foreground=TEXT,
            font=("Segoe UI Semibold", 23)
        )
        style.configure(
            "Subtitle.TLabel", background=BG, foreground=MUTED,
            font=("Segoe UI", 10)
        )
        style.configure(
            "CardTitle.TLabel", background=PANEL, foreground=MUTED,
            font=("Segoe UI", 10)
        )
        style.configure(
            "CardEyebrow.TLabel", background=PANEL, foreground=PURPLE,
            font=("Segoe UI Semibold", 9)
        )
        style.configure(
            "CardValue.TLabel", background=PANEL, foreground=TEXT,
            font=("Segoe UI Semibold", 25)
        )
        style.configure(
            "TButton", background=PANEL_ALT, foreground=TEXT,
            padding=(12, 8), borderwidth=0, font=("Segoe UI", 10)
        )
        style.map(
            "TButton",
            background=[("active", "#343443"), ("disabled", PANEL)],
            foreground=[("disabled", MUTED)],
        )
        style.configure(
            "Accent.TButton", background=PURPLE, foreground="#ffffff",
            font=("Segoe UI Semibold", 10), padding=(13, 9)
        )
        style.map(
            "Accent.TButton",
            background=[("active", PURPLE_HOVER)],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "Danger.TButton", background="#46232d", foreground="#ffdce2",
            padding=(12, 8)
        )
        style.map("Danger.TButton", background=[("active", "#60303d")])
        style.configure(
            "Treeview", background=PANEL, fieldbackground=PANEL,
            foreground=TEXT, borderwidth=0, rowheight=34,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading", background=PANEL_ALT, foreground=MUTED,
            borderwidth=0, font=("Segoe UI Semibold", 9), padding=(8, 9)
        )
        style.map(
            "Treeview",
            background=[("selected", "#493773")],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "TEntry", fieldbackground=PANEL_ALT, foreground=TEXT,
            insertcolor=TEXT, padding=9, borderwidth=1
        )
        style.configure(
            "TCombobox", fieldbackground=PANEL_ALT, foreground=TEXT,
            padding=7
        )
        style.configure(
            "YUI.Horizontal.TProgressbar",
            troughcolor=PANEL_ALT, background=PURPLE, bordercolor=PANEL_ALT,
            lightcolor=PURPLE, darkcolor=VIOLET, thickness=8
        )
        style.configure(
            "Vertical.TScrollbar",
            background=PANEL_ALT, troughcolor=BG, bordercolor=BG,
            arrowcolor=MUTED, relief="flat", width=10,
        )
        style.configure(
            "Treeview", bordercolor=OUTLINE, lightcolor=PANEL,
            darkcolor=PANEL
        )

    def _build_shell(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=236)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(27, 0))
        tk.Label(
            brand, text="Y", bg=PURPLE, fg="white", width=2, height=1,
            font=("Segoe UI Semibold", 17), padx=5, pady=3
        ).pack(side="left")
        tk.Label(
            brand, text="YUI", bg=SIDEBAR, fg=TEXT,
            font=("Segoe UI Semibold", 23)
        ).pack(side="left", padx=(11, 0))
        tk.Label(
            self.sidebar, text="PERSONAL COMMAND CENTER", bg=SIDEBAR,
            fg=MUTED, font=("Segoe UI", 8)
        ).pack(anchor="w", padx=24, pady=(7, 27))

        tk.Label(
            self.sidebar, text="WORKSPACE", bg=SIDEBAR,
            fg="#726C7F", font=("Segoe UI Semibold", 8)
        ).pack(anchor="w", padx=25, pady=(0, 7))

        for page, icon in self.NAVIGATION:
            button = tk.Button(
                self.sidebar,
                text=f"{icon}    {page}",
                anchor="w",
                relief="flat",
                bd=0,
                padx=15,
                pady=7,
                bg=SIDEBAR,
                fg=MUTED,
                activebackground="#2A2038",
                activeforeground=TEXT,
                font=("Segoe UI Semibold", 10),
                command=lambda name=page: self.show_page(name),
            )
            button.pack(fill="x", padx=11, pady=2)
            self.nav_buttons[page] = button

        tk.Label(
            self.sidebar,
            text="YUI v1.0",
            bg=SIDEBAR, fg="#777486", font=("Segoe UI", 9)
        ).pack(side="bottom", anchor="w", padx=24, pady=(0, 8))
        tk.Label(
            self.sidebar,
            text="●  SYSTEM ONLINE",
            bg=SIDEBAR, fg="#8D83A0", font=("Segoe UI", 8)
        ).pack(side="bottom", anchor="w", padx=24, pady=(0, 6))

        self.body = ttk.Frame(self.root, padding=(34, 27, 34, 28))
        self.body.grid(row=0, column=1, sticky="nsew")
        self.body.grid_rowconfigure(1, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.header = ttk.Frame(self.body)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 23))
        self.header.grid_columnconfigure(0, weight=1)
        content_host = ttk.Frame(self.body)
        content_host.grid(row=1, column=0, sticky="nsew")
        content_host.grid_rowconfigure(0, weight=1)
        content_host.grid_columnconfigure(0, weight=1)

        self.content_canvas = tk.Canvas(
            content_host, bg=BG, highlightthickness=0, bd=0,
        )
        self.content_canvas.grid(row=0, column=0, sticky="nsew")
        self.content_scrollbar = ttk.Scrollbar(
            content_host, orient="vertical",
            command=self.content_canvas.yview,
        )
        self.content_scrollbar.grid(row=0, column=1, sticky="ns")
        self.content_canvas.configure(
            yscrollcommand=self.content_scrollbar.set
        )
        self.page_area = ttk.Frame(self.content_canvas)
        self.page_area.grid_columnconfigure(0, weight=1)
        self.page_window = self.content_canvas.create_window(
            (0, 0), window=self.page_area, anchor="nw"
        )
        self.page_area.bind("<Configure>", self._update_scroll_region)
        self.content_canvas.bind(
            "<Configure>", self._resize_scroll_content
        )
        self._mousewheel_bindings = [
            (sequence, self.root.bind_all(sequence, callback, add="+"))
            for sequence, callback in (
                ("<MouseWheel>", self._scroll_main_content),
                ("<Button-4>", self._scroll_main_content),
                ("<Button-5>", self._scroll_main_content),
            )
        ]

    def _update_scroll_region(self, event=None):
        if event is not None and event.widget not in (
            self.page_area, self.content_canvas
        ):
            return
        self.content_canvas.configure(
            scrollregion=self.content_canvas.bbox("all")
        )

    def _resize_scroll_content(self, event):
        self.content_canvas.itemconfigure(self.page_window, width=event.width)
        self._update_scroll_region()

    def _scroll_main_content(self, event):
        pointer_x, pointer_y = self.root.winfo_pointerxy()
        left = self.content_canvas.winfo_rootx()
        top = self.content_canvas.winfo_rooty()
        right = left + self.content_canvas.winfo_width()
        bottom = top + self.content_canvas.winfo_height()
        if not (left <= pointer_x <= right and top <= pointer_y <= bottom):
            return

        if event.num == 4:
            direction = -1
        elif event.num == 5:
            direction = 1
        else:
            direction = -1 if event.delta > 0 else 1
        self.content_canvas.yview_scroll(direction * 3, "units")
        return "break"

    def show_page(self, page):
        self.current_page = page
        for name, button in self.nav_buttons.items():
            button.configure(
                bg="#33264e" if name == page else SIDEBAR,
                fg=TEXT if name == page else MUTED,
            )

        for child in self.header.winfo_children():
            child.destroy()
        for child in self.page_area.winfo_children():
            child.destroy()

        pages = {
            "Dashboard": self._dashboard_page,
            "Tasks": self._tasks_page,
            "Study": self._study_page,
            "Fitness": self._fitness_page,
            "Notes": self._notes_page,
            "Focus Timer": self._timer_page,
            "Assistant": self._assistant_page,
            "Settings": self._settings_page,
        }
        try:
            if page == "Dashboard":
                title, subtitle = "Welcome back", "Here's your personal command center."
            else:
                title, subtitle = page, "Manage your YUI workspace."
            title_block = ttk.Frame(self.header)
            title_block.grid(row=0, column=0, sticky="w")
            ttk.Label(title_block, text=title, style="Title.TLabel").pack(anchor="w")
            ttk.Label(title_block, text=subtitle, style="Subtitle.TLabel").pack(
                anchor="w", pady=(3, 0)
            )
            header_right = ttk.Frame(self.header)
            header_right.grid(row=0, column=1, sticky="e")
            ttk.Label(
                header_right,
                text=date.today().strftime("%A, %d %B %Y"),
                style="Subtitle.TLabel",
            ).pack(anchor="e")
            status = tk.Label(
                header_right, text="●  SYSTEM READY", bg="#20172E",
                fg="#C2A6FF", padx=10, pady=5,
                font=("Segoe UI Semibold", 8)
            )
            status.pack(anchor="e", pady=(7, 0))
            pages[page]()
            self.content_canvas.yview_moveto(0)
            self.root.after_idle(self._update_scroll_region)
        except (StorageError, OSError) as error:
            self._show_page_error(error)

    def _show_page_error(self, error):
        for child in self.page_area.winfo_children():
            child.destroy()
        ttk.Label(
            self.page_area,
            text=f"Unable to load this section:\n{error}",
            style="Subtitle.TLabel",
            wraplength=600,
        ).grid(row=0, column=0, sticky="nw")

    def _load(self, name):
        return load_collection(name)

    def _save(self, name, data):
        save_collection(name, data)

    def _run_action(self, callback, refresh=None):
        try:
            callback()
            if refresh is not None:
                self.show_page(refresh)
        except (StorageError, OSError) as error:
            messagebox.showerror("YUI - Data error", str(error), parent=self.root)

    def _page_body(self):
        frame = ttk.Frame(self.page_area)
        frame.grid(row=0, column=0, sticky="new")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        return frame

    def _make_tree(self, parent, columns, headings, widths=None):
        container = ttk.Frame(parent, style="Panel.TFrame", padding=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        tree = ttk.Treeview(
            container, columns=columns, show="headings", selectmode="browse"
        )
        for index, (column, heading) in enumerate(zip(columns, headings)):
            tree.heading(column, text=heading)
            tree.column(
                column,
                width=widths[index] if widths else 150,
                minwidth=70,
                stretch=index == 0,
                anchor="w",
            )
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        return container, tree

    def _stat_card(self, parent, icon, title, value, caption):
        card = tk.Frame(
            parent, bg=PANEL, highlightbackground=OUTLINE,
            highlightthickness=1, padx=16, pady=13,
        )
        heading = tk.Frame(card, bg=PANEL)
        heading.pack(fill="x")
        tk.Label(
            heading, text=icon, bg="#281D3A", fg="#C4A9FF",
            width=3, height=1, font=("Segoe UI Semibold", 10),
            padx=3, pady=4,
        ).pack(side="left")
        tk.Label(
            heading, text=title.upper(), bg=PANEL, fg=MUTED,
            font=("Segoe UI Semibold", 8),
        ).pack(side="left", padx=(9, 0))
        tk.Label(
            card, text=value, bg=PANEL, fg=TEXT,
            font=("Segoe UI Semibold", 24),
        ).pack(anchor="w", pady=(10, 0))
        tk.Label(
            card, text=caption, bg=PANEL, fg=MUTED,
            font=("Segoe UI", 9), anchor="w",
        ).pack(anchor="w", pady=(1, 0))
        return card

    def _dashboard_page(self):
        tasks = self._load("tasks")
        subjects = self._load("subjects")
        goals = self._load("goals")
        workouts = self._load("workouts")
        notes = self._load("notes")

        task_items = [
            item for item in tasks if isinstance(item, (str, dict))
        ]
        completed_tasks = sum(
            1 for item in task_items
            if isinstance(item, dict) and item.get("completed", False)
        )
        pending_tasks = len(task_items) - completed_tasks
        valid_goals = [item for item in goals if isinstance(item, dict)]
        completed_goals = sum(
            1 for item in valid_goals if item.get("completed", False)
        )
        valid_workouts = [item for item in workouts if isinstance(item, dict)]
        valid_notes = [item for item in notes if isinstance(item, dict)]
        valid_subjects = [item for item in subjects if isinstance(item, str)]
        workout_minutes = sum(
            item.get("duration", 0)
            for item in valid_workouts
            if isinstance(item.get("duration", 0), (int, float))
            and not isinstance(item.get("duration", 0), bool)
        )

        page = self._page_body()
        for row, weight in ((0, 0), (1, 3), (2, 2)):
            page.grid_rowconfigure(row, weight=weight)
        stats = ttk.Frame(page)
        stats.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        stat_data = (
            ("✓", "Tasks", str(len(task_items)),
             f"{completed_tasks} completed · {pending_tasks} pending"),
            ("▤", "Study", str(len(valid_subjects)),
             f"{len(valid_goals)} goals · {completed_goals} complete"),
            ("✦", "Fitness", str(len(valid_workouts)),
             f"{workout_minutes} total minutes"),
            ("▧", "Notes", str(len(valid_notes)),
             "Saved in your local notebook"),
        )
        self.dashboard_stat_cards = [
            self._stat_card(stats, *values) for values in stat_data
        ]
        self._layout_dashboard_stats()
        stats.bind("<Configure>", self._layout_dashboard_stats)

        content = ttk.Frame(page)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=3, uniform="middle")
        content.grid_columnconfigure(1, weight=2, uniform="middle")
        content.grid_rowconfigure(0, weight=1)
        recent_panel = ttk.Frame(content, style="Panel.TFrame", padding=16)
        recent_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        recent_panel.grid_columnconfigure(0, weight=1)
        recent_panel.grid_rowconfigure(1, weight=1)
        self._panel_heading(recent_panel, "Recent Tasks", "TASK OVERVIEW")
        recent_list = tk.Frame(recent_panel, bg=PANEL)
        recent_list.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        if not task_items:
            tk.Label(
                recent_list, text="All clear — add a task to get started.",
                bg=PANEL, fg=MUTED, font=("Segoe UI", 10),
            ).pack(anchor="w", pady=12)
        else:
            for task in task_items[-5:][::-1]:
                title, status = display_task(task)
                line = tk.Frame(recent_list, bg=PANEL)
                line.pack(fill="x", pady=5)
                marker_color = PURPLE if status == "Pending" else "#5BCB9A"
                tk.Label(
                    line, text="●", bg=PANEL, fg=marker_color,
                    font=("Segoe UI", 10),
                ).pack(side="left", padx=(0, 9))
                tk.Label(
                    line, text=title, bg=PANEL, fg=TEXT,
                    font=("Segoe UI", 10), anchor="w",
                ).pack(side="left", fill="x", expand=True)
                tk.Label(
                    line, text=status.upper(), bg=PANEL,
                    fg=marker_color, font=("Segoe UI Semibold", 8),
                ).pack(side="right", padx=(6, 0))
        ttk.Button(
            recent_panel, text="View all tasks  →",
            command=lambda: self.show_page("Tasks"),
        ).grid(row=2, column=0, sticky="w", pady=(9, 0))

        study_panel = ttk.Frame(content, style="Panel.TFrame", padding=16)
        study_panel.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        study_panel.grid_columnconfigure(0, weight=1)
        self._panel_heading(study_panel, "Study Progress", "GOALS")
        progress = (
            int(completed_goals * 100 / len(valid_goals))
            if valid_goals else 0
        )
        progress_row = tk.Frame(study_panel, bg=PANEL)
        progress_row.grid(row=1, column=0, sticky="ew", pady=(16, 4))
        tk.Label(
            progress_row, text=f"{progress}%", bg=PANEL, fg=TEXT,
            font=("Segoe UI Semibold", 21),
        ).pack(side="left")
        tk.Label(
            progress_row,
            text=f"{completed_goals} of {len(valid_goals)} goals complete",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9),
        ).pack(side="left", padx=(10, 0), pady=(7, 0))
        ttk.Progressbar(
            study_panel, maximum=100, value=progress,
            style="YUI.Horizontal.TProgressbar",
        ).grid(row=2, column=0, sticky="ew", pady=(3, 12))
        goals_list = tk.Frame(study_panel, bg=PANEL)
        goals_list.grid(row=3, column=0, sticky="nsew")
        if not valid_goals:
            tk.Label(
                goals_list, text="No study goals yet. Add one in Study.",
                bg=PANEL, fg=MUTED, font=("Segoe UI", 9),
                wraplength=260, justify="left",
            ).pack(anchor="w", pady=7)
        else:
            for goal in valid_goals[:3]:
                status = "Done" if goal.get("completed") else "In progress"
                color = "#5BCB9A" if goal.get("completed") else "#C2A6FF"
                label = f"{goal.get('subject', 'Unknown')}  ·  {goal.get('goal', 'Untitled goal')}"
                tk.Label(
                    goals_list, text=label, bg=PANEL, fg=TEXT,
                    font=("Segoe UI", 9), anchor="w", justify="left",
                    wraplength=260,
                ).pack(anchor="w", fill="x", pady=(3, 0))
                tk.Label(
                    goals_list, text=status.upper(), bg=PANEL, fg=color,
                    font=("Segoe UI Semibold", 8),
                ).pack(anchor="w", pady=(0, 4))
        ttk.Button(
            study_panel, text="Open Study  →",
            command=lambda: self.show_page("Study"),
        ).grid(row=4, column=0, sticky="w", pady=(5, 0))

        bottom = ttk.Frame(page)
        bottom.grid(row=2, column=0, sticky="nsew", pady=(14, 0))
        bottom.grid_columnconfigure(0, weight=3, uniform="bottom")
        bottom.grid_columnconfigure(1, weight=2, uniform="bottom")
        quick = ttk.Frame(bottom, style="Panel.TFrame", padding=15)
        quick.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        quick.grid_columnconfigure((0, 1), weight=1, uniform="quick")
        self._panel_heading(quick, "Quick Actions", "SHORTCUTS")
        ttk.Button(
            quick, text="＋  Add Task", style="Accent.TButton",
            command=self._add_task,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(12, 5))
        ttk.Button(
            quick, text="◷  Start Focus Timer",
            command=self._quick_start_timer,
        ).grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(12, 5))
        ttk.Button(
            quick, text="✦  Log Workout",
            command=self._add_workout,
        ).grid(row=2, column=0, sticky="ew", padx=(0, 5), pady=5)
        ttk.Button(
            quick, text="▧  Create Note",
            command=self._add_note,
        ).grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=5)

        focus = ttk.Frame(bottom, style="Panel.TFrame", padding=15)
        focus.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        focus.grid_columnconfigure(0, weight=1)
        self._panel_heading(focus, "Focus Session", "TIMER")
        self.focus_summary = tk.Label(
            focus, text="", bg=PANEL, fg=TEXT,
            font=("Segoe UI Semibold", 15), anchor="w",
        )
        self.focus_summary.grid(row=1, column=0, sticky="w", pady=(13, 1))
        self.focus_state_label = tk.Label(
            focus, text="", bg=PANEL, fg=MUTED,
            font=("Segoe UI", 9), anchor="w",
        )
        self.focus_state_label.grid(row=2, column=0, sticky="w")
        ttk.Button(
            focus, text="Open Focus Timer  →",
            command=lambda: self.show_page("Focus Timer"),
        ).grid(row=3, column=0, sticky="w", pady=(9, 0))
        self._refresh_dashboard_timer()

    def _layout_dashboard_stats(self, event=None):
        if not hasattr(self, "dashboard_stat_cards"):
            return
        stats = self.dashboard_stat_cards[0].master
        width = (
            event.width if event is not None
            else max(stats.winfo_width(), self.root.winfo_width() - 320)
        )
        columns = 4 if width >= 900 else 2 if width >= 510 else 1
        if (
            getattr(self, "_dashboard_stat_columns", None) == columns
            and all(card.grid_info() for card in self.dashboard_stat_cards)
        ):
            return
        self._dashboard_stat_columns = columns
        for column in range(4):
            stats.grid_columnconfigure(column, weight=0, uniform="")
        for card in self.dashboard_stat_cards:
            card.grid_forget()
        for column in range(columns):
            stats.grid_columnconfigure(column, weight=1, uniform="stat-cards")
        for index, card in enumerate(self.dashboard_stat_cards):
            card.grid(
                row=index // columns, column=index % columns,
                sticky="nsew", padx=5, pady=5,
            )

    def _panel_heading(self, parent, title, eyebrow):
        heading = tk.Frame(parent, bg=PANEL)
        heading.grid(row=0, column=0, sticky="ew")
        heading.grid_columnconfigure(0, weight=1)
        tk.Label(
            heading, text=title, bg=PANEL, fg=TEXT,
            font=("Segoe UI Semibold", 12),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            heading, text=eyebrow, bg=PANEL, fg="#8E879D",
            font=("Segoe UI Semibold", 8),
        ).grid(row=0, column=1, sticky="e")

    def _quick_start_timer(self):
        self.show_page("Focus Timer")
        self.root.after_idle(self._start_timer)

    def _refresh_dashboard_timer(self):
        if not hasattr(self, "focus_summary"):
            return
        if not self.focus_summary.winfo_exists():
            return
        if self.timer_remaining > 0:
            minutes, seconds = divmod(self.timer_remaining, 60)
            display = f"{minutes:02d}:{seconds:02d}"
        else:
            display = f"{self.timer_minutes.get() or '25'}:00"
        self.focus_summary.configure(text=display)
        if self.timer_running:
            state, color = "SESSION IN PROGRESS", "#C2A6FF"
        elif self.timer_status_text == "Paused.":
            state, color = "PAUSED", "#E8C477"
        elif self.timer_status_text == "Focus session complete.":
            state, color = "SESSION COMPLETE", "#68D5A0"
        else:
            state, color = "READY TO FOCUS", MUTED
        self.focus_state_label.configure(text=state, fg=color)

    def _settings_page(self):
        page = self._page_body()
        page.grid_rowconfigure(1, weight=1)
        preferences = ttk.Frame(page, style="Panel.TFrame", padding=22)
        preferences.grid(row=0, column=0, sticky="ew")
        preferences.grid_columnconfigure(0, weight=1)
        ttk.Label(
            preferences, text="Preferences", style="CardValue.TLabel"
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            preferences,
            text="Choose the default duration used when starting a new focus session.",
            style="CardTitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 15))
        timer_row = ttk.Frame(preferences, style="Panel.TFrame")
        timer_row.grid(row=2, column=0, sticky="ew")
        ttk.Label(
            timer_row, text="Focus session length (minutes)",
            style="CardTitle.TLabel",
        ).pack(side="left")
        ttk.Entry(
            timer_row, textvariable=self.timer_minutes, width=10
        ).pack(side="left", padx=12)
        ttk.Button(
            timer_row, text="Apply", style="Accent.TButton",
            command=self._apply_timer_setting,
        ).pack(side="left")

        data_panel = ttk.Frame(page, style="Panel.TFrame", padding=22)
        data_panel.grid(row=1, column=0, sticky="new", pady=(14, 0))
        ttk.Label(
            data_panel, text="Local data", style="CardValue.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            data_panel,
            text="YUI reads and writes your existing JSON files. No cloud services or "
                 "external AI are used.",
            style="CardTitle.TLabel", wraplength=650, justify="left",
        ).pack(anchor="w", pady=(6, 14))
        for label, path in DATA_PATHS.items():
            ttk.Label(
                data_panel, text=f"{label.title()}:  {path}",
                style="CardTitle.TLabel", wraplength=800, justify="left",
            ).pack(anchor="w", pady=2)

    def _apply_timer_setting(self):
        try:
            minutes = int(self.timer_minutes.get())
        except ValueError:
            messagebox.showwarning(
                "YUI", "Enter a whole number of minutes.", parent=self.root
            )
            return
        if minutes <= 0:
            messagebox.showwarning(
                "YUI", "Timer duration must be greater than zero.",
                parent=self.root,
            )
            return
        if not self.timer_running:
            self.timer_remaining = minutes * 60
            self.timer_status_text = "Ready when you are."
        messagebox.showinfo(
            "YUI", f"Default focus session set to {minutes} minutes.",
            parent=self.root,
        )

    def _tasks_page(self):
        tasks = self._load("tasks")
        page = self._page_body()
        toolbar = ttk.Frame(page)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 13))
        ttk.Button(
            toolbar, text="＋  Add task", style="Accent.TButton",
            command=self._add_task
        ).pack(side="left")
        ttk.Button(
            toolbar, text="✓  Complete selected",
            command=self._complete_task
        ).pack(side="left", padx=8)
        ttk.Button(
            toolbar, text="Delete selected", style="Danger.TButton",
            command=self._delete_task
        ).pack(side="left")

        container, self.task_tree = self._make_tree(
            page, ("title", "status"), ("TASK", "STATUS"), (560, 130)
        )
        container.grid(row=1, column=0, sticky="nsew")
        for index, task in enumerate(tasks):
            title, status = display_task(task)
            self.task_tree.insert("", "end", iid=str(index), values=(title, status))

    def _selected_index(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showinfo(
                "YUI", "Select an item first.", parent=self.root
            )
            return None
        return int(selection[0])

    def _add_task(self):
        values = self._form_dialog("Add task", [("Task", "", False)])
        if values is None:
            return
        title = values["Task"].strip()
        if not title:
            messagebox.showwarning("YUI", "Task cannot be empty.", parent=self.root)
            return

        def save():
            tasks = self._load("tasks")
            tasks.append({"title": title, "completed": False})
            self._save("tasks", tasks)
        self._run_action(save, "Tasks")

    def _complete_task(self):
        index = self._selected_index(self.task_tree)
        if index is None:
            return

        def save():
            tasks = self._load("tasks")
            task = tasks[index]
            if isinstance(task, str):
                task = {"title": task, "completed": True}
                tasks[index] = task
            elif isinstance(task, dict):
                task["completed"] = True
            else:
                raise StorageError("The selected task record is invalid.")
            self._save("tasks", tasks)
        self._run_action(save, "Tasks")

    def _delete_task(self):
        index = self._selected_index(self.task_tree)
        if index is None:
            return
        title = self.task_tree.item(str(index), "values")[0]
        if not messagebox.askyesno(
            "Delete task", f"Delete '{title}'?", parent=self.root
        ):
            return

        def save():
            tasks = self._load("tasks")
            tasks.pop(index)
            self._save("tasks", tasks)
        self._run_action(save, "Tasks")

    def _study_page(self):
        subjects = self._load("subjects")
        goals = self._load("goals")
        page = self._page_body()
        page.grid_rowconfigure(1, weight=0)
        page.grid_rowconfigure(2, weight=1)
        subject_panel = ttk.Frame(page)
        subject_panel.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        subject_panel.grid_columnconfigure(0, weight=1)
        ttk.Label(
            subject_panel, text="Subjects", style="Subtitle.TLabel"
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(
            subject_panel, text="＋  Add subject", style="Accent.TButton",
            command=self._add_subject
        ).grid(row=0, column=1, sticky="e")
        self.subject_chips = tk.Label(
            page,
            text="   •   ".join(s for s in subjects if isinstance(s, str))
            or "No subjects yet",
            anchor="w", bg=PANEL, fg=TEXT, padx=14, pady=12,
            font=("Segoe UI", 10),
        )
        self.subject_chips.grid(row=1, column=0, sticky="ew")

        goal_section = ttk.Frame(page)
        goal_section.grid(row=2, column=0, sticky="nsew", pady=(16, 0))
        goal_section.grid_columnconfigure(0, weight=1)
        goal_section.grid_rowconfigure(1, weight=1)
        goal_toolbar = ttk.Frame(goal_section)
        goal_toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(
            goal_toolbar, text="Study goals", style="Subtitle.TLabel"
        ).pack(side="left")
        ttk.Button(
            goal_toolbar, text="＋  Add goal", style="Accent.TButton",
            command=self._add_goal
        ).pack(side="right")
        ttk.Button(
            goal_toolbar, text="Complete selected",
            command=self._complete_goal
        ).pack(side="right", padx=8)
        ttk.Button(
            goal_toolbar, text="Delete selected", style="Danger.TButton",
            command=self._delete_goal
        ).pack(side="right")

        container, self.goal_tree = self._make_tree(
            goal_section, ("subject", "goal", "status"),
            ("SUBJECT", "GOAL", "STATUS"), (170, 430, 120)
        )
        container.grid(row=1, column=0, sticky="nsew")
        for index, goal in enumerate(goals):
            if not isinstance(goal, dict):
                continue
            status = "Completed" if goal.get("completed", False) else "Pending"
            self.goal_tree.insert(
                "", "end", iid=str(index),
                values=(
                    goal.get("subject", "Unknown"),
                    goal.get("goal", "Untitled goal"),
                    status,
                )
            )

    def _add_subject(self):
        values = self._form_dialog("Add subject", [("Subject", "", False)])
        if values is None:
            return
        subject = values["Subject"].strip()
        if not subject:
            messagebox.showwarning(
                "YUI", "Subject cannot be empty.", parent=self.root
            )
            return

        def save():
            subjects = self._load("subjects")
            if any(
                isinstance(item, str) and item.strip().lower() == subject.lower()
                for item in subjects
            ):
                raise StorageError("That subject already exists.")
            subjects.append(subject)
            self._save("subjects", subjects)
        self._run_action(save, "Study")

    def _add_goal(self):
        subjects = [
            subject for subject in self._load("subjects")
            if isinstance(subject, str) and subject.strip()
        ]
        if not subjects:
            messagebox.showinfo(
                "YUI", "Add a subject before creating a study goal.",
                parent=self.root,
            )
            return
        values = self._form_dialog(
            "Add study goal",
            [("Subject", subjects[0], False), ("Goal", "", False)],
            choices={"Subject": subjects},
        )
        if values is None:
            return
        goal_text = values["Goal"].strip()
        if not goal_text:
            messagebox.showwarning(
                "YUI", "Study goal cannot be empty.", parent=self.root
            )
            return

        def save():
            goals = self._load("goals")
            goals.append({
                "subject": values["Subject"],
                "goal": goal_text,
                "completed": False,
            })
            self._save("goals", goals)
        self._run_action(save, "Study")

    def _complete_goal(self):
        index = self._selected_index(self.goal_tree)
        if index is None:
            return

        def save():
            goals = self._load("goals")
            if not isinstance(goals[index], dict):
                raise StorageError("The selected study goal is invalid.")
            goals[index]["completed"] = True
            self._save("goals", goals)
        self._run_action(save, "Study")

    def _delete_goal(self):
        index = self._selected_index(self.goal_tree)
        if index is None:
            return
        goal = self.goal_tree.item(str(index), "values")[1]
        if not messagebox.askyesno(
            "Delete study goal", f"Delete '{goal}'?", parent=self.root
        ):
            return

        def save():
            goals = self._load("goals")
            goals.pop(index)
            self._save("goals", goals)
        self._run_action(save, "Study")

    def _fitness_page(self):
        workouts = self._load("workouts")
        page = self._page_body()
        toolbar = ttk.Frame(page)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 13))
        ttk.Button(
            toolbar, text="＋  Log workout", style="Accent.TButton",
            command=self._add_workout
        ).pack(side="left")
        minutes = sum(
            item.get("duration", 0)
            for item in workouts
            if isinstance(item, dict)
            and isinstance(item.get("duration", 0), (int, float))
        )
        ttk.Label(
            toolbar, text=f"{len(workouts)} workouts  •  {minutes} minutes",
            style="Subtitle.TLabel"
        ).pack(side="right", pady=8)

        container, self.workout_tree = self._make_tree(
            page, ("date", "activity", "duration", "notes"),
            ("DATE", "ACTIVITY", "MINUTES", "NOTES"),
            (130, 220, 110, 320),
        )
        container.grid(row=1, column=0, sticky="nsew")
        for index, workout in enumerate(workouts):
            if not isinstance(workout, dict):
                continue
            self.workout_tree.insert(
                "", "end", iid=str(index),
                values=(
                    workout.get("date", "Not recorded"),
                    workout.get("activity", "Unknown activity"),
                    workout.get("duration", ""),
                    workout.get("notes", ""),
                )
            )

    def _add_workout(self):
        today = date.today().isoformat()
        values = self._form_dialog(
            "Log workout",
            [
                ("Activity", "", False),
                ("Duration (minutes)", "", False),
                ("Date (YYYY-MM-DD)", today, False),
                ("Notes (optional)", "", True),
            ],
        )
        if values is None:
            return
        activity = values["Activity"].strip()
        if not activity:
            messagebox.showwarning(
                "YUI", "Activity cannot be empty.", parent=self.root
            )
            return
        try:
            duration = int(values["Duration (minutes)"])
        except ValueError:
            messagebox.showwarning(
                "YUI", "Enter a whole number of minutes.", parent=self.root
            )
            return
        if duration <= 0:
            messagebox.showwarning(
                "YUI", "Duration must be greater than zero.", parent=self.root
            )
            return
        try:
            workout_date = date.fromisoformat(values["Date (YYYY-MM-DD)"].strip())
        except ValueError:
            messagebox.showwarning(
                "YUI", "Enter a valid date in YYYY-MM-DD format.",
                parent=self.root,
            )
            return

        def save():
            workouts = self._load("workouts")
            workouts.append({
                "date": workout_date.isoformat(),
                "activity": activity,
                "duration": duration,
                "notes": values["Notes (optional)"].strip(),
            })
            self._save("workouts", workouts)
        self._run_action(save, "Fitness")

    def _notes_page(self):
        notes = self._load("notes")
        page = self._page_body()
        page.grid_rowconfigure(1, weight=0)
        page.grid_rowconfigure(2, weight=1)
        toolbar = ttk.Frame(page)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Button(
            toolbar, text="＋  Add note", style="Accent.TButton",
            command=self._add_note
        ).pack(side="left")
        ttk.Button(
            toolbar, text="Edit selected", command=self._edit_note
        ).pack(side="left", padx=8)
        ttk.Button(
            toolbar, text="Delete selected", style="Danger.TButton",
            command=self._delete_note
        ).pack(side="left")

        search_row = ttk.Frame(page)
        search_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(search_row, text="Search notes", style="Subtitle.TLabel").pack(
            side="left", padx=(0, 12)
        )
        self.note_search = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.note_search)
        search_entry.pack(side="left", fill="x", expand=True)
        self.note_search.trace_add("write", lambda *_: self._filter_notes())

        content = ttk.Frame(page)
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=3)
        content.grid_rowconfigure(0, weight=1)
        left, self.note_tree = self._make_tree(
            content, ("title", "date"), ("TITLE", "DATE"), (260, 120)
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = ttk.Frame(content, style="Panel.TFrame", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        ttk.Label(
            right, text="Note preview", style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.note_preview = tk.Text(
            right, wrap="word", state="disabled", relief="flat", bd=0,
            bg=PANEL, fg=TEXT, insertbackground=TEXT,
            font=("Segoe UI", 10), padx=8, pady=8,
        )
        self.note_preview.grid(row=1, column=0, sticky="nsew")
        self.note_tree.bind("<<TreeviewSelect>>", self._preview_note)
        self.note_records = notes
        self._filter_notes()

    def _filter_notes(self):
        if not hasattr(self, "note_tree") or not self.note_tree.winfo_exists():
            return
        for item in self.note_tree.get_children():
            self.note_tree.delete(item)
        query = self.note_search.get().strip().casefold()
        for index, note in enumerate(self.note_records):
            if not isinstance(note, dict):
                continue
            title = str(note.get("title", "Untitled"))
            body = str(note.get("content", ""))
            if query and query not in title.casefold() and query not in body.casefold():
                continue
            self.note_tree.insert(
                "", "end", iid=str(index),
                values=(title, note.get("date", "Not recorded"))
            )
        self._set_note_preview("")

    def _set_note_preview(self, text):
        self.note_preview.configure(state="normal")
        self.note_preview.delete("1.0", "end")
        self.note_preview.insert("1.0", text)
        self.note_preview.configure(state="disabled")

    def _preview_note(self, event=None):
        if event is not None and event.widget is not self.note_tree:
            return
        selection = self.note_tree.selection()
        if not selection:
            return
        index = int(selection[0])
        note = self.note_records[index]
        self._set_note_preview(
            f"{note.get('title', 'Untitled')}\n"
            f"{note.get('date', 'Not recorded')}\n\n"
            f"{note.get('content', '')}"
        )

    def _add_note(self):
        values = self._form_dialog(
            "Add note", [("Title", "", False), ("Content", "", True)]
        )
        if values is None:
            return
        title = values["Title"].strip()
        content = values["Content"].strip()
        if not title or not content:
            messagebox.showwarning(
                "YUI", "Both title and content are required.", parent=self.root
            )
            return

        def save():
            notes = self._load("notes")
            notes.append({
                "title": title,
                "content": content,
                "date": date.today().isoformat(),
            })
            self._save("notes", notes)
        self._run_action(save, "Notes")

    def _edit_note(self):
        index = self._selected_index(self.note_tree)
        if index is None:
            return
        note = self.note_records[index]
        values = self._form_dialog(
            "Edit note",
            [
                ("Title", str(note.get("title", "")), False),
                ("Content", str(note.get("content", "")), True),
            ],
        )
        if values is None:
            return
        title = values["Title"].strip()
        content = values["Content"].strip()
        if not title or not content:
            messagebox.showwarning(
                "YUI", "Both title and content are required.", parent=self.root
            )
            return

        def save():
            notes = self._load("notes")
            notes[index]["title"] = title
            notes[index]["content"] = content
            self._save("notes", notes)
        self._run_action(save, "Notes")

    def _delete_note(self):
        index = self._selected_index(self.note_tree)
        if index is None:
            return
        title = self.note_tree.item(str(index), "values")[0]
        if not messagebox.askyesno(
            "Delete note", f"Delete '{title}'?", parent=self.root
        ):
            return

        def save():
            notes = self._load("notes")
            notes.pop(index)
            self._save("notes", notes)
        self._run_action(save, "Notes")

    def _timer_page(self):
        page = ttk.Frame(self.page_area)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)
        panel = ttk.Frame(page, style="Panel.TFrame", padding=32)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        ttk.Label(
            panel, text="FOCUS SESSION", style="CardTitle.TLabel"
        ).grid(row=0, column=0, pady=(8, 18))
        display_remaining = self.timer_remaining
        if display_remaining <= 0:
            try:
                display_minutes = int(self.timer_minutes.get())
            except ValueError:
                display_minutes = 25
            display_remaining = (
                0 if self.timer_status_text == "Focus session complete."
                else max(1, display_minutes) * 60
            )
        minutes, seconds = divmod(display_remaining, 60)
        self.timer_display = tk.Label(
            panel, text=f"{minutes:02d}:{seconds:02d}", bg=PANEL, fg=TEXT,
            font=("Segoe UI Light", 62)
        )
        self.timer_display.grid(row=1, column=0, pady=15)

        controls = ttk.Frame(panel, style="Panel.TFrame")
        controls.grid(row=2, column=0, pady=(15, 4))
        ttk.Button(
            controls, text="Start", style="Accent.TButton",
            command=self._start_timer
        ).pack(side="left", padx=5)
        ttk.Button(
            controls, text="Pause", command=self._pause_timer
        ).pack(side="left", padx=5)
        ttk.Button(
            controls, text="Reset", command=self._reset_timer
        ).pack(side="left", padx=5)

        setting = ttk.Frame(panel, style="Panel.TFrame")
        setting.grid(row=3, column=0, pady=(22, 4))
        ttk.Label(
            setting, text="Session length (minutes)", style="CardTitle.TLabel"
        ).pack(side="left", padx=(0, 10))
        ttk.Entry(
            setting, textvariable=self.timer_minutes, width=7
        ).pack(side="left")
        self.timer_status = ttk.Label(
            panel, text=self.timer_status_text, style="CardTitle.TLabel"
        )
        self.timer_status.grid(row=4, column=0, pady=(12, 5))

    def _start_timer(self):
        if self.timer_running:
            return
        if self.timer_remaining <= 0:
            try:
                minutes = int(self.timer_minutes.get())
            except ValueError:
                messagebox.showwarning(
                    "YUI", "Enter a whole number of minutes.",
                    parent=self.root,
                )
                return
            if minutes <= 0:
                messagebox.showwarning(
                    "YUI", "Timer length must be greater than zero.",
                    parent=self.root,
                )
                return
            self.timer_remaining = minutes * 60
        self.timer_running = True
        self.timer_deadline = time.monotonic() + self.timer_remaining
        self.timer_status_text = "Focus session in progress."
        self.timer_status.configure(text=self.timer_status_text)
        self._timer_tick()

    def _timer_tick(self):
        if not self.timer_running:
            return
        self.timer_remaining = max(
            0, math.ceil(self.timer_deadline - time.monotonic())
        )
        minutes, seconds = divmod(self.timer_remaining, 60)
        if hasattr(self, "timer_display") and self.timer_display.winfo_exists():
            if (
                hasattr(self, "timer_display")
                and self.timer_display.winfo_exists()
            ):
                self.timer_display.configure(text=f"{minutes:02d}:{seconds:02d}")
            self._refresh_dashboard_timer()
        if self.timer_remaining == 0:
            self.timer_running = False
            self.timer_after_id = None
            if (
                hasattr(self, "timer_status")
                and self.timer_status.winfo_exists()
            ):
                self.timer_status_text = "Focus session complete."
                self.timer_status.configure(text=self.timer_status_text)
            messagebox.showinfo(
                "YUI Focus Timer", "Focus session complete!",
                parent=self.root,
            )
            return
        self.timer_after_id = self.root.after(200, self._timer_tick)

    def _pause_timer(self):
        if not self.timer_running:
            return
        self.timer_remaining = max(
            0, math.ceil(self.timer_deadline - time.monotonic())
        )
        self.timer_running = False
        if self.timer_after_id is not None:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        minutes, seconds = divmod(self.timer_remaining, 60)
        if hasattr(self, "timer_display") and self.timer_display.winfo_exists():
            self.timer_display.configure(text=f"{minutes:02d}:{seconds:02d}")
        self.timer_status_text = "Paused."
        if hasattr(self, "timer_status") and self.timer_status.winfo_exists():
            self.timer_status.configure(text=self.timer_status_text)

    def _reset_timer(self):
        self.timer_running = False
        if self.timer_after_id is not None:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        try:
            minutes = int(self.timer_minutes.get())
        except ValueError:
            minutes = 25
        if minutes <= 0:
            minutes = 25
        self.timer_remaining = minutes * 60
        self.timer_display.configure(text=f"{minutes:02d}:00")
        self.timer_status_text = "Ready when you are."
        self.timer_status.configure(text=self.timer_status_text)

    def _assistant_page(self):
        page = ttk.Frame(self.page_area)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=0)
        self.chat = tk.Text(
            page, state="disabled", wrap="word", relief="flat", bd=0,
            bg=PANEL, fg=TEXT, insertbackground=TEXT,
            font=("Segoe UI", 10), padx=18, pady=16,
        )
        self.chat.grid(row=0, column=0, sticky="nsew")
        self.chat.tag_configure("user", foreground="#c1a8ff")
        self.chat.tag_configure("assistant", foreground=TEXT)
        self.chat.tag_configure("muted", foreground=MUTED)
        self.chat_input = ttk.Entry(page)
        self.chat_input.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        self.chat_input.bind("<Return>", self._send_chat_command)
        self._chat_write(
            "YUI Assistant is offline and uses your local data only.\n"
            "Type 'help' to see supported commands. This is not an external AI.",
            "muted",
        )

    def _chat_write(self, message, tag="assistant"):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{message}\n\n", tag)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _send_chat_command(self, event=None):
        if event is not None and event.widget is not self.chat_input:
            return "break"
        command = self.chat_input.get().strip()
        if not command:
            return "break"
        self.chat_input.delete(0, "end")
        self._chat_write(f"You: {command}", "user")
        try:
            response = self._handle_assistant_command(command)
        except (StorageError, OSError) as error:
            response = f"Data error: {error}"
        self._chat_write(response)
        return "break"

    def _handle_assistant_command(self, command):
        normalized = command.casefold().strip()
        if normalized in ("help", "commands"):
            return (
                "Commands: help, status, tasks, study, study goals, fitness, "
                "notes, time, date, motivate, complete task N, "
                "complete study goal N.\n"
                "You can also use: add task TITLE; "
                "add study goal SUBJECT | GOAL; "
                "log workout ACTIVITY | MINUTES | NOTES; "
                "add note TITLE | CONTENT; search notes TEXT.\n"
                "Use the Tasks, Study, Fitness, and Notes screens for full "
                "editing controls."
            )
        if normalized in ("time", "what time is it"):
            return f"Current time: {datetime.now().strftime('%I:%M %p')}"
        if normalized in ("date", "today's date"):
            return f"Today's date: {date.today().strftime('%d %B %Y')}"
        if normalized in ("motivate", "motivate me"):
            return "Small steps every day create big results. Keep building YUI!"
        if normalized == "status":
            tasks = self._load("tasks")
            goals = self._load("goals")
            return (
                f"Tasks: {len(tasks)}; Study goals: {len(goals)}; "
                f"Subjects: {len(self._load('subjects'))}; "
                f"Workouts: {len(self._load('workouts'))}; "
                f"Notes: {len(self._load('notes'))}."
            )
        if normalized == "tasks":
            tasks = self._load("tasks")
            if not tasks:
                return "You have no tasks yet."
            return "\n".join(
                f"{index}. [{status}] {title}"
                for index, (title, status) in enumerate(
                    (display_task(task) for task in tasks), 1
                )
            )
        if normalized == "study":
            return (
                f"{len(self._load('subjects'))} subjects and "
                f"{len(self._load('goals'))} study goals."
            )
        if normalized == "study goals":
            goals = self._load("goals")
            if not goals:
                return "No study goals yet."
            return "\n".join(
                f"{index}. [{'Completed' if item.get('completed') else 'Pending'}] "
                f"{item.get('subject', 'Unknown')} - {item.get('goal', 'Untitled')}"
                for index, item in enumerate(goals, 1)
                if isinstance(item, dict)
            )
        if normalized == "fitness":
            workouts = self._load("workouts")
            minutes = sum(
                item.get("duration", 0)
                for item in workouts
                if isinstance(item, dict)
                and isinstance(item.get("duration", 0), (int, float))
            )
            return f"{len(workouts)} workouts logged ({minutes} minutes)."
        if normalized == "notes":
            return f"{len(self._load('notes'))} saved notes."
        if normalized.startswith("add task "):
            title = command[9:].strip()
            if not title:
                return "Task title cannot be empty."
            tasks = self._load("tasks")
            tasks.append({"title": title, "completed": False})
            self._save("tasks", tasks)
            return f"Task saved: {title}"
        if normalized.startswith("complete task "):
            return self._assistant_complete("tasks", command[14:])
        if normalized.startswith("complete study goal "):
            return self._assistant_complete("goals", command[20:])
        if normalized.startswith("add study goal "):
            parts = command[15:].split("|", 1)
            if len(parts) != 2 or not all(part.strip() for part in parts):
                return "Use: add study goal SUBJECT | GOAL"
            subject, goal_text = (part.strip() for part in parts)
            subjects = self._load("subjects")
            matching_subject = next(
                (
                    item for item in subjects
                    if isinstance(item, str)
                    and item.casefold() == subject.casefold()
                ),
                None,
            )
            if matching_subject is None:
                return "That subject was not found. Add it in the Study screen first."
            goals = self._load("goals")
            goals.append({
                "subject": matching_subject,
                "goal": goal_text,
                "completed": False,
            })
            self._save("goals", goals)
            return f"Study goal saved for {matching_subject}: {goal_text}"
        if normalized.startswith("log workout "):
            parts = command[12:].split("|")
            if len(parts) < 2 or not parts[0].strip():
                return "Use: log workout ACTIVITY | MINUTES | optional notes"
            try:
                duration = int(parts[1].strip())
            except ValueError:
                return "Workout duration must be a whole number of minutes."
            if duration <= 0:
                return "Workout duration must be greater than zero."
            workouts = self._load("workouts")
            workouts.append({
                "date": date.today().isoformat(),
                "activity": parts[0].strip(),
                "duration": duration,
                "notes": parts[2].strip() if len(parts) > 2 else "",
            })
            self._save("workouts", workouts)
            return f"Workout saved: {parts[0].strip()} ({duration} minutes)."
        if normalized.startswith("add note "):
            parts = command[9:].split("|", 1)
            if len(parts) != 2 or not all(part.strip() for part in parts):
                return "Use: add note TITLE | CONTENT"
            notes = self._load("notes")
            notes.append({
                "title": parts[0].strip(),
                "content": parts[1].strip(),
                "date": date.today().isoformat(),
            })
            self._save("notes", notes)
            return f"Note saved: {parts[0].strip()}"
        if normalized.startswith("search notes "):
            query = command[12:].strip().casefold()
            if not query:
                return "Enter a search term after 'search notes'."
            matches = [
                item for item in self._load("notes")
                if isinstance(item, dict)
                and (
                    query in str(item.get("title", "")).casefold()
                    or query in str(item.get("content", "")).casefold()
                )
            ]
            if not matches:
                return "No matching notes found."
            return "\n".join(
                f"{item.get('title', 'Untitled')}: {item.get('content', '')}"
                for item in matches
            )
        return "I don't recognize that command. Type 'help' for the offline command list."

    def _assistant_complete(self, kind, raw_number):
        try:
            number = int(raw_number.strip())
        except ValueError:
            return "Enter a valid item number."
        items = self._load(kind)
        valid_items = [
            (index, item)
            for index, item in enumerate(items)
            if isinstance(item, (str, dict))
        ] if kind == "tasks" else [
            (index, item)
            for index, item in enumerate(items)
            if isinstance(item, dict)
        ]
        if not 1 <= number <= len(valid_items):
            return "That item number is out of range."
        actual_index, selected = valid_items[number - 1]
        if kind == "tasks":
            if isinstance(selected, str):
                items[actual_index] = {"title": selected, "completed": True}
            else:
                selected["completed"] = True
        else:
            if selected.get("completed"):
                return "That study goal is already completed."
            selected["completed"] = True
        self._save(kind, items)
        return "Marked as completed."

    def _form_dialog(self, title, fields, choices=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, True)
        dialog.minsize(390, 220)
        dialog.grid_columnconfigure(0, weight=1)
        widgets = {}

        for row, (label, initial, multiline) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(
                row=row * 2, column=0, sticky="w", padx=20, pady=(14, 5)
            )
            if choices and label in choices:
                widget = ttk.Combobox(
                    dialog, values=choices[label], state="readonly"
                )
                widget.set(initial)
            elif multiline:
                widget = tk.Text(
                    dialog, height=6, wrap="word", bg=PANEL_ALT, fg=TEXT,
                    insertbackground=TEXT, relief="flat", padx=9, pady=8,
                    font=("Segoe UI", 10),
                )
                widget.insert("1.0", initial)
            else:
                widget = ttk.Entry(dialog)
                widget.insert(0, initial)
            widget.grid(
                row=row * 2 + 1, column=0, sticky="ew",
                padx=20, pady=(0, 2),
            )
            widgets[label] = (widget, multiline)

        result = {"values": None}

        def submit():
            values = {}
            for label, (widget, multiline) in widgets.items():
                values[label] = (
                    widget.get("1.0", "end-1c")
                    if multiline else widget.get()
                )
            result["values"] = values
            dialog.destroy()

        def cancel():
            dialog.destroy()

        buttons = ttk.Frame(dialog)
        buttons.grid(
            row=len(fields) * 2, column=0, sticky="e",
            padx=20, pady=18,
        )
        ttk.Button(buttons, text="Cancel", command=cancel).pack(
            side="right", padx=(8, 0)
        )
        ttk.Button(
            buttons, text="Save", style="Accent.TButton", command=submit
        ).pack(side="right")
        dialog.bind(
            "<Escape>",
            lambda event: cancel() if event.keysym == "Escape" else None,
        )
        dialog.wait_window()
        return result["values"]


def main():
    root = tk.Tk()
    YuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
