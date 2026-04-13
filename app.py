import streamlit as st
from fpdf import FPDF
import math
import re
from datetime import datetime

# --- TENTATIVA SEGURA DE IMPORTAR LEITOR DE PDF ---
try:
    from PyPDF2 import PdfReader
    PDF_READY = True
except ImportError:
    PDF_READY = False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- BARRA LATERAL ---
st.sidebar.header("📋 Dados da Área")
produtor = st.sidebar.text_input("Nome do Produtor:", "Cesário")
talhao = st.sidebar.text_input("Talhão/Gleba:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0)
cultura = st.sidebar.selectbox("Cultura de Destino:", ["Soja", "Milho"])

st.sidebar.subheader("📄 Importar Análise")
arquivo_pdf = st.sidebar.file_uploader("Subir PDF da Análise", type=["pdf"])

def extrair_dados_pdf(pdf):
    try:
        reader = PdfReader(pdf)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
        def buscar(reg):
            match = re.search(reg, texto, re.IGNORECASE)
            return float(match.group(1).replace(",", ".")) if match else 0.0
        return {
            "p": buscar(r"F[oó]sforo.*?(\d+[.,]?\d*)"),
            "k": buscar(r"Pot[aá]ssio.*?(\d+[.,]?\d*)"),
            "v": buscar(r"V%.*?(\d+[.,]?\d*)"),
            "ctc": buscar(r"CTC.*?(\d+[.,]?\d*)")
        }
    except:
        return None

# Valores Iniciais
p_ini, k_ini, v_ini, ctc_ini = 0.0, 0.0, 0.0, 5.0

if arquivo_pdf and PDF_READY:
    dados = extrair_dados_pdf(arquivo_pdf)
    if dados:
        st.sidebar.success("✅ Dados extraídos!")
        p_ini, k_ini, v_ini, ctc_ini = dados.values()
elif arquivo_pdf and not PDF_READY:
    st.sidebar.warning("Aguarde a instalação da biblioteca PyPDF2 no servidor.")

# --- 1. ENTRADA DE DADOS ---
st.header("1️⃣ Dados da Análise")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³):", value=p_ini)
    k_solo = st.number_input("Potássio (cmolc/dm³):", value=k_ini)
with col2:
    v_atual = st.number_input("V% Atual:", value=v_ini)
    ctc = st.number_input("CTC Total:", value=ctc_ini)
with col3:
    prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# --- 2. CALAGEM ---
v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
total_calc = nc * area_ha
st.info(f"👉 Calagem: {nc:.2f} t/ha | Total: {total_calc:.2f} toneladas.")

# --- 3. NÍVEIS NPK ---
st.header("2️⃣ Recomendação de Adubação")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
i1, i2, i3 = st.columns(3)
n_nivel = i1.selectbox("Nitrogênio:", niveis, index=2)
p_nivel = i2.selectbox("Fósforo:", niveis, index=2)
k_nivel = i3.selectbox("Potássio:", niveis, index=2)

# Tabelas Simplificadas
if cultura == "Soja":
    t_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}
    req_p = t_p[p_nivel]
    req_n, req_k = 0, 80 # Valores base
else:
    t_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    req_p = t_p[p_nivel]
    req_n, req_k = 100, 60

# --- 4. CÁLCULO ADUBO ---
st.header("3️⃣ Adubo Formulado")
f1, f2, f3 = st.columns(3)
f_p = f2.number_input("P na Fórmula (%):", value=14.0)
nome_f = st.text_input("Fórmula do Adubo:", "04-14-08")

if f_p > 0:
    dose = (req_p * 100) / f_p
    sacos = math.ceil((dose * area_ha) / 50)
    st.success(f"🚀 Aplicar {dose:.0f} kg/ha. Total: {sacos} sacos.")
else:
    dose, sacos = 0, 0

# --- 5. GERAR PDF ---
st.header("4️⃣ Laudo Técnico")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def cl(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, cl("CONSULTORIA AGRONÔMICA"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0); pdf.ln(20); pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, cl(f"Produtor: {produtor} | Talhão: {talhao}"), ln=True)
    pdf.cell(0, 10, cl(f"Recomendação: {dose:.0f} kg/ha de {nome_f}"), ln=True)
    return pdf.output(dest='S')

if st.button("📄 Criar Relatório"):
    try:
        laudo = gerar_pdf()
        st.download_button("⬇️ Baixar PDF", laudo, f"Laudo_{talhao}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro ao gerar: {e}")

st.caption("AgroCalc Pro | Felipe Amorim")
