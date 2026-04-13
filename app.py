import streamlit as st
from fpdf import FPDF
import math
import re
from PyPDF2 import PdfReader
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")

area = st.sidebar.number_input("Área (ha):", min_value=0.01, value=1.0, step=0.1)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# Upload PDF
st.sidebar.subheader("📄 Upload da Análise de Solo")
uploaded_file = st.sidebar.file_uploader("Enviar PDF", type=["pdf"])

# ---------------- FUNÇÃO PDF ----------------
def extrair_dados_pdf(file):
    reader = PdfReader(file)
    texto = ""

    for page in reader.pages:
        texto += page.extract_text()

    def buscar_valor(padrao):
        match = re.search(padrao, texto, re.IGNORECASE)
        return float(match.group(1).replace(",", ".")) if match else None

    return {
        "p": buscar_valor(r"F[oó]sforo.*?(\d+[.,]?\d*)"),
        "k": buscar_valor(r"Pot[aá]ssio.*?(\d+[.,]?\d*)"),
        "argila": buscar_valor(r"Argila.*?(\d+[.,]?\d*)"),
        "v": buscar_valor(r"V%.*?(\d+[.,]?\d*)"),
        "ctc": buscar_valor(r"CTC.*?(\d+[.,]?\d*)"),
    }

# ---------------- VALORES PADRÃO ----------------
p = 0.0
k = 0.0
argila = 0.0
v_atual = 0.0
ctc = 5.0

# ---------------- AUTO PREENCHIMENTO ----------------
if uploaded_file is not None:
    dados_pdf = extrair_dados_pdf(uploaded_file)

    if dados_pdf:
        st.success("✅ Dados da análise carregados automaticamente!")

        if dados_pdf["p"]: p = dados_pdf["p"]
        if dados_pdf["k"]: k = dados_pdf["k"]
        if dados_pdf["argila"]: argila = dados_pdf["argila"]
        if dados_pdf["v"]: v_atual = dados_pdf["v"]
        if dados_pdf["ctc"]: ctc = dados_pdf["ctc"]

# ---------------- ANÁLISE DO SOLO ----------------
st.header("1️⃣ Análise de Solo (Química)")

col1, col2, col3 = st.columns(3)

with col1:
    p = st.number_input("Fósforo (mg/dm³)", value=p)
    k = st.number_input("Potássio (cmolc/dm³)", value=k)

with col2:
    argila = st.number_input("Argila", value=argila)
    v_atual = st.number_input("V% Atual", value=v_atual)

with col3:
    ctc = st.number_input("CTC", value=ctc)
    prnt = st.number_input("PRNT (%)", value=80.0)

# ---------------- CALAGEM ----------------
st.header("2️⃣ Calagem")

v_alvo = 70 if cultura == "Soja" else 60

if v_atual >= v_alvo:
    nc = 0
    obs_calagem = "Não é necessário realizar calagem."
else:
    nc = ((v_alvo - v_atual) * ctc) / 100
    nc = nc / (prnt / 100) if prnt > 0 else 0
    obs_calagem = "Realizar calagem conforme recomendação."

total_calc = nc * area

colc1, colc2 = st.columns(2)
colc1.metric("Calcário (t/ha)", f"{nc:.2f}")
colc2.metric("Total (t)", f"{total_calc:.2f}")

st.info(obs_calagem)

# ---------------- INTERPRETAÇÃO ----------------
st.header("3️⃣ Interpretação do Solo")

niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]

col1, col2, col3 = st.columns(3)

with col1:
    nivel_n = st.selectbox("Nitrogênio", niveis)

with col2:
    nivel_p = st.selectbox("Fósforo", niveis)

with col3:
    nivel_k = st.selectbox("Potássio", niveis)

# ---------------- TABELA ----------------
tabela = {
    "Soja": {
        "N": {n: 0 for n in niveis},
        "P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 30},
        "K": {"Muito Baixo": 100, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 30}
    },
    "Milho": {
        "N": {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 40},
        "P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 40},
        "K": {"Muito Baixo": 100, "Baixo": 90, "Médio": 70, "Alto": 60, "Muito Alto": 40}
    }
}

req_n = tabela[cultura]["N"][nivel_n]
req_p = tabela[cultura]["P"][nivel_p]
req_k = tabela[cultura]["K"][nivel_k]

obs_n = "Nitrogênio dispensado." if cultura == "Soja" else "Aplicar nitrogênio."

st.success(f"N: {req_n} | P₂O₅: {req_p} | K₂O: {req_k} kg/ha")
st.warning(obs_n)

# ---------------- ADUBO ----------------
st.header("4️⃣ Adubo Formulado")

col1, col2, col3 = st.columns(3)

f_n = col1.number_input("N (%)", 0)
f_p = col2.number_input("P (%)", 20)
f_k = col3.number_input("K (%)", 20)

dose = 0
sacos = 0

if f_p > 0:
    dose = (req_p / f_p) * 100
    total_adubo = dose * area
    sacos = math.ceil(total_adubo / 50)

    st.success(f"Dose: {dose:.0f} kg/ha | Total: {sacos} sacos")

# ---------------- PDF ----------------
st.header("5️⃣ Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    def txt(t):
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    data = datetime.now().strftime("%d/%m/%Y")

    pdf.set_font("Arial","B",14)
    pdf.cell(190,10, txt("CONSULTORIA AGRONÔMICA"), ln=True, align="C")

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"Felipe Amorim - {data}"), ln=True, align="C")

    pdf.ln(10)

    pdf.cell(190,8, txt(f"Produtor: {cliente}"), ln=True)
    pdf.cell(190,8, txt(f"Talhão: {talhao}"), ln=True)
    pdf.cell(190,8, txt(f"Área: {area} ha"), ln=True)
    pdf.cell(190,8, txt(f"Cultura: {cultura}"), ln=True)

    pdf.ln(5)

    pdf.cell(190,8, txt(f"P₂O₅: {req_p} kg/ha"), ln=True)
    pdf.cell(190,8, txt(f"K₂O: {req_k} kg/ha"), ln=True)

    return bytes(pdf.output(dest='S'))

if st.button("📄 Gerar PDF"):
    st.download_button("⬇️ Baixar Relatório", gerar_pdf(), file_name="relatorio.pdf")
