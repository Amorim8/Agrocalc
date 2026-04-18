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

div[data-testid="stMetric"] label {
    color: #9ca3af !important;
}

div[data-testid="stMetric"] div {
    color: #f9fafb !important;
    font-size: 28px;
    font-weight: bold;
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
    st.title("🌿 Configurações")

    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])

    st.divider()

    area = st.number_input("📏 Área Total (ha):", min_value=0.001, value=1.0, step=0.001, format="%.3f")
    st.caption("Permite áreas menores que 1 ha (ex: 0.100 ha)")

    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma"], horizontal=True)

    if cultura == "Palma":
        variedade = st.selectbox("🌵 Variedade:", ["Miúda", "Orelha de Elefante"])
        st.info("Aplicar entre 20 e 30 t/ha de esterco curtido")

    meta_ton = st.number_input("🎯 Meta (t/ha):", value=4.0 if cultura=="Soja" else 8.0)

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- CABEÇALHO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"Consultor: Felipe Amorim | Data: {data_hoje}")

# ---------------- SOLO ----------------
st.subheader("Análise de Solo")

c1,c2,c3 = st.columns(3)

with c1:
    p = st.number_input("Fósforo", value=8.0)
    k = st.number_input("Potássio", value=0.15)
    ph = st.number_input("pH", value=5.5)

with c2:
    arg = st.number_input("Argila (%)", value=35.0)
    v = st.number_input("V%", value=40.0)
    al = st.number_input("Alumínio", value=0.0)

with c3:
    ctc = st.number_input("CTC", value=3.25)
    prnt = st.number_input("PRNT", value=85.0)

# ---------------- LÓGICA ----------------
v_alvo = 70 if cultura in ["Soja","Palma"] else 60

nc = max(0, ((v_alvo - v) * ctc) / prnt)
total_calc = nc * area

ng = (50 * arg)/1000 if (al > 0.5 or arg > 40) else 0
total_gesso = ng * area

# ---------------- ADUBAÇÃO ----------------
rec_p = meta_ton * 15
rec_k = meta_ton * 20

if cultura == "Milho":
    rec_n = meta_ton * 25
    n_plantio = rec_n * 0.2
    n_cobertura = rec_n * 0.8

st.subheader("Adubação")

a1,a2,a3 = st.columns(3)
f_n = a1.number_input("N%", value=4)
f_p = a2.number_input("P%", value=20)
f_k = a3.number_input("K%", value=20)

dose_final = max(
    (rec_p/f_p*100) if f_p>0 else 0,
    (rec_k/f_k*100) if f_k>0 else 0
)

total_adubo = dose_final * area
sacos = math.ceil(total_adubo / 50)

# ---------------- RESULTADOS ----------------
st.subheader("Resultados")

r1,r2,r3 = st.columns(3)

r1.metric("Calcário (t/ha)", f"{nc:.2f}")
r1.metric("Total Calcário (t)", f"{total_calc:.2f}")

r2.metric("Gesso (t/ha)", f"{ng:.2f}")
r2.metric("Total Gesso (t)", f"{total_gesso:.2f}")

r3.metric("Adubo (kg/ha)", f"{dose_final:.0f}")
r3.metric("Total Adubo (kg)", f"{total_adubo:.0f}")

st.success(f"Sacos necessários: {sacos}")

