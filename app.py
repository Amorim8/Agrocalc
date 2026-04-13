import streamlit as st
from fpdf import FPDF
import math
import re
from PyPDF2 import PdfReader
from datetime import datetime

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR (LADO ESQUERDO) ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area = st.sidebar.number_input("Área (ha):", min_value=0.01, value=1.0, step=0.1)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# Importar Análise (Upload)
st.sidebar.subheader("📄 Importar Análise")
uploaded_file = st.sidebar.file_uploader("Enviar PDF da Análise", type=["pdf"])

# ---------------- FUNÇÃO DE EXTRAÇÃO DE DADOS ----------------
def extrair_dados_pdf(file):
    try:
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
    except:
        return None

# Valores padrão iniciais
p_ini, k_ini, arg_ini, v_ini, ctc_ini = 0.0, 0.0, 0.0, 0.0, 5.0

if uploaded_file is not None:
    dados_pdf = extrair_dados_pdf(uploaded_file)
    if dados_pdf:
        st.sidebar.success("✅ Dados importados com sucesso!")
        p_ini = dados_pdf["p"] or 0.0
        k_ini = dados_pdf["k"] or 0.0
        arg_ini = dados_pdf["argila"] or 0.0
        v_ini = dados_pdf["v"] or 0.0
        ctc_ini = dados_pdf["ctc"] or 5.0

# ---------------- 1️⃣ ANÁLISE DO SOLO (CORPO PRINCIPAL) ----------------
st.header("1️⃣ Análise de Solo (Química)")
col1, col2, col3 = st.columns(3)

with col1:
    p = st.number_input("Fósforo (mg/dm³)", value=p_ini)
    k = st.number_input("Potássio (cmolc/dm³)", value=k_ini)
with col2:
    argila = st.number_input("Argila (g/kg ou %)", value=arg_ini)
    v_atual = st.number_input("V% Atual", value=v_ini)
with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", value=ctc_ini)
    prnt = st.number_input("PRNT (%)", value=80.0)

# ---------------- 2️⃣ CALAGEM (AUTOMÁTICO) ----------------
st.header("2️⃣ Calagem")
v_alvo = 70 if cultura == "Soja" else 60

if v_atual >= v_alvo:
    nc = 0.0
    obs_calagem = "Não é necessário realizar calagem. Solo em equilíbrio."
else:
    nc = ((v_alvo - v_atual) * ctc) / prnt if prnt > 0 else 0.0
    obs_calagem = "Realizar calagem conforme recomendação técnica."

total_calc = nc * area

cc1, cc2 = st.columns(2)
cc1.metric("Calcário (t/ha)", f"{nc:.2f}")
cc2.metric("Total para a Área (t)", f"{total_calc:.2f}")
st.info(obs_calagem)

# ---------------- 3️⃣ INTERPRETAÇÃO E RECOMENDAÇÃO ----------------
st.header("3️⃣ Interpretação e NPK")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]

col_int1, col_int2, col_int3 = st.columns(3)
with col_int1: nivel_n = st.selectbox("Nitrogênio", niveis, index=2)
with col_int2: nivel_p = st.selectbox("Fósforo", niveis, index=2)
with col_int3: nivel_k = st.selectbox("Potássio", niveis, index=2)

# Tabela de Recomendação (Exemplo simplificado)
tabela = {
    "Soja": {"P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 30}},
    "Milho": {"P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 40}}
}
req_p = tabela[cultura]["P"][nivel_p]

# ---------------- 4️⃣ ADUBO FORMULADO ----------------
st.header("4️⃣ Adubo Formulado")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N (%) do adubo", value=4)
f_p = f2.number_input("P (%) do adubo", value=14)
f_k = f3.number_input("K (%) do adubo", value=8)

dose = (req_p / f_p) * 100 if f_p > 0 else 0.0
sacos = math.ceil((dose * area) / 50)

st.success(f"Dose: {dose:.0f} kg/ha | Total: {sacos} sacos de 50kg para a área.")

# ---------------- 5️⃣ GERAR PDF (RELATÓRIO TÉCNICO) ----------------
st.header("5️⃣ Relatório Final")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    def txt(t):
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Estética do PDF
    pdf.set_fill_color(34, 139, 34) # Verde
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 20, txt("CONSULTORIA AGRONÔMICA"), ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 5, txt(f"Consultor: Felipe Amorim"), ln=True, align="C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)

    # Conteúdo organizado
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("DADOS DA ÁREA"), ln=True, fill=False)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"Produtor: {cliente} | Talhão: {talhao}"), ln=True)
    pdf.cell(190, 7, txt(f"Cultura: {cultura} | Área: {area} ha"), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("RECOMENDAÇÃO DE CALAGEM"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"Necessidade: {nc:.2f} t/ha | Total Área: {total_calc:.2f} t"), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("RECOMENDAÇÃO DE ADUBAÇÃO"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"Adubo: {f_n}-{f_p}-{f_k}"), ln=True)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(190, 10, txt(f"DOSE FORMULADO: {dose:.0f} kg/ha"), ln=True)
    pdf.cell(190, 10, txt(f"TOTAL DE SACOS (50kg): {sacos}"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar Relatório PDF"):
    try:
        pdf_out = gerar_pdf()
        st.download_button(
            label="⬇️ Baixar Relatório",
            data=pdf_out,
            file_name=f"Relatorio_{talhao}.pdf",
            mime="application/pdf"
        )
    except:
        st.error("Erro ao gerar PDF. Verifique os dados.")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
