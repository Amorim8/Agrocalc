import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1a1c23 !important;
        border: 1px solid #2e3139;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745 !important;
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Configurações")
    cliente = st.text_input("👨‍🌾 Nome do Cliente:", "Produtor Exemplo")
    fazenda = st.text_input("🏠 Fazenda:", "Nome da Propriedade")
    talhao = st.text_input("📍 Talhão:", "Gleba 01")
    municipio = st.text_input("🏙️ Município:", "Cidade")
    estado = st.selectbox("🌎 Estado:", ["GO", "MT", "MS", "MG", "PR", "SP", "BA", "TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    
    meta_ton = st.select_slider(
        "🎯 Meta de Produtividade (t/ha):", 
        options=[float(i/2) for i in range(2, 31)], 
        value=4.0 if cultura == "Soja" else 8.0
    )

# ---------------- CABEÇALHO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {datetime.now().strftime('%d/%m/%Y')}")

# ---------------- 1️⃣ ANÁLISE DE SOLO ----------------
st.subheader("1️⃣ Análise de Solo (Química e Física)")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
with col2:
    argila = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
    prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA TÉCNICA ----------------
def interpretar_solo(p, k, arg):
    if arg > 35: lim_p = [3, 6, 9, 12]
    else: lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return "Argiloso" if arg > 35 else "Arenoso/Médio", niv_p, niv_k

classe_txt, nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)
v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

# Lógica de Nitrogênio detalhada
n_plantio = 0
n_cobertura = 0

if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    obs_n = "Nitrogênio via Fixação Biológica. Realizar inoculação."
else:
    rec_n = meta_ton * 22 # Estimativa de 22kg de N por tonelada produzida
    n_plantio = 30 # Padronizado 30kg de N no plantio para segurança
    n_cobertura = max(0.0, rec_n - n_plantio)
    
    rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
    obs_n = f"Distribuir N: {n_plantio} kg/ha no Plantio e {n_cobertura:.0f} kg/ha em Cobertura (V4-V6)."

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Metas")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Textura Solo", classe_txt)
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Status P", nivel_p)
m4.metric("Status K", nivel_k)

# ---------------- 3️⃣ PRESCRIÇÃO E DIVISÃO DE N ----------------
st.write("---")
st.subheader("3️⃣ Planejamento de Fertilizantes")
r1, r2 = st.columns([1, 2])

with r1:
    st.markdown("### 🪨 Calagem")
    st.metric("Dose (t/ha)", f"{nc:.2f}")
    st.write(f"Total: **{total_calc:.2f} toneladas**")

with r2:
    st.markdown("### 🧪 Nitrogênio Detalhado (N)")
    if cultura == "Milho":
        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Total N", f"{rec_n:.0f} kg/ha")
        nc2.metric("Plantio", f"{n_plantio} kg/ha")
        nc3.metric("Cobertura", f"{n_cobertura:.0f} kg/ha")
    else:
        st.info("Soja: Nitrogênio fornecido via inoculação das sementes.")

    st.markdown("---")
    st.markdown("### 🛒 Escolha a Formulação Comercial")
    c_n, c_p, c_k = st.columns(3)
    f_n = c_n.number_input("N (%)", 0, value=0 if cultura == "Soja" else 4)
    f_p = c_p.number_input("P₂O₅ (%)", 0, value=20)
    f_k = c_k.number_input("K₂O (%)", 0, value=20)
    
    if f_p > 0 or f_k > 0:
        dose_p = (rec_p / f_p * 100) if f_p > 0 else 0
        dose_k = (rec_k / f_k * 100) if f_k > 0 else 0
        dose_final = max(dose_p, dose_k)
        total_sacos = math.ceil((dose_final * area) / 50)
        
        st.success(f"✅ Recomendação: **{dose_final:.0f} kg/ha** do {f_n}-{f_p}-{f_k}")
        st.write(f"📦 Total: **{total_sacos} sacos de 50kg**")
    
# ---------------- 4️⃣ PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, txt("LAUDO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 11); pdf.cell(190, 5, txt(f"Consultor: Felipe Amorim | Data: {datetime.now().strftime('%d/%m/%Y')}"), align="C", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(220, 220, 220); pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("1. INFORMAÇÕES GERAIS"), ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"Cliente: {cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, txt(f"Cultura: {cultura} | Area: {area:.2f} ha | Meta: {meta_ton} t/ha"), ln=True)
    pdf.ln(5); pdf.cell(190, 8, txt("2. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
    pdf.cell(190, 7, txt(f"Calagem: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), ln=True)
    
    if cultura == "Milho":
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 7, txt(f"MANEJO DE NITROGÊNIO: Total {rec_n:.0f} kg/ha"), ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(190, 7, txt(f"  - No Plantio: {n_plantio} kg/ha"), ln=True)
        pdf.cell(190, 7, txt(f"  - Em Cobertura: {n_cobertura:.0f} kg/ha"), ln=True)
    
    pdf.cell(190, 7, txt(f"Adubação Plantio: {dose_final:.0f} kg/ha do {f_n}-{f_p}-{f_k}"), ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Laudo", pdf_bytes, file_name=f"Laudo_{cliente}.pdf")
