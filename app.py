import streamlit as st
from fpdf import FPDF
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Acessar Sistema"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- LÓGICA DE TABELA DE RECOMENDAÇÃO ----------------

def obter_recomendacao_p2o5(p_solo, argila, cultura):
    # 1. Definir Classes de Disponibilidade baseada na Argila
    if argila > 60: faixas = [2.0, 4.0]
    elif argila > 35: faixas = [3.0, 6.0]
    elif argila > 15: faixas = [4.0, 9.0]
    else: faixas = [6.0, 12.0]
    
    if p_solo <= faixas[0]: status = "Baixo"
    elif p_solo <= faixas[1]: status = "Médio"
    else: status = "Alto"

    # 2. Tabela de Recomendação (kg/ha de P2O5)
    tabela = {
        "Milho": {"Baixo": 120, "Médio": 80, "Alto": 40},
        "Soja":  {"Baixo": 100, "Médio": 60, "Alto": 30},
        "Palma": {"Baixo": 80,  "Médio": 40, "Alto": 20}
    }
    return tabela[cultura][status], status

def obter_recomendacao_k2o(k_solo, cultura):
    # Classificação de Potássio
    if k_solo <= 0.15: status = "Baixo"
    elif k_solo <= 0.30: status = "Médio"
    else: status = "Alto"

    # Tabela de Recomendação (kg/ha de K2O)
    tabela = {
        "Milho": {"Baixo": 100, "Médio": 60, "Alto": 30},
        "Soja":  {"Baixo": 80,  "Médio": 50, "Alto": 20},
        "Palma": {"Baixo": 120, "Médio": 60, "Alto": 30}
    }
    return tabela[cultura][status], status

# ---------------- CONFIGURAÇÃO VISUAL STREAMLIT ----------------
st.set_page_config(page_title="Sistema de Prescrição Agronômica", layout="wide")

st.markdown("""
<style>
.main { background-color: #f8fafc; }
div[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    padding: 20px;
    border-radius: 12px;
    border-left: 10px solid #16a34a !important;
}
div[data-testid="stMetricValue"] > div { color: #000000 !important; font-size: 34px !important; font-weight: 800 !important; }
div[data-testid="stMetricLabel"] > div > p { color: #000000 !important; font-size: 16px !important; font-weight: 900 !important; text-transform: uppercase; }
.stButton>button { background-color: #16a34a !important; color: white !important; font-weight: bold; height: 3.5em; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ---------------- COLETA DE DADOS ----------------
with st.sidebar:
    st.header("📍 Localização")
    nome_cliente = st.text_input("Produtor:")
    fazenda = st.text_input("Fazenda:")
    area = st.number_input("Área (ha):", value=1.0)
    cultura = st.radio("Cultura Alvo:", ["Soja", "Milho", "Palma"])
    variedade = ""
    if cultura == "Palma":
        variedade = st.selectbox("Variedade:", ["Orelha de Elefante", "Palma Miúda"])
    meta = st.number_input("Meta de Produção (t/ha):", value=8.0)

st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")

st.subheader("📝 Dados da Análise de Solo")
col1, col2, col3, col4 = st.columns(4)
with col1: ph = st.number_input("pH (Água)", 5.5); p_mg = st.number_input("P (mg/dm³)", 8.0)
with col2: al = st.number_input("Al (cmolc)", 0.0); k_cmol = st.number_input("K (cmolc)", 0.15)
with col3: argila = st.number_input("Argila (%)", 35.0); v_at = st.number_input("V% Atual", 40.0)
with col4: ctc = st.number_input("CTC (T)", 3.25); prnt = st.number_input("PRNT (%)", 85.0)

# Lógica de Recomendação
p_necessario, status_p = obter_recomendacao_p2o5(p_mg, argila, cultura)
k_necessario, status_k = obter_recomendacao_k2o(k_cmol, cultura)

# ---------------- CÁLCULOS TÉCNICOS ----------------
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_at) * ctc) / prnt)

st.subheader("🧪 Adubação Comercial")
af1, af2, af3 = st.columns(3)
fn = af1.number_input("N %", 4); fp = af2.number_input("P2O5 %", 20); fk = af3.number_input("K2O %", 20)

# Dose baseada na necessidade da tabela dividida pela concentração do adubo
dose_p = (p_necessario / (fp/100)) if fp > 0 else 0
dose_k = (k_necessario / (fk/100)) if fk > 0 else 0
dose_final_ha = max(dose_p, dose_k)

# ---------------- RESULTADOS EM TELA ----------------
st.divider()
st.success(f"Interpretação: Fósforo {status_p} | Potássio {status_k}")

r1, r2, r3 = st.columns(3)
r1.metric("CALCÁRIO (T/HA)", f"{nc:.2f}")
r2.metric("ADUBO (KG/HA)", f"{dose_final_ha:.0f}")
r3.metric("ADUBO TOTAL (KG)", f"{(dose_final_ha * area):.0f}")

# ---------------- GERADOR DE PDF COM FORMATAÇÃO ORIGINAL ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def txt(t): return str(t).encode('cp1252', 'replace').decode('cp1252')

    # Cabeçalho Original Verde
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 18); pdf.ln(12)
    pdf.cell(190, 10, txt("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12); pdf.cell(190, 7, txt(f"Consultoria: Felipe Amorim | Data: {data_hoje}"), 0, 1, "C")
    
    # Corpo do PDF
    pdf.set_text_color(0, 0, 0); pdf.ln(25)
    
    # Seção 1: Dados da Análise
    pdf.set_font("Helvetica", "B", 12); pdf.set_fill_color(230, 230, 230)
    pdf.cell(190, 8, txt("1. RESULTADOS DA ANÁLISE DE SOLO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 10); pdf.ln(2)
    pdf.cell(95, 7, txt(f"pH: {ph} | Al: {al} | CTC: {ctc}"), 0, 0)
    pdf.cell(95, 7, txt(f"Argila: {argila}% | V% Atual: {v_at}%"), 0, 1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 7, txt(f"Fósforo: {p_mg} mg/dm3 ({status_p})"), 1, 0)
    pdf.cell(95, 7, txt(f"Potássio: {k_cmol} cmolc/dm3 ({status_k})"), 1, 1)

    # Seção 2: Recomendações
    pdf.ln(5); pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, txt("2. PRESCRIÇÃO E RECOMENDAÇÃO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11); pdf.ln(2)
    pdf.cell(190, 7, txt(f"Propriedade: {fazenda} | Cultura: {cultura} {variedade}"), 0, 1)
    pdf.cell(190, 7, txt(f"- Necessidade Calcário: {nc:.2f} t/ha"), 0, 1)
    pdf.cell(190, 7, txt(f"- Demanda P2O5 (Tabela): {p_necessario} kg/ha"), 0, 1)
    pdf.cell(190, 7, txt(f"- Demanda K2O (Tabela): {k_necessario} kg/ha"), 0, 1)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 9, txt(f"DOSE DO ADUBO ({fn}-{fp}-{fk}): {dose_final_ha:.0f} kg/ha"), 1, 1, "C", fill=True)

    # Rodapé
    pdf.ln(20); pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, txt("Responsável Técnico: Felipe Amorim"), 0, 1, "R")
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR PDF COMPLETO"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name=f"Prescricao_{nome_cliente}.pdf")
