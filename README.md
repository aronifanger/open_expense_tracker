# Open Expense Tracker

A project to audit public spending by Brazilian members of parliament to identify inconsistencies and potential fraud.

## Features

*   **Automated Data Download**: Fetches raw expense data from the official API, with an intelligent cache system to avoid re-downloads.
*   **Modular Auditing**: Applies a set of configurable rules (flags) to identify suspicious transactions.
*   **Fraud Scoring**: Calculates a weighted fraud score for each flagged transaction.
*   **Flexible Reporting**: Generates daily, weekly, or monthly summary reports in CSV format.
*   **Interactive Web Application**: A multi-page Streamlit application to control the pipeline, monitor progress, and explore data.
*   **On-Demand Detailed Reports**: View detailed analysis directly in the app and download comprehensive Word (.docx) reports on-demand.
*   **Data Exploration**: Navigate, search, and download raw expenses, flagged transactions, and summary reports through a user-friendly interface.

## Project Structure

```
mbl-auditor/
├── data/
│   ├── raw/                  # Raw data from API (e.g., deputies.csv, expenses/{id}/{year}-{month}.csv)
│   │   └── download_summary.json # Tracks downloaded years for each deputy
│   └── processed/            # Data with flags and scores (e.g., flags_and_scores/{id}/flagged_expenses.csv)
├── reports/                  # Generated CSV summary reports
├── src/                      # Python modules
│   ├── __init__.py
│   ├── auditor.py            # Applies flags and calculates fraud scores
│   ├── config.py             # Centralized project configurations
│   ├── doc_reporter.py       # Generates Word reports on-demand
│   ├── downloader.py         # Handles data downloading from API
│   ├── reporter.py           # Generates CSV summary reports
│   └── summary_manager.py    # Manages download summary file for efficiency
├── Home.py                   # Main Streamlit app entry point
├── pages/                    # Streamlit sub-pages
│   ├── 1_Painel_de_Controle.py
│   ├── 3_Dados_Processados_(Flags).py
│   ├── 4_Dados_Brutos_(Despesas).py
│   ├── 5_Relatorios_(CSVs).py
│   └── 7_Relatorio_Detalhado.py
├── .gitignore
├── main.py                   # Main script to orchestrate the backend pipeline
├── pyproject.toml            # Project metadata and dependencies
└── README.md
```

## Setup & Installation

This project uses `uv` for package management. It's recommended to use a virtual environment.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mbl-auditor
    ```

2.  **Create and activate the virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    Use `uv` to install the project dependencies from `pyproject.toml`. The `-e` flag installs the project in "editable" mode.
    ```bash
    uv pip install -e .
    ```

## How to Run

There are two main ways to use this project: via the command-line for backend processing or through the interactive Streamlit application.

### Backend Pipeline (Command Line)

The `main.py` script runs the backend pipeline to download data, perform the audit, and generate the summary CSV reports. This is useful for automated (e.g., cron job) executions.

```bash
python main.py --date YYYY-MM-DD --period [diário|semanal|mensal] --limit N
```

*   `--date`: The reference date in `YYYY-MM-DD` format. Defaults to the current day.
*   `--period`: The analysis period: `diário`, `semanal`, or `mensal`. Defaults to `diário`.
*   `--limit`: Optional. Limits the number of deputies to process for a quicker run.

**Example:** Run the daily pipeline for today, processing only the first 5 deputies:
```bash
python main.py --limit 5
```

### Interactive Web Application (Streamlit)

This is the recommended way for most users. The web app provides a full interface to run the pipeline, monitor its progress, and explore all the data and reports.

1.  **Ensure your virtual environment is activated.**
2.  **Run the Streamlit app:**
    ```bash
    streamlit run Home.py
    ```
    Your browser will open automatically with the application. From there, you can use the "Painel de Controle" to start the analysis.
