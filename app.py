import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- BLOCO 1: IDENTIFICAÇÃO ---
with st.sidebar:
    st.header("📋 Dados do Cliente")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao_id = st.text_input("Talhão/Gleba:", "Gleba 01")
    area_ha = st.number_input("Área da Gleba (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- BLOCO 2: ANÁLISE E NÍVEIS ---
st.header("1️⃣ Análise do Solo e Níveis")
col_laudo1, col_laudo2, col_laudo3 = st.columns(3)
with col_laudo1:
    v_atual = st.number_input("V% atual (Saturação):", 0.0)
    ctc_total = st.number_input("CTC Total (cmolc/dm³):", 5.0)
with col_laudo2:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_laudo3:
    nivel_n = st.selectbox("Nível de Nitrogênio (N):", ["Baixo", "Médio", "Alto"])

st.markdown("---")

# --- BLOCO 3: CALAGEM ---
st.header("2️⃣ Recomendação de Calagem")
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc_total) / 80.0 if (v_atual < v_alvo) else 0.0
total_calcario = nc_ha * area_ha

c_res1, c_res2 = st.columns(2)
c_res1.metric("Necessidade de Calcário (t/ha)", f"{nc_ha:.2f}")
c_res2.metric(f"Total para {area_ha} ha (Toneladas)", f"{total_calcario:.2f}")

st.markdown("---")

# --- BLOCO 4: ADUBAÇÃO (SIMPLES E FORMULADA) ---
st.header("3️⃣ Recomendação de Adubação")

# Tabelas de Recomendação Simples (kg/ha de nutriente puro)
if cultura == "Soja":
    req_n = 0
    tab_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 110, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 0}
else: # Milho
    tab_n_val = {"Baixo": 120, "Médio": 80, "Alto": 40}
    req_n = tab_n_val[nivel_n]
    tab_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}

req_p, req_k = tab_p[nivel_p], tab_k[nivel_k]

st.subheader("📍 Necessidade de Nutrientes (kg/ha)")
n1, n2, n3 = st.columns(3)
n1.metric("Nitrogênio (N)", f"{req_n} kg/ha")
n2.metric("Fósforo (P2O5)", f"{req_p} kg/ha")
n3.metric("Potássio (K2O)", f"{req_k} kg/ha")

st.markdown("#### 🧪 Cálculo do Adubo Formulado")
st.write("Escolha a formulação disponível para calcular a dose total:")
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1: f_n = st.number_input("% N na fórmula", 0)
with f_col2: f_p = st.number_input("% P2O5 na fórmula", 0)
with f_col3: f_k = st.number_input("% K2O na fórmula", 0)

# Cálculo da dose do formulado baseado no Fósforo (geralmente o nutriente base na semeadura)
if f_p > 0:
    dose_formulado = (req_p * 100) / f_p
else:
    dose_formulado = 0.0

st.success(f"✅ Recomendo aplicar: **{dose_formulado:.2f} kg/ha** do formulado {f_n}-{f_p}-{f_k}")

# --- BLOCO 5: PDF ---
st.markdown("---")
def gerar_pdf_completo():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Verde
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.set_xy(0, 15)
    pdf.cell(210, 10, "RELATORIO TECNICO DE ADUBACAO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Dados Gerais
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 50)
    pdf.cell(0, 10, f"Produtor: {cliente} | Area: {area_ha} ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 10, f"Cultura: {cultura} | Talhao: {talhao_id}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Seção Calagem
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "1. RECOMENDACAO DE CALAGEM:".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"- Necessidade: {nc_ha:.2f} t/ha | Total: {total_calcario:.2f} toneladas".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    # Seção Nutrientes
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "2. NECESSIDADE DE NUTRIENTES (kg/ha):".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"- Nitrogenio (N): {req_n} kg/ha | Fosforo (P2O5): {req_p} kg/ha | Potassio (K2O): {req_k} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Seção Formulado
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "3. ADUBACAO FORMULADA SUGERIDA:".encode('latin-1', '
