import streamlit as st
import pandas as pd
from pathlib import Path

# Constants
PROCESSED_DIR = Path("data/processed/flags_and_scores")
DEPUTIES_FILE = Path("data/raw/deputados.csv")

@st.cache_data
def get_deputies_list():
    """Loads the deputies list for the selector."""
    if not DEPUTIES_FILE.exists():
        return pd.DataFrame({'nome': [], 'id': []})
    return pd.read_csv(DEPUTIES_FILE)

def load_processed_data(deputy_id):
    """Loads the flagged expenses for a given deputy."""
    file_path = PROCESSED_DIR / str(deputy_id) / "flagged_expenses.csv"
    if not file_path.exists():
        return None
    return pd.read_csv(file_path, parse_dates=['dataDocumento'])

st.set_page_config(page_title="Dados Processados", layout="wide")
st.title("🔎 Explorador de Dados Processados (com Flags)")
st.markdown("Navegue pelas despesas que receberam pelo menos uma flag de suspeita.")

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
        df = load_processed_data(deputy_id)
        
        if df is not None:
            # Date range filter
            min_date = df['dataDocumento'].min().date()
            max_date = df['dataDocumento'].max().date()
            
            date_range = col2.date_input(
                "Filtrar por data do documento",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (df['dataDocumento'].dt.date >= start_date) & (df['dataDocumento'].dt.date <= end_date)
                filtered_df = df[mask]
                
                st.dataframe(filtered_df)
                
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar Tabela como CSV",
                    data=csv,
                    file_name=f"dados_processados_{deputy_id}_{start_date}_a_{end_date}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("Por favor, selecione um intervalo de datas válido.")
        else:
            st.info("Nenhum dado processado encontrado para este deputado. Execute o pipeline de auditoria.")
