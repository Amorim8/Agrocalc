import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# -------------------------------
# CONFIGURAÇÃO
# -------------------------------
st.set_page_config(page_title="AgroCalc Pro", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.header("📋 Configuração da Área")

talhao = st.sidebar.text_input("Talhão:", "Área 01")
area = st.sidebar.number_input("Área (ha)", 1.0)

cultura = st.sidebar.selectbox("Cultura", ["Soja", "Milho"])

# -------------------------------
# ANÁLISE DO SOLO
# -------------------------------
st.header("1. Análise de Solo")

with st.expander("🧪 Inserir dados da análise de solo"):

    col1, col2, col3 = st.columns(3)

    with col1:
        p = st.number_input("Fósforo (ppm)", 0.0)
        k = st.number_input("Potássio (ppm)", 0.0)

    with col2:
        ca = st.number_input("Cálcio (cmolc/dm³)", 0.0)
        mg = st.number_input("Magnésio (cmolc/dm³)", 0.0)

    with col3:
        hal = st.number_input("H+Al (cmolc/dm³)", 0.0)
        argila = st.number_input("Argila (%)", 0.0)

ctc = ca + mg + hal
st.info(f"CTC calculada: {ctc:.2f}")

# -------------------------------
# CALAGEM
# -------------------------------
st.header("2. Calagem")

v1 = st.number_input("V1 (%)", 30.0)
v2 = 60 if cultura == "Soja" else 70
prnt = st.number_input("PRNT (%)", 80.0)

st.caption(f"V2 recomendado: {v2}%")

if v2 > v1:
    nc = ((v2 - v1) * ctc) / 100 / (prnt / 100)
else:
    nc = 0

st.success(f"Necessidade: {nc:.2f} t/ha")

# -------------------------------
# INTERPRETAÇÃO (MANUAL)
# -------------------------------
st.header("3. Interpretação do Solo")

with st.expander("Selecionar nível do solo"):

    nivel_p = st.selectbox("Fósforo", ["Baixo", "Médio", "Alto"])
    nivel_k = st.selectbox("Potássio", ["Baixo", "Médio", "Alto"])

# -------------------------------
# ADUBAÇÃO
# -------------------------------
st.header("4. Adubação")

if cultura == "Soja":
    tabela = {
        "Baixo": (100, 80),
        "Médio": (80, 60),
        "Alto": (60, 40)
    }
else:
    tabela = {
        "Baixo": (120, 100),
        "Médio": (90, 80),
        "Alto": (60, 60)
    }

req_p = tabela[nivel_p][0]
req_k = tabela[nivel_k][1]

st.info(f"P2O5: {req_p} kg/ha | K2O: {req_k} kg/ha")

# Adubo
f_p = st.number_input("P2O5 (%)", 20.0)
f_k = st.number_input("K2O (%)", 20.0)

dose_p = (req_p / f_p) * 100 if f_p > 0 else 0
dose_k = (req_k / f_k) * 100 if f_k > 0 else 0

dose = max(dose_p, dose_k)

st.success(f"Dose recomendada: {dose:.1f} kg/ha")

# -------------------------------
# PDF PROFISSIONAL
# -------------------------------
if st.button("📄 Gerar Relatório Profissional"):

    pdf = FPDF()
    pdf.add_page()

    # Cabeçalho verde
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 30, 'F')

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "RELATÓRIO AGRONÔMICO", align="C")

    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(0, 20)
    pdf.cell(210, 10, "Consultor: Felipe Amorim", align="C")

    pdf.ln(30)
    pdf.set_text_color(0, 0, 0)

    # Seção cinza
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Dados da Área", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Talhão: {talhao}", ln=True)
    pdf.cell(190, 8, f"Área: {area} ha", ln=True)
    pdf.cell(190, 8, f"Cultura: {cultura}", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Resultados", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Calagem: {nc:.2f} t/ha", ln=True)
    pdf.cell(190, 8, f"Fósforo: {nivel_p}", ln=True)
    pdf.cell(190, 8, f"Potássio: {nivel_k}", ln=True)
    pdf.cell(190, 8, f"Dose de adubo: {dose:.1f} kg/ha", ln=True)

    pdf_bytes = bytes(pdf.output(dest="S"))

    st.download_button(
        "⬇️ Baixar PDF",
        pdf_bytes,
        file_name=f"Relatorio_{talhao}.pdf"
    )
