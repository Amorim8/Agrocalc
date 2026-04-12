import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- IDENTIFICAÇÃO ---
with st.sidebar:
    st.header("📋 Identificação")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao = st.text_input("Talhão:", "Gleba 01")
    # Agora a área será usada explicitamente no PDF
    area_ha = st.number_input("Área total da gleba (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ANÁLISE DO SOLO ---
st.header("1️⃣ Análise do Solo (Dados do Laboratório)")
col_laudo1, col_laudo2, col_laudo3 = st.columns(3)

with col_laudo1:
    v_atual = st.number_input("V% atual (Saturação):", 0.0)
    argila = st.number_input("Argila (g/kg):", 0.0)
with col_laudo2:
    p_valor = st.number_input("Fósforo (P) encontrado:", 0.0)
    p_unid = st.selectbox("Unidade P:", ["mg/dm³", "cmolc/dm³"])
    ctc = st.number_input("CTC total (cmolc/dm³):", 5.0)
with col_laudo3:
    k_valor = st.number_input("Potássio (K) encontrado:", 0.0)
    k_unid = st.selectbox("Unidade K:", ["mg/dm³", "cmolc/dm³"])

st.markdown("---")

# --- 2. NÍVEIS DE FERTILIDADE ---
st.header("2️⃣ Níveis de Fertilidade")
col_niv1, col_niv2, col_niv3 = st.columns(3)
with col_niv1:
    nivel_n = st.selectbox("Nível de Nitrogênio (N):", ["Baixo", "Médio", "Alto"])
with col_niv2:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_niv3:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])

# --- 3. CÁLCULOS ---
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc) / 80.0 if (v_atual < v_alvo) else 0.0
total_calcario = nc_ha * area_ha

# Tabelas de Recomendação
if cultura == "Soja":
    req_n = 0
    tab_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 110, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 0}
else:
    tab_n = {"Baixo": 120, "Médio": 80, "Alto": 40}
    req_n = tab_n[nivel_n]
    tab_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}

req_p, req_k = tab_p[nivel_p], tab_k[nivel_k]

# Cálculo da Quantidade Bruta de NPK (Soma Total dos Nutrientes)
total_bruto_npk = req_n + req_p + req_k

# --- 4. RESULTADOS NA TELA ---
st.header("3️⃣ Recomendação de Adubação")
c1, c2, c3, c4 = st.columns(4)
c1.metric("N (Nitrogênio)", f"{req_n} kg/ha")
c2.metric("P2O5 (Fósforo)", f"{req_p} kg/ha")
c3.metric("K2O (Potássio)", f"{req_k} kg/ha")
c4.metric("Bruto NPK Total", f"{total_bruto_npk} kg/ha", delta_color="off")

# --- 5. PDF PROFISSIONAL ---
st.markdown("---")
st.header("4️⃣ Gerar Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Verde
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.set_xy(0, 15)
    pdf.cell(210, 10, "RELATÓRIO TÉCNICO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    pdf.set_font("Arial", "I", 12)
    pdf.set_xy(0, 28)
    pdf.cell(210, 10, f"Consultoria Agronômica - Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Informações Gerais (Com inclusão da ÁREA)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 55)
    pdf.cell(0, 10, f"Produtor: {cliente} | Cultura: {cultura}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 10, f"Talhão: {talhão} | ÁREA TOTAL: {area_ha} Hectares".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Dados da Análise
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- DADOS DA ANÁLISE ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"V% Atual: {v_atual}% | Argila: {argila} g/kg | CTC: {ctc}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"P Encontrado: {p_valor} {p_unid} | K Encontrado: {k_valor} {k_unid}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Recomendações
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- RECOMENDAÇÃO DE INSUMOS ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Calagem: {nc_ha:.2f} t/ha (Total para a área: {total_calcario:.2f} toneladas)".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(3)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Formulação NPK (kg por hectare):".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"  - Nitrogênio (N): {req_n} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"  - Fósforo (P2O5): {req_p} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"  - Potássio (K2O): {req_k} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f"TOTAL BRUTO NPK: {total_bruto_npk} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    return bytes(pdf.output(dest='S'))

try:
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="⬇️ BAIXAR RELATÓRIO PDF COMPLETO",
        data=pdf_bytes,
        file_name=f"Relatorio_{talhao}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao preparar PDF. Detalhes: {e}")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
