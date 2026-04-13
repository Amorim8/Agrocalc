import streamlit as st
from fpdf import FPDF
import math
import re
from datetime import datetime

# Tenta importar PyPDF2; se não estiver instalado, o sistema avisa mas não trava
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ---------------- CONFIGURAÇÃO DO SISTEMA ----------------
st.set_page_config(page_title="Consultoria Agronômica - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- BARRA LATERAL (SIDEBAR) ----------------
st.sidebar.header("📋 Informações da Área")

produtor = st.sidebar.text_input("Nome do Produtor:", "CESARIO")
talhao = st.sidebar.text_input("Identificação do Talhão:", "Gleba 01")
area_total = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0, step=0.1)
cultura_destino = st.sidebar.selectbox("Cultura de Destino:", ["Soja", "Milho"])

# Importar Análise Automática
st.sidebar.subheader("📄 Importar Análise")
if PDF_SUPPORT:
    uploaded_file = st.sidebar.file_uploader("Enviar PDF da Análise", type=["pdf"])
else:
    st.sidebar.warning("⚠️ Biblioteca PyPDF2 não encontrada. O preenchimento deve ser manual.")
    uploaded_file = None

# ---------------- FUNÇÃO DE EXTRAÇÃO ----------------
def extrair_dados(file):
    try:
        reader = PdfReader(file)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
        
        def buscar(padrao):
            m = re.search(padrao, texto, re.IGNORECASE)
            return float(m.group(1).replace(",", ".")) if m else 0.0

        return {
            "p": buscar(r"F[oó]sforo.*?(\d+[.,]?\d*)"),
            "k": buscar(r"Pot[aá]ssio.*?(\d+[.,]?\d*)"),
            "argila": buscar(r"Argila.*?(\d+[.,]?\d*)"),
            "v": buscar(r"V%.*?(\d+[.,]?\d*)"),
            "ctc": buscar(r"CTC.*?(\d+[.,]?\d*)"),
        }
    except:
        return None

# Valores Iniciais
p_ini, k_ini, arg_ini, v_ini, ctc_ini = 0.0, 0.0, 0.0, 0.0, 5.0

if uploaded_file:
    dados = extrair_dados(uploaded_file)
    if dados:
        st.sidebar.success("✅ Dados carregados!")
        p_ini, k_ini, arg_ini, v_ini, ctc_ini = dados["p"], dados["k"], dados["argila"], dados["v"], dados["ctc"]

# ---------------- 1️⃣ ANÁLISE DO SOLO (CORPO) ----------------
st.header("1️⃣ Análise de Solo (Entrada de Dados)")
c1, c2, c3 = st.columns(3)

with c1:
    fosforo = st.number_input("Fósforo (mg/dm³):", value=p_ini)
    potassio = st.number_input("Potássio (cmolc/dm³):", value=k_ini)
with c2:
    teor_argila = st.number_input("Teor de Argila (g/kg):", value=arg_ini)
    v_atual = st.number_input("V% Atual (Saturação):", value=v_ini)
with c3:
    ctc_total = st.number_input("CTC Total (cmolc/dm³):", value=ctc_ini)
    prnt_calc = st.number_input("PRNT do Calcário (%):", value=80.0)

# ---------------- 2️⃣ CALAGEM (AUTOMÁTICO) ----------------
st.header("2️⃣ Necessidade de Calagem")
v_alvo = 70.0 if cultura_destino == "Soja" else 60.0

nc = max(0.0, ((v_alvo - v_atual) * ctc_total) / prnt_calc) if prnt_calc > 0 else 0.0
total_ton = nc * area_total

col_c1, col_c2 = st.columns(2)
col_c1.metric("Calcário (t/ha)", f"{nc:.2f}")
col_c2.metric("Total para a Gleba (t)", f"{total_ton:.2f}")

# ---------------- 3️⃣ ADUBAÇÃO E INTERPRETAÇÃO ----------------
st.header("3️⃣ Recomendação de NPK")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]

# Tabela simplificada de exemplo
tabela_p = {"Soja": 80.0, "Milho": 90.0} # kg/ha para nível Médio
tabela_k = {"Soja": 70.0, "Milho": 80.0} # kg/ha para nível Médio

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1: nivel_p = st.selectbox("Nível Fósforo:", niveis, index=2)
with col_r2: nivel_k = st.selectbox("Nível Potássio:", niveis, index=2)
with col_r3: adubo_formula = st.text_input("Fórmula Sugerida:", "04-14-08")

req_p = tabela_p[cultura_destino]
req_k = tabela_k[cultura_destino]
req_n = 0.0 if cultura_destino == "Soja" else 80.0

st.success(f"Recomendação Final: N:{req_n} | P₂O₅:{req_p} | K₂O:{req_k} kg/ha")

# ---------------- 4️⃣ ADUBO FORMULADO ----------------
st.header("4️⃣ Cálculo de Quantidade")
perc_p_adubo = 14.0 # Baseado no formulado 04-14-08 como exemplo
dose_kg_ha = (req_p * 100) / perc_p_adubo if perc_p_adubo > 0 else 0.0
total_sacos = math.ceil((dose_kg_ha * area_total) / 50)

st.warning(f"👉 Aplicar {dose_kg_ha:.0f} kg/ha de {adubo_formula}. Total: {total_sacos} sacos.")

# ---------------- 5️⃣ RELATÓRIO PDF ----------------
st.header("5️⃣ Laudo Técnico")

def gerar_laudo():
    pdf = FPDF()
    pdf.add_page()
    def t(texto): return str(texto).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho Profissional
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, t("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 5, t(f"Consultor: Felipe Amorim | {datetime.now().strftime('%d/%m/%Y')}"), align="C", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)

    # Sessões
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, t("1. DADOS DA UNIDADE DE PRODUÇÃO"), ln=True, fill=False)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, t(f"Produtor: {produtor} | Talhão: {talhao}"), ln=True)
    pdf.cell(190, 7, t(f"Área: {area_total} ha | Cultura: {cultura_destino}"), ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, t("2. NECESSIDADE DE CALAGEM"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, t(f"Dose Recomendada: {nc:.2f} t/ha | Total Gleba: {total_ton:.2f} toneladas"), ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, t("3. ADUBAÇÃO FORMULADA SUGERIDA"), ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, t(f"DOSE: {dose_kg_ha:.0f} kg/ha de {adubo_formula}"), ln=True)
    pdf.cell(190, 10, t(f"TOTAL PARA A ÁREA: {total_sacos} sacos de 50kg"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar Laudo Técnico"):
    try:
        laudo
