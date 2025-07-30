"""
Reporter Module

This module is responsible for aggregating the processed data and generating
human-readable reports, such as daily summaries, suspicious CNPJ lists,
and detailed deputy profiles.
"""
import pandas as pd
import logging
from datetime import datetime
from src import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _load_all_flagged_expenses(deputies_df: pd.DataFrame) -> pd.DataFrame:
    """Loads and concatenates all flagged expense files for the given deputies."""
    all_flagged_dfs = []
    for _, deputy in deputies_df.iterrows():
        deputy_id = deputy['id']
        processed_file = config.PROCESSED_DATA_DIR / "flags_and_scores" / str(deputy_id) / "flagged_expenses.csv"
        
        if processed_file.exists():
            df = pd.read_csv(processed_file)
            df['deputy_id'] = deputy_id
            df['deputy_name'] = deputy['nome']
            all_flagged_dfs.append(df)
            
    if not all_flagged_dfs:
        logging.warning("No flagged expense data found to generate reports.")
        return pd.DataFrame()
        
    return pd.concat(all_flagged_dfs, ignore_index=True)

def generate_daily_reports(deputies_df: pd.DataFrame, processing_date: datetime):
    """
    Generates and saves the daily summary reports.
    - A summary of scores for each deputy.
    - A detailed list of all critical expenses.
    """
    logging.info("--- Starting Report Generation ---")
    
    all_expenses_df = _load_all_flagged_expenses(deputies_df)
    
    if all_expenses_df.empty:
        logging.info("No data to report. Skipping report generation.")
        return

    # Report 1: Deputy Scores Summary
    deputy_scores = all_expenses_df.groupby(['deputy_id', 'deputy_name']).agg(
        total_suspicious_expenses=('score_fraude', 'count'),
        total_suspicious_value=('valorLiquido', 'sum'),
        max_suspicion_score=('score_fraude', 'max'),
        average_suspicion_score=('score_fraude', 'mean')
    ).reset_index().sort_values(by='total_suspicious_value', ascending=False)

    # Report 2: Critical Expenses
    critical_expenses = all_expenses_df[all_expenses_df['score_fraude'] >= config.SCORE_THRESHOLD].copy()
    critical_expenses = critical_expenses.sort_values(by='score_fraude', ascending=False)
    
    # Save reports
    date_str = processing_date.strftime('%Y-%m-%d')
    config.REPORTS_DIR.mkdir(exist_ok=True)
    
    deputy_scores_path = config.REPORTS_DIR / f"{date_str}_deputy_scores.csv"
    critical_expenses_path = config.REPORTS_DIR / f"{date_str}_critical_expenses.csv"
    
    logging.info(f"Saving deputy scores summary to {deputy_scores_path}")
    deputy_scores.to_csv(deputy_scores_path, index=False, float_format='%.2f')
    
    logging.info(f"Saving critical expenses report to {critical_expenses_path}")
    critical_expenses.to_csv(critical_expenses_path, index=False, float_format='%.2f')

    logging.info("--- Report Generation Finished ---")
