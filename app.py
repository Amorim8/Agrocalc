import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- IDENTIFICAÇÃO ---
with st.sidebar:
    st.header("📋 Dados do Cliente")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao_id = st.text_input("Identificação do Talhão:", "Gleba 01")
    area_ha = st.number_input("Área da Gleba (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ANÁLISE E NÍVEIS ---
st.header("1️⃣ Níveis de Fertilidade (Interpretação)")
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    nivel_n = st.selectbox("Nível de Nitrogênio (N):", ["Baixo", "Médio", "Alto"])
with col_n2:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_n3:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])

# --- 2. NECESSIDADE DE NUTRIENTES (SEPARADOS) ---
if cultura == "Soja":
    req_n = 0
    tab_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 110, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 0}
else: # Milho
    tab_n = {"Baixo": 120, "Médio": 80, "Alto": 40}
    req_n = tab_n[nivel_n]
    tab_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}

req_p, req_k = tab_p[nivel_p], tab_k[nivel_k]

st.subheader("🚀 Necessidade por Hectare (Simples)")
c1, c2, c3 = st.columns(3)
c1.metric("Nitrogênio (N)", f"{req_n} kg/ha")
c2.metric("Fósforo (P2O5)", f"{req_p} kg/ha")
c3.metric("Potássio (K2O)", f"{req_k} kg/ha")

st.markdown("---")

# --- 3. CÁLCULO DO FORMULADO (NPK) ---
st.header("2️⃣ Escolha do Adubo Formulado")
st.write("Insira a formulação que você vai usar (ex: 04-14-08):")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1: f_n = st.number_input("% N na fórmula", 0)
with col_f2: f_p = st.number_input("% P2O5 na fórmula", 0)
with col_f3: f_k = st.number_input("% K2O na fórmula", 0)

# Cálculo da dose baseada no nutriente limitante (exemplo simples)
if (f_n + f_p + f_k) > 0:
    # Calcula a dose necessária para suprir o Fósforo ou Potássio (o que for maior)
    dose_p = (req_p * 100 / f_p) if f_p > 0 else 0
    dose_k = (req_k * 100 / f_k) if f_k > 0 else 0
    dose_final = max(dose_p, dose_k)
else:
    dose_final = 0.0

st.info(f"💡 Para suprir a necessidade, o produtor deve aplicar: **{dose_final:.2f} kg/ha** do formulado {f_n}-{f_p}-{f_k}")

# --- 4. GERAÇÃO DO PDF ---
st.markdown("---")
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 22)
    pdf.set_xy(0, 15)
    pdf.cell(210
