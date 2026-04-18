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
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha para acessar o sistema:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- ESTILO DARK PREMIUM ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide", page_icon="🌿")

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
        height: 3em;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (CONFIGURAÇÕES) ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Configurações")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    talhao = st.text_input("📍 Talhão:", "")
    municipio = st.text_input("🏙️ Município:", "Redenção do Gurguéia")
    estado = st.selectbox("🌎 Estado:", ["PI", "MA", "BA", "TO", "CE", "PE", "RN", "PB", "AL", "SE", "MG", "GO", "MT", "MS", "SP", "RJ", "ES", "PR", "SC", "RS", "AM", "RR", "AP", "PA", "AC", "RO", "DF"], index=0)
    
    st.divider()
    area_ha = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    variedade_palma = ""
    if cultura == "Palma Forrageira":
        variedade_palma = st.selectbox("🌵 Variedade da Palma:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta de Matéria Seca (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta de Produtividade (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

nome_arquivo = nome_cliente.replace(" ", "_") if nome_cliente else "Cliente"

# ---------------- CABEÇALHO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {data_hoje}")

# ---------------- 1️⃣ ANÁLISE DE SOLO ----------------
st.subheader("1️⃣ Análise de Solo (Química e Física)")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
    ph_solo = st.number_input("pH do Solo", 0.0, 14.0, value=5.5)
with col2:
    argila = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.0)
with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
    prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA TÉCNICA ----------------
def interpretar_solo(p, k, arg):
    if arg > 35: lim_p = [3, 6, 9, 12]
    else: lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return niv_p, niv_k

nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)

v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area_ha

if cultura == "Soja":
    rec_n, rec_p, rec_k = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0), (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
elif cultura == "Milho":
    rec_n, rec_p, rec_k = (meta_ton * 22), (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0), (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
else: # Palma Forrageira
    rec_n = meta_ton * 10 
    rec_p = 90 * (1.5 if nivel_p == "Baixo" else 1.0) 
    rec_k = 120 * (1.5 if nivel_k == "Baixo" else 1.0) 

# ---------------- 2️⃣ DASHBOARD E ADUBAÇÃO ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Planejamento")
r1, r2, r3 = st.columns([1, 1, 2])
with r1:
    st.metric("Calagem (t/ha)", f"{nc:.2f}")
    st.write(f"Total: **{total_calc:.2f} t**")
with r2:
    gesso_dose = (argila * 50) / 1000 if (al_solo > 0.5) else 0.0
    st.metric("Gessagem (t/ha)", f"{gesso_dose:.2f}")
with r3:
    st.write("**Formulação Comercial**")
    f_n = st.number_input("N%", 0, value=10 if cultura=="Palma Forrageira" else 4)
    f_p = st.number_input("P%", 0, value=10 if cultura=="Palma Forrageira" else 20)
    f_k = st.number_input("K%", 0, value=20)
    
    dose_p = (rec_p / f_p * 100) if f_p > 0 else 0
    dose_k = (rec_k / f_k * 100) if f_k > 0 else 0
    dose_final = max(dose_p, dose_k)
    st.success(f"Dose: {dose_final:.0f} kg/ha | Total: {math.ceil(dose_final * area_ha / 50)} sacos")

# ---------------- FUNÇÃO PDF (CARACTERES CORRIGIDOS) ----------------
def clean_txt(t):
    return str(t).encode('latin-1', 'replace').decode('latin-1').replace('?', '-')

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, clean_txt("RELATÓRIO DE PRESCRIÇÃO AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, clean_txt(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
    
    # Infos Gerais
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 1. DIAGNÓSTICO E CULTURA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, clean_txt(f" Cliente: {nome_cliente} | Fazenda: {fazenda}"), ln=True)
    cult_str = f"{cultura} ({variedade_palma})" if cultura == "Palma Forrageira" else cultura
    pdf.cell(190, 7, clean_txt(f" Cultura: {cult_str} | Área: {area_ha} ha | Meta: {meta_ton} t/ha"), ln=True)
    
    # Prescrição
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 2. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, clean_txt(f" Calagem: {nc:.2f} t/ha | Gessagem: {gesso_dose:.2f} t/ha"), ln=True)
    pdf.cell(190, 7, clean_txt(f" Adubação: {dose_final:.0f} kg/ha do formulado {f_n}-{f_p}-{f_k}"), ln=True)

    # Manejo
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 3. OBSERVAÇÕES DE MANEJO"), ln=True, fill=True)
    pdf.set_font("Arial", "I", 9)
    
    if cultura == "Palma Forrageira":
        obs_var = "Variedade Miúda: Exige solo de alta fertilidade e drenagem." if "Miúda" in variedade_palma else "Variedade Orelha de Elefante: Alta robustez e teto produtivo."
        notas = [
            f"- {obs_var}",
            "- REGRA DE OURO: JAMAIS cortar o cladódio inicial (RAQUETE MÃE).",
            "- A preservação da raquete mãe garante a longevidade do palmal.",
            "- Realizar o primeiro corte entre 18 e 24 meses após o plantio.",
            "- Recomendado aplicar 20-30 t/ha de esterco bovino curtido no plantio."
        ]
    elif cultura == "Milho":
        notas = ["- Nitrogênio: Fracionar 1/3 no plantio e 2/3 em cobertura (V4-V6)."]
    else:
        notas = ["- Soja: Focar em inoculação de qualidade e controle de pragas."]

    for linha in notas:
        pdf.cell(190, 6, clean_txt(linha), ln=True)

    return pdf.output(dest='S').encode('latin-1')

# ---------------- FINALIZAÇÃO ----------------
st.divider()
st.info(f"💡 O sistema está configurado para a cultura: **{cultura}**.")

if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name=f"Prescricao_{nome_arquivo}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
