# Open Expense Tracker

A project to audit public spending by Brazilian members of parliament to identify inconsistencies and potential fraud.

## Features

*   **Data Downloader**: Fetches data from the `dadosabertos.camara.leg.br` API.
    *   Downloads a complete list of members of parliament (deputies).
    *   Downloads historical expense data for each deputy.
*   **Structured Pipeline**: Organized into modules for downloading (`downloader.py`), auditing (`auditor.py`), and reporting (`reporter.py`).
*   **Configurable Execution**: The main pipeline can be executed for a specific date and can be limited to a certain number of deputies for testing.

## Project Structure

```
mbl-auditor/
├── data/                 # For raw, processed, and report data
├── notebooks/            # Jupyter notebooks for analysis
├── src/                  # Source code for the pipeline
│   ├── __init__.py
│   ├── auditor.py
│   ├── config.py
│   ├── downloader.py
│   └── reporter.py
├── .gitignore
├── main.py               # Main script to orchestrate the pipeline
├── pyproject.toml        # Project metadata and dependencies
└── README.md
```

## Setup & Installation

This project uses `uv` for package management and a Python virtual environment.

1.  **Create and activate the virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    Use `uv` to install the project dependencies from `pyproject.toml`. The `-e` flag installs the project in "editable" mode, which is recommended for development.
    ```bash
    uv pip install -e .
    ```

## How to Run the Pipeline

The main script `main.py` orchestrates the data download process.

You can run it from the command line:
```bash
python main.py
```

### Command-Line Arguments

*   `--date`: The processing date in `YYYY-MM-DD` format. Defaults to the current day.
*   `--limit`: Limits the number of deputies to process. Defaults to 2.

**Example:** Run the pipeline for today, processing only the first 5 deputies from the list:
```bash
python main.py --limit 5
```