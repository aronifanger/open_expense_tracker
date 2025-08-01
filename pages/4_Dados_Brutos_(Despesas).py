import streamlit as st
import pandas as pd
from pathlib import Path
import os

# Constants
RAW_EXPENSES_DIR = Path("data/raw/expenses")
DEPUTIES_FILE = Path("data/raw/deputados.csv")

@st.cache_data
def get_deputies_list():
    """Loads the deputies list for the selector."""
    if not DEPUTIES_FILE.exists():
        return pd.DataFrame({'nome': [], 'id': []})
    return pd.read_csv(DEPUTIES_FILE)

def get_available_months(deputy_id):
    """Gets a list of available year-month CSVs for a deputy."""
    deputy_dir = RAW_EXPENSES_DIR / str(deputy_id)
    if not deputy_dir.exists():
        return []
    files = [f.stem for f in deputy_dir.glob("*.csv")]
    return sorted(files, reverse=True)

def load_raw_data(deputy_id, month_file):
    """Loads a specific month of raw expenses."""
    file_path = RAW_EXPENSES_DIR / str(deputy_id) / f"{month_file}.csv"
    if not file_path.exists():
        return None
    return pd.read_csv(file_path)

st.set_page_config(page_title="Dados Brutos", layout="wide")
st.title("🗂️ Explorador de Dados Brutos (Despesas)")
st.markdown("Navegue pelos arquivos de despesas baixados da API.")

deputies_df = get_deputies_list()

if deputies_df.empty:
    st.warning("A lista de deputados (`deputados.csv`) não foi encontrada. Execute o pipeline primeiro.")
else:
    # --- User Selection ---
    col1, col2 = st.columns(2)
    selected_deputy_name = col1.selectbox(
        "Selecione um Deputado",
        options=deputies_df['nome'],
        index=None,
        placeholder="Digite o nome para buscar..."
    )
    
    if selected_deputy_name:
        deputy_id = deputies_df[deputies_df['nome'] == selected_deputy_name]['id'].iloc[0]
        available_months = get_available_months(deputy_id)
        
        if available_months:
            selected_month = col2.selectbox(
                "Selecione o Mês/Ano",
                options=available_months
            )
            
            df = load_raw_data(deputy_id, selected_month)
            
            if df is not None:
                st.dataframe(df)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar Tabela como CSV",
                    data=csv,
                    file_name=f"dados_brutos_{deputy_id}_{selected_month}.csv",
                    mime="text/csv",
                    key=f"download_{deputy_id}_{selected_month}"
                )
        else:
            st.info("Nenhum dado bruto encontrado para este deputado. Execute o pipeline de download.")
