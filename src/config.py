"""
Project Configuration

This file centralizes all configurations for the project, such as API URLs,
directory paths, and other constants.
"""
import os
from pathlib import Path

# API Base URL
BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"

# Number of months of expense history to download for each deputy.
MONTHS_OF_HISTORY = 12

# --- Auditor & Reporter Configuration ---

# The score above which an expense is considered "critical" for reporting.
SCORE_THRESHOLD = 5

# Weights for each flag when calculating the fraud score.
FLAG_WEIGHTS = {
    "flag_transacao_duplicada": 4,
    "flag_valor_atipico": 3,
    "flag_valor_redondo": 2,
    "flag_valor_alto_percentil": 2,
    "flag_fim_de_semana": 1,
}

# Project root directory
# Assuming this file is in src/
ROOT_DIR = Path(__file__).parent.parent

# Data and reports directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = ROOT_DIR / "reports"
SUMMARY_FILE = RAW_DATA_DIR / "download_summary.json"

# Ensure all data directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
(RAW_DATA_DIR / "expenses").mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
(PROCESSED_DATA_DIR / "flags_and_scores").mkdir(exist_ok=True)
(PROCESSED_DATA_DIR / "cnpjs").mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
