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

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR ---
st.sidebar.header("📋 Dados da Área")
produtor = st.sidebar.text_input("Nome do Produtor:", "Cesário")
talhao = st.sidebar.text_input("Talhão/Gleba:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0)
cultura = st.sidebar.selectbox("Cultura de Destino:", ["Soja", "Milho"])

# --- SISTEMA DE UPLOAD ---
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
            "argila": buscar(r"Argila.*?(\d+[.,]?\d*)"),
            "v": buscar(r"V%.*?(\d+[.,]?\d*)"),
            "ctc": buscar(r"CTC.*?(\d+[.,]?\d*)")
        }
    except:
        return None

# Valores Iniciais
p_ini, k_ini, arg_ini, v_ini, ctc_ini = 0.0, 0.0, 0.0, 0.0, 5.0

if arquivo_pdf:
    if PDF_READY:
        dados = extrair_dados_pdf(arquivo_pdf)
        if dados:
            st.sidebar.success("✅ Dados extraídos do PDF!")
            p_ini, k_ini, arg_ini, v_ini, ctc_ini = dados.values()
    else:
        st.sidebar.error("⚠️ Biblioteca 'PyPDF2' não instalada. Preencha os campos manualmente abaixo.")

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
st.header("2️⃣ Calagem")
v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
total_calc = nc * area_ha
st.info(f"👉 Recomendação: {nc:.2f} t/ha | Total Gleba: {total_calc:.2f} toneladas.")

# --- 3. ESCOLHA DE NÍVEIS (N, P, K) ---
st.header("3️⃣ Interpretação e NPK")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
i1, i2, i3 = st.columns(3)
with i1: n_nivel = i1.selectbox("Nível de Nitrogênio:", niveis, index=2)
with i2: p_nivel = i2.selectbox("Nível de Fósforo:", niveis, index=2)
with i3: k_nivel = i3.selectbox("Nível de Potássio:", niveis, index=2)

# Tabelas de Recomendação
if cultura == "Soja":
    t_n = {"Muito Baixo": 20, "Baixo": 10, "Médio": 0, "Alto": 0, "Muito Alto": 0}
    t_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
else: # Milho
    t_n = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 40, "Muito Alto": 0}
    t_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 90, "Médio": 60, "Alto": 40, "Muito Alto": 0}

req_n, req_p, req_k = t_n[n_nivel], t_p[p_nivel], t_k[k_nivel]
st.success(f"📌 Necessidade: N:{req_n} | P2O5:{req_p} | K2O:{req_k} kg/ha")

# --- 4. FORMULADO ---
st.header("4️⃣ Adubo Formulado")
f1, f2, f3, f4 = st.columns(4)
with f1: f_n = f1.number_input("N (%)", value=4.0)
with f2: f_p = f2.number_input("P (%)", value=14.0)
with f3: f_k = f3.number_input("K (%)", value=8.0)
with f4: nome_f = f4.text_input("Fórmula:", "04-14-08")

if f_p > 0:
    dose = (req_p * 100) / f_p
    sacos = math.ceil((dose * area_ha) / 50)
    st.warning(f"🚀 Dose: {dose:.0f} kg/ha. Total: {sacos} sacos (50kg).")
else:
    dose, sacos = 0, 0

# --- 5. RELATÓRIO PDF ---
st.header("5️⃣ Gerar Laudo")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def cl(text): return str(text).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 20, cl("CONSULTORIA AGRONÔMICA"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 5, cl(f"Consultor: Felipe Amorim | {datetime.now().strftime('%d/%m/%Y')}"), ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, cl(f"Produtor: {produtor} | Gleba: {talhao}"), ln=True)
    pdf.cell(0, 10, cl(f"Área: {area_ha} ha | Cultura: {cultura}"), ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, cl(f"- Calagem: {nc:.2f} t/ha"), ln=True)
    pdf.cell(0, 8, cl(f"- Recomendado: {req_n}-{req_p}-{req_k} kg/ha"), ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 12, cl(f"APLICAR: {dose:.0f} kg/ha de {nome_f}"), ln=True)
    pdf.cell(0, 12, cl(f"TOTAL: {sacos} sacos de 50kg"), ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Criar Relatório Técnico"):
    try:
        pdf_bytes = gerar_pdf()
        st.download_button("⬇️ Baixar PDF Agora", pdf_bytes, f"Laudo_{talhao}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("AgroCalc Pro | Felipe Amorim")
