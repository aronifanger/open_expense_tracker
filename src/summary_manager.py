"""
Summary Manager

This module handles reading and writing the download summary file, which keeps
track of which years of expense data have been downloaded for each deputy.
This prevents redundant, slow filesystem checks.
"""
import json
import logging
from src import config

def load_summary() -> dict:
    """Loads the download summary data from the JSON file."""
    if not config.SUMMARY_FILE.exists():
        return {}
    try:
        with open(config.SUMMARY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Could not read or parse summary file, starting fresh. Error: {e}")
        return {}

def save_summary(summary_data: dict):
    """Saves the summary data to the JSON file."""
    try:
        with open(config.SUMMARY_FILE, 'w') as f:
            json.dump(summary_data, f, indent=4)
    except IOError as e:
        logging.error(f"Could not write to summary file: {e}")

def add_downloaded_year(deputy_id: int, year: int):
    """
    Adds a record to the summary indicating that a year's worth of data
    has been successfully downloaded for a deputy.
    """
    summary_data = load_summary()
    deputy_id_str = str(deputy_id)
    
    if deputy_id_str not in summary_data:
        summary_data[deputy_id_str] = []
        
    if year not in summary_data[deputy_id_str]:
        summary_data[deputy_id_str].append(year)
        summary_data[deputy_id_str].sort()
        save_summary(summary_data)

def check_if_downloaded(summary_data: dict, deputy_id: int, year: int) -> bool:
    """Checks the summary data to see if a year has been downloaded for a deputy."""
    deputy_id_str = str(deputy_id)
    return year in summary_data.get(deputy_id_str, [])
