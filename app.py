import streamlit as st
from fpdf import FPDF
import math

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Dados Gerais")
cliente = st.sidebar.text_input("Produtor:", "Nome do Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área (ha):", value=1.0)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# ---------------- ENTRADA ----------------
st.header("1️⃣ Análise de Solo")

with st.expander("📊 Inserir dados do laudo"):

    col1, col2 = st.columns(2)

    with col1:
        argila = st.number_input("Argila:", 0.0)
        p_solo = st.number_input("Fósforo (mg/dm³):", 0.0)
        v_atual = st.number_input("V% atual:", 0.0)

    with col2:
        k_solo = st.number_input("Potássio:", 0.0)
        ctc = st.number_input("CTC:", 5.0)
        prnt = st.number_input("PRNT (%):", 80.0)

# ---------------- INTERPRETAÇÃO ----------------
st.header("2️⃣ Interpretação do Solo")

col_n1, col_n2 = st.columns(2)

with col_n1:
    nivel_p = st.selectbox("Fósforo (P)", ["Baixo", "Médio", "Alto"])

with col_n2:
    nivel_k = st.selectbox("Potássio (K)", ["Baixo", "Médio", "Alto"])

st.info(f"Classificação: P = {nivel_p} | K = {nivel_k}")

# ---------------- CALAGEM ----------------
st.header("3️⃣ Calagem")

v_alvo = 70 if cultura == "Soja" else 60

if v_alvo > v_atual:
    nc_ha = ((v_alvo - v_atual) * ctc) / 100
    nc_ha = nc_ha / (prnt / 100) if prnt > 0 else 0
else:
    nc_ha = 0

total_calcario = nc_ha * area_ha

# ---------------- ADUBAÇÃO ----------------
st.header("4️⃣ Adubação")

tabela = {
    "Soja": {
        "P": {"Baixo": 100, "Médio": 80, "Alto": 50},
        "K": {"Baixo": 90, "Médio": 70, "Alto": 50}
    },
    "Milho": {
        "P": {"Baixo": 120, "Médio": 90, "Alto": 60},
        "K": {"Baixo": 100, "Médio": 80, "Alto": 60}
    }
}

req_p = tabela[cultura]["P"][nivel_p]
req_k = tabela[cultura]["K"][nivel_k]

res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc_ha:.2f}")
res2.metric("P₂O₅ (kg/ha)", f"{req_p}")
res3.metric("K₂O (kg/ha)", f"{req_k}")

# ---------------- FORMULADO ----------------
st.subheader("📦 Adubo Formulado")

f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N", 0)
f_p = f2.number_input("P", 20)
f_k = f3.number_input("K", 20)

dose_adubo = 0
sacos_total = 0

if f_p > 0:
    dose_adubo = (req_p / f_p) * 100
    sacos_total = (dose_adubo * area_ha) / 50

    st.success(f"Dose: {int(dose_adubo)} kg/ha | {math.ceil(sacos_total)} sacos")

# ---------------- PDF ----------------
st.header("5️⃣ Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    # FUNDO VERDE CLARO
    pdf.set_fill_color(230, 255, 230)
    pdf.rect(0, 0, 210, 297, 'F')

    # CABEÇALHO VERDE
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 35, 'F')

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "RELATORIO AGRONOMICO", align="C")

    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(0, 22)
    pdf.cell(210, 10, "Felipe Amorim - Eng. Agronomo", align="C")

    pdf.ln(40)
    pdf.set_text_color(0, 0, 0)

    # BLOCO CINZA
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "DADOS DA AREA", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Produtor: {cliente}", ln=True)
    pdf.cell(190, 8, f"Talhao: {talhao}", ln=True)
    pdf.cell(190, 8, f"Area: {area_ha} ha", ln=True)
    pdf.cell(190, 8, f"Cultura: {cultura}", ln=True)

    pdf.ln(5)

    # ANÁLISE
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "ANALISE DO SOLO", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Fosforo: {p_solo} ({nivel_p})", ln=True)
    pdf.cell(190, 8, f"Potassio: {k_solo} ({nivel_k})", ln=True)
    pdf.cell(190, 8, f"Argila: {argila}", ln=True)

    pdf.ln(5)

    # RESULTADOS
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "RECOMENDACOES", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Calcario: {nc_ha:.2f} t/ha", ln=True)
    pdf.cell(190, 8, f"Total: {total_calcario:.2f} t", ln=True)
    pdf.cell(190, 8, f"P2O5: {req_p} kg/ha", ln=True)
    pdf.cell(190, 8, f"K2O: {req_k} kg/ha", ln=True)

    if dose_adubo > 0:
        pdf.cell(190, 8, f"Adubo: {int(dose_adubo)} kg/ha ({f_n}-{f_p}-{f_k})", ln=True)
        pdf.cell(190, 8, f"Sacos: {math.ceil(sacos_total)}", ln=True)

    return pdf.output(dest='S')

if st.button("📄 Gerar PDF"):
    pdf_bytes = gerar_pdf()

    st.download_button(
        "⬇️ Baixar Relatório",
        pdf_bytes,
        file_name=f"Relatorio_{talhao}.pdf"
    )

st.caption("AgroCalc Pro | Felipe Amorim")
