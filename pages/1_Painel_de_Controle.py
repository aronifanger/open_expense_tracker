import streamlit as st
import time
import os
import signal
import pandas as pd
from pathlib import Path
from datetime import date
from src import process_manager

# Constants
LOG_FILE = "pipeline.log"
REPORTS_DIR = Path("reports")
DEPUTIES_FILE = Path("data/raw/deputados.csv")

# --- Helper Functions ---

@st.cache_data
def get_total_deputies():
    """Gets the total number of deputies from the local file."""
    if not DEPUTIES_FILE.exists():
        return 0
    if DEPUTIES_FILE.exists():
        df = pd.read_csv(DEPUTIES_FILE)
        return len(df)
    return 0

def get_reports(limit=None):
    """Returns a list of generated DOCX report files."""
    if not REPORTS_DIR.exists():
        return []
    all_reports = sorted(list(REPORTS_DIR.glob("*.docx")), reverse=True)
    if limit:
        return all_reports[:limit]
    return all_reports

def read_log_file_reversed():
    """Reads the log file and returns its content with lines reversed."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return "".join(reversed(lines))
    except FileNotFoundError:
        return "Arquivo de log não encontrado. Inicie o pipeline para gerá-lo."

# --- App UI ---

st.set_page_config(page_title="Painel de Controle", layout="wide")
st.title("Open Expense Tracker")
st.subheader("Painel de Controle")
st.caption("Esta é a página principal para iniciar e acompanhar o pipeline de análise.")

total_deputies = get_total_deputies()
process_info = process_manager.get_process_info()

# --- Sidebar (Controls and Configuration) ---
st.sidebar.header("Configuração da Execução")

st.sidebar.selectbox("Período de Análise", ['diário', 'semanal', 'mensal'], key='period', disabled=bool(process_info))
st.sidebar.date_input("Data de Referência", value=date.today(), key='processing_date', disabled=bool(process_info))
st.sidebar.number_input(
    f"Processar quantos deputados? (Total: {total_deputies})", 
    min_value=0, 
    max_value=total_deputies, 
    value=total_deputies, 
    key='limit_input',
    help="Use 0 para processar todos os deputados.",
    disabled=bool(process_info)
)

st.sidebar.header("Controles do Pipeline")

if st.sidebar.button("Iniciar Pipeline", disabled=bool(process_info), type="primary"):
    limit_value = st.session_state.get('limit_input', total_deputies)
    date_value = st.session_state.get('processing_date').strftime('%Y-%m-%d')
    period_value = st.session_state.get('period', 'diário')
    
    command = ["python", "main.py", "--date", date_value, "--period", period_value]
    if limit_value > 0:
        command.extend(["--limit", str(limit_value)])
    
    process_manager.start_process(command)
    st.rerun()

if process_info:
    is_paused = process_info.get("status") == "paused"
    col1, col2 = st.sidebar.columns(2)
    
    if not is_paused:
        if col1.button("Pausar", use_container_width=True):
            process_manager.send_signal_to_process(signal.SIGSTOP)
            process_manager.update_process_status("paused")
            st.rerun()
    else:
        if col1.button("Continuar", use_container_width=True):
            process_manager.send_signal_to_process(signal.SIGCONT)
            process_manager.update_process_status("running")
            st.rerun()

st.sidebar.header("Logs")
if st.sidebar.button("Limpar Logs", disabled=bool(process_info)):
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    st.rerun()

# --- Main Page Layout ---
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("Status")
    if process_info:
        if process_info.get("status") == "paused":
            st.warning("Pausado")
        else:
            st.info("Em execução...")
    else:
        st.success("Ocioso / Concluído")

    st.subheader("Relatórios Recentes")
    recent_reports = get_reports(limit=3)
    if recent_reports:
        for report in recent_reports:
            with open(report, "rb") as file:
                st.download_button(
                    label=f"Baixar {report.name}",
                    data=file,
                    file_name=report.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_{report.name}"
                )
        st.info("Para ver todos os relatórios, acesse a página 'Relatório Detalhado'.")
    else:
        st.info("Nenhum relatório .docx encontrado.")

with col1:
    st.subheader("Logs em Tempo Real")
    log_content = read_log_file_reversed() if process_info else "Nenhum log para exibir."
    st.text_area("Logs", value=log_content, height=600, key="log_area", disabled=True)

# --- UI Auto-Refresh Logic ---
if process_info:
    # If a process is running, this script will rerun every second to update logs.
    time.sleep(1)
    st.rerun()
