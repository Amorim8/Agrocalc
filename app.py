import streamlit as st
from fpdf import FPDF
import math
import re
from datetime import datetime

# --- TENTATIVA DE IMPORTAR PYPDF2 ---
try:
    from PyPDF2 import PdfReader
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

# Estilo para organizar o formulado
st.markdown("""
    <style>
    .metric-container { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #228B22; }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- BARRA LATERAL ---
st.sidebar.header("📋 Cadastro e Profundidade")
produtor = st.sidebar.text_input("Produtor:", "Cesário")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área (ha):", min_value=0.01, value=1.0)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# OPÇÃO DE PROFUNDIDADE
camada = st.sidebar.radio("Selecione a Profundidade da Análise:", ["0-20 cm", "20-40 cm"])

st.sidebar.subheader("📄 Upload da Análise")
arquivo_pdf = st.sidebar.file_uploader("Enviar PDF", type=["pdf"])

def extrair_dados(pdf, prof):
    try:
        reader = PdfReader(pdf)
        texto = ""
        for page in reader.pages: texto += page.extract_text()
        
        # Busca específica baseada na profundidade selecionada
        # (Aqui o código procura o bloco da profundidade antes de pegar os números)
        bloco = texto.split(prof)[1] if prof in texto else texto
        
        def pegar(regex):
            match = re.search(regex, bloco, re.IGNORECASE)
            return float(match.group(1).replace(",", ".")) if match else 0.0

        return {
            "p": pegar(r"F[oó]sforo.*?(\d+[.,]?\d*)"),
            "k": pegar(r"Pot[aá]ssio.*?(\d+[.,]?\d*)"),
            "argila": pegar(r"Argila.*?(\d+[.,]?\d*)"),
            "v": pegar(r"V%.*?(\d+[.,]?\d*)"),
            "ctc": pegar(r"CTC.*?(\d+[.,]?\d*)")
        }
    except: return None

# Valores Iniciais
p_ini, k_ini, arg_ini, v_ini, ctc_ini = 0.0, 0.0, 0.0, 0.0, 5.0

if arquivo_pdf and PDF_DISPONIVEL:
    dados = extrair_dados(arquivo_pdf, camada)
    if dados:
        st.sidebar.success(f"✅ Dados {camada} extraídos!")
        p_ini, k_ini, arg_ini, v_ini, ctc_ini = dados.values()

# --- 1. ENTRADA DE DADOS ---
st.header(f"1️⃣ Resultados da Análise ({camada})")
c1, c2, c3 = st.columns(3)
with c1:
    p_solo = st.number_input("Fósforo (mg/dm³):", value=p_ini)
    k_solo = st.number_input("Potássio (cmolc/dm³):", value=k_ini)
with c2:
    argila = st.number_input("Argila (% ou g/kg):", value=arg_ini)
    v_atual = st.number_input("V% Atual:", value=v_ini)
with c3:
    ctc = st.number_input("CTC Total:", value=ctc_ini)
    prnt = st.number_input("PRNT (%):", value=80.0)

# --- 2. CALAGEM ---
v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
total_calc = nc * area_ha

# --- 3. RECOMENDAÇÃO NPK ---
st.header("2️⃣ Níveis e Necessidade Técnica")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
i1, i2, i3 = st.columns(3)
n_nv = i1.selectbox("Nível Nitrogênio:", niveis, index=2)
p_nv = i2.selectbox("Nível Fósforo:", niveis, index=2)
k_nv = i3.selectbox("Nível Potássio:", niveis, index=2)

# Tabelas (Kg/ha)
if cultura == "Soja":
    t_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    req_n, req_p, req_k = 0, t_p[p_nv], t_k[k_nv]
else:
    t_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 90, "Médio": 60, "Alto": 40, "Muito Alto": 0}
    req_n, req_p, req_k = 100, t_p[p_nv], t_k[k_nv]

# --- 4. ADUBO FORMULADO (ORGANIZADO) ---
st.header("3️⃣ Calculadora de Adubo Formulado")
with st.container():
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    with f1: f_n = st.number_input("N (%)", value=4.0)
    with f2: f_p = st.number_input("P (%)", value=14.0)
    with f3: f_k = st.number_input("K (%)", value=8.0)
    with f4: nome_adubo = st.text_input("Fórmula:", "04-14-08")
    
    if f_p > 0:
        dose = (req_p * 100) / f_p
        sacos = math.ceil((dose * area_ha) / 50)
        st.markdown(f"### 🎯 Resultado: **{dose:.0f} kg/ha** de {nome_adubo}")
        st.markdown(f"### 📦 Total: **{sacos} sacos** para a área de {area_ha} ha")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. GERAR PDF ---
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def cl(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, cl("CONSULTORIA AGRONÔMICA - FELIPE AMORIM"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0); pdf.ln(20); pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, cl(f"Produtor: {produtor} | Talhão: {talhao} | Profundidade: {camada}"), ln=True)
    pdf.cell(0, 10, cl(f"Calagem: {nc:.2f} t/ha | Recomendação NPK: {req_n}-{req_p}-{req_k}"), ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 12, cl(f"ADUBAÇÃO: {dose:.0f} kg/ha de {nome_adubo} ({sacos} sacos total)"), ln=True)
    return pdf.output(dest='S')

if st.button("📄 Gerar Laudo Final"):
    try:
        laudo_out = gerar_pdf()
        st.download_button("⬇️ Baixar Relatório PDF", laudo_out, f"Laudo_{talhao}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro ao gerar: {e}")

st.caption("AgroCalc Pro | Desenvolvido para Felipe Amorim")
