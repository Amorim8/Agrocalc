import streamlit as st
from fpdf import FPDF
import math
import re
from datetime import datetime

# ---------------- CONFIGURAÇÃO INICIAL ----------------
st.set_page_config(page_title="Consultoria Agronômica - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- BARRA LATERAL (SIDEBAR) ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente Exemplo")
talhao = st.sidebar.text_input("Identificação do Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0, step=0.1)
cultura = st.sidebar.selectbox("Cultura de Destino:", ["Soja", "Milho"])

# Sistema de Upload (Protegido contra erros de biblioteca)
st.sidebar.subheader("📄 Importar Análise")
arquivo_pdf = st.sidebar.file_uploader("Enviar PDF da Análise", type=["pdf"])

# ---------------- FUNÇÃO DE LEITURA (VERSÃO SEGURA) ----------------
def processar_pdf(arquivo):
    try:
        from PyPDF2 import PdfReader
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
    except ImportError:
        st.sidebar.error("Erro: Instale 'PyPDF2' para usar o upload.")
        return None
    except Exception:
        return None

# Valores Iniciais
p_ini, k_ini, arg_ini, v_ini, ctc_ini = 0.0, 0.0, 0.0, 0.0, 5.0

if arquivo_pdf:
    dados = processar_pdf(arquivo_pdf)
    if dados:
        st.sidebar.success("✅ Dados carregados!")
        p_ini, k_ini, arg_ini, v_ini, ctc_ini = dados.values()

# ---------------- 1️⃣ ANÁLISE DE SOLO ----------------
st.header("1️⃣ Análise de Solo")
c1, c2, c3 = st.columns(3)

with c1:
    p_solo = c1.number_input("Fósforo (mg/dm³):", value=p_ini)
    k_solo = c1.number_input("Potássio (cmolc/dm³):", value=k_ini)
with c2:
    argila_solo = c2.number_input("Teor de Argila (g/kg):", value=arg_ini)
    v_solo = c2.number_input("V% Atual (Saturação):", value=v_ini)
with c3:
    ctc_solo = c3.number_input("CTC Total:", value=ctc_ini)
    prnt_calc = c3.number_input("PRNT do Calcário (%):", value=80.0)

# ---------------- 2️⃣ CALAGEM (AUTOMÁTICO) ----------------
st.header("2️⃣ Necessidade de Calagem")
v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_solo) * ctc_solo) / prnt_calc) if prnt_calc > 0 else 0.0
total_calc = nc * area_ha

col_c1, col_c2 = st.columns(2)
col_c1.metric("Calcário (t/ha)", f"{nc:.2f}")
col_c2.metric("Total para a Área (t)", f"{total_calc:.2f}")

# ---------------- 3️⃣ ADUBAÇÃO ----------------
st.header("3️⃣ Recomendação NPK")
col_n1, col_n2, col_n3 = st.columns(3)

with col_n1:
    nivel_p = col_n1.selectbox("Nível de Fósforo:", ["Baixo", "Médio", "Alto"], index=1)
with col_n2:
    formula = col_n2.text_input("Fórmula do Adubo:", "04-14-08")
with col_n3:
    p_na_formula = col_n3.number_input("% de P na Fórmula:", value=14.0)

# Cálculo Simples de Dose
req_p2o5 = 80.0 if cultura == "Soja" else 100.0
dose_ha = (req_p2o5 * 100) / p_na_formula if p_na_formula > 0 else 0.0
sacos = math.ceil((dose_ha * area_ha) / 50)

st.success(f"Dose: {dose_ha:.0f} kg/ha | Total: {sacos} sacos de 50kg.")

# ---------------- 4️⃣ RELATÓRIO PDF ----------------
st.header("4️⃣ Gerar Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def t(texto): return str(texto).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 20, t("CONSULTORIA AGRONÔMICA"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 5, t(f"Consultor: Felipe Amorim | {datetime.now().strftime('%d/%m/%Y')}"), ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, t(f"Produtor: {cliente} | Talhão: {talhao}"), ln=True)
    pdf.cell(190, 8, t(f"Área: {area_ha} ha | Cultura: {cultura}"), ln=True)
    pdf.ln(5)
    pdf.cell(190, 8, t(f"Recomendação Calagem: {nc:.2f} t/ha"), ln=True)
    pdf.cell(190, 8, t(f"Dose Adubo: {dose_ha:.0f} kg/ha de {formula}"), ln=True)
    pdf.cell(190, 8, t(f"Total de Sacos: {sacos}"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar Laudo"):
    try:
        pdf_data = gerar_pdf()
        st.download_button("⬇️ Baixar PDF", pdf_data, f"Relatorio_{talhao}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
