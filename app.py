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

    profundidade = st.selectbox(
        "Profundidade da amostra",
        ["0–20 cm", "20–40 cm", "0–40 cm"]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        p = st.number_input("Fósforo (mg/dm³)", 0.0)

    with col2:
        k = st.number_input("Potássio (cmolc/dm³ ou mg/dm³)", 0.0)

    with col3:
        argila = st.number_input("Argila (valor do laudo)", 0.0)

# CTC simplificada (usuário define ou pode evoluir depois)
ctc = st.number_input("CTC (cmolc/dm³)", 5.0)

st.info(f"Profundidade selecionada: {profundidade}")

# -------------------------------
# CALAGEM
# -------------------------------
st.header("2. Calagem")

v1 = st.number_input("V1 (%)", 30.0)

v2 = 60 if cultura == "Soja" else 70
prnt = st.number_input("PRNT (%)", 80.0)

st.caption(f"V2 recomendado para {cultura}: {v2}%")

if v2 > v1:
    nc = ((v2 - v1) * ctc) / 100 / (prnt / 100)
else:
    nc = 0

st.success(f"Necessidade de calagem: {nc:.2f} t/ha")

# -------------------------------
# INTERPRETAÇÃO MANUAL (SOLO)
# -------------------------------
st.header("3. Interpretação da Análise")

with st.expander("Classificar níveis do solo"):

    nivel_p = st.selectbox("Fósforo no solo (interpretação)", ["Baixo", "Médio", "Alto"])
    nivel_k = st.selectbox("Potássio no solo (interpretação)", ["Baixo", "Médio", "Alto"])

# -------------------------------
# ADUBAÇÃO
# -------------------------------
st.header("4. Adubação")

if cultura == "Soja":
    tabela_p = {"Baixo": 100, "Médio": 80, "Alto": 60}
    tabela_k = {"Baixo": 80, "Médio": 60, "Alto": 40}
else:
    tabela_p = {"Baixo": 120, "Médio": 90, "Alto": 60}
    tabela_k = {"Baixo": 100, "Médio": 80, "Alto": 60}

req_p = tabela_p[nivel_p]
req_k = tabela_k[nivel_k]

st.markdown(f"""
### Recomendação da cultura
- Fósforo: {req_p} kg/ha  
- Potássio: {req_k} kg/ha  
""")

# Adubo comercial
f_p = st.number_input("P2O5 (%) do fertilizante", 20.0)
f_k = st.number_input("K2O (%) do fertilizante", 20.0)

dose_p = (req_p / f_p) * 100 if f_p > 0 else 0
dose_k = (req_k / f_k) * 100 if f_k > 0 else 0

dose_final = max(dose_p, dose_k)

st.success(f"Dose recomendada: {dose_final:.1f} kg/ha")

# -------------------------------
# PDF PROFISSIONAL
# -------------------------------
if st.button("📄 Gerar Relatório"):

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

    pdf.ln(35)
    pdf.set_text_color(0, 0, 0)

    # Dados área
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Dados da Área", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Talhão: {talhao}", ln=True)
    pdf.cell(190, 8, f"Área: {area} ha", ln=True)
    pdf.cell(190, 8, f"Cultura: {cultura}", ln=True)
    pdf.cell(190, 8, f"Profundidade: {profundidade}", ln=True)

    pdf.ln(5)

    # Resultados
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "Resultados", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Fósforo (mg/dm³): {p}", ln=True)
    pdf.cell(190, 8, f"Potássio: {k}", ln=True)
    pdf.cell(190, 8, f"Argila: {argila}", ln=True)
    pdf.cell(190, 8, f"Calagem: {nc:.2f} t/ha", ln=True)
    pdf.cell(190, 8, f"Adubação: {dose_final:.1f} kg/ha", ln=True)

    pdf_bytes = bytes(pdf.output(dest="S"))

    st.download_button(
        "⬇️ Baixar Relatório",
        pdf_bytes,
        file_name=f"Relatorio_{talhao}.pdf"
    )
