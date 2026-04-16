import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO PREMIUM (CORES FORTES E SEM TRANSPARÊNCIA) ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

# CSS customizado para contraste alto e visual profissional
st.markdown("""
    <style>
    /* Fundo da página mais suave para destacar os cards */
    .main { background-color: #f0f2f6; }
    
    /* Cards brancos sólidos, sem transparência, com bordas verdes fortes */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 8px solid #1e7e34 !important;
    }
    
    /* Estilo dos inputs para facilitar a leitura */
    .stNumberInput, .stTextInput, .stSelectbox {
        background-color: #ffffff !important;
    }

    /* Botão Principal */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #1e7e34;
        color: white;
        font-weight: bold;
        font-size: 18px;
        border: none;
    }
    
    /* Títulos */
    h1, h2, h3 { color: #1e7e34; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (CONFIGURAÇÕES) ----------------
with st.sidebar:
    # Trocado o ícone para uma planta
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Menu de Dados")
    
    cliente = st.text_input("👨‍🌾 Nome do Cliente:", "Produtor Exemplo")
    fazenda = st.text_input("🏠 Fazenda:", "Nome da Propriedade")
    talhao = st.text_input("📍 Talhão:", "Gleba 01")
    municipio = st.text_input("🏙️ Município:", "Cidade")
    estado = st.selectbox("🌎 Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    
    meta_ton = st.select_slider(
        "🎯 Meta de Produtividade (t/ha):", 
        options=[i/2 for i in range(2, 31)], 
        value=4.0 if cultura == "Soja" else 8.0
    )

# ---------------- CABEÇALHO PRINCIPAL ----------------
col_tit, col_data = st.columns([3, 1])
with col_tit:
    st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
    st.write(f"**Consultor Responsável:** Felipe Amorim")
with col_data:
    st.write(f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y')}")

# ---------------- 1️⃣ ENTRADA DE DADOS DA ANÁLISE ----------------
st.subheader("1️⃣ Análise de Solo (Química e Física)")
with st.container():
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    p_solo = c1.number_input("P (mg/dm³)", 0.0, value=8.0)
    k_solo = c2.number_input("K (cmolc)", 0.0, value=0.15)
    argila = c3.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = c4.number_input("V% Atual", 0.0, 100.0, value=40.0)
    ctc = c5.number_input("CTC Total", 0.0, value=3.25)
    prnt = c6.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA TÉCNICA (EMBRAPA) ----------------
def interpretar_solo(p, k, arg):
    if arg > 60: lim_p = [2, 4, 6, 9]
    elif arg > 35: lim_p = [3, 6, 9, 12]
    elif arg > 15: lim_p = [4, 8, 12, 18]
    else: lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return "Muito Argiloso" if arg > 60 else "Argiloso" if arg > 35 else "Médio" if arg > 15 else "Arenoso", niv_p, niv_k

classe_txt, nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)

v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    obs_n = "Nitrogênio via Fixação Biológica. Realizar inoculação."
else:
    rec_n, rec_p = meta_ton * 22, (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
    obs_n = "Dividir aplicação de Nitrogênio em V4 e V6."

# ---------------- 2️⃣ DASHBOARD DE RESULTADOS ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Prescrição Técnica")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Textura Solo", classe_txt)
m2.metric("Saturação Alvo", f"{v_alvo}%")
m3.metric("Status Fósforo", nivel_p)
m4.metric("Status Potássio", nivel_k)

# Bloco de Recomendações
r1, r2, r3 = st.columns([1, 1, 1])

with r1:
    st.markdown("### 🪨 Calagem")
    st.metric("Dose (t/ha)", f"{nc:.2f}")
    st.write(f"Total para {area} ha: **{total_calc:.2f} t**")

with r2:
    st.markdown("### 🧪 NPK Necessário")
    st.write(f"**N:** {rec_n:.0f} kg/ha")
    st.write(f"**P₂O₅:** {rec_p:.0f} kg/ha")
    st.write(f"**K₂O:** {rec_k:.0f} kg/ha")
    st.info(f"💡 {obs_n}")

with r3:
    st.markdown("### 🛒 Insumo Comercial")
    col_n, col_p, col_k = st.columns(3)
    f_n = col_n.number_input("N%", 0)
    f_p = col_p.number_input("P%", 20)
    f_k = col_k.number_input("K%", 20)
    
    if f_p > 0:
        dose = (rec_p / f_p) * 100
        total_sacos = math.ceil((dose * area) / 50)
        st.success(f"Dose: **{dose:.0f} kg/ha**")
        st.write(f"Pedido: **{total_sacos} sacos (50kg)**")

# ---------------- 3️⃣ RELATÓRIO PDF ----------------
st.divider()
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho Verde Forte
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, txt("LAUDO TÉCNICO DE RECOMENDAÇÃO"), align="C", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 5, txt(f"Consultor: Felipe Amorim | Emissão: {datetime.now().strftime('%d/%m/%Y')}"), align="C", ln=True)
    
    pdf.set_text_color(0, 0, 0); pdf.ln(15)
    
    # Dados da Área
    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, txt(" 1. INFORMAÇÕES DO PRODUTOR E ÁREA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, txt(f" Cliente: {cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, txt(f" Local: {municipio}-{estado} | Área: {area} ha | Talhão: {talhao}"), ln=True)
    pdf.cell(190, 7, txt(f" Cultura: {cultura} | Meta de Produtividade: {meta_ton} t/ha"), ln=True)
    
    # Resultados
    pdf.ln(5); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, txt(" 2. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, txt(f" Correção (Calcário): {nc:.2f} t/ha | Total Área: {total_calc:.2f} t"), ln=True)
    pdf.cell(190, 7, txt(f" Adubação NPK (kg/ha): {rec_n:.0f} - {rec_p:.0f} - {rec_k:.0f}"), ln=True)
    
    if f_p > 0:
        pdf.cell(190, 7, txt(f" Sugestão de Adubo: {f_n}-{f_p}-{f_k} | Dose: {dose:.0f} kg/ha | Sacos: {total_sacos}"), ln=True)
    
    pdf.ln(10); pdf.set_font("Arial", "I", 8); pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(190, 5, txt("Fontes Técnicas: Embrapa Cerrados, Embrapa Soja, IPNI Brasil. Este laudo deve ser acompanhado por um Engenheiro Agrônomo."), align="C")
    
    return pdf.output(dest='S').encode('latin-1')

c_bt1, c_bt2, c_bt3 = st.columns([1,1,1])
with c_bt2:
    if st.button("📄 GERAR LAUDO PDF"):
        pdf_bytes = gerar_pdf()
        st.download_button("⬇️ Baixar Laudo", pdf_bytes, file_name=f"Laudo_{cliente}.pdf")

st.caption("Felipe Amorim | Consultoria de Solos & Nutrição de Plantas")
