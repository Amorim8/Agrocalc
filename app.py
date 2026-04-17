import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- SISTEMA DE ACESSO ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha para acessar o sistema:", type="password")
    if st.button("Entrar"):
        if senha == "@Lipe1928":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- CONFIGURAÇÃO VISUAL ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria Agronômica", layout="wide", page_icon="🌱")

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
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
    }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- BARRA LATERAL (MENU DE ESCOLHA) ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🚜</h1>", unsafe_allow_html=True)
    st.title("Painel de Controle")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0)
    
    st.divider()
    
    # 1. Escolha a Cultura Principal
    cultura_selecionada = st.selectbox("🌱 Selecione a Cultura:", ["Selecione...", "Palma Forrageira", "Soja", "Milho"])
    
    # 2. Se for Palma, abre as opções específicas que você pediu
    if cultura_selecionada == "Palma Forrageira":
        st.subheader("Opções de Palma")
        variedade = st.radio("🧬 Escolha o Tipo:", ["Orelha de Elefante (Mexicana)", "Palma Miúda (Doce)"])
        meta_producao = st.select_slider("🎯 Meta de Produção (t/ha/ano):", options=[40, 60, 80, 100, 150, 200], value=80)
    elif cultura_selecionada == "Selecione...":
        st.info("Por favor, selecione uma cultura para iniciar.")
    else:
        st.warning(f"Módulo de {cultura_selecionada} em desenvolvimento.")

# ---------------- CORPO PRINCIPAL DO SISTEMA ----------------
st.title("SISTEMA DE CONSULTORIA AGRONÔMICA")
st.write(f"**Agrônomo:** Felipe Amorim | **Redenção do Gurguéia - PI**")

if cultura_selecionada != "Selecione...":
    st.subheader(f"📋 Análise de Solo e Prescrição: {cultura_selecionada}")
    
    # Entrada de Dados da Análise
    col1, col2, col3 = st.columns(3)
    with col1:
        p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=5.0)
        k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.10)
        ph_solo = st.number_input("pH do Solo", 0.0, 14.0, value=5.0)
    with col2:
        argila = st.number_input("Argila (%)", 0.0, 100.0, value=25.0)
        v_atual = st.number_input("V% Atual", 0.0, 100.0, value=30.0)
        al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.5)
    with col3:
        ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=4.0)
        prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

    # Lógica de Cálculo (Ativada se for Palma)
    if cultura_selecionada == "Palma Forrageira":
        v_alvo = 70
        nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
        total_calc = nc * area
        
        base_n = 150 if meta_producao >= 100 else 100
        rec_n = base_n * (1.2 if variedade == "Orelha de Elefante (Mexicana)" else 1.0)
        rec_p = 80 if p_solo < 10 else 40
        rec_k = 180 if k_solo < 0.15 else 100
        dose_esterco = 30 if meta_producao >= 100 else 20

        # Resultados na Tela
        st.divider()
        st.subheader(f"📊 Recomendações Técnicas - {variedade}")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Calcário (t/ha)", f"{nc:.2f}")
        r2.metric("Esterco (t/ha)", f"{dose_esterco}")
        r3.metric("Nitrogênio (kg N/ha)", f"{rec_n:.0f}")
        r4.metric("Potássio (kg K2O/ha)", f"{rec_k:.0f}")

        # PDF Funcional
        def gerar_pdf():
            pdf = FPDF()
            pdf.add_page()
            def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
            
            pdf.set_fill_color(40, 40, 40); pdf.rect(0, 0, 210, 40, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 16)
            pdf.cell(190, 15, fix("LAUDO DE RECOMENDAÇÃO AGRONÔMICA"), align="C", ln=True)
            pdf.set_font("Helvetica", "", 10); pdf.cell(190, 5, fix(f"Agrônomo: Felipe Amorim | {cultura_selecionada}"), align="C", ln=True)
            
            pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 11)
            pdf.cell(190, 8, fix(f" 1. DADOS E PRESCRIÇÃO - {variedade.upper()}"), ln=True, fill=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(190, 7, fix(f" Cliente: {nome_cliente} | Fazenda: {fazenda} | Área: {area:.2f} ha"), ln=True)
            pdf.cell(190, 7, fix(f" - Calcário: {nc:.2f} t/ha | Esterco Bovino: {dose_esterco} t/ha"), ln=True)
            pdf.cell(190, 7, fix(f" - Nutrição (N-P-K): {rec_n:.0f}-{rec_p:.0f}-{rec_k:.0f} kg/ha"), ln=True)
            
            pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 11)
            pdf.cell(190, 8, fix(" 2. INSTRUÇÕES TÉCNICAS DE MANEJO"), ln=True, fill=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(190, 6, fix("- COLHEITA: Realizar entre 24 a 36 meses.\n- PRESERVAÇÃO: Proibido cortar raquete mãe e primárias.\n- TÉCNICA: Corte inclinado, deixar toco de 2 a 3 cm na base."))

            return pdf.output(dest='S').encode('latin-1')

        st.divider()
        if st.button("📄 GERAR RELATÓRIO"):
            pdf_bytes = gerar_pdf()
            st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Laudo_{nome_cliente}.pdf")

st.caption("Felipe Amorim | Engenheiro Agrônomo")
