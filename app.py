import streamlit as st
from fpdf import FPDF
import math
import re
from datetime import datetime

# --- TENTATIVA DE IMPORTAR BIBLIOTECAS ---
try:
    from PyPDF2 import PdfReader
    PDF_OK = True
except:
    PDF_OK = False

st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- 1. LÓGICA DE EXTRAÇÃO ---
st.sidebar.header("📄 1. Arquivo de Análise")
arquivo_pdf = st.sidebar.file_uploader("Subir PDF com as análises", type=["pdf"])

dados_finais = {"p": 0.0, "k": 0.0, "arg": 0.0, "v": 0.0, "ctc": 5.0}

if arquivo_pdf and PDF_OK:
    reader = PdfReader(arquivo_pdf)
    texto_total = ""
    paginas_texto = []
    for page in reader.pages:
        t = page.extract_text()
        texto_total += t + "\n"
        paginas_texto.append(t)
    
    # Identifica possíveis nomes de áreas/análises
    areas_encontradas = re.findall(r"(?:Identifica[çã]o|Gleba|Talh[ã]o|Lote|Amostra):\s*([A-Za-z0-9\s\-]+)", texto_total, re.IGNORECASE)
    if not areas_encontradas:
        areas_encontradas = ["Análise Encontrada 01", "Análise Encontrada 02"]
    
    area_selecionada = st.sidebar.selectbox("Escolha qual área carregar:", list(set(areas_encontradas)))
    camada = st.sidebar.radio("Qual profundidade?", ["0-20", "20-40"])

    # Busca os valores no bloco de texto específico
    def extrair(termo, txt):
        match = re.search(termo + r".*?(\d+[.,]?\d*)", txt, re.IGNORECASE)
        return float(match.group(1).replace(",", ".")) if match else 0.0

    # Pega o texto referente à área escolhida
    bloco = texto_total.split(area_selecionada)[-1]
    dados_finais = {
        "p": extrair(r"F[oó]sforo", bloco),
        "k": extrair(r"Pot[aá]ssio", bloco),
        "arg": extrair(r"Argila", bloco),
        "v": extrair(r"V%", bloco),
        "ctc": extrair(r"CTC", bloco)
    }
    st.sidebar.success(f"✅ {area_selecionada} carregada!")

# --- 2. PAINEL DE DADOS ---
st.header("1️⃣ Dados do Solo")
c1, c2, c3 = st.columns(3)
with c1:
    p_solo = st.number_input("Fósforo (mg/dm³):", value=dados_finais["p"])
    k_solo = st.number_input("Potássio (cmolc/dm³):", value=dados_finais["k"])
with c2:
    argila = st.number_input("Argila (%):", value=dados_finais["arg"])
    v_atual = st.number_input("V% Atual:", value=dados_finais["v"])
with c3:
    ctc = st.number_input("CTC Total:", value=dados_finais["ctc"])
    prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# --- 3. CALAGEM (ADICIONADO) ---
st.header("2️⃣ Necessidade de Calagem")
col_cal1, col_cal2 = st.columns(2)
area_total = st.sidebar.number_input("Área (ha):", value=1.0)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
calc_total = nc * area_total

with col_cal1:
    st.metric("Necessidade (t/ha)", f"{nc:.2f}")
with col_cal2:
    st.metric("Total para a Área (t)", f"{calc_total:.2f}")

# --- 4. ADUBAÇÃO ---
st.header("3️⃣ Planejamento NPK")
i1, i2, i3 = st.columns(3)
n_nv = i1.selectbox("Nível N:", ["Baixo", "Médio", "Alto"], index=1)
p_nv = i2.selectbox("Nível P:", ["Muito Baixo", "Baixo", "Médio", "Alto"], index=1)
k_nv = i3.selectbox("Nível K:", ["Baixo", "Médio", "Alto"], index=1)

# Tabelas Simplificadas
if cultura == "Soja":
    req_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60}[p_nv]
    req_n, req_k = 0, 80
else:
    req_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60}[p_nv]
    req_n, req_k = 100, 60

st.info(f"Recomendação: {req_n}N - {req_p}P - {req_k}K")

# Cálculo do Adubo
f1, f2, f3, f4 = st.columns(4)
f_p = f2.number_input("P na Fórmula (%)", value=14.0)
nome_f = f4.text_input("Fórmula:", "04-14-08")

if f_p > 0:
    dose = (req_p * 100) / f_p
    sacos = math.ceil((dose * area_total) / 50)
    st.success(f"🚀 Aplicar {dose:.0f} kg/ha | Total: {sacos} sacos.")

# --- 5. PDF ---
def gerar_laudo():
    pdf = FPDF()
    pdf.add_page()
    def cl(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, cl("LAUDO AGRONÔMICO - FELIPE AMORIM"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, cl(f"Cultura: {cultura} | Área: {area_total} ha"), ln=True)
    pdf.cell(0, 10, cl(f"Calagem: {nc:.2f} t/ha"), ln=True)
    pdf.cell(0, 10, cl(f"Adubação: {dose:.0f} kg/ha de {nome_f}"), ln=True)
    return pdf.output(dest='S')

if st.button("📄 Baixar Relatório"):
    st.download_button("Clique aqui para baixar", gerar_laudo(), "Relatorio.pdf", "application/pdf")
