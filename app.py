import streamlit as st
from fpdf import FPDF
import math
import re

# --- VERIFICAÇÃO DE BIBLIOTECA ---
try:
    from PyPDF2 import PdfReader
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- 1. LÓGICA DE EXTRAÇÃO DE DADOS ---
st.sidebar.header("📄 Importar Análise")
arquivo_pdf = st.sidebar.file_uploader("Subir PDF da Análise", type=["pdf"])

# Dicionário para guardar os dados que serão exibidos nos campos
val = {"p": 0.0, "k": 0.0, "arg": 0.0, "v": 0.0, "ctc": 5.0}

if arquivo_pdf and PDF_DISPONIVEL:
    try:
        reader = PdfReader(arquivo_pdf)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        
        # 1. Identifica os nomes das áreas/glebas no PDF para você escolher
        areas = re.findall(r"(?:Gleba|Lote|Talh[ã]o|Área|Amostra)\s*[:\-]?\s*([A-Za-z0-9\s]+)", texto_completo, re.IGNORECASE)
        areas = list(set([a.strip() for a in areas if len(a.strip()) > 1]))
        
        if not areas:
            areas = ["Análise Principal"]
        
        escolha = st.sidebar.selectbox("Selecione a Área/Gleba do PDF:", areas)
        camada = st.sidebar.radio("Profundidade:", ["0-20", "20-40"])

        # 2. Isola o texto da área e profundidade escolhida
        bloco_busca = texto_completo.split(escolha)[-1]
        
        # 3. Função "Caçadora" de números
        def capturar(label, texto):
            # Procura a palavra e pega o primeiro número com vírgula ou ponto depois dela
            padrao = label + r".*?(\d+[.,]?\d*)"
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", "."))
            return 0.0

        val["p"] = capturar(r"F[oó]sforo", bloco_busca)
        val["k"] = capturar(r"Pot[aá]ssio", bloco_busca)
        val["arg"] = capturar(r"Argila", bloco_busca)
        val["v"] = capturar(r"V%", bloco_busca)
        val["ctc"] = capturar(r"CTC", bloco_busca)
        
        st.sidebar.success(f"✅ Dados de {escolha} extraídos!")
    except Exception as e:
        st.sidebar.error(f"Erro na leitura: {e}")

# --- 2. EXIBIÇÃO DOS DADOS (Onde os dados extraídos aparecem) ---
st.header("1️⃣ Resultados da Análise de Solo")
c1, c2, c3 = st.columns(3)
with c1:
    p_solo = st.number_input("Fósforo (mg/dm³):", value=val["p"])
    k_solo = st.number_input("Potássio (cmolc/dm³):", value=val["k"])
with c2:
    argila = st.number_input("Argila (%):", value=val["arg"])
    v_atual = st.number_input("V% Atual:", value=val["v"])
with c3:
    ctc = st.number_input("CTC Total:", value=val["ctc"])
    prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# --- 3. CÁLCULO DE CALAGEM ---
st.header("2️⃣ Recomendação de Calagem")
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])
area_ha = st.sidebar.number_input("Área (ha):", value=1.0)

v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
total_calcario = nc * area_ha

col_res1, col_res2 = st.columns(2)
col_res1.metric("Necessidade (t/ha)", f"{nc:.2f}")
col_res2.metric("Total para a Área (t)", f"{total_calcario:.2f}")

# --- 4. ADUBAÇÃO NPK ---
st.header("3️⃣ Planejamento de Adubação")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto"]
i1, i2, i3 = st.columns(3)
n_nv = i1.selectbox("Nível N:", niveis, index=1)
p_nv = i2.selectbox("Nível P:", niveis, index=1)
k_nv = i3.selectbox("Nível K:", niveis, index=1)

# Lógica de Recomendação Simplificada
if cultura == "Soja":
    req_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60}[p_nv]
    req_n, req_k = 0, 80
else:
    req_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60}[p_nv]
    req_n, req_k = 100, 60

# Escolha do Adubo
st.subheader("Cálculo do Formulado")
f1, f2, f3, f4 = st.columns(4)
f_p = f2.number_input("P na Fórmula (%)", value=14.0)
nome_f = f4.text_input("Fórmula Comercial:", "04-14-08")

if f_p > 0:
    dose = (req_p * 100) / f_p
    sacos = math.ceil((dose * area_ha) / 50)
    st.success(f"🎯 Aplicar {dose:.0f} kg/ha de {nome_f} | Total: {sacos} sacos.")

# --- 5. GERAÇÃO DE PDF ---
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def cl(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, cl("LAUDO TÉCNICO - FELIPE AMORIM"), ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, cl(f"Cultura: {cultura} | Área: {area_ha} ha"), ln=True)
    pdf.cell(0, 10, cl(f"Calagem Sugerida: {nc:.2f} t/ha"), ln=True)
    pdf.cell(0, 10, cl(f"Adubação Sugerida: {dose:.0f} kg/ha de {nome_f}"), ln=True)
    return pdf.output(dest='S')

if st.button("📄 Gerar e Baixar Laudo"):
    try:
        pdf_out = gerar_pdf()
        st.download_button("⬇️ Clique para Baixar PDF", pdf_out, "Laudo_Felipe_Amorim.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("AgroCalc Pro | Sistema desenvolvido para Felipe Amorim")
