import streamlit as st
from fpdf import FPDF

# --- CONFIGURACAO DA PAGINA ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronomica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- ENTRADA DE DADOS (SIDEBAR) ---
with st.sidebar:
    st.header("📋 Identificacao")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao = st.text_input("Talhao:", "Gleba 01")
    area_ha = st.number_input("Area (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. DADOS TECNICOS ---
st.header("1️⃣ Analise de Solo")
col1, col2 = st.columns(2)
with col1:
    v_atual = st.number_input("V% atual (do laudo):", 0.0)
    ctc = st.number_input("CTC total:", 5.0)
with col2:
    prnt = st.number_input("PRNT do Calcario:", 80.0)
    argila = st.number_input("Teor de Argila:", 0.0)

# --- 2. SELECAO DE NIVEIS (ORGANIZADO) ---
st.header("2️⃣ Niveis de Fertilidade")
st.info("Escolha os niveis de acordo com a interpretacao do seu laudo:")
c_n1, c_n2, c_n3 = st.columns(3)
with c_n1:
    nivel_n = st.selectbox("Nivel de Nitrogenio (N):", ["Baixo", "Medio", "Alto"])
with c_n2:
    nivel_p = st.selectbox("Nivel de Fosforo (P):", ["Baixo", "Medio", "Alto"])
with c_n3:
    nivel_k = st.selectbox("Nivel de Potassio (K):", ["Baixo", "Medio", "Alto"])

# --- 3. CALCULOS ---
# Calagem
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc) / prnt if (v_alvo > v_atual and prnt > 0) else 0.0
total_calcario = nc_ha * area_ha

# Adubacao NPK
if cultura == "Soja":
    req_n = 0
    obs_n = "Nitrogenio zero: Fixacao biologica (Inoculacao)."
else:
    tab_n = {"Baixo": 120, "Medio": 80, "Alto": 40}
    req_n = tab_n[nivel_n]
    obs_n = "Nitrogenio mineral para Milho."

tab_pk = {
    "Soja": {"P": {"Baixo": 100, "Medio": 80, "Alto": 50}, "K": {"Baixo": 90, "Medio": 70, "Alto": 50}},
    "Milho": {"P": {"Baixo": 120, "Medio": 90, "Alto": 60}, "K": {"Baixo": 100, "Medio": 80, "Alto": 60}}
}
req_p = tab_pk[cultura]["P"][nivel_p]
req_k = tab_pk[cultura]["K"][nivel_k]

# --- 4. EXIBICAO DOS RESULTADOS ---
st.markdown("---")
st.header("3️⃣ Recomendacao Final")

st.subheader("🚜 Correcao (Calagem)")
r1, r2 = st.columns(2)
r1.metric("Necessidade (t/ha)", f"{nc_ha:.2f}")
r2.metric("Total para Area (Ton)", f"{total_calcario:.2f}")

st.subheader("🌱 Adubacao (kg/ha)")
a1, a2, a3 = st.columns(3)
a1.metric("N (Nitrogenio)", f"{req_n}")
a2.metric(f"P2O5 ({nivel_p})", f"{req_p}")
a3.metric(f"K2O ({nivel_k})", f"{req_k}")

if cultura == "Soja":
    st.success(f"Nota: {obs_n}")

# --- 5. GERACAO DE PDF (SEM SIMBOLOS QUE TRAVAM) ---
st.markdown("---")
st.header("4️⃣ Gerar Documento")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Design do Topo
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255
