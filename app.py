import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO DARK PREMIUM (PADRONIZADO) ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* PADRONIZAÇÃO DOS QUADROS DE MÉTRICA - ALTURA FIXA E SEM CORTES */
    div[data-testid="stMetric"] {
        background-color: #1a1c23 !important;
        border: 1px solid #2e3139;
        padding: 10px !important;
        border-radius: 8px;
        border-left: 4px solid #28a745 !important;
        
        /* Força todos os quadros a terem a mesma altura para evitar desorganização */
        height: 100px !important; 
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* TÍTULO DA MÉTRICA */
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.8rem !important;
        color: #aeb0b7 !important;
        white-space: normal !important;
        line-height: 1.2 !important;
        height: 32px; /* Espaço fixo para o título */
        overflow: hidden;
        text-overflow: clip !important;
    }

    /* VALOR DA MÉTRICA (REMOVE RETICÊNCIAS) */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
        white-space: nowrap !important;
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
    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    talhao = st.text_input("📍 Talhão:", "")
    municipio = st.text_input("🏙️ Município:", "")
    estado = st.selectbox("🌎 Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    
    meta_ton = st.select_slider(
        "🎯 Meta de Produtividade (t/ha):", 
        options=[float(i/2) for i in range(2, 31)], 
        value=4.0 if cultura == "Soja" else 8.0
    )

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- CABEÇALHO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {datetime.now().strftime('%d/%m/%Y')}")

# ---------------- 1️⃣ ANÁLISE DE SOLO ----------------
st.subheader("1️⃣ Análise de Solo (Química e Física)")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
    ph_solo = st.number_input("pH (CaCl2)", 0.0, 14.0, value=5.2)
with col2:
    argila = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.2)
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

# Lógica de Gessagem
m_atual = (al_solo / (al_solo + (ctc - al_solo))) * 100 if (al_solo + (ctc - al_solo)) > 0 else 0
ng = 0.0
if m_atual > 20 or al_solo > 0.5:
    ng = (argila * 50) / 1000
total_gesso = ng * area

# Lógica de N
n_plantio, n_cobertura = 0, 0
if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
else:
    rec_n = meta_ton * 22
    n_plantio = 30
    n_cobertura = max(0.0, rec_n - n_plantio)
    rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)

# ---------------- 2️⃣ DASHBOARD (COM AJUSTE DE COLUNA) ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Metas")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Textura Solo", classe_txt)
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Status P", nivel_p)
m4.metric("Status K", nivel_k)
m5.metric("Saturação Al", f"{m_atual:.1f}%")

# ---------------- 3️⃣ PRESCRIÇÃO E ADUBO ----------------
st.write("---")
st.subheader("3️⃣ Planejamento de Fertilizantes e Corretivos")
r1, r2, r3 = st.columns([1, 1, 2])
with r1:
    st.markdown("### 🪨 Calagem")
    st.metric("Dose (t/ha)", f"{nc:.2f}")
    st.write(f"Total: **{total_calc:.2f} t**")
with r2:
    st.markdown("### ⚪ Gessagem")
    st.metric("Dose (t/ha)", f"{ng:.2f}")
    st.write(f"Total: **{total_gesso:.2f} t**")
with r3:
    if cultura == "Milho":
        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Total N", f"{rec_n:.0f} kg")
        nc2.metric("Plantio", f"{n_plantio} kg")
        nc3.metric("Cobertura", f"{n_cobertura:.0f} kg")
    st.markdown("### 🛒 Formulação Comercial")
    cn, cp, ck = st.columns(3)
    f_n = cn.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
    f_p = cp.number_input("P%", 0, value=20)
    f_k = ck.number_input("K%", 0, value=20)
    if f_p > 0 or f_k > 0:
        dose_final = max((rec_p/f_p*100) if f_p>0 else 0, (rec_k/f_k*100) if f_k>0 else 0)
        total_sacos = math.ceil((dose_final * area) / 50)
        st.success(f"Dose: {dose_final:.0f} kg/ha | Total: {total_sacos} sacos")

# ---------------- 4️⃣ PDF RELATÓRIO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, txt(f"Consultor: Felipe Amorim | Data: {datetime.now().strftime('%d/%m/%Y')}"), align="C", ln=True)
    
    # Dados Gerais
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, txt(" 1. INFORMAÇÕES GERAIS E DIAGNÓSTICO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, txt(f" Cliente: {nome_cliente_input if nome_cliente_input else 'Nao informado'} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, txt(f" Cultura: {cultura} | Area: {area:.2f} ha | Meta: {meta_ton} t/ha"), ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 7, txt(f" Solo: pH ({ph_solo}) | P ({nivel_p}) | K ({nivel_k}) | m% ({m_atual:.1f}%) | Textura ({classe_txt})"), ln=True)
    
    # Prescrição Corretivos
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, txt(" 2. PRESCRIÇÃO DE CORRETIVOS"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, txt(f" Calagem: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), ln=True)
    pdf.cell(190, 7, txt(f" Gessagem: {ng:.2f} t/ha (Total: {total_gesso:.2f} t)"), ln=True)
    if ng > 0:
        pdf.set_font("Arial", "I", 9)
        pdf.cell(190, 5, txt("  * Aplicar gesso a lanco em superficie. Nao e necessaria a incorporacao."), ln=True)
    
    # Adubação
    pdf.ln(2); pdf.set_font("Arial", "B", 10)
    if cultura == "Milho":
        pdf.cell(190, 7, txt(f" Recomendação de Nitrogênio (N): Total {rec_n:.0f} kg/ha"), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 6, txt(f"  - Plantio: {n_plantio} kg/ha | Cobertura (V4-V6): {n_cobertura:.0f} kg/ha"), ln=True)
    
    pdf.ln(2); pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 7, txt(f" Adubação Comercial Sugerida: {dose_final:.0f} kg/ha do {f_n}-{f_p}-{f_k}"), ln=True)
    pdf.cell(190, 7, txt(f" Necessidade de Compra: {total_sacos} sacos (50kg) para a área total."), ln=True)

    # Fontes
    pdf.ln(10); pdf.set_font("Arial", "B", 10); pdf.set_text_color(34, 139, 34)
    pdf.cell(190, 8, txt("FONTES E REFERÊNCIAS TÉCNICAS:"), ln=True)
    pdf.set_font("Arial", "I", 9); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(190, 5, txt("- Interpretacao: Embrapa Cerrados/Soja.\n- Exportacao: IPNI Brasil.\n- Manejo N: Boletim 100.\n- Gessagem: Metodo da Argila e Saturacao por Al (m%)."))
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name=f"Relatorio_{nome_para_arquivo}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
