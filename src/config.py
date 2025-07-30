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

# Project root directory
# Assuming this file is in src/
ROOT_DIR = Path(__file__).parent.parent

# Data and reports directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = ROOT_DIR / "reports"

# Ensure all data directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
(RAW_DATA_DIR / "expenses").mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
(PROCESSED_DATA_DIR / "flags_and_scores").mkdir(exist_ok=True)
(PROCESSED_DATA_DIR / "cnpjs").mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
