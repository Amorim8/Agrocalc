import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO DARK PREMIUM (CORREÇÃO DE FUNDO) ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

# CSS para eliminar o fundo branco e destacar os valores
st.markdown("""
    <style>
    /* Fundo geral mais escuro para combinar com o print */
    .main { background-color: #0e1117; }
    
    /* Ajuste dos Cards: Fundo cinza grafite, texto branco e borda verde */
    div[data-testid="stMetric"] {
        background-color: #1a1c23 !important;
        border: 1px solid #2e3139;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border-left: 5px solid #28a745 !important;
    }
    
    /* Forçar a cor do texto dentro dos cards para branco */
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div {
        color: #ffffff !important;
    }

    /* Inputs com fundo escuro para não cansar os olhos */
    .stNumberInput, .stTextInput, .stSelectbox {
        background-color: #262730 !important;
        color: white !important;
    }

    /* Botão Verde Vibrante */
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3em;
    }
    
    /* Esconder menus desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Configurações")
    cliente = st.text_input("👨‍🌾 Cliente:", "Produtor Exemplo")
    fazenda = st.text_input("🏠 Fazenda:", "Propriedade")
    talhao = st.text_input("📍 Talhão:", "01")
    municipio = st.text_input("🏙️ Município:", "Cidade")
    estado = st.selectbox("🌎 Estado:", ["GO", "MT", "MS", "MG", "PR", "SP", "BA", "TO"])
    
    st.divider()
    area = st.number_input("📏 Área (ha):", min_value=0.01, value=1.0, step=0.01)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[i/2 for i in range(2, 31)], value=4.0)

# ---------------- CONTEÚDO PRINCIPAL ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {datetime.now().strftime('%d/%m/%Y')}")

st.subheader("1️⃣ Dados da Análise de Solo")
with st.container():
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    p_solo = c1.number_input("P (mg/dm³)", 0.0, value=8.0)
    k_solo = c2.number_input("K (cmolc)", 0.0, value=0.15)
    argila = c3.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = c4.number_input("V% Atual", 0.0, 100.0, value=40.0)
    ctc = c5.number_input("CTC Total", 0.0, value=3.25)
    prnt = c6.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

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

if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    obs_n = "Focar em Inoculação (Nitrogênio Biológico)."
else:
    rec_n, rec_p = meta_ton * 22, (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
    obs_n = "Dividir N em cobertura."

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Recomendações")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Textura Solo", classe_txt)
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Status P", nivel_p)
m4.metric("Status K", nivel_k)

st.write("---")
r1, r2, r3 = st.columns([1, 1, 1])
with r1:
    st.markdown("### 🪨 Calagem")
    st.metric("Dose (t/ha)", f"{nc:.2f}")
    st.caption(f"Total: {total_calc:.2f} toneladas")

with r2:
    st.markdown("### 🧪 NPK (kg/ha)")
    st.write(f"**N:** {rec_n:.0f} | **P:** {rec_p:.0f} | **K:** {rec_k:.0f}")
    st.info(obs_n)

with r3:
    st.markdown("### 🛒 Insumo")
    col_f_p = st.number_input("P% do Adubo", 20)
    if col_f_p > 0:
        dose = (rec_p / col_f_p) * 100
        st.success(f"Dose: **{dose:.0f} kg/ha**")
        st.write(f"Pedido: {math.ceil((dose*area)/50)} sacos")

# ---------------- 3️⃣ PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 20, txt("LAUDO TÉCNICO"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, txt(f"Felipe Amorim | {datetime.now().strftime('%d/%m/%Y')}"), align="C", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.ln(15)
    pdf.set_font("Arial", "B", 11); pdf.cell(190, 8, txt(f" Cliente: {cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 8, txt(f" Meta: {meta_ton} t/ha | Dose Calcário: {nc:.2f} t/ha"), ln=True)
    pdf.cell(190, 8, txt(f" NPK Recomendado: {rec_n:.0f}-{rec_p:.0f}-{rec_k:.0f} kg/ha"), ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 GERAR LAUDO PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Laudo", pdf_bytes, file_name=f"Laudo_{cliente}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
