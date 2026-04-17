import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO DARK PREMIUM - CORES E TAMANHO AJUSTADOS ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* PADRONIZAÇÃO DOS QUADROS DE MÉTRICA - BEM MAIS COMPACTOS */
    div[data-testid="stMetric"] {
        background-color: #1a1c23 !important;
        border: 1px solid #2e3139;
        padding: 5px 10px !important; /* Padding mínimo para diminuir o quadro */
        border-radius: 6px;
        border-left: 4px solid #ff0000 !important; /* Borda esquerda vermelha para combinar */
        
        /* Força uma altura bem menor (Slim) */
        min-height: 65px !important;
        max-height: 65px !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* TÍTULOS (LABELS) EM VERMELHO PARA MÁXIMA VISIBILIDADE */
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.8rem !important;
        color: #ff0000 !important; /* VERMELHO PURO */
        font-weight: bold !important;
        opacity: 1 !important;
        white-space: nowrap !important;
        line-height: 1.0 !important;
        overflow: visible !important;
    }

    /* VALORES EM BRANCO PARA CONTRASTAR COM O TÍTULO VERMELHO */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
        line-height: 1.0 !important;
    }

    /* ALINHAMENTO DAS COLUNAS */
    [data-testid="column"] {
        display: flex;
        align-items: stretch;
    }
    
    .stButton>button {
        background-color: #ff0000 !important; /* Botão combinando com o tema */
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 3em;
        border: none;
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
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    
    meta_ton = st.select_slider(
        "🎯 Meta de Produtividade (t/ha):", 
        options=[float(i/2) for i in range(2, 31)], 
        value=4.0 if cultura == "Soja" else 8.0
    )

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- 1️⃣ ANÁLISE DE SOLO ----------------
st.subheader("1️⃣ Dados da Análise de Solo")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=12.9)
    k_solo_mg = st.number_input("Potássio (mg/dm³)", 0.0, value=22.0)
    ph_solo = st.number_input("pH (H2O)", 0.0, 14.0, value=6.54)
with col2:
    argila = st.number_input("Argila (%)", 0.0, 100.0, value=25.0)
    v_atual = st.number_input("V% Atual", 0.0, 100.0, value=66.0)
    al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.00)
with col3:
    ctc = st.number_input("CTC (T) (cmolc/dm³)", 0.0, value=3.25)
    prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA TÉCNICA ----------------
k_cmolc = k_solo_mg / 391
v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

m_atual = (al_solo / (al_solo + (ctc - al_solo))) * 100 if (al_solo + (ctc - al_solo)) > 0 else 0
ng = (argila * 50) / 1000 if (m_atual > 20 or al_solo > 0.5) else 0.0
total_gesso = ng * area

if cultura == "Soja":
    rec_p = (meta_ton * 15) * (1.2 if p_solo < 10 else 1.0)
    rec_k = (meta_ton * 20) * (1.2 if k_cmolc < 0.15 else 1.0)
    rec_n = 0
else:
    rec_n = meta_ton * 22
    rec_p = (meta_ton * 12) * (1.2 if p_solo < 10 else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if k_cmolc < 0.15 else 1.0)

# ---------------- 2️⃣ DASHBOARD COMPACTO ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Textura", "Argil." if argila > 35 else "Média/Aren.")
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Fósforo", "Baixo" if p_solo < 10 else "Bom")
m4.metric("Potássio", "Baixo" if k_cmolc < 0.15 else "Bom")
m5.metric("Alumínio", f"{m_atual:.1f}%")

# ---------------- 3️⃣ PRESCRIÇÃO SLIM ----------------
st.divider()
st.subheader("3️⃣ Recomendações Técnicas")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Dose Calcário", f"{nc:.2f} t/ha")
r2.metric("Dose Gesso", f"{ng:.2f} t/ha")
r3.metric("Total Calcário", f"{total_calc:.1f} t")
r4.metric("Total Gesso", f"{total_gesso:.1f} t")

# ---------------- 4️⃣ ADUBAÇÃO COMERCIAL ----------------
st.divider()
st.subheader("4️⃣ Sugestão de Adubação")
c1, c2, c3 = st.columns(3)
with c1:
    f_n = st.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
with c2:
    f_p = st.number_input("P%", 0, value=20)
with c3:
    f_k = st.number_input("K%", 0, value=20)

if f_p > 0 or f_k > 0:
    dose = max((rec_p/f_p*100) if f_p>0 else 0, (rec_k/f_k*100) if f_k>0 else 0)
    st.error(f"Dose recomendada: {dose:.0f} kg/ha | Total: {math.ceil((dose*area)/50)} sacos")

st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    st.success("Relatório preparado com sucesso!")

st.caption(f"Felipe Amorim | Consultoria | {datetime.now().year}")
