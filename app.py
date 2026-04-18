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

# ---------------- ESTILO VISUAL LIGHT ----------------
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
    area_input = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01)
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    var_palma = ""
    if cultura == "Palma Forrageira":
        var_palma = st.selectbox("🌵 Variedade:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

# ---------------- 1️⃣ ENTRADA DE DADOS ----------------
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
nc_ha = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)
ng_ha = (arg * 50) / 1000 if (al_s > 0.5) else 0.0

# Nitrogênio, Fósforo e Potássio (Recomendação Bruta por ha)
if cultura == "Soja":
    r_n, r_p, r_k = 0, (meta_ton * 15), (meta_ton * 20)
elif cultura == "Milho":
    r_n, r_p, r_k = (meta_ton * 22), (meta_ton * 12), (meta_ton * 18)
else: # Palma
    r_n = meta_ton * 12
    r_p = 90 * (1.5 if st_p == "Baixo" else 1.0)
    r_k = 150 * (1.5 if st_k == "Baixo" else 1.0)

# ---------------- 2️⃣ DASHBOARD (COM CÁLCULO DE ÁREA TOTAL) ----------------
st.divider()
st.subheader(f"2️⃣ Diagnóstico e Prescrição (Área: {area_input} ha)")
r1, r2, r3, r4 = st.columns(4)

with r1:
    st.metric("CALAGEM (t/ha)", f"{nc_ha:.2f}")
    st.write(f"**Total Área:** {nc_ha * area_input:.2f} t")

with r2:
    st.metric("GESSAGEM (t/ha)", f"{ng_ha:.2f}")
    st.write(f"**Total Área:** {ng_ha * area_input:.2f} t")

with r3:
    st.metric("STATUS P", st_p)
    st.write(f"Teor: {p_s} mg/dm³")

with r4:
    st.metric("STATUS K", st_k)
    st.write(f"Teor: {k_s} cmolc/dm³")

# ---------------- 3️⃣ ADUBAÇÃO COMERCIAL ----------------
st.write("---")
st.subheader("3️⃣ Planejamento de Adubação Comercial")
f1, f2, f3 = st.columns(3)
val_n = 10 if cultura == "Palma Forrageira" else 0
val_p = 10 if cultura == "Palma Forrageira" else 20
f_n = f1.number_input("N% (Nitrogênio)", 0, value=val_n)
f_p = f2.number_input("P% (Fósforo)", 0, value=val_p)
f_k = f3.number_input("K% (Potássio)", 0, value=20)

if f_p > 0 or f_k > 0:
    dose_ha = max((r_p/f_p*100) if f_p>0 else 0, (r_k/f_k*100) if f_k>0 else 0)
    total_necessario = dose_ha * area_input
    total_sacos = math.ceil(total_necessario / 50)
    
    st.success(f"📌 **Dose por Hectare:** {dose_ha:.0f} kg/ha")
    st.info(f"🚜 **TOTAL PARA A ÁREA ({area_input} ha):** {total_necessario:.0f} kg — **({total_sacos} sacos de 50kg)**")

# ---------------- 4️⃣ PDF COMPLETO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, fix("RECOMENDAÇÃO TÉCNICA AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, fix(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
    
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 1. DIAGNÓSTICO E ÁREA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, fix(f" Cliente: {nome_cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, fix(f" Cultura: {cultura} {var_palma} | Área Total: {area_input} ha"), ln=True)
    
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 2. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, fix(f" Calagem: {nc_ha:.2f} t/ha (Total area: {nc_ha*area_input:.2f} t)"), ln=True)
    pdf.cell(190, 7, fix(f" Gessagem: {ng_ha:.2f} t/ha (Total area: {ng_ha*area_input:.2f} t)"), ln=True)
    pdf.cell(190, 7, fix(f" Adubacao Comercial ({f_n}-{f_p}-{f_k}): {dose_ha:.0f} kg/ha"), ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 7, fix(f" COMPRA TOTAL: {total_sacos} sacos de 50kg para os {area_input} ha."), ln=True)

    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 3. MANEJO E OBSERVAÇÕES"), ln=True, fill=True)
    pdf.set_font("Arial", "", 9)
    
    if cultura == "Palma Forrageira":
        obs = [
            f"- Variedade: {var_palma}.",
            "- PROIBIDO cortar a raquete mae.",
            "- Primeiro corte sugerido entre 18-24 meses.",
            "- Aplicar nitrogenio (N) apos o inicio das chuvas ou irrigacao."
        ]
    else:
        obs = ["- Monitorar pragas e doencas.", "- Aplicar cobertura conforme umidade do solo."]
    
    for item in obs: pdf.multi_cell(190, 5, fix(item))

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Relatorio_{nome_cliente}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
