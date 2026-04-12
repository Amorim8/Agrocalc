import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- BLOCO 1: IDENTIFICAÇÃO ---
with st.sidebar:
    st.header("📋 Dados do Cliente")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao_id = st.text_input("Identificação do Talhão:", "Gleba 01")
    area_ha = st.number_input("Área da Gleba (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- BLOCO 2: NÍVEIS DE FERTILIDADE ---
st.header("1️⃣ Níveis de Fertilidade (Interpretação)")
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    nivel_n = st.selectbox("Nível de Nitrogênio (N):", ["Baixo", "Médio", "Alto"])
with col_n2:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_n3:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])

# --- BLOCO 3: NECESSIDADE DE NUTRIENTES (SEPARADOS) ---
if cultura == "Soja":
    req_n = 0
    tab_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 110, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 0}
else: # Milho
    tab_n_val = {"Baixo": 120, "Médio": 80, "Alto": 40}
    req_n = tab_n_val[nivel_n]
    tab_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}

req_p, req_k = tab_p[nivel_p], tab_k[nivel_k]

st.subheader("📍 Necessidade de Nutrientes (Puro/kg por ha)")
n1, n2, n3 = st.columns(3)
n1.metric("Nitrogênio (N)", f"{req_n} kg/ha")
n2.metric("Fósforo (P2O5)", f"{req_p} kg/ha")
n3.metric("Potássio (K2O)", f"{req_k} kg/ha")

# --- BLOCO 4: ADUBAÇÃO FORMULADA ---
st.markdown("---")
st.header("2️⃣ Cálculo do Adubo Formulado")
st.write("Digite a porcentagem de cada nutriente no seu adubo (ex: 04-14-08):")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1: f_n_val = st.number_input("% N na fórmula", 0)
with col_f2: f_p_val = st.number_input("% P2O5 na fórmula", 0)
with col_f3: f_k_val = st.number_input("% K2O na fórmula", 0)

# Cálculo da dose do adubo baseado no Fósforo (Limitante)
if f_p_val > 0:
    dose_kg_ha = (req_p * 100) / f_p_val
else:
    dose_kg_ha = 0.0

st.success(f"✅ Recomendo aplicar: **{dose_kg_ha:.2f} kg/ha** do adubo {f_n_val}-{f_p_val}-{f_k_val}")

# --- BLOCO 5: PDF ---
st.markdown("---")
def exportar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.set_xy(0, 15)
    pdf.cell(210, 10, "RECOMENDACAO TECNICA AGRO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Dados Gerais
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 50)
    pdf.cell(0, 10, f"Cliente: {cliente} | Gleba: {talhao_id}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 10, f"Cultura: {cultura} | Area: {area_ha} ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Resultados
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "DETALHES DA NECESSIDADE (kg/ha):".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"- Nitrogenio (N): {req_n} | Fosforo (P2O5): {req_p} | Potassio (K2O): {req_k}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "ADUBACAO FORMULADA SUGERIDA:".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, f"APLICAR: {dose_kg_ha:.2f} kg/ha do NPK {f_n_val}-{f_p_val}-{f_k_val}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Responsavel: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    return pdf.output(dest='S').encode('latin-1')

try:
    pdf_final = exportar_pdf()
    st.download_button(
        label="⬇️ BAIXAR RELATÓRIO PDF",
        data=pdf_final,
        file_name=f"Recomendacao_{talhao_id}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao gerar o PDF. Verifique os dados.")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
