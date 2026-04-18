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
    senha = st.text_input("Digite a senha para acessar o sistema:", type="password")
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

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Configurações")

    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    municipio = st.text_input("🏙️ Município:", "")
    estado = st.selectbox("🌎 Estado:", ["PI","MA","BA","CE","TO","GO","MT","MS","MG","SP"])

    st.divider()

    # ✅ ÁREA CORRIGIDA
    area = st.number_input("📏 Área Total (ha):", min_value=0.001, value=1.0, step=0.001, format="%.3f")
    st.caption("Permite áreas menores que 1 ha (ex: 0.100 ha, 0.500 ha)")

    # ✅ CULTURA COM PALMA
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma"], horizontal=True)

    if cultura == "Palma":
        variedade = st.selectbox("🌵 Variedade de Palma:", ["Miúda", "Orelha de Elefante"])
        st.info("💡 Aplicar entre 20 e 30 t/ha de esterco curtido")

    meta_ton = st.select_slider(
        "🎯 Meta de Produtividade (t/ha):",
        options=[float(i/2) for i in range(2, 31)],
        value=4.0 if cultura == "Soja" else 8.0
    )

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- CABEÇALHO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {data_hoje}")

# ---------------- SOLO ----------------
st.subheader("1️⃣ Análise de Solo")

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

# ---------------- LÓGICA ----------------
def classificar_textura(arg):
    if arg < 15: return "Arenoso"
    elif arg < 35: return "Médio"
    elif arg < 60: return "Argiloso"
    else: return "Muito Argiloso"

classe_txt = classificar_textura(argila)

v_alvo = 70 if cultura in ["Soja", "Palma"] else 60

nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

ng = (50 * argila) / 1000 if (al_solo > 0.5 or argila > 40) else 0.0
total_gesso = ng * area

# ---------------- ADUBAÇÃO ----------------
rec_p = meta_ton * 15
rec_k = meta_ton * 20

st.subheader("3️⃣ Adubação")

c1, c2, c3 = st.columns(3)
f_n = c1.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
f_p = c2.number_input("P%", 0, value=20)
f_k = c3.number_input("K%", 0, value=20)

dose_final = 0
if f_p > 0 or f_k > 0:
    dose_p = (rec_p / f_p * 100) if f_p > 0 else 0
    dose_k = (rec_k / f_k * 100) if f_k > 0 else 0
    dose_final = max(dose_p, dose_k)

total_adubo = dose_final * area
sacos = math.ceil(total_adubo / 50)

# ---------------- RESULTADOS ----------------
st.subheader("📊 Resultados")

r1, r2, r3 = st.columns(3)

r1.metric("Calcário (t/ha)", f"{nc:.2f}")
r1.metric("Total Calcário (t)", f"{total_calc:.2f}")

r2.metric("Gesso (t/ha)", f"{ng:.2f}")
r2.metric("Total Gesso (t)", f"{total_gesso:.2f}")

r3.metric("Adubo (kg/ha)", f"{dose_final:.0f}")
r3.metric("Total Adubo (kg)", f"{total_adubo:.0f}")

st.success(f"📦 Sacos necessários: {sacos}")

# ---------------- PDF ORIGINAL (MANTIDO) ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix_txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    data_pdf = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 15, fix_txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 5, fix_txt(f"Consultor: Felipe Amorim | Data: {data_pdf}"), align="C", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f"Cliente: {nome_cliente_input}"), ln=True)
    pdf.cell(190, 7, fix_txt(f"Área: {area} ha"), ln=True)

    pdf.cell(190, 7, fix_txt(f"Calcário: {nc:.2f} t/ha | Total: {total_calc:.2f} t"), ln=True)
    pdf.cell(190, 7, fix_txt(f"Gesso: {ng:.2f} t/ha | Total: {total_gesso:.2f} t"), ln=True)
    pdf.cell(190, 7, fix_txt(f"Adubo: {dose_final:.0f} kg/ha | Total: {total_adubo:.0f} kg"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 GERAR RELATÓRIO"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Relatorio_{nome_para_arquivo}.pdf")
