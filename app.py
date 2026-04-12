import streamlit as st
from fpdf import FPDF
import math

# --- CONFIGURACAO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronomica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- ENTRADA DE DADOS ---
with st.sidebar:
    st.header("📋 Identificacao")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao = st.text_input("Talhao:", "Gleba 01")
    area_ha = st.number_input("Area (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

st.header("1️⃣ Analise de Solo")
col_in1, col_in2 = st.columns(2)
with col_in1:
    v_atual = st.number_input("V% atual (do laudo):", 0.0)
    ctc = st.number_input("CTC (cmolc/dm3):", 5.0)
with col_in2:
    prnt = st.number_input("PRNT do Calcario (%):", 80.0)
    argila = st.number_input("Teor de Argila (%):", 0.0)

# --- ESCOLHA MANUAL DOS NIVEIS (COMO VOCE PEDIU) ---
st.header("2️⃣ Niveis de Fertilidade (Escolha Manual)")
c_n1, c_n2, c_n3 = st.columns(3)
with c_n1:
    nivel_n = st.selectbox("Nivel de Nitrogenio (N):", ["Baixo", "Medio", "Alto"])
with c_n2:
    nivel_p = st.selectbox("Nivel de Fosforo (P):", ["Baixo", "Medio", "Alto"])
with c_n3:
    nivel_k = st.selectbox("Nivel de Potassio (K):", ["Baixo", "Medio", "Alto"])

# --- CALCULOS TECNICOS ---
# 1. Calagem
v_alvo = 70 if cultura == "Soja" else 60
if v_alvo > v_atual and prnt > 0:
    nc_ha = ((v_alvo - v_atual) * ctc) / prnt
else:
    nc_ha = 0.0
total_calcario = nc_ha * area_ha

# 2. Adubacao (Tabela)
tabelas = {
    "Soja": {"N": {"Baixo": 20, "Medio": 10, "Alto": 0}, "P": {"Baixo": 100, "Medio": 80, "Alto": 50}, "K": {"Baixo": 90, "Medio": 70, "Alto": 50}},
    "Milho": {"N": {"Baixo": 120, "Medio": 80, "Alto": 40}, "P": {"Baixo": 120, "Medio": 90, "Alto": 60}, "K": {"Baixo": 100, "Medio": 80, "Alto": 60}}
}
req_n = tabelas[cultura]["N"][nivel_n]
req_p = tabelas[cultura]["P"][nivel_p]
req_k = tabelas[cultura]["K"][nivel_k]

# --- EXIBICAO ORGANIZADA DOS RESULTADOS ---
st.markdown("---")
st.header("3️⃣ Resultados da Recomendacao")

# Destaque para Calagem (O que estava sumido)
st.subheader("🚜 Correcao (Calagem)")
c1, c2 = st.columns(2)
c1.metric("Necessidade de Calcario", f"{nc_ha:.2f} t/ha")
c2.metric("Total para a Area", f"{total_calcario:.2f} Toneladas")

# Destaque para Adubacao
st.subheader("🌱 Adubacao (N-P-K)")
a1, a2, a3 = st.columns(3)
a1.metric(f"N ({nivel_n})", f"{req_n} kg/ha")
a2.metric(f"P2O5 ({nivel_p})", f"{req_p} kg/ha")
a3.metric(f"K2O ({nivel_k})", f"{req_k} kg/ha")

# --- FINALIZACAO E PDF ---
st.markdown("---")
st.header("4️⃣ Gerar Relatorio Final")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(230, 255, 230) # Fundo Verde
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_fill_color(34, 139, 34)  # Topo Verde Escuro
    pdf.rect(0, 0, 210, 30, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "RELATORIO TECNICO - FEL
