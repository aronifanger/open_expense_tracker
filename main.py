"""
Main Orchestrator

This script serves as the main entry point to run the entire data pipeline.
It orchestrates the process of downloading, auditing, and reporting data.

To run the script for a specific date and with a limit on the number of deputies:
    python main.py --date 2024-05-21 --limit 10
"""
import argparse
import pandas as pd
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src import downloader, config, auditor, reporter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_deputies(limit: int = None) -> pd.DataFrame:
    """
    Loads the deputies dataframe from the local CSV file.
    If the file doesn't exist, it triggers the download.
    """
    downloader.download_deputies()
    deputies_df = pd.read_csv(config.RAW_DATA_DIR / "deputados.csv")
    
    if limit:
        return deputies_df.head(limit)
    return deputies_df

def run_download_pipeline(processing_date: datetime, limit: int = None) -> pd.DataFrame:
    """
    Runs the data download pipeline and returns the dataframe of deputies processed.
    """
    logging.info("--- Starting Download Pipeline ---")
    
    deputies_df = get_deputies(limit)
    logging.info(f"Processing {len(deputies_df)} deputies.")

    years_to_check = set()
    for i in range(config.MONTHS_OF_HISTORY):
        target_date = processing_date - relativedelta(months=i)
        years_to_check.add(target_date.year)

    for _, deputy in deputies_df.iterrows():
        deputy_id = deputy['id']
        logging.info(f"Processing deputy: {deputy['nome']} (ID: {deputy_id})")

        deputy_dir = config.RAW_DATA_DIR / "expenses" / str(deputy_id)
        deputy_dir.mkdir(parents=True, exist_ok=True)

        for year in sorted(list(years_to_check)):
            year_files = list(deputy_dir.glob(f"{year}-*.csv"))
            if year_files:
                logging.info(f"Expense data for year {year} for deputy {deputy_id} already exists. Skipping download.")
                continue
            downloader.download_deputy_expenses(deputy_id, year)
    
    logging.info("--- Download Pipeline Finished ---")
    return deputies_df

def run_audit_pipeline(deputies_df: pd.DataFrame):
    """
    Runs the data auditing pipeline for the given list of deputies.
    """
    logging.info("--- Starting Audit Pipeline ---")
    
    for _, deputy in deputies_df.iterrows():
        auditor.run_deputy_audit(deputy['id'])
        
    logging.info("--- Audit Pipeline Finished ---")

def run_report_pipeline(deputies_df: pd.DataFrame, processing_date: datetime):
    """
    Runs the report generation pipeline.
    """
    logging.info("--- Starting Report Pipeline ---")
    reporter.generate_daily_reports(deputies_df, processing_date)
    logging.info("--- Report Pipeline Finished ---")


def main():
    """Main function to run the pipeline."""
    parser = argparse.ArgumentParser(description="Run the Open Expense Tracker pipeline.")
    parser.add_argument(
        '--date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help="The processing date in YYYY-MM-DD format. Defaults to today."
    )
    parser.add_argument(
        '--limit',
        type=int,
        help="Limit the number of deputies to process (for testing purposes).",
        default=2
    )
    args = parser.parse_args()

    try:
        processing_date = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        logging.error("Invalid date format. Please use YYYY-MM-DD.")
        return

    logging.info(f"Starting the audit pipeline for date: {processing_date.strftime('%Y-%m-%d')}")
    
    processed_deputies_df = run_download_pipeline(processing_date, args.limit)
    run_audit_pipeline(processed_deputies_df)
    run_report_pipeline(processed_deputies_df, processing_date)
    
    logging.info("Pipeline finished.")

if __name__ == "__main__":
    main()
