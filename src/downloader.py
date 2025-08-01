"""
Downloader Module

This module is responsible for fetching raw data from the Chamber of Deputies API.
It should not perform any data transformation, only download and save the data
in the 'data/raw' directory.
"""
import requests
import pandas as pd
import logging
import time
from src import config, summary_manager

def _get_all_pages(url: str, params: dict) -> list:
    """
    Handles API pagination to retrieve all data from an endpoint.
    The API uses 'Link' headers for pagination.
    """
    all_data = []
    next_url = url
    
    while next_url:
        try:
            response = requests.get(next_url, params=params, headers={"accept": "application/json"})
            response.raise_for_status()
            json_response = response.json()
            all_data.extend(json_response["dados"])

            # Check for the 'next' link in the headers
            if 'next' in response.links:
                next_url = response.links['next']['url']
                params = {} # Params are already included in the next_url
            else:
                next_url = None

            # Respect API rate limits
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading data from {next_url}: {e}")
            return None
        except KeyError:
            logging.error(f"Could not find 'dados' key in the response from {next_url}.")
            return None
            
    return all_data

def download_deputies():
    """
    Downloads the full list of deputies and saves it to a CSV file.
    """
    filepath = config.RAW_DATA_DIR / "deputados.csv"
    if filepath.exists():
        logging.info("Deputies list already exists. Skipping download.")
        return

    logging.info("Downloading deputies list...")
    endpoint = "/deputados"
    params = {"ordem": "ASC", "ordenarPor": "nome"}
    url = f"{config.BASE_URL}{endpoint}"
    data = _get_all_pages(url, params)
    
    if data is not None:
        df = pd.DataFrame(data)
        logging.info(f"Saving deputies list to {filepath}")
        df.to_csv(filepath, index=False)
        logging.info("Deputies list saved successfully.")

def download_deputy_expenses(deputy_id: int, year: int):
    """
    Downloads all expenses for a specific deputy for a given year.
    The data is saved by month, and the summary is updated on success.
    """
    logging.info(f"Downloading expenses for deputy {deputy_id}, year {year}.")
    endpoint = f"/deputados/{deputy_id}/despesas"
    params = {"ano": year, "ordem": "ASC", "ordenarPor": "mes"}
    url = f"{config.BASE_URL}{endpoint}"
    
    all_expenses = _get_all_pages(url, params)

    if all_expenses is None:
        logging.error(f"Failed to download expenses for deputy {deputy_id}, year {year}.")
        return

    if not all_expenses:
        logging.warning(f"No expenses found for deputy {deputy_id} in {year}.")
        summary_manager.add_downloaded_year(deputy_id, year)
        return

    df = pd.DataFrame(all_expenses)
    
    deputy_dir = config.RAW_DATA_DIR / "expenses" / str(deputy_id)
    deputy_dir.mkdir(parents=True, exist_ok=True)

    for month, month_df in df.groupby('mes'):
        month_filepath = deputy_dir / f"{year}-{month:02d}.csv"
        month_df.to_csv(month_filepath, index=False)

    summary_manager.add_downloaded_year(deputy_id, year)
    logging.info(f"Finished downloading expenses for deputy {deputy_id}, year {year}.")
