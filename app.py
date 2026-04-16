import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")

area = st.sidebar.number_input("Área (ha):", min_value=0.01, value=1.0)

cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

v_alvo = 70 if cultura == "Soja" else 60

# ---------------- ANÁLISE ----------------
st.header("1️⃣ Análise de Solo")

col1, col2, col3 = st.columns(3)

with col1:
    p = st.number_input("Fósforo (mg/dm³)", 0.0)
    k = st.number_input("Potássio (cmolc/dm³)", 0.0)

with col2:
    v_atual = st.number_input("V% Atual", 0.0)
    argila = st.number_input("Argila", 0.0)

with col3:
    ctc = st.number_input("CTC", min_value=0.0, value=5.0)
    prnt = st.number_input("PRNT (%)", 80.0)

# ---------------- CALAGEM ----------------
st.header("2️⃣ Calagem")

if v_atual >= v_alvo:
    nc = 0
    obs_calagem = "V% já adequado, não é necessário calagem."
else:
    nc = ((v_alvo - v_atual) * ctc) / 100
    nc = nc / (prnt / 100) if prnt > 0 else 0
    obs_calagem = "Aplicar calcário para elevar V%."

st.metric("Calcário (t/ha)", f"{nc:.2f}")
st.info(obs_calagem)

# ---------------- ADUBAÇÃO ----------------
st.header("3️⃣ Recomendação")

if cultura == "Soja":
    produtividade = st.selectbox("Produtividade (t/ha)", [3, 4, 5])
else:
    produtividade = st.number_input("Produtividade (sc/ha)", value=60)

# N
req_n = 0 if cultura == "Soja" else (100 if produtividade <= 60 else 120)

# P
if cultura == "Milho":
    if p <= 5:
        req_p, nivel_p = 100, "Muito Baixo"
    elif p <= 10:
        req_p, nivel_p = 80, "Baixo"
    elif p <= 15:
        req_p, nivel_p = 60, "Médio"
    elif p <= 20:
        req_p, nivel_p = 40, "Alto"
    else:
        req_p, nivel_p = 20, "Muito Alto"
else:
    classe_p = "Adequado" if p <= 15 else "Alto"
    tabela = {
        3: {"Adequado": 60, "Alto": 30},
        4: {"Adequado": 80, "Alto": 40},
        5: {"Adequado": 100, "Alto": 50}
    }
    req_p = tabela[produtividade][classe_p]

# K
if cultura == "Milho":
    if k <= 0.15:
        req_k, nivel_k = 80, "Muito Baixo"
    elif k <= 0.30:
        req_k, nivel_k = 60, "Baixo"
    elif k <= 0.45:
        req_k, nivel_k = 40, "Médio"
    elif k <= 0.60:
        req_k, nivel_k = 20, "Alto"
    else:
        req_k, nivel_k = 0, "Muito Alto"
else:
    classe_k = "Adequado" if k <= 0.45 else "Alto"
    tabela_k = {
        3: {"Adequado": 60, "Alto": 40},
        4: {"Adequado": 80, "Alto": 50},
        5: {"Adequado": 100, "Alto": 70}
    }
    req_k = tabela_k[produtividade][classe_k]

st.success(f"N: {req_n} | P2O5: {req_p} | K2O: {req_k}")

# ---------------- FORMULADO ----------------
st.header("4️⃣ Adubo Formulado")

f_n = st.number_input("N (%)", 0.0)
f_p = st.number_input("P (%)", 20.0)
f_k = st.number_input("K (%)", 20.0)

doses = []
limitantes = []

# Milho usa N
if cultura == "Milho" and f_n > 0:
    dn = (req_n / f_n) * 100
    doses.append(dn)
    limitantes.append(("N", dn))

if f_p > 0:
    dp = (req_p / f_p) * 100
    doses.append(dp)
    limitantes.append(("P", dp))

if f_k > 0:
    dk = (req_k / f_k) * 100
    doses.append(dk)
    limitantes.append(("K", dk))

if doses:
    dose = max(doses)
    st.success(f"Dose: {dose:.0f} kg/ha")

    lim = [n for n, d in limitantes if d == dose]
    st.info(f"Limitante: {', '.join(lim)}")

# ---------------- PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",14)
    pdf.cell(190,10,"Relatório Agronômico", ln=True)

    data = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(190,10,f"Data: {data}", ln=True)

    pdf.cell(190,10,f"N: {req_n} | P: {req_p} | K: {req_k}", ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("Gerar PDF"):
    st.download_button("Baixar", gerar_pdf(), "relatorio.pdf")
