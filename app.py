import streamlit as st
from fpdf import FPDF
import math

# --- CONFIGURACAO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronomica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- IDENTIFICACAO (Lado Esquerdo) ---
with st.sidebar:
    st.header("📋 Identificacao")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao = st.text_input("Talhao:", "Gleba 01")
    area_ha = st.number_input("Area (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ENTRADA DE DADOS DA ANALISE ---
st.header("1️⃣ Dados da Analise de Solo")
col_in1, col_in2 = st.columns(2)
with col_in1:
    v_atual = st.number_input("V% atual (do laudo):", 0.0)
    ctc = st.number_input("CTC total:", 5.0)
with col_in2:
    prnt = st.number_input("PRNT do Calcario (%):", 80.0)
    argila = st.number_input("Teor de Argila (%):", 0.0)

# --- 2. NIVEIS DE FERTILIDADE (O QUE VOCE PEDIU) ---
st.header("2️⃣ Niveis de Fertilidade (Escolha Manual)")
st.info("Selecione os niveis conforme a sua interpretacao do laudo:")
c_n1, c_n2, c_n3 = st.columns(3)
with c_n1:
    nivel_n = st.selectbox("Nivel de Nitrogenio (N):", ["Baixo", "Medio", "Alto"])
with c_n2:
    nivel_p = st.selectbox("Nivel de Fosforo (P):", ["Baixo", "Medio", "Alto"])
with c_n3:
    nivel_k = st.selectbox("Nivel de Potassio (K):", ["Baixo", "Medio", "Alto"])

# --- 3. CALCULOS DE RECOMENDACAO ---
# Calculo de Calagem (Destaque)
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual and prnt > 0 else 0.0
total_calcario = nc_ha * area_ha

# Tabela de Adubacao NPK
tabelas = {
    "Soja": {"N": {"Baixo": 20, "Medio": 10, "Alto": 0}, "P": {"Baixo": 100, "Medio": 80, "Alto": 50}, "K": {"Baixo": 90, "Medio": 70, "Alto": 50}},
    "Milho": {"N": {"Baixo": 120, "Medio": 80, "Alto": 40}, "P": {"Baixo": 120, "Medio": 90, "Alto": 60}, "K": {"Baixo": 100, "Medio": 80, "Alto": 60}}
}
req_n = tabelas[cultura]["N"][nivel_n]
req_p = tabelas[cultura]["P"][nivel_p]
req_k = tabelas[cultura]["K"][nivel_k]

# --- 4. EXIBICAO ORGANIZADA ---
st.markdown("---")
st.header("3️⃣ Recomendacao Final")

# Secao de Calagem bem visivel
st.subheader("🚜 Correcao do Solo (Calagem)")
res_c1, res_c2 = st.columns(2)
res_c1.metric("Necessidade de Calcario", f"{nc_ha:.2f} t/ha")
res_c2.metric("Total para a Area", f"{total_calcario:.2f} Ton")

# Secao de Adubacao
st.subheader("🌱 Adubacao de Plantio (kg/ha)")
res_a1, res_a2, res_a3 = st.columns(3)
res_a1.metric(f"N ({nivel_n})", f"{req_n}")
res_a2.metric(f"P2O5 ({nivel_p})", f"{req_p}")
res_a3.metric(f"K2O ({nivel_k})", f"{req_k}")

# --- 5. GERACAO DE PDF ---
st.markdown("---")
st.header("4️⃣ Relatorio Final")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(235, 255, 235) # Fundo verde clarinho
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_fill_color(34, 139, 34) # Faixa topo
    pdf.rect(0, 0, 210, 30, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "RELATORIO TECNICO - FELIPE AMORIM", align="C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 40)
    pdf.cell(0, 10, f"Cliente: {cliente} | Cultura: {cultura}", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.cell(0, 8, f"--- RECOMENDACOES ---", ln=True)
    pdf.cell(0, 8, f"- Calagem: {nc_ha:.2f} t/ha", ln=True)
    pdf.cell(0, 8, f"- Nitrogenio (N): {req_n} kg/ha", ln=True)
    pdf.cell(0, 8, f"- Fosforo (P2O5): {req_p} kg/ha", ln=True)
    pdf.cell(0, 8, f"- Potassio (K2O): {req_k} kg/ha", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

try:
    pdf_out = gerar_pdf()
    st.download_button(
        label="⬇️ BAIXAR RELATORIO PDF",
        data=pdf_out,
        file_name=f"Relatorio_{talhao}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao preparar o PDF: {e}")

st.caption("AgroCalc Pro | Felipe Amorim")
