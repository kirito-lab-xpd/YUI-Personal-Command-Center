# YUI — Personal Command Center

YUI is a lightweight personal productivity project with a native desktop app
and an isolated browser demo. The desktop app keeps its existing local JSON
workflow; the browser demo uses temporary sample data and does not read those
files.

## Features

- **Desktop app:** Dashboard, Tasks, Study, Focus Timer, Fitness, Notes,
  Assistant, and Settings.
- **Terminal app:** Existing command-line entry point and offline assistant.
- **Browser demo:** Dark dashboard with overview cards, tasks, study progress,
  workout statistics, notes, and a simple offline Assistant panel.
- **Privacy:** Desktop records remain local. Browser-demo edits are stored only
  in Streamlit session state and are temporary.

The web demo does not connect to an AI service and does not require an API key.

## Screenshot

Add a screenshot of the browser demo here before publishing:

![YUI browser demo screenshot](docs/screenshots/yui-demo.png)

## Run the desktop app on Windows

From the project directory, launch the graphical app:

```powershell
py gui.py
```

To use the existing terminal application instead:

```powershell
py main.py
```

The desktop application stores private records in local JSON files. These files
are excluded by `.gitignore`; keep them out of any public commit.

## Run the browser demo locally

Python 3.9 or newer is recommended. From the project directory:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run streamlit_app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. All changes made
in the demo are temporary and will reset when the session is restarted.

`requirements.txt` is intentionally limited to the browser demo. The optional
Shorts Creator in the existing terminal app uses Pillow and MoviePy; those
desktop-side packages are not needed to run the Streamlit demo.

## Free online demo deployment

One free hosting option is Streamlit Community Cloud:

1. Review the privacy checklist below and commit only files intended for public
   release.
2. Push the repository to a GitHub account/repository.
3. Sign in to Streamlit Community Cloud with GitHub and create a new app.
4. Select the repository and branch, set the app file to `streamlit_app.py`,
   and deploy.
5. Open the deployed URL and confirm the demo banner and sample data appear.

The app needs no secrets or Streamlit secrets configuration. Deployment is not
complete until the repository has been published and the hosting platform has
successfully built the app.

## Before making the repository public

- Inspect the existing JSON records locally and confirm they are excluded from
  the commit. `.gitignore` does not remove files that were already committed.
- Review `first_yui_short.mp4` and `short_background.png` for personal or
  licensed content and decide whether they should be included.
- Review the complete staged file list and scan any newly added files for
  credentials, personal information, and machine-specific paths.
- Add a real screenshot at `docs/screenshots/yui-demo.png`, or remove the
  placeholder above.
- Confirm the project name, author attribution, and any third-party asset
  licenses are appropriate for public release.

## Project layout

```text
gui.py                 Tkinter desktop app
main.py                Existing terminal app
streamlit_app.py       Session-only browser demo
requirements.txt       Browser-demo dependency only
app/                   Existing application modules
business/              Existing optional Shorts Creator
```
