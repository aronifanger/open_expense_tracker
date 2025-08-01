import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# Constants
REPORTS_DIR = Path("reports")

def find_report_file(ref_date, period, report_type):
    """Finds the correct report CSV file based on user selection."""
    date_str = ref_date.strftime('%Y-%m-%d')
    file_name = f"{date_str}_{period}_{report_type}.csv"
    file_path = REPORTS_DIR / file_name
    if file_path.exists():
        return file_path
    return None

st.set_page_config(page_title="Relatórios (CSVs)", layout="wide")
st.title("📄 Explorador de Relatórios (CSVs)")
st.markdown("Visualize e baixe os relatórios de resumo gerados pelo pipeline.")

# --- User Selection ---
col1, col2, col3 = st.columns(3)
selected_date = col1.date_input("Selecione a Data de Referência", value=date.today())
selected_period = col2.selectbox("Selecione o Período", ['diário', 'semanal', 'mensal'])
report_type_map = {
    "Ranking de Deputados": "deputy_scores",
    "Despesas Críticas": "critical_expenses"
}
selected_report_name = col3.selectbox("Selecione o Tipo de Relatório", list(report_type_map.keys()))

if selected_date and selected_period and selected_report_name:
    report_type = report_type_map[selected_report_name]
    report_file = find_report_file(selected_date, selected_period, report_type)
    
    if report_file:
        df = pd.read_csv(report_file)
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Baixar {report_file.name}",
            data=csv,
            file_name=report_file.name,
            mime="text/csv",
        )
    else:
        st.warning(
            f"Relatório não encontrado para os parâmetros selecionados. "
            f"Verifique se o pipeline foi executado para a data e período desejados."
        )
