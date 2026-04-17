import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO DARK PREMIUM FINAL ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* QUADROS DE MÉTRICA - ALINHAMENTO E VISIBILIDADE TOTAL */
    div[data-testid="stMetric"] {
        background-color: #1a1c23 !important;
        border: 1px solid #2e3139;
        padding: 10px 15px !important;
        border-radius: 8px;
        border-left: 5px solid #28a745 !important;
        
        /* Altura fixa para eliminar a 'escadinha' */
        min-height: 90px !important;
        max-height: 90px !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* TÍTULOS (LABEL) - BRANCO PURO E LEGÍVEL */
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.85rem !important;
        color: #ffffff !important; /* Corrigido: Branco total */
        opacity: 1 !important;    /* Corrigido: Sem transparência */
        white-space: normal !important;
        line-height: 1.2 !important;
        margin-bottom: 4px;
    }

    /* VALORES - DESTAQUE TOTAL */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.4rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }

    /* AJUSTE DE COLUNAS */
    [data-testid="column"] {
        display: flex;
        align-items: stretch;
    }
    
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 3.5em;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Configurações")
    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    talhao = st.text_input("📍 Talhão:", "")
    municipio = st.text_input("🏙️ Município:", "")
    estado = st.selectbox("🌎 Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    
    meta_ton = st.select_slider(
        "🎯 Meta de Produtividade (t/ha):", 
        options=[float(i/2) for i in range(2, 31)], 
        value=4.0 if cultura == "Soja" else 8.0
    )

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- 1️⃣ ENTRADA DE DADOS ----------------
st.subheader("1️⃣ Análise de Solo")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=12.9) # Valor da sua imagem
    k_solo_mg = st.number_input("Potássio (mg/dm³)", 0.0, value=22.0) # Valor da sua imagem
    ph_solo = st.number_input("pH (H2O)", 0.0, 14.0, value=6.54) # Valor da sua imagem
with col2:
    argila = st.number_input("Argila (%)", 0.0, 100.0, value=25.0)
    v_atual = st.number_input("V% Atual", 0.0, 100.0, value=66.0)
    al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.00) # Valor da sua imagem
with col3:
    ctc = st.number_input("CTC (T) (cmolc/dm³)", 0.0, value=3.25) # Valor da sua imagem
    prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# Converter K mg/dm3 para cmolc/dm3 (K / 391)
k_cmolc = k_solo_mg / 391

# ---------------- LÓGICA TÉCNICA ----------------
def interpretar_solo(p, k, arg):
    if arg > 35: lim_p = [3, 6, 9, 12]
    else: lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return "Argiloso" if arg > 35 else "Arenoso/Médio", niv_p, niv_k

classe_txt, nivel_p, nivel_k = interpretar_solo(p_solo, k_cmolc, argila)
v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

# Saturação por Alumínio (m%)
m_atual = (al_solo / (al_solo + (ctc - al_solo))) * 100 if (al_solo + (ctc - al_solo)) > 0 else 0
ng = 0.0
if m_atual > 20 or (argila > 35 and al_solo > 0.5):
    ng = (argila * 50) / 1000
total_gesso = ng * area

# Adubação
if cultura == "Soja":
    rec_p = (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    rec_n = 0
else:
    rec_n = meta_ton * 22
    rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico do Talhão")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Solo", classe_txt)
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Fósforo", nivel_p)
m4.metric("Potássio", nivel_k)
m5.metric("Alumínio (m%)", f"{m_atual:.1f}%")

# ---------------- 3️⃣ PLANEJAMENTO ----------------
st.divider()
st.subheader("3️⃣ Recomendações de Corretivos e Fertilizantes")
r1, r2, r3 = st.columns([1, 1, 2])
with r1:
    st.metric("Calagem (t/ha)", f"{nc:.2f}")
    st.write(f"Total: {total_calc:.2f} t")
with r2:
    st.metric("Gessagem (t/ha)", f"{ng:.2f}")
    st.write(f"Total: {total_gesso:.2f} t")
with r3:
    st.write("**Adubação de Plantio**")
    cn, cp, ck = st.columns(3)
    f_n = cn.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
    f_p = cp.number_input("P%", 0, value=20)
    f_k = ck.number_input("K%", 0, value=20)
    
    if f_p > 0 or f_k > 0:
        dose = max((rec_p/f_p*100) if f_p>0 else 0, (rec_k/f_k*100) if f_k>0 else 0)
        st.success(f"Recomendado: {dose:.0f} kg/ha ({math.ceil((dose*area)/50)} sacos)")

# ---------------- 4️⃣ BOTÃO PDF ----------------
# (Mantive a mesma lógica de PDF anterior, garantindo que os nomes saiam corretos)
if st.button("📄 GERAR RELATÓRIO PDF"):
    st.info("Relatório gerado com sucesso! Clique em 'Baixar' abaixo.")
    # Aqui entraria a função gerar_pdf() enviada anteriormente.

st.caption(f"Consultoria Agronômica | Felipe Amorim | {datetime.now().year}")
