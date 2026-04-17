import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO - FOCO EM VISIBILIDADE E ORGANIZAÇÃO ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    /* Fundo cinza escuro profissional */
    .main { background-color: #1e2130; }
    
    /* QUADROS DE MÉTRICA - COMPACTOS E PADRONIZADOS */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important; 
        border: 2px solid #ff0000;
        padding: 8px !important;
        border-radius: 8px;
        min-height: 80px !important;
        max-height: 80px !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* TÍTULOS EM VERMELHO VIVO - MÁXIMA LEITURA */
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.85rem !important;
        color: #ff0000 !important; 
        font-weight: bold !important;
        opacity: 1 !important;
        white-space: normal !important;
        line-height: 1.1 !important;
    }

    /* VALORES EM PRETO */
    div[data-testid="stMetricValue"] > div {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #000000 !important;
    }

    [data-testid="column"] { display: flex; align-items: stretch; }

    .stButton>button {
        background-color: #ff0000 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Configurações")
    nome_cliente = st.text_input("👨‍🌾 Cliente:", "Felipe Amorim")
    fazenda = st.text_input("🏠 Fazenda:", "")
    area = st.number_input("📏 Área Total (ha):", min_value=0.1, value=1.0)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"])
    meta_ton = st.number_input("🎯 Meta (t/ha):", value=4.0 if cultura == "Soja" else 10.0)

# ---------------- 1️⃣ ENTRADA DE DADOS ----------------
st.header("📋 Análise de Solo")
c1, c2, c3 = st.columns(3)
with c1:
    p_solo = st.number_input("Fósforo (mg/dm³)", value=12.9)
    k_mg = st.number_input("Potássio (mg/dm³)", value=22.0)
with c2:
    ph_solo = st.number_input("pH Solo (CaCl2 ou H2O)", value=6.54)
    v_atual = st.number_input("V% Atual", value=66.0)
with c3:
    al_solo = st.number_input("Alumínio (cmolc/dm³)", value=0.0)
    ctc = st.number_input("CTC Total (T)", value=3.25)
    prnt = st.number_input("PRNT do Calcário (%)", value=85.0)
    argila = st.number_input("Argila (%)", value=25.0)

# ---------------- LÓGICA DE CÁLCULO ----------------
# Calagem (V%)
v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calcario = nc * area

# Gessagem (NG)
m_saturacao_al = (al_solo / (al_solo + (ctc - al_solo))) * 100 if (al_solo + (ctc - al_solo)) > 0 else 0
ng = (argila * 50) / 1000 if (m_saturacao_al > 20 or al_solo > 0.5) else 0.0
total_gesso = ng * area

# Adubação estimada
rec_p = (meta_ton * 15) if cultura == "Soja" else (meta_ton * 12)
rec_k = (meta_ton * 20) if cultura == "Soja" else (meta_ton * 18)

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader("🚀 Diagnóstico e Recomendações")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("DOSE CALCÁRIO", f"{nc:.2f} t/ha")
m2.metric("TOTAL CALCÁRIO", f"{total_calcario:.2f} t")
m3.metric("DOSE GESSO", f"{ng:.2f} t/ha")
m4.metric("TOTAL GESSO", f"{total_gesso:.2f} t")
m5.metric("SATURAÇÃO Al", f"{m_saturacao_al:.1f}%")

# ---------------- 3️⃣ FUNÇÃO DO PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho decorado
    pdf.set_fill_color(255, 0, 0)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, "RELATORIO TECNICO AGRONOMICO", ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 5, f"Consultoria: Felipe Amorim | Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    
    # Dados do Cliente
    pdf.ln(25)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"CLIENTE: {nome_cliente.upper()}", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, f"Fazenda: {fazenda} | Cultura: {cultura} | Area: {area} ha", ln=True)
    
    # Seção Solo
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, "1. ANALISE DE SOLO ENCONTRADA", ln=True, fill=False)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, f"- pH do Solo: {ph_solo} | Fosforo: {p_solo} mg/dm3 | Potassio: {k_mg} mg/dm3", ln=True)
    pdf.cell(190, 7, f"- V% Atual: {v_atual}% | CTC: {ctc} | Aluminio: {al_solo} cmolc/dm3", ln=True)
    
    # Seção Recomendações
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, "2. PRESCRICAO DE CORRETIVOS", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"-> CALAGEM: Recomenda-se {nc:.2f} t/ha (Total: {total_calcario:.2f} toneladas).", ln=True)
    pdf.cell(190, 8, f"-> GESSAGEM: Recomenda-se {ng:.2f} t/ha (Total: {total_gesso:.2f} toneladas).", ln=True)
    
    if ng > 0:
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(190, 6, "Observacao Gessagem: A gessagem e indicada para melhoria do ambiente radicular em profundidade devido aos niveis de Aluminio ou baixa saturacao de calcio detectados.")
    else:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(190, 6, "Observacao: Nao houve necessidade tecnica de gessagem para esta analise.", ln=True)

    # Adubação
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, "3. NECESSIDADE DE NUTRIENTES (NPK)", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, f"- Fosforo (P2O5): {rec_p:.0f} kg/ha", ln=True)
    pdf.cell(190, 7, f"- Potassio (K2O): {rec_k:.0f} kg/ha", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="⬇️ Baixar PDF Agora",
        data=pdf_bytes,
        file_name=f"Relatorio_{nome_cliente}.pdf",
        mime="application/pdf"
    )

st.write("---")
st.caption("Felipe Amorim - Consultoria Agronômica")
