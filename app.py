import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 AgroCalc Pro - Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- 1. IDENTIFICAÇÃO DA ÁREA ---
st.header("1️⃣ Informações da Área")
with st.container():
    col_id1, col_id2, col_id3 = st.columns(3)
    with col_id1:
        cliente = st.text_input("Nome do Produtor:", "Cliente Exemplo")
    with col_id2:
        talhao_id = st.text_input("Identificação do Talhão:", "Gleba 01")
    with col_id3:
        area_ha = st.number_input("Área Total (ha):", value=1.0, min_value=0.1)

st.markdown("---")

# --- 2. DADOS DA ANÁLISE DO SOLO ---
st.header("2️⃣ Dados da Análise (Laboratório)")
col_an1, col_an2, col_an3 = st.columns(3)
with col_an1:
    v_atual = st.number_input("V% Atual (Saturação):", value=0.0)
    ctc_total = st.number_input("CTC Total (cmolc/dm³):", value=0.0)
with col_an2:
    prnt_calc = st.number_input("PRNT do Calcário (%):", value=80.0)
    teor_argila = st.number_input("Teor de Argila (g/kg):", value=0.0)
with col_an3:
    cultura = st.selectbox("Cultura de Destino:", ["Soja", "Milho"])
    v_alvo = st.number_input("V% Alvo (Desejado):", value=70.0 if cultura == "Soja" else 60.0)

st.markdown("---")

# --- 3. CALAGEM ---
st.header("3️⃣ Recomendação de Calagem")
if prnt_calc > 0 and ctc_total > 0:
    nc_ha = ((v_alvo - v_atual) * ctc_total) / prnt_calc
    nc_ha = max(0.0, nc_ha)
else:
    nc_ha = 0.0

total_calc = nc_ha * area_ha

c_col1, c_col2 = st.columns(2)
c_col1.metric("Necessidade de Calcário (t/ha)", f"{nc_ha:.2f}")
c_col2.metric(f"Total para {area_ha} ha (Toneladas)", f"{total_calc:.2f}")

st.markdown("---")

# --- 4. ADUBAÇÃO E NÍVEIS ---
st.header("4️⃣ Recomendação de Adubação")
col_ad1, col_ad2, col_ad3 = st.columns(3)

with col_ad1:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
    p_puro = st.number_input("Necessidade de P2O5 (kg/ha):", value=0.0)
with col_ad2:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
    perc_p_adubo = st.number_input("% de P2O5 no Adubo:", value=14.0)
with col_ad3:
    formulado = st.text_input("Adubo NPK Sugerido:", "04-14-08")
    # Cálculo da quantidade de adubo baseado no Fósforo
    dose_adubo = (p_puro * 100) / perc_p_adubo if perc_p_adubo > 0 else 0.0

if dose_adubo > 0:
    st.success(f"✅ Dose Recomendada: **{dose_adubo:.2f} kg/ha** do formulado {formulado}")

st.markdown("---")

# --- GERADOR DE PDF COM ACENTOS ---
def gerar_relatorio():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.set_xy(0, 15)
    # Título com acento corrigido
    pdf.cell(210, 10, "RELATÓRIO TÉCNICO AGRONÔMICO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Identificação
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 50)
    pdf.cell(0, 10, f"Produtor: {cliente} | Gleba: {talhao_id}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 10, f"Área: {area_ha} ha | Cultura: {cultura}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Seção Calagem com acentos
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- RECOMENDAÇÃO DE CALAGEM ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Necessidade: {nc_ha:.2f} t/ha | Total da Área: {total_calc:.2f} t".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Seção Adubação com acentos e Dose
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- RECOMENDAÇÃO DE ADUBAÇÃO ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Nível P: {nivel_p} | Nível K: {nivel_k}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Adubo Sugerido: {formulado}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"QUANTIDADE A APLICAR: {dose_adubo:.2f} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Consultor Responsável: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), align="C")