# ---------------- PDF COMPLETO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    def fix(t): return str(t).encode('latin-1','replace').decode('latin-1')

    data_pdf = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

    # Cabeçalho verde
    pdf.set_fill_color(34,139,34)
    pdf.rect(0,0,210,45,'F')

    pdf.set_text_color(255,255,255)
    pdf.set_font("Helvetica","B",18)
    pdf.ln(10)
    pdf.cell(190,10,fix("PRESCRIÇÃO TÉCNICA AGRONÔMICA"),0,1,"C")

    pdf.set_font("Helvetica","",11)
    pdf.cell(190,8,fix(f"Consultor: Felipe Amorim | Data: {data_pdf}"),0,1,"C")

    pdf.set_text_color(0,0,0)
    pdf.ln(20)

    # Identificação
    pdf.set_font("Helvetica","B",12)
    pdf.cell(190,8,fix("1. Identificação"),0,1)

    pdf.set_font("Helvetica","",11)
    pdf.cell(190,7,fix(f"Cliente: {nome_cliente_input}"),0,1)
    pdf.cell(190,7,fix(f"Fazenda: {fazenda}"),0,1)
    pdf.cell(190,7,fix(f"Município: {municipio} - {estado}"),0,1)
    pdf.cell(190,7,fix(f"Área: {area:.3f} ha"),0,1)

    # Cultura
    pdf.ln(5)
    pdf.set_font("Helvetica","B",12)
    pdf.cell(190,8,fix("2. Cultura e Manejo"),0,1)

    pdf.set_font("Helvetica","",11)
    pdf.cell(190,7,fix(f"Cultura: {cultura}"),0,1)

    if cultura == "Palma":
        pdf.set_font("Helvetica","B",11)
        pdf.cell(190,7,fix("Manejo da Palma Forrageira"),0,1)

        pdf.set_font("Helvetica","",10)
        pdf.cell(190,6,fix(f"Variedade: {variedade}"),0,1)
        pdf.cell(190,6,fix("Adubação: 20 a 30 t/ha de esterco curtido"),0,1)
        pdf.cell(190,6,fix("Não cortar o cladódio mãe"),0,1)
        pdf.cell(190,6,fix("Primeiro corte: 12 a 18 meses"),0,1)

    if cultura == "Milho":
        pdf.cell(190,7,fix(f"N total: {rec_n:.0f} kg/ha"),0,1)
        pdf.cell(190,7,fix(f"Plantio: {n_plantio:.0f} kg/ha"),0,1)
        pdf.cell(190,7,fix(f"Cobertura: {n_cobertura:.0f} kg/ha"),0,1)

    # Solo
    pdf.ln(5)
    pdf.set_font("Helvetica","B",12)
    pdf.cell(190,8,fix("3. Correção do Solo"),0,1)

    pdf.set_font("Helvetica","",11)
    pdf.cell(190,7,fix(f"Calcário: {nc:.2f} t/ha | Total: {total_calc:.2f} t"),0,1)
    pdf.cell(190,7,fix(f"Gesso: {ng:.2f} t/ha | Total: {total_gesso:.2f} t"),0,1)

    # Adubação
    pdf.ln(5)
    pdf.set_font("Helvetica","B",12)
    pdf.cell(190,8,fix("4. Adubação"),0,1)

    pdf.set_font("Helvetica","",11)
    pdf.cell(190,7,fix(f"Dose: {dose_final:.0f} kg/ha"),0,1)
    pdf.cell(190,7,fix(f"Total: {total_adubo:.0f} kg"),0,1)

    # Fontes
    pdf.ln(8)
    pdf.set_font("Helvetica","B",11)
    pdf.cell(190,7,fix("Referências Técnicas"),0,1)

    pdf.set_font("Helvetica","",9)
    pdf.multi_cell(190,5,fix(
        "- Manual de Adubação e Calagem (SBCS)\n"
        "- Embrapa Cerrados\n"
        "- Embrapa Milho e Sorgo\n"
        "- IPA Palma Forrageira\n"
        "- IPNI Brasil"
    ))

    # Nota técnica
    pdf.ln(8)
    pdf.set_fill_color(255,240,240)
    pdf.set_font("Helvetica","B",10)
    pdf.cell(190,7,fix("NOTA DE RESPONSABILIDADE TÉCNICA"),0,1,fill=True)

    pdf.set_font("Helvetica","",9)
    pdf.multi_cell(190,5,fix(
        "Esta recomendação foi elaborada com base nos dados fornecidos pelo usuário. "
        "Os resultados podem variar conforme condições de campo e manejo."
    ))

    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO PDF ----------------
if st.button("📄 Gerar Relatório"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Relatorio_{nome_para_arquivo}.pdf")
