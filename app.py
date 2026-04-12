import streamlit as st
from fpdf import FPDF
import math

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")

area = st.sidebar.number_input(
    "Área (ha):",
    min_value=0.01,
    value=1.0,
    step=0.1
)

cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# V% automático
v_alvo = 70 if cultura == "Soja" else 60

# ---------------- ANÁLISE COMPLETA ----------------
st.header("1️⃣ Análise de Solo (Química)")

col1, col2, col3 = st.columns(3)

with col1:
    p = st.number_input("Fósforo (mg/dm³)", 0.0)
    k = st.number_input("Potássio (cmolc/dm³)", 0.0)

with col2:
    argila = st.number_input("Argila (g/kg ou %)", 0.0)
    v_atual = st.number_input("V% Atual", 0.0)

with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", 5.0)
    prnt = st.number_input("PRNT (%)", 80.0)

# ---------------- CALAGEM ----------------
st.header("2️⃣ Calagem")

if v_atual >= v_alvo:
    nc = 0
    obs_calagem = "Nao e necessario realizar calagem. Considerar uso de silicio."
else:
    nc = ((v_alvo - v_atual) * ctc) / 100
    nc = nc / (prnt / 100) if prnt > 0 else 0
    obs_calagem = "Realizar calagem conforme recomendacao."

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

if cultura == "Soja":
    obs_n = "Nitrogenio dispensado. Focar na inoculacao."
else:
    obs_n = "Aplicar nitrogenio conforme recomendacao."

st.success(f"N: {req_n} | P: {req_p} | K: {req_k} kg/ha")
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

    pdf.set_fill_color(230,255,230)
    pdf.rect(0,0,210,297,'F')

    pdf.set_fill_color(34,139,34)
    pdf.rect(0,0,210,35,'F')

    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",18)
    pdf.cell(210,15,"CONSULTORIA AGRONOMICA", align="C")

    pdf.ln(10)
    pdf.set_font("Arial","B",12)
    pdf.cell(210,10,"Consultor: Felipe Amorim", align="C")

    pdf.ln(25)
    pdf.set_text_color(0,0,0)

    pdf.set_font("Arial","B",12)
    pdf.cell(190,8,"DADOS DA AREA",ln=True,fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8,f"Produtor: {cliente}",ln=True)
    pdf.cell(190,8,f"Area: {area} ha",ln=True)
    pdf.cell(190,8,f"Cultura: {cultura}",ln=True)

    pdf.ln(5)

    pdf.set_font("Arial","B",12)
    pdf.cell(190,8,"ANALISE DO SOLO",ln=True,fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8,f"P: {p}",ln=True)
    pdf.cell(190,8,f"K: {k}",ln=True)
    pdf.cell(190,8,f"Argila: {argila}",ln=True)
    pdf.cell(190,8,f"V%: {v_atual}",ln=True)

    pdf.ln(5)

    pdf.set_font("Arial","B",12)
    pdf.cell(190,8,"CALAGEM",ln=True,fill=True)

    pdf.set_font("Arial","",11)

    if nc == 0:
        pdf.multi_cell(190,8,obs_calagem)
    else:
        pdf.cell(190,8,f"Necessidade: {nc:.2f} t/ha",ln=True)

    pdf.ln(5)

    pdf.set_font("Arial","B",12)
    pdf.cell(190,8,"ADUBACAO",ln=True,fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8,f"N: {req_n} | P: {req_p} | K: {req_k}",ln=True)
    pdf.cell(190,8,obs_n,ln=True)

    return bytes(pdf.output(dest='S'))

if st.button("📄 Gerar PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar", pdf_bytes, file_name="relatorio.pdf")
