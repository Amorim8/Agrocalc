import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronomica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- IDENTIFICAÇÃO (LATERAL) ---
with st.sidebar:
    st.header("📋 Identificacao")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao = st.text_input("Talhao:", "Gleba 01")
    area_ha = st.number_input("Area (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ANALISE DO SOLO (DADOS DO LABORATORIO) ---
st.header("1️⃣ Analise do Solo")
st.write("Insira os dados técnicos do laudo do laboratório:")
col_lab1, col_lab2, col_lab3 = st.columns(3)
with col_lab1:
    v_atual = st.number_input("V% atual (Saturacao por Bases):", 0.0)
with col_lab2:
    ctc = st.number_input("CTC total (cmolc/dm3):", 5.0)
with col_lab3:
    prnt = st.number_input("PRNT do Calcario (%):", 80.0)

# --- 2. CALAGEM (RECOMENDAÇÃO DE CORREÇÃO) ---
st.header("2️⃣ Recomendacao de Calagem")
v_alvo = 70 if cultura == "Soja" else 60
# Cálculo da Necessidade de Calcário (NC)
if v_alvo > v_atual and prnt > 0:
    nc_ha = ((v_alvo - v_atual) * ctc) / prnt
else:
    nc_ha = 0.0
total_calcario = nc_ha * area_ha

# Exibição em destaque
c1, c2 = st.columns(2)
c1.metric("Calcario Necessario (t/ha)", f"{nc_ha:.2f}")
c2.metric("Total para a Area (Toneladas)", f"{total_calcario:.2f}")
st.markdown("---")

# --- 3. ADUBAÇÃO (NÍVEIS PADRONIZADOS) ---
st.header("3️⃣ Recomendacao de Adubacao")
st.info("Escolha os níveis conforme o laudo para ver a sugestão de adubo:")
c_n1, c_n2, c_n3 = st.columns(3)
with c_n1:
    nivel_n = st.selectbox("Nivel de Nitrogenio (N):", ["Baixo", "Medio", "Alto"])
with c_n2:
    nivel_p = st.selectbox("Nivel de Fosforo (P):", ["Baixo", "Medio", "Alto"])
with c_n3:
    nivel_k = st.selectbox("Nivel de Potassio (K):", ["Baixo", "Medio", "Alto"])

# Lógica técnica de adubação
if cultura == "Soja":
    req_n = 0
    obs_n = "Soja produz o proprio N via bacterias (Inoculacao)."
    tab_pk = {"P": {"Baixo": 100, "Medio": 80, "Alto": 50}, "K": {"Baixo": 90, "Medio": 70, "Alto": 50}}
else:
    tab_n_milho = {"Baixo": 120, "Medio": 80, "Alto": 40}
    req_n = tab_n_milho[nivel_n]
    obs_n = "Adubacao nitrogenada mineral para Milho."
    tab_pk = {"P": {"Baixo": 120, "Medio": 90, "Alto": 60}, "K": {"Baixo": 100, "Medio": 80, "Alto": 60}}

req_p = tab_pk["P"][nivel_p]
req_k = tab_pk["K"][nivel_k]

# Exibição dos adubos
a1, a2, a3 = st.columns(3)
a1.metric("N (Nitrogenio)", f"{req_n} kg/ha")
a2.metric(f"P2O5 ({nivel_p})", f"{req_p} kg/ha")
a3.metric(f"K2O ({nivel_k})", f"{req_k} kg/ha")

if cultura == "Soja":
    st.success(f"Nota Tecnica: {obs_n}")

# --- 4. RELATÓRIO PDF (SOLUÇÃO DO ERRO) ---
st.markdown("---")
st.header("4️⃣ Relatorio Final")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(34, 139, 34) # Verde
    pdf.rect(0, 0, 210, 30, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "RELATORIO TECNICO - FELIPE AMORIM", align="C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 40)
    pdf.cell(0, 10, f"Produtor: {cliente} | Cultura: {cultura}", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.cell(0, 8, f"--- RECOMENDACOES ---", ln=True)
    pdf.cell(0, 8, f"Calagem: {nc_ha:.2f} t/ha (Total: {total_calcario:.2f} t)", ln=True)
    pdf.cell(0, 8, f"Nitrogenio: {req_n} kg/ha", ln=True)
    if cultura == "Soja":
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 6, f"Obs: {obs_n}", ln=True)
        pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Fosforo: {req_p} kg/ha (Nivel {nivel_p})", ln=True)
    pdf.cell(0, 8, f"Potassio: {req_k} kg/ha (Nivel {nivel_k})", ln=True)
    
    # Retorna os bytes diretamente, sem .encode()
    return pdf.output(dest='S')

try:
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="⬇️ BAIXAR RELATORIO PDF",
        data=pdf_bytes,
        file_name=f"Relatorio_{talhao}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao gerar o arquivo: {e}")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
