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

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- 1. UPLOAD E DETECÇÃO DE ÁREAS ---
st.sidebar.header("📄 1. Subir Análise")
arquivo_pdf = st.sidebar.file_uploader("Subir PDF com múltiplas análises", type=["pdf"])

# Variáveis de controle
dados_extraidos = None
lista_lugares = []

if arquivo_pdf and PDF_DISPONIVEL:
    try:
        reader = PdfReader(arquivo_pdf)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        
        # Tenta identificar nomes de Talhões ou Áreas (Ex: Gleba, Área, Lote)
        # Se não achar nomes específicos, ele divide por blocos de profundidade
        lista_lugares = re.findall(r"(Gleba\s*\d+|[Áá]rea\s*\d+|Lote\s*\d+)", texto_completo, re.IGNORECASE)
        lista_lugares = list(set(lista_lugares)) # Remove duplicados
        
        if not lista_lugares:
            lista_lugares = ["Análise Geral 01", "Análise Geral 02"]

        st.sidebar.success(f"🔍 Encontrei {len(lista_lugares)} áreas no arquivo.")
        escolha_area = st.sidebar.selectbox("Qual área deseja carregar?", lista_lugares)
        camada = st.sidebar.radio("Qual profundidade?", ["0-20", "20-40"])

        # Função de busca refinada
        def buscar_valor(termo, texto_alvo):
            padrao = termo + r".*?(\d+[.,]?\d*)"
            match = re.search(padrao, texto_alvo, re.IGNORECASE)
            return float(match.group(1).replace(",", ".")) if match else 0.0

        # Filtra o texto baseado na área e profundidade escolhida
        bloco_area = texto_completo.split(escolha_area)[-1].split(camada)[-1]
        
        dados_extraidos = {
            "p": buscar_valor(r"F[oó]sforo", bloco_area),
            "k": buscar_valor(r"Pot[aá]ssio", bloco_area),
            "argila": buscar_valor(r"Argila", bloco_area),
            "v": buscar_valor(r"V%", bloco_area),
            "ctc": buscar_valor(r"CTC", bloco_area)
        }
    except Exception as e:
        st.sidebar.error(f"Erro ao ler PDF: {e}")

# --- 2. DADOS DA ÁREA ---
st.sidebar.header("📋 2. Configurar Área")
produtor = st.sidebar.text_input("Nome do Produtor:", "Cesário")
area_ha = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# --- 3. EXIBIÇÃO E AJUSTE DOS DADOS ---
st.header("1️⃣ Resultados da Análise")
p_ini = dados_extraidos["p"] if dados_extraidos else 0.0
k_ini = dados_extraidos["k"] if dados_extraidos else 0.0
arg_ini = dados_extraidos["argila"] if dados_extraidos else 0.0
v_ini = dados_extraidos["v"] if dados_extraidos else 0.0
ctc_ini = dados_extraidos["ctc"] if dados_extraidos else 5.0

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

# --- 4. CÁLCULOS TÉCNICOS ---
st.header("2️⃣ Planejamento Nutricional")
v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0

niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
i1, i2, i3 = st.columns(3)
n_nv = i1.selectbox("Nível N:", niveis, index=2)
p_nv = i2.selectbox("Nível P:", niveis, index=1) # Ajustado para sugerir 'Baixo' conforme foto
k_nv = i3.selectbox("Nível K:", niveis, index=2)

# Tabelas Soja/Milho
if cultura == "Soja":
    t_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    req_n, req_p, req_k = 0, t_p[p_nv], t_k[k_nv]
else:
    t_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 90, "Médio": 60, "Alto": 40, "Muito Alto": 0}
    req_n, req_p, req_k = 100, t_p[p_nv], t_k[k_nv]

# --- 5. ADUBO FORMULADO ---
st.header("3️⃣ Sugestão de Adubação")
st.info(f"Recomendação Técnica: {req_n} de N | {req_p} de P2O5 | {req_k} de K2O (kg/ha)")

f1, f2, f3, f4 = st.columns(4)
f_n = f1.number_input("N (%)", value=4.0)
f_p = f2.number_input("P (%)", value=14.0)
f_k = f3.number_input("K (%)", value=8.0)
nome_f = f4.text_input("Fórmula:", "04-14-08")

if f_p > 0:
    dose = (req_p * 100) / f_p
    total_sacos = math.ceil((dose * area_ha) / 50)
    st.success(f"🎯 Aplicar: {dose:.0f} kg/ha de {nome_f} | Total: {total_sacos} sacos.")
else:
    dose, total_sacos = 0, 0

# --- 6. GERAR PDF (CORRIGIDO) ---
def criar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def cl(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 20, cl("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), ln=True, align="C")
    
    pdf.set_text_color(0, 0, 0); pdf.ln(20); pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, cl(f"Produtor: {produtor} | Cultura: {cultura}"), ln=True)
    pdf.cell(0, 10, cl(f"Calagem: {nc:.2f} t/ha | NPK: {req_n}-{req_p}-{req_k} kg/ha"), ln=True)
    pdf.cell(0, 10, cl(f"ADUBAÇÃO: {dose:.0f} kg/ha de {nome_f} ({total_sacos} sacos)"), ln=True)
    return pdf.output(dest='S')

if st.button("📄 Gerar Relatório PDF"):
    try:
        pdf_bytes = criar_pdf()
        st.download_button("⬇️ Baixar Laudo", pdf_bytes, "Laudo_Agro.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("AgroCalc Pro | Consultor Felipe Amorim")
