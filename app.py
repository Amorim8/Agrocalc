import streamlit as st
from fpdf import FPDF
import math
import re
from PyPDF2 import PdfReader
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide", page_icon="🌿")

st.title("🌿 Consultoria Agronômica")
st.subheader(f"Consultor: Felipe Amorim")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente Padrão")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area = st.sidebar.number_input("Área (ha):", min_value=0.01, value=1.0, step=0.1)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

st.sidebar.subheader("📄 Upload da Análise de Solo")
uploaded_file = st.sidebar.file_uploader("Enviar PDF da Análise", type=["pdf"])

# ---------------- FUNÇÕES ----------------
def extrair_dados_pdf(file):
    try:
        reader = PdfReader(file)
        texto = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                texto += content

        def buscar_valor(padrao):
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                # Limpa o valor para converter em float
                val = match.group(1).replace(",", ".")
                return float(val)
            return None

        return {
            "p": buscar_valor(r"F[oó]sforo.*?(\d+[.,]?\d*)"),
            "k": buscar_valor(r"Pot[aá]ssio.*?(\d+[.,]?\d*)"),
            "argila": buscar_valor(r"Argila.*?(\d+[.,]?\d*)"),
            "v": buscar_valor(r"V%.*?(\d+[.,]?\d*)"),
            "ctc": buscar_valor(r"CTC.*?(\d+[.,]?\d*)"),
        }
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return None

# Valores Iniciais
p_val, k_val, argila_val, v_atual_val, ctc_val = 0.0, 0.0, 0.0, 0.0, 5.0

if uploaded_file:
    dados = extrair_dados_pdf(uploaded_file)
    if dados:
        st.success("✅ Dados carregados com sucesso!")
        p_val = dados["p"] or 0.0
        k_val = dados["k"] or 0.0
        argila_val = dados["argila"] or 0.0
        v_atual_val = dados["v"] or 0.0
        ctc_val = dados["ctc"] or 5.0

# ---------------- 1. ANÁLISE QUÍMICA ----------------
st.header("1️⃣ Análise de Solo")
c1, c2, c3 = st.columns(3)

with c1:
    p = st.number_input("Fósforo (mg/dm³)", value=p_val)
    k = st.number_input("Potássio (cmolc/dm³)", value=k_val)
with c2:
    argila = st.number_input("Argila (%)", value=argila_val)
    v_atual = st.number_input("V% Atual", value=v_atual_val)
with c3:
    ctc = st.number_input("CTC (T)", value=ctc_val)
    prnt = st.number_input("PRNT do Calcário (%)", value=80.0)

# ---------------- 2. CALAGEM ----------------
st.divider()
st.header("2️⃣ Recomendação de Calagem")

v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0
total_calc = nc * area

colc1, colc2, colc3 = st.columns(3)
colc1.metric("Necessidade (t/ha)", f"{nc:.2f}")
colc2.metric("Total para Área (t)", f"{total_calc:.2f}")
colc3.info(f"V% Alvo para {cultura}: {v_alvo}%")

# ---------------- 3. ADUBAÇÃO ----------------
st.divider()
st.header("3️⃣ Recomendação de NPK")

tabela = {
    "Soja": {
        "N": {"Muito Baixo": 0, "Baixo": 0, "Médio": 0, "Alto": 0, "Muito Alto": 0},
        "P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 30},
        "K": {"Muito Baixo": 100, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 30}
    },
    "Milho": {
        "N": {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 40},
        "P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 40},
        "K": {"Muito Baixo": 100, "Baixo": 90, "Médio": 70, "Alto": 60, "Muito Alto": 40}
    }
}

niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
i1, i2, i3 = st.columns(3)
n_nv = i1.selectbox("Nível N", niveis, index=2)
p_nv = i2.selectbox("Nível P", niveis, index=2)
k_nv = i3.selectbox("Nível K", niveis, index=2)

req_n = tabela[cultura]["N"][n_nv]
req_p = tabela[cultura]["P"][p_nv]
req_k = tabela[cultura]["K"][k_nv]

st.subheader(f"Dose Alvo: N:{req_n} | P₂O₅:{req_p} | K₂O:{req_k} kg/ha")

# Formulado
st.write("---")
st.write("**Cálculo do Adubo Formulado**")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("% N (Adubo)", value=0)
f_p = f2.number_input("% P₂O₅ (Adubo)", value=20)
f_k = f3.number_input("% K₂O (Adubo)", value=20)

if f_p > 0:
    dose_ha = (req_p / f_p) * 100
    total_quilos = dose_ha * area
    sacos = math.ceil(total_quilos / 50)
    
    st.success(f"Dose Recomendada: **{dose_ha:.0f} kg/ha**")
    st.metric("Total de Sacos (50kg)", sacos)

# ---------------- 4. PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    def t(texto_str): return str(texto_str).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, t("RELATÓRIO DE RECOMENDAÇÃO AGRONÔMICA"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 8, t(f"Consultor: Felipe Amorim | Data: {datetime.now().strftime('%d/%m/%Y')}"), ln=True, align="C")
    pdf.ln(10)

    # Dados do Cliente
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(190, 8, t(" DADOS DA ÁREA"), ln=True, fill=True)
    pdf.cell(95, 8, t(f"Produtor: {cliente}"))
    pdf.cell(95, 8, t(f"Talhão: {talhao}"), ln=True)
    pdf.cell(95, 8, t(f"Á : {area} ha"))
    pdf.cell(95, 8, t(f"Cultura: {cultura}"), ln=True)
    pdf.ln(5)

    # Calagem
    pdf.cell(190, 8, t(" RECOMENDAÇÃO DE CALAGEM"), ln=True, fill=True)
    pdf.cell(190, 8, t(f"Necessidade de Calcário: {nc:.2f} t/ha"), ln=True)
    pdf.cell(190, 8, t(f"Total para a área: {total_calc:.2f} toneladas"), ln=True)
    pdf.ln(5)

    # Adubação
    pdf.cell(190, 8, t(" RECOMENDAÇÃO DE ADUBAÇÃO"), ln=True, fill=True)
    pdf.cell(190, 8, t(f"Dose Alvo NPK: {req_n}-{req_p}-{req_k} kg/ha"), ln=True)
    if f_p > 0:
        pdf.cell(190, 8, t(f"Formulado Utilizado: {f_n}-{f_p}-{f_k}"), ln=True)
        pdf.cell(190, 8, t(f"Quantidade: {dose_ha:.0f} kg/ha (Total: {sacos} sacos)"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📊 Finalizar e Gerar Relatório"):
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="⬇️ Baixar PDF",
        data=pdf_bytes,
        file_name=f"Recomendacao_{cliente}_{talhao}.pdf",
        mime="application/pdf"
    )
