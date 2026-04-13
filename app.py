import streamlit as st
from fpdf import FPDF
import math
import re
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR ---
st.sidebar.header("📋 Dados da Área")
produtor = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ANÁLISE DE SOLO ---
st.header("1️⃣ Análise de Solo")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³):", value=0.0)
    k_solo = st.number_input("Potássio (cmolc/dm³):", value=0.0)
with col2:
    v_atual = st.number_input("V% Atual:", value=0.0)
    ctc = st.number_input("CTC Total:", value=5.0)
with col3:
    prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# --- 2. CALAGEM (AUTOMÁTICA) ---
st.header("2️⃣ Calagem")
v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
total_calc = nc * area_ha

c1, c2 = st.columns(2)
c1.metric("Calcário (t/ha)", f"{nc:.2f}")
c2.metric("Total Área (t)", f"{total_calc:.2f}")

# --- 3. INTERPRETAÇÃO PADRONIZADA (TABELAS) ---
st.header("3️⃣ Interpretação e Recomendação")
st.write(f"Defina os níveis conforme o manual da **{cultura}**:")

niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
int1, int2 = st.columns(2)

with int1:
    nivel_p = st.selectbox("Nível de Fósforo (P):", niveis, index=2)
with int2:
    nivel_k = st.selectbox("Nível de Potássio (K):", niveis, index=2)

# Lógica de Recomendação baseada nos manuais (kg/ha de P2O5 e K2O)
if cultura == "Soja":
    tab_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
else: # Milho
    tab_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 90, "Médio": 60, "Alto": 40, "Muito Alto": 0}

req_p = tab_p[nivel_p]
req_k = tab_k[nivel_k]

st.info(f"📌 Recomendação Técnica: {req_p} kg/ha de P₂O₅ e {req_k} kg/ha de K₂O")

# --- 4. ADUBO FORMULADO ---
st.header("4️⃣ Adubo Formulado")
st.write("Escolha a formulação NPK que será utilizada no plantio:")

f1, f2, f3 = st.columns(3)
with f1:
    n_f = st.number_input("N (%)", value=4.0)
with f2:
    p_f = st.number_input("P (%)", value=14.0)
with f3:
    k_f = st.number_input("K (%)", value=8.0)

# Cálculo da dose baseada no Fósforo (mais comum no plantio)
if p_f > 0:
    dose_ha = (req_p * 100) / p_f
    total_sacos = math.ceil((dose_ha * area_ha) / 50)
    
    st.warning(f"🚀 Dose Sugerida: {dose_ha:.0f} kg/ha")
    st.success(f"📦 Total para a área: {total_sacos} sacos de 50kg")
else:
    st.error("A porcentagem de P na fórmula deve ser maior que zero.")

# --- 5. RELATÓRIO PDF ---
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def cl(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Visual Agronômico
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 20, cl("CONSULTORIA AGRONÔMICA"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 5, cl(f"Consultor: Felipe Amorim | {datetime.now().strftime('%d/%m/%Y')}"), ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, cl(f"Produtor: {cliente} | Talhão: {talhao}"), ln=True)
    pdf.cell(0, 10, cl(f"Cultura: {cultura} | Área: {area_ha} ha"), ln=True)
    pdf.ln(5)
    
    pdf.cell(0, 10, cl(f"Necessidade de Calcário: {nc:.2f} t/ha"), ln=True)
    pdf.cell(0, 10, cl(f"Recomendação NPK: {req_p} P / {req_k} K (kg/ha)"), ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, cl(f"ADUBAÇÃO: {dose_ha:.0f} kg/ha da fórmula {n_f:.0f}-{p_f:.0f}-{k_f:.0f}"), ln=True)
    pdf.cell(0, 10, cl(f"TOTAL DE SACOS: {total_sacos}"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar Relatório Profissional"):
    pdf_out = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório", pdf_out, f"Relatorio_{talhao}.pdf", "application/pdf")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
