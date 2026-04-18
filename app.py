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

# ---------------- ESTILO VISUAL ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745 !important;
    }
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("Configurações")
    nome_cliente = st.text_input("👨‍🌾 Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    municipio = st.text_input("🏙️ Município:", "")
    estado = st.selectbox("🌎 Estado:", ["PI", "MA", "BA", "TO", "CE", "PE", "RN", "PB", "AL", "SE", "MG", "GO", "MT", "MS", "SP", "RJ", "ES", "PR", "SC", "RS", "AM", "RR", "AP", "PA", "AC", "RO", "DF"])
    
    st.divider()
    area = st.number_input("📏 Área (ha):", min_value=0.01, value=1.0, step=0.01)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    var_palma = ""
    if cultura == "Palma Forrageira":
        var_palma = st.selectbox("🌵 Variedade:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

# ---------------- 1️⃣ ANÁLISE DE SOLO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {data_hoje}")

st.subheader("1️⃣ Dados da Análise de Solo")
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

# ---------------- LÓGICA TÉCNICA ----------------
classe_txt = "Argiloso" if arg > 35 else "Arenoso/Médio"
if arg > 35: st_p = "Baixo" if p_s <= 6 else "Médio" if p_s <= 9 else "Bom"
else: st_p = "Baixo" if p_s <= 12 else "Médio" if p_s <= 18 else "Bom"
st_k = "Baixo" if k_s <= 0.15 else "Médio" if k_s <= 0.30 else "Bom"

v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)
ng = (arg * 50) / 1000 if (al_s > 0.5) else 0.0

# Recomendação de N-P-K
if cultura == "Soja":
    r_n, r_p, r_k = 0, (meta_ton * 15), (meta_ton * 20)
elif cultura == "Milho":
    r_n, r_p, r_k = (meta_ton * 22), (meta_ton * 12), (meta_ton * 18)
else: # Palma Forrageira (Lógica de exportação por t MS)
    r_n = meta_ton * 12 # Palma exige muito N para proteína
    r_p = 90 * (1.5 if st_p == "Baixo" else 1.0)
    r_k = 150 * (1.5 if st_k == "Baixo" else 1.0) # Potássio é a alma da palma

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Recomendações")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Calagem", f"{nc:.2f} t/ha")
m2.metric("Gessagem", f"{ng:.2f} t/ha")
m3.metric("Status P", st_p)
m4.metric("Status K", st_k)

st.write("---")
st.subheader("3️⃣ Planejamento de Adubação")
c1, c2 = st.columns([1, 2])
with c1:
    st.info(f"Cultura: {cultura}")
    if cultura == "Palma Forrageira":
        st.metric("Nitrogênio Total (N)", f"{r_n:.0f} kg/ha")
    elif cultura == "Milho":
        st.metric("Nitrogênio Total (N)", f"{r_n:.0f} kg/ha")

with c2:
    st.markdown("### 🛒 Formulação Comercial")
    f1, f2, f3 = st.columns(3)
    val_n = 10 if cultura == "Palma Forrageira" else 0
    val_p = 10 if cultura == "Palma Forrageira" else 20
    f_n = f1.number_input("N%", 0, value=val_n)
    f_p = f2.number_input("P%", 0, value=val_p)
    f_k = f3.number_input("K%", 0, value=20)
    
    if f_p > 0 or f_k > 0:
        dose = max((r_p/f_p*100) if f_p>0 else 0, (r_k/f_k*100) if f_k>0 else 0)
        st.success(f"**Dose Sugerida:** {dose:.0f} kg/ha | **Total:** {math.ceil(dose*area/50)} sacos")

# ---------------- 4️⃣ PDF COM OBSERVAÇÕES ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, fix("RECOMENDAÇÃO TÉCNICA AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, fix(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
    
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 1. DIAGNÓSTICO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, fix(f" Cliente: {nome_cliente} | Fazenda: {fazenda} | Cultura: {cultura} {var_palma}"), ln=True)
    pdf.cell(190, 7, fix(f" Area: {area} ha | Meta: {meta_ton} t/ha | Textura: {classe_txt}"), ln=True)
    
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 2. PRESCRIÇÃO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, fix(f" Calagem: {nc:.2f} t/ha | Gessagem: {ng:.2f} t/ha"), ln=True)
    pdf.cell(190, 7, fix(f" Adubacao Comercial: {dose:.0f} kg/ha do {f_n}-{f_p}-{f_k}"), ln=True)
    if cultura == "Palma Forrageira" or cultura == "Milho":
        pdf.cell(190, 7, fix(f" Necessidade de Nitrogenio (N): {r_n:.0f} kg/ha"), ln=True)

    # OBSERVAÇÕES DE MANEJO (O que você pediu!)
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 3. OBSERVAÇÕES TÉCNICAS E MANEJO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 9)
    
    if cultura == "Palma Forrageira":
        obs = [
            f"- Variedade selecionada: {var_palma}.",
            "- REGRA DE OURO: JAMAIS realizar o corte na RAQUETE MAE (Cladodio inicial).",
            "- A preservacao da raquete mae garante a longevidade e o rebrote do palmal.",
            "- O primeiro corte deve ser feito entre 18 e 24 meses apos o plantio.",
            "- Para a Palma Miuda: exige maior controle de plantas daninhas e maior aporte de K.",
            "- Para a Orelha de Elefante: foco em espacamento para permitir mecanizacao.",
            "- Recomendado aplicar 20 a 30 t/ha de esterco bovino curtido no plantio."
        ]
    else:
        obs = ["- Monitorar pragas e doencas periodicamente.", "- Realizar cobertura nitrogenada com solo umido."]
    
    for item in obs:
        pdf.multi_cell(190, 5, fix(item))

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO COMPLETO (PDF)"):
    pdf_out = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_out, file_name=f"Relatorio_{cultura}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
