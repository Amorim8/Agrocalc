import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- SISTEMA DE ACESSO ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center; color: white;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha para acessar o sistema:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- ESTILO VISUAL DE ALTO CONTRASTE ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    /* Fundo Preto Absoluto */
    .stApp { background-color: #000000 !important; }
    
    /* Forçar Branco Puro em TODOS os textos e etiquetas */
    p, span, label, h1, h2, h3, .stMarkdown, [data-testid="stMetricLabel"] > div {
        color: #FFFFFF !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }

    /* Ajuste específico para as etiquetas dos campos (Labels) */
    .stNumberInput label, .stSelectbox label, .stTextInput label, .stRadio label {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        background-color: transparent !important;
    }

    /* Cartões de Métrica (Resultados do Dashboard) */
    div[data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 2px solid #28a745 !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }
    div[data-testid="stMetricValue"] > div { 
        color: #FFFFFF !important; 
        font-size: 2rem !important;
    }

    /* Botão Verde de Ação */
    .stButton>button {
        background-color: #28a745 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        width: 100% !important;
        height: 4em !important;
        border-radius: 10px !important;
        border: none !important;
    }

    /* Estilo dos campos de entrada de dados */
    input {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #444444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (CONFIGURAÇÕES) ----------------
with st.sidebar:
    st.markdown("<h2 style='color: white;'>⚙️ Painel</h2>", unsafe_allow_html=True)
    nome_cliente = st.text_input("👨‍🌾 Cliente:", "Felipe")
    fazenda = st.text_input("🏠 Fazenda:", "")
    municipio = st.text_input("🏙️ Município:", "Redenção do Gurguéia")
    estado = st.selectbox("🌎 Estado:", ["PI", "MA", "BA", "TO", "CE", "PE", "RN", "PB", "AL", "SE", "MG", "GO", "MT", "MS", "SP", "RJ", "ES", "PR", "SC", "RS", "AM", "RR", "AP", "PA", "AC", "RO", "DF"])
    
    st.divider()
    area_ha = st.number_input("📏 Área (ha):", min_value=0.01, value=1.0, step=0.01)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    var_palma = ""
    if cultura == "Palma Forrageira":
        var_palma = st.selectbox("🌵 Variedade:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

# ---------------- 1️⃣ ENTRADA DE DADOS ----------------
st.markdown("<h1 style='color: white;'>CONSULTORIA AGRONÔMICA</h1>", unsafe_allow_html=True)
st.write(f"**Consultor:** Felipe Amorim | **Data:** {data_hoje}")

st.markdown("### 1️⃣ Dados da Análise de Solo")
col1, col2, col3 = st.columns(3)
with col1:
    p_s = st.number_input("Fósforo (P) - mg/dm³", 0.0, value=8.0)
    k_s = st.number_input("Potássio (K) - cmolc/dm³", 0.0, value=0.15)
    ph_s = st.number_input("pH em Água", 0.0, 14.0, value=5.5)
with col2:
    arg = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_at = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    al_s = st.number_input("Alumínio (Al)", 0.0, value=0.0)
with col3:
    ctc_s = st.number_input("CTC Total (T)", 0.0, value=3.25)
    prnt_s = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- CÁLCULOS ----------------
if arg > 35: 
    st_p = "Baixo" if p_s <= 6 else "Médio" if p_s <= 9 else "Bom"
else: 
    st_p = "Baixo" if p_s <= 12 else "Médio" if p_s <= 18 else "Bom"
st_k = "Baixo" if k_s <= 0.15 else "Médio" if k_s <= 0.30 else "Bom"

v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc_ha = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)

if cultura == "Soja":
    r_p, r_k = (meta_ton * 15), (meta_ton * 20)
elif cultura == "Milho":
    r_p, r_k = (meta_ton * 12), (meta_ton * 18)
else: # Palma
    r_p, r_k = 90 * (1.5 if st_p == "Baixo" else 1.0), 120 * (1.5 if st_k == "Baixo" else 1.0)

# ---------------- 2️⃣ RESULTADOS VISÍVEIS ----------------
st.divider()
st.markdown("### 2️⃣ Prescrição e Diagnóstico")
r1, r2, r3 = st.columns(3)
r1.metric("CALAGEM", f"{nc_ha:.2f} t/ha")
r2.metric("STATUS P", st_p)
r3.metric("STATUS K", st_k)

st.write("---")
st.markdown("### 3️⃣ Adubação Sugerida")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N%", 0, value=10)
f_p = f2.number_input("P%", 0, value=10)
f_k = f3.number_input("K%", 0, value=20)

dose_kg = max((r_p/f_p*100) if f_p>0 else 0, (r_k/f_k*100) if f_k>0 else 0)
st.success(f"**DOSE:** {dose_kg:.0f} kg/ha | **TOTAL ÁREA:** {math.ceil(dose_kg * area_ha / 50)} sacos")

# ---------------- PDF ----------------
def clean_txt(t):
    return str(t).encode('latin-1', 'replace').decode('latin-1').replace('?', '-')

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, clean_txt("RELATÓRIO DE PRESCRIÇÃO AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, clean_txt(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
    
    pdf.set_text_color(0, 0, 0); pdf.ln(20); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 1. DIAGNÓSTICO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, clean_txt(f" Cliente: {nome_cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, clean_txt(f" Cultura: {cultura} {var_palma} | Area: {area_ha} ha"), ln=True)
    
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 2. ANÁLISE DE SOLO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 7, clean_txt(f" P: {p_s} mg/dm3 ({st_p})"), ln=0)
    pdf.cell(95, 7, clean_txt(f" K: {k_s} cmolc/dm3 ({st_k})"), ln=1)
    pdf.cell(190, 7, clean_txt(f" Argila: {arg}% | pH: {ph_s} | V%: {v_at}%"), ln=1)

    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 3. RECOMENDAÇÃO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, clean_txt(f" Calagem: {nc_ha:.2f} t/ha | Gessagem: {(arg * 50 / 1000):.2f} t/ha"), ln=True)
    pdf.cell(190, 7, clean_txt(f" Adubacao: {dose_kg:.0f} kg/ha ({f_n}-{f_p}-{f_k})"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO FINAL ----------------
st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Recomendacao_{nome_cliente}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
