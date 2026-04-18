import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- LOGIN ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- CONFIG VISUAL ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
<style>
.main { background-color: #0e1117; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1f2937, #111827) !important;
    border: 1px solid #374151;
    padding: 18px;
    border-radius: 12px;
    border-left: 6px solid #22c55e !important;
}
div[data-testid="stMetric"] label { color: #9ca3af !important; }
div[data-testid="stMetric"] div { color: #f9fafb !important; font-size: 26px; font-weight: bold; }
.stButton>button {
    background-color: #28a745 !important;
    color: white !important;
    font-weight: bold;
    width: 100%;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🌿 Configurações")
    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma"], horizontal=True)

    variedade = ""
    if cultura == "Palma":
        variedade = st.selectbox("🌵 Variedade:", ["Miúda", "Orelha de Elefante"])
    
    meta_ton = st.number_input("🎯 Meta (t/ha):", value=4.0 if cultura=="Soja" else 8.0)

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- ANÁLISE DE SOLO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"Consultor: Felipe Amorim | Data: {data_hoje}")

st.subheader("Análise de Solo")
c1, c2, c3 = st.columns(3)
with c1:
    p_solo = st.number_input("Fósforo (mg/dm³)", value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", value=0.15)
with c2:
    argila = st.number_input("Argila (%)", value=35.0)
    v_atual = st.number_input("V% Atual", value=40.0)
with c3:
    ctc_t = st.number_input("CTC (T)", value=3.25)
    prnt_calc = st.number_input("PRNT do Calcário (%)", value=85.0)

# ---------------- LÓGICA TÉCNICA ----------------
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area

ng = (50 * argila)/1000 if (argila > 40) else 0 
total_gesso = ng * area

rec_p = meta_ton * 15
rec_k = meta_ton * 20

# Nitrogênio (N) - Ref: Embrapa Milho
rec_n = meta_ton * 25 if cultura == "Milho" else 0
n_plantio = rec_n * 0.2
n_cobertura = rec_n * 0.8
n_plantio_total = n_plantio * area
n_cobertura_total = n_cobertura * area

# Configuração do Adubo
st.subheader("Configuração da Adubação")
f1, f2, f3 = st.columns(3)
fn = f1.number_input("N (%)", value=4)
fp = f2.number_input("P (%)", value=20)
fk = f3.number_input("K (%)", value=20)

dose_ha = max((rec_p/fp*100) if fp>0 else 0, (rec_k/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area
sacos_50kg = math.ceil(total_adubo / 50)

# ---------------- RESULTADOS ----------------
st.subheader("Resultados da Recomendação")
res1, res2, res3 = st.columns(3)

with res1:
    st.metric("Calcário (t/ha)", f"{nc:.2f}")
    st.metric("Total Calcário (t)", f"{total_calc:.2f}")
with res2:
    st.metric("Gesso (t/ha)", f"{ng:.2f}")
    st.metric("Total Gesso (t)", f"{total_gesso:.2f}")
with res3:
    st.metric("Adubo (kg/ha)", f"{dose_ha:.0f}")
    st.metric("Total Adubo (kg)", f"{total_adubo:.1f}")

if cultura == "Milho":
    st.divider()
    st.subheader("📊 Detalhamento Nitrogenado (Embrapa)")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.metric("N Plantio (kg/ha)", f"{n_plantio:.1f}")
        st.metric("Total N Plantio (kg)", f"{n_plantio_total:.1f}")
    with col_n2:
        st.metric("N Cobertura (kg/ha)", f"{n_cobertura:.1f}")
        st.metric("Total N Cobertura (kg)", f"{n_cobertura_total:.1f}")

st.success(f"Logística: {sacos_50kg} sacos de 50kg necessários.")

# ---------------- GERAR PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.ln(10)
    pdf.cell(190, 10, fix("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(190, 5, fix(f"Consultor: Felipe Amorim | Data: {data_hoje}"), 0, 1, "C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)

    # Identificação
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(235, 245, 235)
    pdf.cell(190, 8, fix("1. IDENTIFICAÇÃO"), 0, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"Cliente: {nome_cliente_input} | Fazenda: {fazenda}"), 0, 1)
    pdf.cell(190, 7, fix(f"Local: {municipio}-{estado} | Área: {area:g} ha | Cultura: {cultura}"), 0, 1)

    # Recomendações
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("2. RECOMENDAÇÃO TÉCNICA"), 0, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"Calcário (PRNT {prnt_calc}%): {nc:.2f} t/ha | Gesso: {ng:.2f} t/ha"), 0, 1)
    pdf.cell(190, 7, fix(f"Adubação NPK: {dose_ha:.0f} kg/ha | Total: {total_adubo:.1f} kg"), 0, 1)

    if cultura == "Milho":
        pdf.cell(190, 7, fix(f"N Plantio: {n_plantio:.1f} kg/ha | N Cobertura: {n_cobertura:.1f} kg/ha"), 0, 1)

    # Observações e Fontes
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("3. OBSERVAÇÕES E FONTES"), 0, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    pdf.multi_cell(190, 5, fix("Recomendação exclusiva pelos dados que foram inseridos.\nFontes: SBCS, Embrapa Cerrados, Embrapa Milho e Sorgo, IPA Brasil."))

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 Gerar Relatório"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Prescricao_{nome_para_arquivo}.pdf", mime="application/pdf")
