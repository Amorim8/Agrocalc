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
        border-radius: 12px;
        border-left: 8px solid #28a745 !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #1a1c23 !important;
    }
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Ajustes de Campo")
    nome_cliente = st.text_input("👨‍🌾 Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    area_total = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01)
    
    st.divider()
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

# ---------------- LÓGICA DE CLASSIFICAÇÃO NPK ----------------
# Lógica para Fósforo (P) baseada em Argila
if arg > 60:
    st_p = "Baixo" if p_s <= 4.0 else "Médio" if p_s <= 6.0 else "Alto"
elif arg > 35:
    st_p = "Baixo" if p_s <= 6.0 else "Médio" if p_s <= 9.0 else "Alto"
elif arg > 15:
    st_p = "Baixo" if p_s <= 12.0 else "Médio" if p_s <= 18.0 else "Alto"
else:
    st_p = "Baixo" if p_s <= 20.0 else "Médio" if p_s <= 30.0 else "Alto"

# Lógica para Potássio (K)
st_k = "Baixo" if k_s <= 0.15 else "Médio" if k_s <= 0.30 else "Alto"

# Lógica para Nitrogênio (N) - Geralmente baseada em Matéria Orgânica ou histórico, 
# aqui simulamos pela meta de produtividade/cultura
st_n = "Baixo" if meta_ton < (10 if cultura=="Palma Forrageira" else 4) else "Médio" if meta_ton < (25 if cultura=="Palma Forrageira" else 8) else "Alto"

# ---------------- CÁLCULOS TÉCNICOS ----------------
v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc_ha = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)
ng_ha = (arg * 50) / 1000 if (al_s > 0.5) else 0.0

if cultura == "Soja":
    r_n, r_p, r_k = 0, (meta_ton * 15), (meta_ton * 20)
elif cultura == "Milho":
    r_n, r_p, r_k = (meta_ton * 22), (meta_ton * 12), (meta_ton * 18)
else: # Palma
    r_n, r_p, r_k = (meta_ton * 12), 90 * (1.5 if st_p == "Baixo" else 1.0), 150 * (1.5 if st_k == "Baixo" else 1.0)

# ---------------- 2️⃣ DASHBOARD: STATUS E CORRETIVOS ----------------
st.divider()
st.subheader(f"2️⃣ Diagnóstico NPK e Corretivos ({area_total} ha)")

# Status Nutricional
s1, s2, s3 = st.columns(3)
s1.metric("Status Nitrogênio (N)", st_n)
s2.metric("Status Fósforo (P)", st_p)
s3.metric("Status Potássio (K)", st_k)

# Calcário e Gesso
st.markdown("---")
c_col1, c_col2, g_col1, g_col2 = st.columns(4)
c_col1.metric("CALCÁRIO (t/ha)", f"{nc_ha:.2f}")
c_col2.metric("TOTAL CALCÁRIO (t)", f"{nc_ha * area_total:.2f}")
g_col1.metric("GESSO (t/ha)", f"{ng_ha:.2f}")
g_col2.metric("TOTAL GESSO (t)", f"{ng_ha * area_total:.2f}")

# ---------------- 3️⃣ ADUBAÇÃO COMERCIAL ----------------
st.write("---")
st.subheader("3️⃣ Planejamento de Adubação Comercial")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N%", 0, value=10 if cultura=="Palma Forrageira" else 0)
f_p = f2.number_input("P%", 0, value=10 if cultura=="Palma Forrageira" else 20)
f_k = f3.number_input("K%", 0, value=20)

if f_p > 0 or f_k > 0:
    dose_ha = max((r_p/f_p*100) if f_p>0 else 0, (r_k/f_k*100) if f_k>0 else 0)
    total_adubo_kg = dose_ha * area_total
    total_sacos = math.ceil(total_adubo_kg / 50)
    
    a1, a2, a3 = st.columns(3)
    a1.metric("DOSE (kg/ha)", f"{dose_ha:.0f}")
    a2.metric(f"TOTAL ({area_total} ha)", f"{total_adubo_kg:.0f} kg")
    a3.metric("COMPRA (SACOS)", f"{total_sacos}")

# ---------------- 4️⃣ PDF RELATÓRIO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 15, fix("RECOMENDAÇÃO TÉCNICA AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, fix(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
    
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(f" 1. STATUS DA FERTILIDADE - AREA: {area_total} ha"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, fix(f" Nitrogenio: {st_n} | Fosforo: {st_p} | Potassio: {st_k}"), ln=True)
    pdf.cell(190, 7, fix(f" Cliente: {nome_cliente} | Fazenda: {fazenda} | Cultura: {cultura}"), ln=True)
    
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 2. RECOMENDACOES TOTAIS"), ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 7, fix(f" - CALCARIO: {nc_ha * area_total:.2f} t"), ln=True)
    pdf.cell(190, 7, fix(f" - GESSO: {ng_ha * area_total:.2f} t"), ln=True)
    pdf.cell(190, 7, fix(f" - ADUBO ({f_n}-{f_p}-{f_k}): {total_adubo_kg:.0f} kg ({total_sacos} sacos)"), ln=True)

    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, fix(" 3. MANEJO E OBSERVACOES"), ln=True, fill=True)
    pdf.set_font("Arial", "", 9)
    if cultura == "Palma Forrageira":
        obs = ["- PROIBIDO cortar a raquete mae.", f"- Variedade: {var_palma}.", "- Manejo de Nitrogenio apos as chuvas."]
    else:
        obs = ["- Monitorar umidade para cobertura.", "- Controle preventivo de pragas e doencas."]
    for item in obs: pdf.multi_cell(190, 5, fix(item))

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Recomendacao_{nome_cliente}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
