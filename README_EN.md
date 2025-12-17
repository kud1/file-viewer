# FViewer

English | [中文](README.md)

FViewer is a lightweight desktop data viewer and query tool built on **DuckDB** with a **CustomTkinter** GUI. It helps you load, preview, and query **CSV / Parquet / JSONL** files, and export results to JSON or CSV.

## Features

- **Load files**: import a single file or a whole folder
- **Multiple formats**: CSV, Parquet, JSONL (line-delimited JSON)
- **Table preview**: browse data in a table UI
- **SQL queries**: query loaded data using standard SQL
- **Export**: export query results to JSON or CSV

## Screenshot

![FViewer UI](file/sample.png)

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

- **Missing Tkinter** (`No module named '_tkinter'`) with Homebrew Python:

```bash
brew install python-tk
```

- **App icon warnings**: the icon/Logo loading tries to use Pillow (`PIL`). It's optional, but you can install it:

```bash
pip install pillow
```

## Quick Start

1. Click **Add File** to load a single file, or **Add Folder** to batch load a folder.
2. Enter a **table name** (used in SQL queries).
3. Click a file/table in the left sidebar to preview data.
4. Run SQL in the bottom query box and export results if needed.

## SQL Examples

```sql
-- preview
SELECT * FROM table_name LIMIT 10;

-- filter
SELECT * FROM table_name WHERE column_name > 100;

-- aggregation
SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name;
```

## Docs

- [User Guide (CN)](USER_GUIDE.md)
- [Changelog](CHANGELOG.md)
- [Design Notes](DESIGN_UPDATE.md)

## Privacy & Security

- **No telemetry**: FViewer does not upload your data.
- **In-memory by default**: data lives in an in-memory DB and is released when the app closes.
- **Before open-sourcing**: avoid committing your own datasets, exports, or screenshots containing sensitive info.

## License

MIT License


