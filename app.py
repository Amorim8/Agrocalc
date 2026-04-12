import streamlit as st
from fpdf import FPDF

# --- CONFIGURACAO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronomica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- IDENTIFICACAO (SIDEBAR) ---
with st.sidebar:
    st.header("📋 Identificacao")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao = st.text_input("Talhao:", "Gleba 01")
    area_ha = st.number_input("Area (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. CAMPO: ANALISE DO SOLO (DADOS DO LAUDO) ---
st.header("1️⃣ Analise do Solo (Dados do Laboratorio)")
col_laudo1, col_laudo2, col_laudo3 = st.columns(3)
with col_laudo1:
    v_atual = st.number_input("V% atual (Saturacao):", 0.0)
with col_laudo2:
    ctc = st.number_input("CTC total (cmolc/dm3):", 5.0)
with col_laudo3:
    argila_gkg = st.number_input("Argila (g/kg):", 0.0)

st.markdown("---")

# --- 2. CAMPO: NIVEIS DE FERTILIDADE (CLASSIFICACAO) ---
st.header("2️⃣ Niveis de Fertilidade")
st.write("Defina os níveis para o cálculo da recomendação:")
col_niv1, col_niv2, col_niv3 = st.columns(3)
with col_niv1:
    nivel_n = st.selectbox("Nivel de Nitrogenio (N):", ["Baixo", "Medio", "Alto"])
with col_niv2:
    nivel_p = st.selectbox("Nivel de Fosforo (P):", ["Muito Baixo", "Baixo", "Medio", "Alto", "Muito Alto"])
with col_niv3:
    nivel_k = st.selectbox("Nivel de Potassio (K):", ["Muito Baixo", "Baixo", "Medio", "Alto", "Muito Alto"])

# --- 3. CALCULOS TECNICOS ---
# Calagem
v_alvo = 70 if cultura == "Soja" else 60
prnt_padrao = 80.0 # Padronizado
nc_ha = ((v_alvo - v_atual) * ctc) / prnt_padrao if (v_alvo > v_atual) else 0.0
total_calcario = nc_ha * area_ha

# Adubacao (Baseada nos Niveis do Campo 2)
if cultura == "Soja":
    req_n = 0
    obs_n = "Nitrogenio zero: Fixacao biologica (Inoculacao)."
    # Tabela Soja
    tab_p = {"Muito Baixo": 120, "Baixo": 100, "Medio": 80, "Alto": 50, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 110, "Baixo": 90, "Medio": 70, "Alto": 50, "Muito Alto": 0}
else:
    tab_n_milho = {"Baixo": 120, "Medio": 80, "Alto": 40}
    req_n = tab_n_milho[nivel_n]
    obs_n = "Nitrogenio mineral para Milho."
    # Tabela Milho
    tab_p = {"Muito Baixo": 140, "Baixo": 120, "Medio": 90, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 100, "Medio": 80, "Alto": 60, "Muito Alto": 0}

req_p = tab_p[nivel_p]
req_k = tab_k[nivel_k]

# --- 4. EXIBICAO DOS RESULTADOS ---
st.markdown("---")
st.header("3️⃣ Recomendacao de Corretivos e Adubos")

# Bloco Calagem
st.subheader("🚜 Calagem")
res_c1, res_c2 = st.columns(2)
res_c1.metric("Necessidade (t/ha)", f"{nc_ha:.2f}")
res_c2.metric("Total Area (Ton)", f"{total_calcario:.2f}")

# Bloco Adubação
st.subheader("🌱 Adubacao de Plantio (kg/ha)")
res_a1, res_a2, res_a3 = st.columns(3)
res_a1.metric("N (Nitrogenio)", f"{req_n}")
res_a2.metric(f"P2O5 ({nivel_p})", f"{req_p}")
res_a3.metric(f"K2O ({nivel_k})", f"{req_k}")

# --- 5. PDF (CORRECAO FINAL) ---
st.markdown("---")
st.header("4️⃣ Finalizacao")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    # Header Verde
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "RELATORIO TECNICO - FELIPE AMORIM", align="C")
    
    # Conteudo
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 40)
    pdf.cell(0, 10, f"Cliente: {cliente} | Cultura: {cultura}", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.cell(0, 8, f"--- DADOS DA ANALISE ---", ln=True)
    pdf.cell(0, 8, f"V% atual: {v_atual} | CTC: {ctc} | Argila: {argila_gkg} g/kg", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, f"--- RECOMENDACOES ---", ln=True)
    pdf.cell(0, 8, f"Calagem: {nc_ha:.2f} t/ha", ln=True)
    pdf.cell(0, 8, f"Nitrogenio (N): {req_n} kg/ha", ln=True)
    pdf.cell(0, 8, f"Fosforo (P2O5): {req_p} kg/ha (Nivel {nivel_p})", ln=True)
    pdf.cell(0, 8, f"Potassio (K2O): {req_k} kg/ha (Nivel {nivel_k})", ln=True)
    
    # Retorna como bytes puros para o download_button
    return bytes(pdf.output(dest='S'))

try:
    pdf_output = gerar_pdf()
    st.download_button(
        label="⬇️ BAIXAR RELATORIO PDF PROFISSIONAL",
        data=pdf_output,
        file_name=f"Recomendacao_{talhao}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao preparar o PDF: {e}")

st.caption("AgroCalc Pro | Felipe Amorim")
