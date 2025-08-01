import streamlit as st

st.set_page_config(
    page_title="Página Inicial - Open Expense Tracker",
    layout="wide"
)

st.title("Bem-vindo ao Open Expense Tracker 🚀")

st.markdown("""
Este é o hub central para o projeto de auditoria de despesas públicas.

**Navegue pelas páginas na barra lateral para:**

- **Painel de Controle**: Iniciar, pausar e acompanhar as execuções do pipeline de análise.
- **Todos os Relatórios**: Acessar o arquivo completo de todos os relatórios `.docx` já gerados.

Selecione uma página na barra de navegação à esquerda para começar.
""")
