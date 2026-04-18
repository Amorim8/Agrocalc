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

# ---------------- ESTILO DARK (VISIBILIDADE TOTAL EM BRANCO) ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    /* Fundo principal preto */
    .main { background-color: #0e1117; }
    
    /* Forçar todos os textos, labels e unidades para Branco */
    label, p, span, h1, h2, h3, .stMarkdown, .stSlider, .stSelectbox, .stNumberInput {
        color: #ffffff !important;
    }
    
    /* Estilização dos Cartões de Métrica */
    div[data-testid="stMetric"] {
        background-color: #1a1c23 !important;
        border: 1px solid #2e3139;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745 !important;
    }
    div[data-testid="stMetricLabel"] > div { color: #ffffff !important; font-weight: bold; }
    div[data-testid="stMetricValue"] > div { color: #ffffff !important; }

    /* Botão Verde */
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 3.5em;
        border-radius: 8px;
    }
    
    /* Inputs visíveis */
    input {
        background-color: #262730 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (CONFIGURAÇÕES) ----------------
with st.sidebar:
    st.title("⚙️ Configurações")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    municipio = st.text_input("🏙️ Município:", "Redenção do Gurguéia")
    estado = st.selectbox("🌎 Estado:", ["PI", "MA", "BA", "TO", "CE", "PE", "RN", "PB", "AL", "SE", "MG", "GO", "MT", "MS", "SP", "RJ", "ES", "PR", "SC", "RS", "AM", "RR", "AP", "PA", "AC", "RO", "DF"])
    
    st.divider()
    area_ha = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    var_palma = ""
    if cultura == "Palma Forrageira":
        var_palma = st.selectbox("🌵 Variedade da Palma:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta de Matéria Seca (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta de Produtividade (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

# ---------------- 1️⃣ ENTRADA DE DADOS DA ANÁLISE ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.subheader("1️⃣ Dados da Análise de Solo")
col1, col2, col3 = st.columns(3)
with col1:
    p_s = st.number_input("Fósforo (P) - mg/dm³", 0.0, value=8.0)
    k_s = st.number_input("Potássio (K) - cmolc/dm³", 0.0, value=0.15)
    ph_s = st.number_input("pH em Água", 0.0, 14.0, value=5.5)
with col2:
    arg = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_at = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    al_s = st.number_input("Alumínio (Al) - cmolc/dm³", 0.0, value=0.0)
with col3:
    ctc_s = st.number_input("CTC Total (T) - cmolc/dm³", 0.0, value=3.25)
    prnt_s = st.number_input("PRNT do Calcário (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA DE INTERPRETAÇÃO (BAIXO, MÉDIO, BOM) ----------------
if arg > 35: 
    status_p = "Baixo" if p_s <= 6 else "Médio" if p_s <= 9 else "Bom"
else: 
    status_p = "Baixo" if p_s <= 12 else "Médio" if p_s <= 18 else "Bom"

status_k = "Baixo" if k_s <= 0.15 else "Médio" if k_s <= 0.30 else "Bom"

# ---------------- CÁLCULOS TÉCNICOS ----------------
v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc_ha = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)

if cultura == "Soja":
    r_n, r_p, r_k = 0, (meta_ton * 15) * (1.5 if status_p == "Baixo" else 1.0), (meta_ton * 20) * (1.4 if status_k == "Baixo" else 1.0)
elif cultura == "Milho":
    r_n, r_p, r_k = (meta_ton * 22), (meta_ton * 12) * (1.3 if status_p == "Baixo" else 1.0), (meta_ton * 18) * (1.2 if status_k == "Baixo" else 1.0)
else: # Palma Forrageira
    r_n = meta_ton * 10
    r_p = 90 * (1.5 if status_p == "Baixo" else 1.0)
    r_k = 120 * (1.5 if status_k == "Baixo" else 1.0)

# ---------------- 2️⃣ EXIBIÇÃO RESULTADOS (DASHBOARD) ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Prescrição")
r1, r2, r3 = st.columns(3)
with r1:
    st.metric("Calagem", f"{nc_ha:.2f} t/ha")
    st.write(f"Total: {(nc_ha * area_ha):.2f} t")
with r2:
    st.metric("Status Fósforo (P)", status_p)
with r3:
    st.metric("Status Potássio (K)", status_k)

st.write("### Simulação de Adubação Comercial")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N% (Nitrogênio)", 0, value=10 if cultura == "Palma Forrageira" else 4)
f_p = f2.number_input("P% (Fósforo)", 0, value=10 if cultura == "Palma Forrageira" else 20)
f_k = f3.number_input("K% (Potássio)", 0, value=20)

dose_final = max((r_p / f_p * 100) if f_p > 0 else 0, (r_k / f_k * 100) if f_k > 0 else 0)
st.success(f"Dose Recomendada: {dose_final:.0f} kg/ha | Total área: {math.ceil(dose_final * area_ha / 50)} sacos de 50kg")

# ---------------- FUNÇÃO PDF PROFISSIONAL ----------------
def clean_txt(t):
    return str(t).encode('latin-1', 'replace').decode('latin-1').replace('?', '-')

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Superior
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, clean_txt("RELATÓRIO DE PRESCRIÇÃO AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, clean_txt(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
    
    # Seção 1: Identificação
    pdf.set_text_color(0, 0, 0); pdf.ln(20); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 1. DADOS DO CLIENTE E CULTURA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, clean_txt(f" Cliente: {nome_cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, clean_txt(f" Municipio: {municipio} - {estado}"), ln=True)
    pdf.cell(190, 7, clean_txt(f" Cultura: {cultura} {var_palma} | Area: {area_ha} ha | Meta: {meta_ton} t/ha"), ln=True)
    
    # Seção 2: Análise de Solo Completa
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 2. ANALISE DE SOLO E INTERPRETACAO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 7, clean_txt(f" Fosforo (P): {p_s} mg/dm3 -> Status: {status_p}"), ln=0)
    pdf.cell(95, 7, clean_txt(f" Potassio (K): {k_s} cmolc/dm3 -> Status: {status_k}"), ln=1)
    pdf.cell(63, 7, clean_txt(f" Argila: {arg}%"), ln=0)
    pdf.cell(63, 7, clean_txt(f" pH: {ph_s}"), ln=0)
    pdf.cell(64, 7, clean_txt(f" V%: {v_at}%"), ln=1)

    # Seção 3: Recomendações
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 3. RECOMENDACOES TECNICAS"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, clean_txt(f" Calagem: {nc_ha:.2f} t/ha | Gessagem: {(arg * 50 / 1000):.2f} t/ha"), ln=True)
    pdf.cell(190, 7, clean_txt(f" Adubacao: {dose_final:.0f} kg/ha do formulado {f_n}-{f_p}-{f_k}"), ln=True)

    # Seção 4: Manejo Específico
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, clean_txt(" 4. ORIENTACOES DE MANEJO"), ln=True, fill=True)
    pdf.set_font("Arial", "I", 9)
    if cultura == "Palma Forrageira":
        notas = [
            f"- Variedade: {var_palma}",
            "- REGRA CRITICA: JAMAIS realizar o corte da RAQUETE MAE.",
            "- A preservacao da base garante a longevidade e vigor do palmal.",
            "- Primeiro corte sugerido entre 18 a 24 meses após o plantio.",
            "- Recomendado aplicacao de adubo organico (esterco bovino curtido)."
        ]
    elif cultura == "Milho":
        notas = ["- Fracionar Nitrogenio: 30% no plantio e 70% em cobertura (V4-V6)."]
    else:
        notas = ["- Realizar inoculacao de sementes e monitorar pragas iniciais."]
    for n in notas: pdf.cell(190, 6, clean_txt(n), ln=True)

    return pdf.output(dest='S').encode('latin-1')

# ---------------- FINALIZAÇÃO ----------------
st.divider()
st.info(f"💡 O sistema está configurado para a cultura: **{cultura}**.")

if st.button("📄 GERAR RELATÓRIO PDF PROFISSIONAL"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Recomendacao_{cultura}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
