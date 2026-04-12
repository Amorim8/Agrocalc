import streamlit as st
from fpdf import FPDF
import math

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# ---------------- SIDEBAR (DADOS GERAIS) ----------------
st.sidebar.header("📋 Dados Gerais")
cliente = st.sidebar.text_input("Produtor:", "Nome do Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (ha):", value=1.0, min_value=0.01, step=0.1)
cultura = st.sidebar.selectbox("Cultura Alvo:", ["Soja", "Milho"])

# ---------------- 1. ENTRADA DE DADOS (MENU RETRÁTIL) ----------------
st.header("1️⃣ Análise de Solo")

with st.expander("📊 CLIQUE PARA INSERIR DADOS DO LAUDO", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        argila = st.number_input("Teor de Argila (%):", 0.0)
        p_solo = st.number_input("Fósforo (P) [mg/dm³]:", 0.0)
        v_atual = st.number_input("V% Atual (Saturação):", 0.0)
    with col2:
        k_solo = st.number_input("Potássio (K) [cmolc/dm³]:", 0.0)
        ctc = st.number_input("CTC Total (pH 7.0):", 5.0)
        prnt = st.number_input("PRNT do Calcário (%):", 80.0)

# ---------------- 2. INTERPRETAÇÃO DE NÍVEIS ----------------
st.header("2️⃣ Interpretação e Níveis")

# Lógica de classificação automática
if p_solo < 10: nivel_p = "Baixo"
elif p_solo < 20: nivel_p = "Médio"
else: nivel_p = "Alto"

if k_solo < 0.15: nivel_k = "Baixo"
elif k_solo < 0.30: nivel_k = "Médio"
else: nivel_k = "Alto"

st.info(f"✅ Níveis Identificados: Fósforo **{nivel_p}** | Potássio **{nivel_k}**")

# ---------------- 3. CÁLCULOS TÉCNICOS ----------------
# Calagem
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual else 0
total_calcario = nc_ha * area_ha

# Tabela de Recomendação (kg/ha) baseada nos níveis
tabela = {
    "Soja": {"P": {"Baixo": 100, "Médio": 80, "Alto": 50}, "K": {"Baixo": 90, "Médio": 70, "Alto": 50}},
    "Milho": {"P": {"Baixo": 120, "Médio": 90, "Alto": 60}, "K": {"Baixo": 100, "Médio": 80, "Alto": 60}}
}
req_p = tabela[cultura]["P"][nivel_p]
req_k = tabela[cultura]["K"][nivel_k]

# ---------------- 4. EXIBIÇÃO DE RESULTADOS ----------------
st.header("3️⃣ Recomendações Técnicas")
res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc_ha:.2f}")
res2.metric(f"P₂O₅ para {nivel_p} (kg/ha)", f"{req_p}")
res3.metric(f"K₂O para {nivel_k} (kg/ha)", f"{req_k}")

st.subheader("📦 Fechamento com Adubo Formulado")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N no formulado:", 0)
f_p = f2.number_input("P no formulado:", 20)
f_k = f3.number_input("K no formulado:", 20)

dose_adubo = 0
sacos_total = 0
if f_p > 0:
    dose_adubo = (req_p / f_p) * 100
    sacos_total = (dose_adubo * area_ha) / 50
    st.success(f"Dose Final: **{int(dose_adubo)} kg/ha** | Total para a área: **{math.ceil(sacos_total)} sacos de 50kg**")

# ---------------- 5. GERAÇÃO DE PDF PROFISSIONAL ----------------
st.divider()
st.header("4️⃣ Relatório Final")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # FUNDO VERDE CLARO
    pdf.set_fill_color(230, 255, 230)
    pdf.rect(0, 0, 210, 297, 'F')

    # CABEÇALHO VERDE ESCURO (
