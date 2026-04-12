import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- BLOCO 1: IDENTIFICAÇÃO (NA LATERAL COMO VOCÊ GOSTA) ---
with st.sidebar:
    st.header("📋 Dados do Cliente")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao_id = st.text_input("Identificação do Talhão:", "Gleba 01")
    area_ha = st.number_input("Área da Gleba (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- BLOCO 2: DADOS TÉCNICOS ---
st.header("1️⃣ Níveis de Fertilidade e Análise")
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    v_atual = st.number_input("V% Atual:", value=0.0)
    ctc_total = st.number_input("CTC Total:", value=0.0)
with col_n2:
    prnt_calc = st.number_input("PRNT do Calcário (%):", value=80.0)
    v_alvo = st.number_input("V% Alvo:", value=70.0 if cultura == "Soja" else 60.0)
with col_n3:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Baixo", "Médio", "Alto"])
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Baixo", "Médio", "Alto"])

# --- BLOCO 3: CÁLCULOS ---
# Calagem
if prnt_calc > 0:
    nc_ha = ((v_alvo - v_atual) * ctc_total) / prnt_calc
    nc_ha = max(0.0, nc_ha)
else:
    nc_ha = 0.0

# Adubação
st.markdown("---")
st.header("2️⃣ Recomendação de Adubação")
c1, c2, c3 = st.columns(3)
with c1:
    p_puro = st.number_input("Necessidade de P2O5 (kg/ha):", value=0.0)
with c2:
    perc_p_adubo = st.number_input("% de P2O5 no Adubo (Ex: 14):", value=14.0)
with c3:
    formulado = st.text_input("NPK Sugerido:", "04-14-08")

dose_adubo = (p_puro * 100) / perc_p_adubo if perc_p_adubo > 0 else 0.0

st.info(f"Dose calculada: {dose_adubo:.2f} kg/ha de {formulado}")

# --- BLOCO 4: PDF CORRIGIDO (COM ACENTOS E DOSE) ---
def exportar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.set_xy(0, 15)
    # Nomes com acentos corrigidos
    pdf.cell(210, 10, "RELATÓRIO DE RECOMENDAÇÃO TÉCNICA".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Informações da Área
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 50)
    pdf.cell(0, 10, f"Produtor: {cliente} | Identificação:
