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
    area_ha = st.number_input("Área (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ANÁLISE DO SOLO ---
st.header("1️⃣ Análise do Solo (Dados do Laboratório)")
col_laudo1, col_laudo2, col_laudo3 = st.columns(3)

with col_laudo1:
    v_atual = st.number_input("V% atual (Saturação):", 0.0, help="Saturação por bases atual do laudo.")
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
st.header("2️⃣ Níveis de Fertilidade (Sua Classificação)")
col_niv1, col_niv2, col_niv3 = st.columns(3)
with col_niv1:
    nivel_n = st.selectbox("Nível de Nitrogênio (N):", ["Baixo", "Médio", "Alto"])
with col_niv2:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_niv3:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])

# --- 3. CÁLCULOS ---
# Definição do Alvo
v_alvo = 70 if cultura == "Soja" else 60

# Cálculo NC (Necessidade de Calagem)
if v_atual < v_alvo:
    nc_ha = ((v_alvo - v_atual) * ctc) / 80.0 # PRNT padrão 80%
else:
    nc_ha = 0.0

total_calcario = nc_ha * area_ha

# Lógica de Adubação
if cultura == "Soja":
    req_n, obs_n = 0, "Nitrogênio zero: Fixação biológica (Inoculação)."
    tab_p = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 110, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 0}
else:
    tab_n_milho = {"Baixo": 120, "Médio": 80, "Alto": 40}
    req_n, obs_n = tab_n_milho[nivel_n], "Nitrogênio mineral para Milho."
    tab_p = {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 0}
    tab_k = {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 0}

req_p, req_k = tab_p[nivel_p], tab_k[nivel_k]

# --- 4. RESULTADOS ---
st.header("3️⃣ Recomendação")
if nc_ha == 0:
    st.warning(f"Calagem: 0.00 t/ha. O V% atual ({v_atual}%) já é superior ou igual ao alvo de {v_alvo}% para {cultura}.")
else:
    st.success(f"Calagem Recomendada: {nc_ha:.2f} t/ha")

c1, c2, c3 = st.columns(3)
c1.metric("N (kg/ha)", req_n)
c2.metric(f"P2O5 ({nivel_p})", req_p)
c3.metric(f"K2O ({nivel_k})", req_k)

# --- 5. PDF (CORRIGIDO) ---
st.markdown("---")
st.header("4️⃣ Gerar Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    
    # Título Maior e com acento corrigido
    pdf.set_font("Arial", "B", 24)
    pdf.set_xy(0, 15)
    pdf.cell(210, 10, "RELATÓRIO TÉCNICO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    pdf.set_font("Arial", "I", 12)
    pdf.set_xy(0, 28)
    pdf.cell(210, 10, f"Consultor: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Corpo
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 55)
    pdf.cell(0, 10, f"Produtor: {cliente} | Cultura: {cultura}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.cell(0, 8, "--- ANÁLISE DO SOLO ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"V% atual: {v_atual}% | V% Alvo: {v_alvo}% | Argila: {argila} g/kg".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Fósforo: {p_valor} {p_unid} | Potássio: {k_valor} {k_unid}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- RECOMENDAÇÕES ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Calagem: {nc_ha:.2f} t/ha (Total: {total_calcario:.2f} toneladas)".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Nitrogênio (N): {req_n} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Fósforo (P2O5): {req_p} kg/ha (Nível {nivel_p})".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Potássio (K2O): {req_k} kg/ha (Nível {nivel_k})".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    if nc_ha == 0:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 8, "Obs: Solo com saturação por bases adequada. Calagem desnecessária.".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    # Retorno seguro em bytes
    return bytes(pdf.output(dest='S'))

try:
    pdf_final = gerar_pdf()
    st.download_button(
        label="⬇️ BAIXAR RELATÓRIO PDF (Fundo Verde)",
        data=pdf_final,
        file_name=f"Relatorio_{talhao}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao gerar o PDF. Verifique os dados.")
    st.write(f"Detalhe: {e}")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
