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

# ---------------- ANÁLISE DO SOLO ----------------
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
    obs_calagem = "Não é necessário realizar calagem. Considerar uso de silício."
else:
    nc = ((v_alvo - v_atual) * ctc) / 100
    nc = nc / (prnt / 100) if prnt > 0 else 0
    obs_calagem = "Realizar calagem conforme recomendação técnica."

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

# Nitrogênio
if cultura == "Soja":
    obs_n = "Nitrogênio dispensado. Focar na inoculação."
else:
    obs_n = "Aplicar nitrogênio conforme recomendação."

st.success(f"N: {req_n} | P: {req_p} | K: {req_k} kg/ha")
st.warning(obs_n)

# ---------------- ADUBO FORMULADO ----------------
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

    # Estilização básica
    pdf.set_fill_color(230,255,23
