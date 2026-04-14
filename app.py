import streamlit as st
from fpdf import FPDF
import pandas as pd
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

v_alvo = 70 if cultura == "Soja" else 60

# ---------------- UPLOAD ----------------
st.header("📂 Upload da Análise de Solo")

arquivo = st.file_uploader("Envie arquivo Excel (.xlsx)", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)

    st.write("📊 Dados encontrados:")
    st.dataframe(df)

    amostra_col = df.columns[0]

    amostra = st.selectbox("Escolha a amostra:", df[amostra_col].unique())

    linha = df[df[amostra_col] == amostra].iloc[0]

    p = float(linha.get("P", 0))
    k = float(linha.get("K", 0))
    argila = float(linha.get("Argila", 0))
    v_atual = float(linha.get("V%", 0))

    st.success("Dados carregados automaticamente!")

else:
    st.header("1️⃣ Análise de Solo (Manual)")

    col1, col2, col3 = st.columns(3)

    with col1:
        p = st.number_input("Fósforo (mg/dm³)", 0.0)
        k = st.number_input("Potássio (cmolc/dm³)", 0.0)

    with col2:
        argila = st.number_input("Argila", 0.0)
        v_atual = st.number_input("V% Atual", 0.0)

    with col3:
        ctc = st.number_input("CTC", 5.0)
        prnt = st.number_input("PRNT (%)", 80.0)

# valores padrão caso venha do Excel
ctc = 5.0 if 'ctc' not in locals() else ctc
prnt = 80.0 if 'prnt' not in locals() else prnt

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

nivel_n = col1.selectbox("Nitrogênio", niveis)
nivel_p = col2.selectbox("Fósforo", niveis)
nivel_k = col3.selectbox("Potássio", niveis)

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
    obs_n = "Nitrogênio dispensado. Focar na inoculação."
else:
    obs_n = "Aplicar nitrogênio conforme recomendação."

st.success(f"N: {req_n} | P2O5: {req_p} | K2O: {req_k} kg/ha")
st.warning(obs_n)

# ---------------- ADUBO ----------------
st.header("4️⃣ Adubo Formulado")

f_n = st.number_input("N (%)", 0)
f_p = st.number_input("P (%)", 20)
f_k = st.number_input("K (%)", 20)

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

    pdf.set_fill_color(230,255,230)
    pdf.rect(0,0,210,297,'F')

    pdf.set_fill_color(34,139,34)
    pdf.rect(0,0,210,35,'F')

    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",18)
    pdf.cell(210,15, txt("CONSULTORIA AGRONÔMICA"), align="C")

    pdf.ln(10)
    pdf.set_font("Arial","B",12)
    pdf.cell(210,10, txt("Consultor: Felipe Amorim"), align="C")

    pdf.ln(25)
    pdf.set_text_color(0,0,0)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"Produtor: {cliente}"), ln=True)
    pdf.cell(190,8, txt(f"Área: {area} ha"), ln=True)

    pdf.ln(5)
    pdf.cell(190,8, txt(f"P: {p} | K: {k} | V%: {v_atual}"), ln=True)

    pdf.ln(5)
    pdf.cell(190,8, txt(f"Calcário: {nc:.2f} t/ha"), ln=True)

    pdf.ln(5)
    pdf.cell(190,8, txt(f"P2O5: {req_p} | K2O: {req_k}"), ln=True)

    if dose > 0:
        pdf.cell(190,8, txt(f"Adubo: {f_n}-{f_p}-{f_k}"), ln=True)
        pdf.cell(190,8, txt(f"Sacos: {sacos}"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar", pdf_bytes, file_name="relatorio.pdf")
