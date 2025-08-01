import streamlit as st
from datetime import date
from src import doc_reporter

st.set_page_config(page_title="Relatório Detalhado", layout="wide")
st.title("📄 Relatório Detalhado de Análise")

st.markdown("Selecione os parâmetros para visualizar o relatório detalhado e gerar o documento Word sob demanda.")

# --- User Selection ---
col1, col2 = st.columns(2)
selected_date = col1.date_input("Selecione a Data de Referência", value=date.today())
selected_period = col2.selectbox("Selecione o Período", ['diário', 'semanal', 'mensal'])

if selected_date and selected_period:
    report_data = doc_reporter.get_report_data(selected_date, selected_period)

    if report_data:
        # --- Download Button ---
        st.sidebar.header("Download")
        report_io = doc_reporter.generate_word_report(selected_date, selected_period, report_data)
        if report_io:
            file_name = f"{selected_date.strftime('%Y-%m-%d')}_{selected_period}_Relatorio_Fiscalizacao.docx"
            st.sidebar.download_button(
                label="Baixar Relatório em Word (.docx)",
                data=report_io,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # --- Display Report On-Screen ---
        st.header(f"Top 10 Deputados com Despesas Críticas ({selected_period.capitalize()})")
        st.dataframe(report_data["top_10_deputies"])

        st.header("Top 10 Fornecedores em Despesas Críticas")
        st.dataframe(report_data["top_suppliers"])
        
        st.header("Top 10 Tipos de Despesa em Despesas Críticas")
        st.dataframe(report_data["top_expense_types"])
        
        st.header("Análise Individual dos Top Deputados")
        for _, deputy in report_data["top_10_deputies"].iterrows():
            st.subheader(f"Deputado: {deputy['deputy_name']}")
            st.markdown("*Gráfico da evolução histórica será inserido aqui.*")
            
            deputy_expenses = report_data["critical_expenses"][
                report_data["critical_expenses"]['deputy_id'] == deputy['deputy_id']
            ].nlargest(1, 'score_fraude')
            
            if not deputy_expenses.empty:
                st.write(f"**Principal Despesa Crítica do Período ({selected_period.capitalize()})**")
                st.dataframe(deputy_expenses)
            else:
                st.info("Nenhuma despesa crítica encontrada para este deputado no período.")
    else:
        st.warning(
            "Dados do relatório não encontrados para os parâmetros selecionados. "
            "Verifique se o pipeline foi executado para a data e período desejados."
        )
