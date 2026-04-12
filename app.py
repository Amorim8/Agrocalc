import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# -------------------------------
# CONFIGURAÇÃO DE INTERFACE
# -------------------------------
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

# Estilo para melhorar a organização visual
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 Consultoria Agronômica Digital")
st.subheader("Responsável Técnico: Felipe Amorim")
st.markdown("---")

# -------------------------------
# SIDEBAR - DADOS DO CLIENTE E ÁREA
# -------------------------------
st.sidebar.header("📋 Identificação e Área")
cliente = st.sidebar.text_input("Nome do Produtor:", "Cliente Exemplo")
talhao = st.sidebar.text_input("Talhão/Gleba:", "Área 01")
area_total = st.sidebar.number_input("Tamanho da Área (Hectares):", value=1.0, min_value=0.01, step=0.1, help="Funciona para áreas menores que 1ha (ex: 0.5) ou grandes áreas.")
cultura = st.sidebar.selectbox("Cultura Alvo:", ["Soja", "Milho"])

# -------------------------------
# 1. ANÁLISE DE SOLO (ORGANIZADA)
# -------------------------------
st.header("1️⃣ Diagnóstico do Solo")
col_an1, col_an2 = st.columns(2)

with col_an1:
    st.subheader("Físico/Químico")
    profundidade = st.selectbox("Profundidade da amostra:", ["0-20 cm", "20-40 cm", "0-40 cm"])
    argila = st.number_input("Teor de Argila (Valor no laudo):", value=0.0)
    v_atual = st.number_input("V% Atual (Saturação por Bases):", value=0.0)

with col_an2:
    st.subheader("Nutrientes")
    p_solo = st.number_input("Fósforo (P) [mg/dm³]:", value=0.0)
    k_solo = st.number_input("Potássio (K) [cmolc/dm³]:", value=0.0)
    ctc_total = st.number_input("CTC Total (pH 7.0):", value=5.0)

# -------------------------------
# 2. CALAGEM E CORREÇÃO
# -------------------------------
st.divider()
st.header("2️⃣ Necessidade de Calagem")

v_alvo = 70 if cultura == "Soja" else 60
prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# Cálculo NC = ((V2 - V1) * CTC) / PRNT
nc_ha = ((v_alvo - v_atual) * ctc_total) / prnt if v_alvo > v_atual else 0
total_calcario = nc_ha * area_total

col_c1, col_c2 = st.columns(2)
with col_c1:
    st.metric("Dose por Hectare", f"{nc_ha:.2f} t/ha")
with col_c2:
    st.metric(f"Total para {area_total} ha", f"{total_calcario:.2f} Ton")

# -------------------------------
# 3. RECOMENDAÇÃO DE ADUBAÇÃO (NPK)
# -------------------------------
st.divider()
st.header("3️⃣ Planejamento de Adubação")
st.write(f"Escolha a meta de produtividade para calcular a extração:")

m1, m2, m3 = st.columns(3)
if m1.button("📉 Baixa"): meta_sug = 5.0 if cultura == "Milho" else 2.5
elif m2.button("📊 Média"): meta_sug = 9.0 if cultura == "Milho" else 3.8
elif m3.button("🚀 Alta"): meta_sug = 13.0 if cultura == "Milho" else 5.5
else: meta_sug = 10.0 if cultura == "Milho" else 3.5

meta_final = st.number_input("Meta Ajustada (t/ha):", value=meta_sug)

# Lógica de Extração (kg/t produzida)
if cultura == "Soja":
    n_kg, p_kg, k_kg = 0, 15, 20
else:
    n_kg, p_kg, k_kg = 22, 9, 18

req_n_total = n_kg * meta_final * area_total
req_p_total = p_kg * meta_final * area_total
req_k_total = k_kg * meta_final * area_total

st.subheader(f"Necessidade Total de Nutrientes para {area_total} ha:")
res_n, res_p, res_k = st.columns(3)
res_n.metric("Nitrogênio (N)", f"{int(req_n_total)} kg")
res_p.metric("Fósforo (P₂O₅)", f"{int(req_p_total)} kg")
res_k.metric("Potássio (K₂O)", f"{int(req_k_total)} kg")

# -------------------------------
# 4. GERAÇÃO DE PDF (CORRIGIDA)
# -------------------------------
st.divider()
st.header("4️⃣ Finalização")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "RELATÓRIO DE RECOMENDAÇÃO TÉCNICA", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Consultor: Felipe Amorim", ln=True)
    pdf.cell(200, 10, f"Produtor: {cliente} | Talhão: {talhao}", ln=True)
    pdf.cell(200, 10, f"Área Total: {area_total} ha | Cultura: {cultura}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "--- Recomendação de Correção ---", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Necessidade de Calcário: {nc_ha:.2f} t/ha", ln=True)
    pdf.cell(200, 10, f"Total de Calcário para a área: {total_calcario:.2f} Ton", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "--- Recomendação de Adubação ---", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Fósforo Total (P2O5): {int(req_p_total)} kg", ln=True)
    pdf.cell(200, 10, f"Potássio Total (K2O): {int(req_k_total)} kg", ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.button("📝 Preparar PDF para Download"):
    pdf_output = gerar_pdf()
    st.download_button(
        label="⬇️ Baixar Relatório Técnico",
        data=pdf_output,
        file_name=f"Recomendacao_{talhao}.pdf",
        mime="application/pdf"
    )

st.caption("© 2026 | Desenvolvido para Felipe Amorim | P (mg/dm³) | K (cmolc/dm³)")
