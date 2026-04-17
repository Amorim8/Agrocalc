import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- SISTEMA DE ACESSO (PROTEÇÃO) ----------------
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

# ---------------- CONFIGURAÇÃO E ESTILO ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria Palma", layout="wide", page_icon="🌵")

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
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (CONFIGURAÇÕES) ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌵</h1>", unsafe_allow_html=True)
    st.title("Configurações Palma")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    
    st.divider()
    variedade = st.selectbox("🧬 Variedade da Palma:", ["Orelha de Elefante (Mexicana)", "Palma Miúda (Doce)"])
    
    meta_producao = st.select_slider(
        "🎯 Meta de Produção (t/ha/ano):", 
        options=[40, 60, 80, 100, 150, 200], 
        value=80
    )

# ---------------- 1️⃣ DADOS DA ANÁLISE DE SOLO ----------------
st.title("SISTEMA TÉCNICO - CONSULTORIA PALMA FORRAGEIRA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {datetime.now().strftime('%d/%m/%Y')}")

st.subheader("1️⃣ Dados da Análise de Solo")
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

# ---------------- LÓGICA TÉCNICA (CALIBRADA) ----------------
# Calagem (V% alvo para Palma é 70%)
v_alvo = 70
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

# Adubação Mineral Sugerida
base_n = 150 if meta_producao >= 100 else 100
rec_n = base_n * (1.2 if variedade == "Orelha de Elefante (Mexicana)" else 1.0)
rec_p = 80 if p_solo < 10 else 40
rec_k = 180 if k_solo < 0.15 else 100
dose_esterco = 30 if meta_producao >= 100 else 20

# ---------------- 2️⃣ DASHBOARD DE PRESCRIÇÃO ----------------
st.divider()
st.subheader(f"2️⃣ Prescrição e Manejo: {variedade}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Calcário (t/ha)", f"{nc:.2f}")
c2.metric("Esterco (t/ha)", f"{dose_esterco}")
c3.metric("Nitrogênio (kg N/ha)", f"{rec_n:.0f}")
c4.metric("Potássio (kg K2O/ha)", f"{rec_k:.0f}")

# ---------------- 3️⃣ ADUBAÇÃO COMERCIAL ----------------
st.write("---")
st.subheader("3️⃣ Sugestão de Adubação Comercial")
col_ureia, col_kcl = st.columns(2)
with col_ureia:
    f_n = st.number_input("N% do adubo (ex: 45 para Ureia)", 1, value=45)
    dose_n_comercial = (rec_n / f_n) * 100
    st.info(f"Dose sugerida: **{dose_n_comercial:.0f} kg/ha** de adubo nitrogenado.")
with col_kcl:
    f_k = st.number_input("K% do adubo (ex: 60 para Cloreto)", 1, value=60)
    dose_k_comercial = (rec_k / f_k) * 100
    st.info(f"Dose sugerida: **{dose_k_comercial:.0f} kg/ha** de adubo potássico.")

# ---------------- 4️⃣ PDF COM MANEJO COMPLETO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 15, fix("RELATÓRIO TÉCNICO: MANEJO DE PALMA"), align="C", ln=True)
    pdf.set_font("Helvetica", "", 10); pdf.cell(190, 5, fix(f"Consultor: Felipe Amorim | Variedade: {variedade}"), align="C", ln=True)
    
    # 1. Recomendação de Nutrição
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix(" 1. CORREÇÃO E NUTRIÇÃO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix(f" - Calcário: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), ln=True)
    pdf.cell(190, 7, fix(f" - Adubação Orgânica: {dose_esterco} t/ha de esterco bovino curtido."), ln=True)
    pdf.cell(190, 7, fix(f" - Nitrogênio (N): {rec_n} kg/ha | Potássio (K2O): {rec_k} kg/ha"), ln=True)
    pdf.multi_cell(190, 5, fix(" CRONOGRAMA: Fósforo e Esterco no fundo do sulco no plantio. Nitrogênio e Potássio devem ser parcelados em 2x: a 1ª dose após as raquetes brotarem (solo úmido) e a 2ª dose 60 dias após."))

    # 2. Manejo de Corte (Instruções do Felipe)
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix(" 2. INSTRUÇÕES DE COLHEITA (CORTE)"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(190, 6, fix("- PRIMEIRO CORTE: Realizar obrigatoriamente entre 24 a 36 meses após o plantio.\n- LOCAL DE CORTE: PRESERVAR a raquete 'mãe' e as raquetes de 1ª ordem (primárias). Colher apenas da 2ª ordem em diante.\n- TÉCNICA: Deixar um 'toco' de 2 a 3 cm da base da raquete colhida para evitar podridões na matriz. Realizar o corte inclinado (chanfro).\n- FREQUÊNCIA: Colheitas bienais (a cada 2 anos) garantem maior longevidade ao palmal no semiárido."))
    
    # Rodapé Legal
    pdf.ln(10); pdf.set_fill_color(255, 235, 235); pdf.set_font("Helvetica", "B", 9)
    pdf.cell(190, 7, fix(" NOTA TÉCNICA E RESPONSABILIDADE"), ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 8); pdf.set_text_color(100, 0, 0)
    pdf.multi_cell(190, 4, fix("Esta recomendação baseia-se em dados de literatura técnica (Embrapa/IPA). O sucesso depende do regime de chuvas e controle de pragas (Cochonilha). O consultor não se responsabiliza por manejos sem supervisão presencial."))

    return pdf.output(dest='S').encode('latin-1')

st.divider()
st.warning("⚠️ **Aviso:** Certifique-se de que o Esterco está bem curtido antes da aplicação para evitar queima das raízes.")
if st.button("📄 GERAR RELATÓRIO TÉCNICO COMPLETO"):
    pdf_bytes = gerar_pdf()
    nome_arquivo = nome_cliente.replace(" ", "_") if nome_cliente else "Cliente"
    st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name=f"Consultoria_Palma_{nome_arquivo}.pdf")

st.caption("Felipe Amorim | Redenção do Gurguéia - PI")
