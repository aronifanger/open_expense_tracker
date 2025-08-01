"""
Reporter Module

This module aggregates processed data to generate human-readable reports
for different time periods (daily, weekly, monthly).
"""
import pandas as pd
import logging
from datetime import datetime, timedelta
from src import config
from dateutil.relativedelta import relativedelta

def _load_all_flagged_expenses(deputies_df: pd.DataFrame) -> pd.DataFrame:
    """Loads and concatenates all flagged expense files for the given deputies."""
    all_flagged_dfs = []
    for _, deputy in deputies_df.iterrows():
        deputy_id = deputy['id']
        processed_file = config.PROCESSED_DATA_DIR / "flags_and_scores" / str(deputy_id) / "flagged_expenses.csv"
        if processed_file.exists():
            df = pd.read_csv(processed_file, parse_dates=['dataDocumento'])
            df['deputy_id'] = deputy_id
            df['deputy_name'] = deputy['nome']
            all_flagged_dfs.append(df)
    if not all_flagged_dfs:
        logging.warning("No flagged expense data found to generate reports.")
        return pd.DataFrame()
    return pd.concat(all_flagged_dfs, ignore_index=True)

def generate_period_reports(deputies_df: pd.DataFrame, ref_date: datetime, period: str):
    """
    Generates and saves summary reports for a specified period (diário, semanal, mensal).
    """
    logging.info(f"Generating reports for period '{period}' with reference date {ref_date.date()}.")
    
    all_expenses_df = _load_all_flagged_expenses(deputies_df)
    if all_expenses_df.empty:
        logging.info("No flagged data available. Skipping report generation.")
        return

    # Determine the date range based on the period
    ref_date_d = ref_date.date()
    if period == 'diário':
        start_date = ref_date_d
        end_date = ref_date_d
    elif period == 'semanal':
        # The week starts on Sunday (6) and ends on Saturday (5).
        # We need to adjust Python's weekday() where Monday is 0 and Sunday is 6.
        # We consider Sunday the start of the week.
        days_since_sunday = (ref_date_d.weekday() + 1) % 7
        start_date = ref_date_d - timedelta(days=days_since_sunday)
        end_date = start_date + timedelta(days=6)
    elif period == 'mensal':
        # The period is the entire month of the reference date.
        start_date = ref_date_d.replace(day=1)
        end_date = start_date + relativedelta(months=1) - timedelta(days=1)
    else:
        logging.error(f"Invalid period specified: {period}")
        return
    
    logging.info(f"Report period defined from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")
    
    period_expenses_df = all_expenses_df[
        (all_expenses_df['dataDocumento'].dt.date >= start_date) &
        (all_expenses_df['dataDocumento'].dt.date <= end_date)
    ].copy()
    
    if period_expenses_df.empty:
        logging.warning(f"No flagged expenses found for the period {start_date} to {end_date}. No reports will be generated.")
        return

    logging.info(f"Found {len(period_expenses_df)} flagged expenses to report on for the period.")

    # Report 1: Deputy Scores Summary
    deputy_scores = period_expenses_df.groupby(['deputy_id', 'deputy_name']).agg(
        critical_expense_count=('score_fraude', lambda x: (x >= config.SCORE_THRESHOLD).sum()),
        total_suspicious_expenses=('score_fraude', 'count'),
        total_suspicious_value=('valorLiquido', 'sum'),
        max_suspicion_score=('score_fraude', 'max'),
        average_suspicion_score=('score_fraude', 'mean')
    ).reset_index()

    deputy_scores = deputy_scores.sort_values(
        by=['critical_expense_count', 'average_suspicion_score'], ascending=[False, False]
    )

    # Report 2: Critical Expenses
    critical_expenses = period_expenses_df[period_expenses_df['score_fraude'] >= config.SCORE_THRESHOLD].copy()
    critical_expenses = critical_expenses.sort_values(by='score_fraude', ascending=False)
    
    # Save reports
    date_str = ref_date.strftime('%Y-%m-%d')
    config.REPORTS_DIR.mkdir(exist_ok=True)
    
    deputy_scores_path = config.REPORTS_DIR / f"{date_str}_{period}_deputy_scores.csv"
    critical_expenses_path = config.REPORTS_DIR / f"{date_str}_{period}_critical_expenses.csv"
    
    logging.info(f"Saving deputy scores summary to {deputy_scores_path}")
    deputy_scores.to_csv(deputy_scores_path, index=False, float_format='%.2f')
    
    logging.info(f"Saving critical expenses report to {critical_expenses_path}")
    critical_expenses.to_csv(critical_expenses_path, index=False, float_format='%.2f')

    logging.info(f"--- {period.capitalize()} reports generated successfully. ---")
