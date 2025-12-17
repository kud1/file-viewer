# FViewer

English | [中文](README.md)

FViewer is a lightweight desktop data viewer and query tool built on **DuckDB** with a **CustomTkinter** GUI. It helps you load, preview, and query **CSV / Parquet / JSONL** files, and export results to JSON or CSV.

## Features

- **Load files**: import a single file or a whole folder
- **Multiple formats**: CSV, Parquet, JSONL (line-delimited JSON)
- **Table preview**: browse data in a table UI (works well for large datasets)
- **SQL queries**: query loaded data using standard SQL
- **Export**: export query results to JSON or CSV
- **Modern UI**: clean macOS-style design

## Screenshot

![FViewer UI](file/sample.png)

## A Fresh macOS-style UI

FViewer uses a modern design language for an elegant and efficient experience:

- **Green theme**: fresh palette that’s easy on the eyes
- **Card layout**: clear hierarchy and tidy information grouping
- **Smooth interactions**: modern buttons and hover effects
- **Responsive**: adapts to different window sizes
- **Straightforward workflow**: key actions are easy to find

## Requirements

- Python 3.9+
- Tk/Tkinter available on your system (GUI)
- Tested mainly on macOS

## Install & Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## macOS Troubleshooting

- **Missing Tkinter** (`ModuleNotFoundError: No module named '_tkinter'`) with Homebrew Python:

```bash
brew install python-tk
```

- **Icon/Logo not loading (optional)**: icon/Logo loading may try to use Pillow (`PIL`). The app works without it; install to enable icons and silence warnings:

```bash
pip install pillow
```

## Quick Start

### 1) Load data files

- Click **📄 Add File** to load a single file
- Or click **📁 Add Folder** to batch load all supported files in a folder
- Enter a **table name** (used in SQL queries); the app will suggest a default based on the filename

### 2) Browse data

- Click any item in the left sidebar file list
- The right pane will show a preview immediately
- Check the stats: total rows, columns, and rows currently displayed

### 3) Run SQL queries

- Type SQL in the bottom editor
- Click **▶ Run Query**
- Query results will replace the preview table (stats are updated as well)

### 4) Export results

- After running a query, click **📄 Export JSON** or **📊 Export CSV**
- Choose a save location to export the full result set

### 5) Manage files

- Click the **×** button on the right of a file item to remove it
- The corresponding table will also be removed from the database

## SQL Examples

```sql
-- preview
SELECT * FROM table_name LIMIT 10;

-- filter
SELECT * FROM table_name WHERE column_name > 100;

-- aggregation
SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name;
```

## UI Layout

### Left sidebar (green theme)

- **App header**: FViewer logo and name
- **Library section**: lists all loaded files
- **Action buttons**:
  - **📄 Add File**: add a single file
  - **📁 Add Folder**: add a whole folder
- **File list**:
  - the currently selected item is highlighted
  - a round **×** remove button per item

### Main content area (right)

- **Top header**: “Data Explorer”
- **Data Preview card**:
  - stats (total rows, columns, rows shown)
  - modern table preview, with green-highlighted selected row
- **SQL Query card**:
  - SQL editor (monospace)
  - **▶ Run Query** primary button
  - **📄 Export JSON / 📊 Export CSV** export buttons

## Tech Stack

- **Python 3.9+**
- **DuckDB**: high-performance analytical database
- **CustomTkinter**: modern Tkinter-based UI
- **Pandas**: data processing

## Project Structure

```
file-viewer/
├── main.py              # entry point
├── gui.py               # GUI module
├── file_manager.py      # file management
├── db_manager.py        # database management
├── requirements.txt     # dependencies
└── README.md            # documentation
```

## Notes

- Files are loaded **line by line** (each line as one record)
- JSON must be **JSONL** (line-delimited JSON)
- Loading very large files may take time
- All data is stored in an **in-memory** database; it won’t persist after closing the app

## Contributing

Issues and pull requests are welcome. For PRs, please include reproduction steps or the motivation for the change.

## License

MIT License
