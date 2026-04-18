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
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide")

st.markdown("""
<style>
.main { background-color: #0e1117; }
.stButton>button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color: white; font-weight:bold; height:3em;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🌿 Configurações")
    nome_cliente = st.text_input("Cliente")
    fazenda = st.text_input("Fazenda")
    municipio = st.text_input("Município")
    estado = st.selectbox("Estado", ["PI","MA","BA","CE","TO","GO","MT","MS","MG","SP"])

    area = st.number_input("Área (ha)", min_value=0.001, value=1.0, step=0.001)
    cultura = st.radio("Cultura", ["Soja", "Milho", "Palma"])

    if cultura == "Palma":
        variedade = st.selectbox("Variedade", ["Miúda", "Orelha de Elefante"])
        st.info("Aplicar 20 a 30 t/ha de esterco")

    meta_ton = st.number_input("Meta (t/ha)", value=4.0)

# ---------------- CABEÇALHO ----------------
st.title("🌱 PRESCRIÇÃO AGRONÔMICA")
st.write(f"Consultor: Felipe Amorim | Data: {data_hoje}")

# ---------------- SOLO ----------------
st.subheader("Análise de Solo")

col1, col2, col3 = st.columns(3)

with col1:
    p = st.number_input("Fósforo", value=8.0)
    k = st.number_input("Potássio", value=0.15)
    ph = st.number_input("pH", value=5.5)

with col2:
    arg = st.number_input("Argila (%)", value=35.0)
    v = st.number_input("V%", value=40.0)
    al = st.number_input("Alumínio", value=0.0)

with col3:
    ctc = st.number_input("CTC", value=3.25)
    prnt = st.number_input("PRNT", value=85.0)

# ---------------- CLASSIFICAÇÃO ----------------
def textura(arg):
    if arg < 15: return "Arenoso"
    elif arg < 35: return "Médio"
    elif arg < 60: return "Argiloso"
    else: return "Muito Argiloso"

classe = textura(arg)

def status(valor, b, m):
    if valor <= b: return "Baixo"
    elif valor <= m: return "Médio"
    else: return "Alto"

status_p = status(p, 8, 15)
status_k = status(k, 0.15, 0.30)

# ---------------- CALAGEM ----------------
v_alvo = 70 if cultura in ["Soja","Palma"] else 60
nc = max(0, ((v_alvo - v) * ctc) / prnt)
total_calc = nc * area

# ---------------- GESSAGEM ----------------
ng = (50 * arg)/1000 if (al > 0.5 or arg > 40) else 0
total_gesso = ng * area

# ---------------- NUTRIENTES ----------------
if cultura == "Milho":
    rec_n = meta_ton * 25
    n_plantio = rec_n * 0.2
    n_cobertura = rec_n * 0.8
else:
    rec_n = 0

rec_p = meta_ton * 15
rec_k = meta_ton * 20

# ---------------- ADUBO ----------------
st.subheader("Formulação")

c1,c2,c3 = st.columns(3)
f_n = c1.number_input("N%", value=4)
f_p = c2.number_input("P%", value=20)
f_k = c3.number_input("K%", value=20)

dose_final = 0
if f_p > 0 or f_k > 0:
    dose_p = (rec_p / f_p * 100) if f_p>0 else 0
    dose_k = (rec_k / f_k * 100) if f_k>0 else 0
    dose_final = max(dose_p, dose_k)

total_adubo = dose_final * area
sacos = math.ceil(total_adubo / 50)

# ---------------- RESULTADOS ----------------
st.subheader("📊 Resultados")

r1,r2,r3 = st.columns(3)

r1.metric("Calcário (t/ha)", f"{nc:.2f}")
r1.metric("Total Calcário (t)", f"{total_calc:.2f}")

r2.metric("Gesso (t/ha)", f"{ng:.2f}")
r2.metric("Total Gesso (t)", f"{total_gesso:.2f}")

r3.metric("Adubo (kg/ha)", f"{dose_final:.0f}")
r3.metric("Total Adubo (kg)", f"{total_adubo:.0f}")

st.success(f"Sacos necessários: {sacos}")

# ---------------- PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1','replace').decode('latin-1')

    pdf.set_font("Arial","B",14)
    pdf.cell(190,10,fix("PRESCRIÇÃO TÉCNICA AGRONÔMICA"),0,1,"C")

    pdf.set_font("Arial","",10)
    pdf.cell(190,6,fix(f"Cliente: {nome_cliente}"),0,1)
    pdf.cell(190,6,fix(f"Área: {area} ha"),0,1)

    pdf.cell(190,6,fix(f"Calcário: {nc:.2f} t/ha | Total: {total_calc:.2f} t"),0,1)
    pdf.cell(190,6,fix(f"Gesso: {ng:.2f} t/ha | Total: {total_gesso:.2f} t"),0,1)
    pdf.cell(190,6,fix(f"Adubo: {dose_final:.0f} kg/ha | Total: {total_adubo:.0f} kg"),0,1)

    pdf.ln(5)
    pdf.multi_cell(190,5,fix(
        "Referências:\n"
        "- Manual de Adubação e Calagem (SBCS)\n"
        "- Embrapa Cerrados\n"
        "- Embrapa Milho e Sorgo\n"
        "- IPA Palma Forrageira"
    ))

    return pdf.output(dest='S').encode('latin-1')

if st.button("Gerar PDF"):
    pdf = gerar_pdf()
    st.download_button("Baixar", pdf, "relatorio.pdf")
