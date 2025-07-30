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

## Jupyter Kernel Setup

The project is configured to use the created virtual environment as a Jupyter kernel.

1.  **Install the kernel:**
    Make sure your virtual environment is activated (`source .venv/bin/activate`) and run:
    ```bash
    python -m ipykernel install --user --name=mbl-auditor --display-name="MBL Auditor (.venv)"
    ```

2.  **Using the kernel in VS Code:**
    *   Open a Jupyter notebook (`.ipynb`).
    *   Click the kernel selector in the top-right corner.
    *   Select "MBL Auditor (.venv)" from the list of available kernels.

## Package Management

This project uses `uv`. To add a new dependency, activate your virtual environment and run:
```bash
uv pip install <package-name>
```
This will install the package and add it to your `pyproject.toml` file.
