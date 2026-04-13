import streamlit as st
from fpdf import FPDF
import math
import re
from datetime import datetime

# Tenta importar a biblioteca de PDF para o Upload
try:
    from PyPDF2 import PdfReader
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

# ---------------- CONFIGURAÇÃO INICIAL ----------------
st.set_page_config(page_title="Consultoria Agronômica - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- BARRA LATERAL (SIDEBAR) ----------------
st.sidebar.header("📋 Informações da Área")

produtor = st.sidebar.text_input("Nome do Produtor:", "Cliente Exemplo")
talhao = st.sidebar.text_input("Identificação do Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0, step=0.1)
cultura = st.sidebar.selectbox("Cultura de Destino:", ["Soja", "Milho"])

# Sistema de Upload na Sidebar
st.sidebar.subheader("📄 Importar Análise")
if PDF_DISPONIVEL:
    arquivo_pdf = st.sidebar.file_uploader("Enviar PDF da Análise", type=["pdf"])
else:
    st.sidebar.warning("⚠️ Biblioteca de leitura de PDF não instalada. Preencha manualmente.")
    arquivo_pdf = None

# ---------------- FUNÇÃO DE LEITURA ----------------
def processar_pdf(arquivo):
    try:
        leitor = PdfReader(arquivo)
        texto_completo = ""
        for pagina in leitor.pages:
            texto_completo += pagina.extract_text()
        
        def extrair(regex):
            match = re.search(regex, texto_completo, re.IGNORECASE)
            return float(match.group(1).replace(",", ".")) if match else 0.0

        return {
            "p": extrair(r"F[oó]sforo.*?(\d+[.,]?\d*)"),
            "k": extrair(r"Pot[aá]ssio.*?(\d+[.,]?\d*)"),
            "argila": extrair(r"Argila.*?(\d+[.,]?\d*)"),
            "v": extrair(r"V%.*?(\d+[.,]?\d*)"),
            "ctc": extrair(r"CTC.*?(\d+[.,]?\d*)")
        }
    except:
        return None

# Valores Iniciais (resetam se houver upload)
p_ini, k_ini, arg_ini, v_ini, ctc_ini = 0.0, 0.0, 0.0, 0.0, 5.0

if arquivo_pdf:
    dados_extraidos = processar_pdf(arquivo_pdf)
    if dados_extraidos:
        st.sidebar.success("✅ Dados carregados!")
        p_ini, k_ini, arg_ini, v_ini, ctc_ini = dados_extraidos.values()

# ---------------- 1️⃣ CORPO: ANÁLISE DE SOLO ----------------
st.header("1️⃣ Análise de Solo")
col1, col2, col3 = st.columns(3)

with col1:
    p_solo = st.number_input("Fósforo (mg/dm³):", value=p_ini)
    k_solo = st.number_input("Potássio (cmolc/dm³):", value=k_ini)
with col2:
    argila_solo = st.number_input("Teor de Argila (g/kg):", value=arg_ini)
    v_solo = st.number_input("V% Atual (Saturação):", value=v_ini)
with col3:
    ctc_solo = st.number_input("CTC Total:", value=ctc_ini)
    prnt_calcario = st.number_input("PRNT do Calcário (%):", value=80.0)

# ---------------- 2️⃣ CORPO: CALAGEM ----------------
st.header("2️⃣ Necessidade de Calagem")
v_alvo = 70.0 if cultura == "Soja" else 60.0

nc = max(0.0, ((v_alvo - v_solo) * ctc_solo) / prnt_calcario) if prnt_calcario > 0 else 0.0
total_calcario = nc * area_ha

c_calc1, c_calc2 = st.columns(2)
c_calc1.metric("Calcário (t/ha)", f"{nc:.2f}")
c_calc2.metric("Total para a Área (t)", f"{total_calcario:.2f}")

# ---------------- 3️⃣ CORPO: ADUBAÇÃO ----------------
st.header("3️⃣ Recomendação NPK")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]

# Tabela simplificada para cálculo da dose
tabela_p2o5 = {"Soja": 80.0, "Milho": 100.0}

col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    nivel_selecionado = st.selectbox("Nível de Fósforo:", niveis, index=2)
with col_n2:
    formula_adubo = st.text_input("Fórmula do Adubo:", "04-14-08")
with col_n3:
    p_na_formula = st.number_input("% de P na Fórmula (ex: 14):", value=14.0)

# Cálculos Adubo
req_p2o5 = tabela_p2o5[cultura]
dose_ha = (req_p2o5 * 100) / p_na_formula if p_na_formula > 0 else 0.0
sacos_total = math.ceil((dose_ha * area_ha) / 50)

st.success(f"Dose Recomendada: {dose_ha:.0f} kg/ha de {formula_adubo}. Total: {sacos_total} sacos.")

# ---------------- 4️⃣ GERAR RELATÓRIO PDF ----------------
st.header("4️⃣ Relatório Técnico")

def gerar_pdf_final():
    pdf = FPDF()
    pdf.add_page()
    
    def formatar(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho Verde
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 20, formatar("CONSULTORIA AGRONÔMICA"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 5, formatar(f"Consultor: Felipe Amorim | Data: {datetime.now().strftime('%d/%m/%Y')}"), ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)

    # Seção 1: Área
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, formatar("1. DADOS DA ÁREA"), ln=True, fill=False)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, formatar(f"Produtor: {produtor} | Talhão: {talhao}"), ln=True)
    pdf.cell(190, 7, formatar(f"Área: {area_ha} ha | Cultura: {cultura}"), ln=True)
    pdf.ln(5)

    # Seção 2: Calagem
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, formatar("2. RECOMENDAÇÃO DE CALAGEM"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, formatar(f"Necessidade: {nc:.2f} t/ha | Total Gleba: {total_calcario:.2f} toneladas"), ln=True)
    pdf.ln(5)

    # Seção 3: Adubação
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, formatar("3. RECOMENDAÇÃO DE ADUBAÇÃO"), ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, formatar(f"APLICAR: {dose_ha:.0f} kg/ha de {formula_adubo}"), ln=True)
    pdf.cell(190, 10, formatar(f"TOTAL PARA A ÁREA: {sacos_total} sacos (50kg)"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar Laudo Técnico"):
    try:
        laudo_pdf = gerar_pdf_final()
        st.download_button("⬇️ Baixar
