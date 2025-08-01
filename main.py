"""
Main Orchestrator

This script serves as the main entry point to run the data pipeline.
It orchestrates the process of downloading, auditing, and generating CSV reports.
The DOCX report is now generated on-demand via the Streamlit interface.
"""
import argparse
import pandas as pd
import logging
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src import downloader, config, auditor, reporter, summary_manager

# --- Logger Configuration ---
def setup_logger():
    """Configures the logger to stream INFO to console and file."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clean up any existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Stream handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_formatter)
    
    # File handler for log file
    file_handler = logging.FileHandler("pipeline.log", mode='w')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

def get_deputies(limit: int = None) -> pd.DataFrame:
    """Loads the deputies dataframe from the local CSV file."""
    downloader.download_deputies()
    deputies_df = pd.read_csv(config.RAW_DATA_DIR / "deputados.csv")
    if limit:
        return deputies_df.head(limit)
    return deputies_df

def run_download_pipeline(processing_date: datetime, limit: int = None) -> pd.DataFrame:
    """Runs the data download pipeline using the summary file for efficiency."""
    logging.info("--- Starting Download Pipeline ---")
    deputies_df = get_deputies(limit)
    logging.info(f"Processing {len(deputies_df)} deputies.")
    summary_data = summary_manager.load_summary()
    years_to_check = set(
        (processing_date - relativedelta(months=i)).year
        for i in range(config.MONTHS_OF_HISTORY)
    )
    for _, deputy in deputies_df.iterrows():
        deputy_id = deputy['id']
        for year in sorted(list(years_to_check)):
            if summary_manager.check_if_downloaded(summary_data, deputy_id, year):
                continue
            downloader.download_deputy_expenses(deputy_id, year)
    logging.info("--- Download Pipeline Finished ---")
    return deputies_df

def run_audit_pipeline(deputies_df: pd.DataFrame):
    """Runs the data auditing pipeline."""
    logging.info("--- Starting Audit Pipeline ---")
    for _, deputy in deputies_df.iterrows():
        auditor.run_deputy_audit(deputy['id'])
    logging.info("--- Audit Pipeline Finished ---")

def run_report_pipeline(deputies_df: pd.DataFrame, processing_date: datetime, period: str):
    """Runs the CSV report generation pipeline for the specified period."""
    logging.info(f"--- Starting CSV Report Pipeline for period: {period} ---")
    reporter.generate_period_reports(deputies_df, processing_date, period)
    logging.info("--- CSV Report Pipeline Finished ---")

def main():
    """Main function to run the pipeline."""
    setup_logger()
    
    parser = argparse.ArgumentParser(description="Run the Open Expense Tracker pipeline.")
    parser.add_argument(
        '--date', type=str, default=datetime.now().strftime('%Y-%m-%d'),
        help="The reference date for the analysis in YYYY-MM-DD format."
    )
    parser.add_argument(
        '--period', type=str, default='diário', choices=['diário', 'semanal', 'mensal'],
        help="The analysis period: 'diário', 'semanal', or 'mensal'."
    )
    parser.add_argument(
        '--limit', type=int, help="Limit the number of deputies to process."
    )
    args = parser.parse_args()

    try:
        processing_date = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        logging.error("Invalid date format. Please use YYYY-MM-DD.")
        return

    logging.info(f"Starting the audit pipeline for date: {args.date}, period: {args.period}")
    
    processed_deputies_df = run_download_pipeline(processing_date, args.limit)
    run_audit_pipeline(processed_deputies_df)
    run_report_pipeline(processed_deputies_df, processing_date, args.period)
    
    logging.info("Pipeline finished.")

if __name__ == "__main__":
    main()
