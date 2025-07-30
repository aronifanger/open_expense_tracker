"""
Auditor Module

This module is the core of the fraud detection system. It loads raw data,
applies business rules to flag suspicious activities, and calculates
fraud scores.
"""
import pandas as pd
import logging
from pathlib import Path
from src import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Data Loading and Preparation ---

def _load_raw_deputy_expenses(deputy_id: int) -> pd.DataFrame:
    """Loads all raw monthly expense CSVs for a given deputy and concatenates them."""
    deputy_expense_dir = config.RAW_DATA_DIR / "expenses" / str(deputy_id)
    if not deputy_expense_dir.exists():
        logging.warning(f"No expense directory found for deputy {deputy_id}.")
        return pd.DataFrame()

    all_months_df = []
    for csv_file in deputy_expense_dir.glob("*.csv"):
        all_months_df.append(pd.read_csv(csv_file))

    if not all_months_df:
        logging.warning(f"No expense files found for deputy {depy_id}.")
        return pd.DataFrame()

    return pd.concat(all_months_df, ignore_index=True)

def _prepare_expense_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepares the expense dataframe for analysis."""
    if df.empty:
        return df
    
    df['dataDocumento'] = pd.to_datetime(df['dataDocumento'], errors='coerce')
    df['valorLiquido'] = pd.to_numeric(df['valorLiquido'], errors='coerce')
    df['dia_semana'] = df['dataDocumento'].dt.dayofweek
    return df.dropna(subset=['dataDocumento', 'valorLiquido'])


# --- Flagging Functions ---

def flag_weekend_expense(df: pd.DataFrame) -> pd.Series:
    """Flags expenses made on weekends (Saturday=5, Sunday=6)."""
    return df['dia_semana'].isin([5, 6])

def flag_round_number_expense(df: pd.DataFrame) -> pd.Series:
    """Flags expenses with suspicious round numbers."""
    return df['valorLiquido'].apply(lambda x: x > 0 and (x % 100 == 0 or x % 500 == 0 or x % 1000 == 0))

def flag_high_value_outlier(df: pd.DataFrame) -> pd.Series:
    """Flags expenses that are outliers based on the IQR method."""
    if df.empty:
        return pd.Series([False] * len(df))
    Q1 = df['valorLiquido'].quantile(0.25)
    Q3 = df['valorLiquido'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    return df['valorLiquido'] > upper_bound

def flag_duplicated_transaction(df: pd.DataFrame) -> pd.Series:
    """Flags transactions that are exact duplicates based on key columns."""
    key_columns = ['dataDocumento', 'cnpjCpfFornecedor', 'valorLiquido']
    return df.duplicated(subset=key_columns, keep=False)

def flag_high_value_percentile(df: pd.DataFrame) -> pd.Series:
    """Flags expenses in the top 5% of all expenses for that deputy."""
    if df.empty:
        return pd.Series([False] * len(df))
    return df['valorLiquido'] > df['valorLiquido'].quantile(0.95)

# --- Score Calculation ---

def calculate_fraud_score(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates a fraud score based on the weighted flags."""
    df['score_fraude'] = 0
    for flag, weight in config.FLAG_WEIGHTS.items():
        if flag in df.columns:
            df['score_fraude'] += df[flag] * weight
    return df

# --- Flag Registry & Columns to Keep ---

FLAG_FUNCTIONS = {
    "flag_fim_de_semana": flag_weekend_expense,
    "flag_valor_redondo": flag_round_number_expense,
    "flag_valor_atipico": flag_high_value_outlier,
    "flag_transacao_duplicada": flag_duplicated_transaction,
    "flag_valor_alto_percentil": flag_high_value_percentile,
}

KEY_COLUMNS = [
    'ano', 'mes', 'dataDocumento', 'tipoDespesa', 
    'valorLiquido', 'nomeFornecedor', 'cnpjCpfFornecedor', 'urlDocumento'
]


# --- Main Auditor Runner ---

def run_deputy_audit(deputy_id: int):
    """
    Loads, processes, and saves the audited expense data for a single deputy.
    """
    logging.info(f"Starting audit for deputy ID: {deputy_id}")
    
    raw_df = _load_raw_deputy_expenses(deputy_id)
    if raw_df.empty:
        logging.info(f"Skipping audit for deputy {deputy_id} due to no data.")
        return
        
    df = _prepare_expense_data(raw_df)
    if df.empty:
        logging.info(f"Skipping audit for deputy {deputy_id} after data preparation.")
        return
    
    flag_names = list(FLAG_FUNCTIONS.keys())
    for flag_name, flag_func in FLAG_FUNCTIONS.items():
        logging.info(f"Applying flag: {flag_name}")
        df[flag_name] = flag_func(df)

    df_with_scores = calculate_fraud_score(df)

    flagged_df = df_with_scores[df_with_scores[flag_names].any(axis=1)].copy()
    
    if flagged_df.empty:
        logging.info(f"No suspicious transactions found for deputy {deputy_id}.")
        return

    columns_to_keep = KEY_COLUMNS + ['score_fraude'] + flag_names
    final_columns = [col for col in columns_to_keep if col in flagged_df.columns]
    final_df = flagged_df[final_columns]

    processed_dir = config.PROCESSED_DATA_DIR / "flags_and_scores" / str(deputy_id)
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "flagged_expenses.csv"
    
    logging.info(f"Saving {len(final_df)} flagged transactions to {output_path}")
    final_df.to_csv(output_path, index=False)
    
    logging.info(f"Finished audit for deputy ID: {deputy_id}")
