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
st.set_page_config(page_title="Felipe Amorim | Consultoria Agronômica", layout="wide", page_icon="🌿")

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

# ---------------- SIDEBAR (PARÂMETROS) ----------------
with st.sidebar:
    st.title("🌿 Parâmetros")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma"], horizontal=True)
    
    variedade = ""
    if cultura == "Palma":
        variedade = st.selectbox("🌵 Variedade:", ["Miúda", "Orelha de Elefante", "Sertânia"])
    
    meta_ton = st.number_input("🎯 Meta de Produtividade (t/ha):", value=8.0)

# ---------------- ANÁLISE DE SOLO ----------------
st.title("SISTEMA DE PRESCRIÇÃO | FELIPE AMORIM")
st.write(f"Data: {data_hoje}")

st.subheader("Entrada de Dados - Solo")
c1, c2, c3, c4 = st.columns(4)
with c1:
    ph_solo = st.number_input("pH (Água)", value=5.5)
    p_solo = st.number_input("Fósforo (mg/dm³)", value=8.0)
with c2:
    al_solo = st.number_input("Alumínio (cmolc/dm³)", value=0.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", value=0.15)
with c3:
    argila = st.number_input("Argila (%)", value=35.0)
    v_atual = st.number_input("V% Atual", value=40.0)
with c4:
    ctc_t = st.number_input("CTC (T)", value=3.25)
    prnt_calc = st.number_input("PRNT Calcário (%)", value=85.0)

# ---------------- CÁLCULOS TÉCNICOS ----------------
# 1. Calagem e Gessagem
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area
ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 
total_gesso = ng * area

# 2. Adubação NPK (kg/ha de nutriente puro)
rec_p = meta_ton * 15
rec_k = meta_ton * 20

# 3. Lógica de Nitrogênio para Milho (Embrapa)
# Extração média: 25kg de N por tonelada de milho produzida
n_necessario_total_ha = meta_ton * 25 if cultura == "Milho" else 0
n_plantio_ha = n_necessario_total_ha * 0.20
n_cobertura_ha = n_necessario_total_ha * 0.80

total_n_plantio_area = n_plantio_ha * area
total_n_cobertura_area = n_cobertura_ha * area

# ---------------- CONFIGURAÇÃO ADUBO COMERCIAL ----------------
st.subheader("Configuração da Fórmula Comercial")
f1, f2, f3 = st.columns(3)
fn, fp, fk = f1.number_input("N %", 4), f2.number_input("P %", 20), f3.number_input("K %", 20)

dose_ha = max((rec_p/fp*100) if fp>0 else 0, (rec_k/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area

# ---------------- RESULTADOS EM TELA ----------------
st.subheader("Resumo das Recomendações")
res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc:.2f}", help=f"Total: {total_calc:.2f} t")
res2.metric("Gesso (t/ha)", f"{ng:.2f}", help=f"Total: {total_gesso:.2f} t")
res3.metric("Adubo (kg/ha)", f"{dose_ha:.0f}", help=f"Total: {total_adubo:.1f} kg")

# NOVA SEÇÃO VISUAL PARA VALORES DE N (MILHO)
if cultura == "Milho":
    st.divider()
    st.subheader("📊 Detalhamento do Manejo de Nitrogênio (N)")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.metric("N no Plantio (20%)", f"{n_plantio_ha:.1f} kg/ha")
        st.write(f"**Total para a área:** {total_n_plantio_area:.1f} kg de N")
    with col_n2:
        st.metric("N na Cobertura (80%)", f"{n_cobertura_ha:.1f} kg/ha")
        st.write(f"**Total para a área:** {total_n_cobertura_area:.1f} kg de N")
    st.info(f"Cálculo baseado na extração de 25kg de N por tonelada para uma meta de {meta_ton} t/ha.")

# ---------------- GERAÇÃO DO PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.ln(12)
    pdf.cell(190, 10, fix("PRESCRIÇÃO AGRONÔMICA ESPECIALIZADA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(190, 7, fix(f"Felipe Amorim - Consultoria Técnica | {data_hoje}"), 0, 1, "C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(18)

    # Identificação
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, fix("1. DADOS DA PROPRIEDADE"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"Produtor: {nome_cliente} | Fazenda: {fazenda}"), 0, 1)
    pdf.cell(190, 7, fix(f"Cultura: {cultura} | Meta: {meta_ton} t/ha | Area: {area:g} ha"), 0, 1)

    # Recomendação
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("2. RECOMENDAÇÃO TÉCNICA"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"- Calcario: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), 0, 1)
    pdf.cell(190, 7, fix(f"- Gesso: {ng:.2f} t/ha (Total: {total_gesso:.2f} t)"), 0, 1)
    pdf.cell(190, 7, fix(f"- Adubo Comercial: {dose_ha:.0f} kg/ha (Total: {total_adubo:.1f} kg)"), 0, 1)

    # DETALHAMENTO DE N NO PDF
    if cultura == "Milho":
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(190, 8, fix("3. DETALHAMENTO DE NITROGÊNIO (N)"), 1, 1, "L", fill=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.ln(2)
        pdf.cell(190, 7, fix(f"A Meta de {meta_ton} t/ha exige um total de {n_necessario_total_ha:.1f} kg/ha de N puro."), 0, 1)
        pdf.cell(190, 7, fix(f"- N no Plantio (20%): {n_plantio_ha:.1f} kg/ha (Total area: {total_n_plantio_area:.1f} kg)"), 0, 1)
        pdf.cell(190, 7, fix(f"- N na Cobertura (80%): {n_cobertura_ha:.1f} kg/ha (Total area: {total_n_cobertura_area:.1f} kg)"), 0, 1)

    # Orientações e Referências
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("4. ORIENTAÇÕES E REFERÊNCIAS"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    if cultura == "Palma":
        pdf.multi_cell(190, 5, fix("- NÃO cortar a planta-mãe. Preservar o 1º cladódio.\n- Adubação orgânica: 20-30 t/ha de esterco."))
    pdf.multi_cell(190, 5, fix("Referências: SBCS, Embrapa Milho e Sorgo, IPA Brasil."))

    return pdf.output(dest='S').encode('latin-1')

# ---------------- DOWNLOAD ----------------
st.divider()
if st.button("📄 Gerar Relatório Profissional"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Consultoria_{nome_cliente}.pdf", mime="application/pdf")
