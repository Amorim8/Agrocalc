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

# Estilo para deixar o formulado organizado
st.markdown("""
    <style>
    .resultado-box { background-color: #e8f5e9; padding: 20px; border-radius: 10px; border: 2px solid #2e7d32; }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- BARRA LATERAL ---
st.sidebar.header("📋 Configurações")
produtor = st.sidebar.text_input("Nome do Produtor:", "Cesário")
talhao = st.sidebar.text_input("Identificação do Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (ha):", min_value=0.01, value=1.0)
cultura = st.sidebar.selectbox("Cultura de Destino:", ["Soja", "Milho"])

# SELEÇÃO DE PROFUNDIDADE (CRUCIAL PARA A EXTRAÇÃO)
st.sidebar.subheader("📍 Profundidade")
camada = st.sidebar.radio("Extrair dados de qual camada?", ["0-20", "20-40"])

st.sidebar.subheader("📄 Análise de Solo")
arquivo_pdf = st.sidebar.file_uploader("Subir PDF com as análises", type=["pdf"])

def extrair_dados_especificos(pdf, profundidade):
    try:
        reader = PdfReader(pdf)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        
        # Tenta isolar apenas a parte do texto que fala da profundidade escolhida
        partes = texto_completo.split(profundidade)
        if len(partes) > 1:
            texto_foco = partes[1] # Pega o texto logo após a menção da profundidade
        else:
            texto_foco = texto_completo

        def buscar_valor(termo):
            # Procura o termo e pega o primeiro número que aparecer depois dele
            padrao = termo + r".*?(\d+[.,]?\d*)"
            match = re.search(padrao, texto_foco, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", "."))
            return 0.0

        return {
            "p": buscar_valor(r"F[oó]sforo"),
            "k": buscar_valor(r"Pot[aá]ssio"),
            "argila": buscar_valor(r"Argila"),
            "v": buscar_valor(r"V%"),
            "ctc": buscar_valor(r"CTC")
        }
    except:
        return None

# Valores iniciais zerados
p_v, k_v, arg_v, v_v, ctc_v = 0.0, 0.0, 0.0, 0.0, 5.0

if arquivo_pdf and PDF_DISPONIVEL:
    dados = extrair_dados_especificos(arquivo_pdf, camada)
    if dados:
        st.sidebar.success(f"✅ Dados da camada {camada} cm identificados!")
        p_v, k_v, arg_v, v_v, ctc_v = dados.values()

# --- 1. DADOS DA ANÁLISE ---
st.header(f"1️⃣ Resultados da Análise ({camada} cm)")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³):", value=p_v, key="p_solo")
    k_solo = st.number_input("Potássio (cmolc/dm³):", value=k_v, key="k_solo")
with col2:
    argila = st.number_input("Argila (% ou g/kg):", value=arg_v, key="argila")
    v_atual = st.number_input("V% Atual:", value=v_v, key="v_atual")
with col3:
    ctc = st.number_input("CTC Total:", value=ctc_v, key="ctc")
    prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# --- 2. CÁLCULO DE CALAGEM ---
v_alvo = 70.0 if cultura == "Soja" else 60.0
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
total_calc = nc * area_ha

# --- 3. RECOMENDAÇÃO TÉCNICA (NÍVEIS) ---
st.header("2️⃣ Necessidade Nutricional")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
i1, i2, i3 = st.columns(3)
with i1: n_nv = i1.selectbox("Nível Nitrogênio:", niveis, index=2)
with i2: p_nv = i2.selectbox("Nível Fósforo:", niveis, index=2)
with i3: k_nv = i3.selectbox("Nível Potássio:", niveis, index=2)

if cultura == "Soja":
    t_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    req_n, req_p, req_k = 0, t_p[p_nv], t_k[k_nv]
else:
    t_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    t_k = {"Muito Baixo": 120, "Baixo": 90, "Médio": 60, "Alto": 40, "Muito Alto": 0}
    req_n, req_p, req_k = 100, t_p[p_nv], t_k[k_nv]

# --- 4. ADUBAÇÃO FORMULADA ---
st.header("3️⃣ Planejamento de Adubação")
st.markdown('<div class="resultado-box">', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
with f1: f_n = st.number_input("N no Adubo (%)", value=4.0)
with f2: f_p = st.number_input("P no Adubo (%)", value=14.0)
with f3: f_k = st.number_input("K no Adubo (%)", value=8.0)
with f4: nome_f = st.text_input("Nome Comercial:", "04-14-08")

if f_p > 0:
    dose_ha = (req_p * 100) / f_p
    total_geral = math.ceil((dose_ha * area_ha) / 50)
    st.markdown(f"### ✅ Recomendação: **{dose_ha:.0f} kg/ha** de {nome_f}")
    st.markdown(f"### 📦 Logística: **{total_geral} sacos** de 50kg para a área total.")
else:
    dose_ha, total_geral = 0, 0
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. GERADOR DE RELATÓRIO PDF ---
def gerar_laudo_tecnico():
    pdf = FPDF()
    pdf.add_page()
    def cl(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho Profissional
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 20, cl("LAUDO DE RECOMENDAÇÃO AGRONÔMICA"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 5, cl(f"Consultor: Felipe Amorim | Data: {datetime.now().strftime('%d/%m/%Y')}"), ln=True, align="C")

    # Conteúdo
    pdf.set_text_color(0, 0, 0); pdf.ln(20); pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, cl(f"PRODUTOR: {produtor}"), ln=True)
    pdf.cell(0, 10, cl(f"TALHÃO: {talhao} | ÁREA: {area_ha} ha | CULTURA: {cultura}"), ln=True)
    pdf.cell(0, 10, cl(f"ANÁLISE CONSIDERADA: Camada de {camada} cm"), ln=True)
    pdf.ln(5); pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    
    pdf.ln(5); pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, cl("RECOMENDAÇÕES FINAIS:"), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, cl(f"- Calagem: {nc:.2f} toneladas por hectare."), ln=True)
    pdf.cell(0, 8, cl(f"- Necessidade NPK: {req_n} de N | {req_p} de P2O5 | {req_k} de K2O (kg/ha)."), ln=True)
    pdf.ln(5); pdf.set_font("Arial", "B", 14); pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, cl(f"ADUBAÇÃO SUGERIDA: {dose_ha:.0f} kg/ha de {nome_f}"), ln=True)
    pdf.cell(0, 10, cl(f"TOTAL PARA A ÁREA: {total_geral} sacos de 50kg"), ln=True)

    return pdf.output(dest='S')

st.header("4️⃣ Finalizar")
if st.button("📄 Gerar Laudo em PDF"):
    try:
        conteudo_pdf = gerar_laudo_tecnico()
        st.download_button("⬇️ Baixar Laudo Completo", conteudo_pdf, f"Laudo_{produtor}_{talhao}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro ao criar o PDF: {e}")

st.caption("AgroCalc Pro - Sistema de Apoio Felipe Amorim")
