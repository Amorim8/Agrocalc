import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica Profissional")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- IDENTIFICAÇÃO (SIDEBAR) ---
with st.sidebar:
    st.header("📋 Dados do Cliente")
    cliente = st.text_input("Produtor:", "Nome do Cliente")
    talhao_id = st.text_input("Identificação do Talhão:", "Gleba 01")
    area_ha = st.number_input("Área da Gleba (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- BLOCO 1: ANÁLISE DO SOLO (DADOS TÉCNICOS) ---
st.header("1️⃣ Análise do Solo (Dados do Laudo)")
col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    v_atual = st.number_input("V% atual (Saturação):", 0.0)
    argila = st.number_input("Argila (g/kg):", 0.0)
with col_a2:
    p_laudo = st.number_input("Fósforo (P) no laudo:", 0.0)
    ctc_total = st.number_input("CTC Total (cmolc/dm³):", 5.0)
with col_a3:
    k_laudo = st.number_input("Potássio (K) no laudo:", 0.0)
    h_al_laudo = st.number_input("H + Al (Acidez Potencial):", 0.0)

st.markdown("---")

# --- BLOCO 2: DEFINIÇÃO DE NÍVEIS (ABINHA DE NÍVEIS) ---
st.header("2️⃣ Classificação de Níveis")
st.info("Defina os níveis conforme sua interpretação técnica:")
col_n1, col_n2, col_n3, col_n4 = st.columns(4)
with col_n1:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_n2:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_n3:
    nivel_h_al = st.selectbox("Nível de H+Al:", ["Baixo", "Médio", "Alto"])
with col_n4:
    nivel_n = st.selectbox("Nível de Nitrogênio (N):", ["Baixo", "Médio", "Alto"])

st.markdown("---")

# --- BLOCO 3: CALAGEM ---
st.header("3️⃣ Cálculo de Calagem")
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc_total) / 80.0 if (v_atual < v_alvo) else 0.0
total_calcario = nc_ha * area_ha

res_c1, res_c2 = st.columns(2)
res_c1.metric("Necessidade de Calcário (t/ha)", f"{nc_ha:.2f}")
res_c2.metric(f"Total para {area_ha} ha (Toneladas)", f"{total_calcario:.2f}")

st.markdown("---")

# --- BLOCO 4: ADUBAÇÃO (NPK) ---
st.header("4️⃣ Recomendação de Adubação")
st.write("Defina a formulação final que o produtor deve aplicar:")

col_ad1, col_ad2 = st.columns(2)
with col_ad1:
    formula_escolhida = st.text_input("Formulação NPK (ex: 04-14-08):", "00-00-00")
with col_ad2:
    dose_adubo = st.number_input("Dose Recomendada (kg/ha):", value=0.0)

# --- GERAÇÃO DO PDF ---
st.markdown("---")
def gerar_relatorio():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Profissional
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.set_xy(0, 15)
    pdf.cell(210, 10, "RELATORIO TECNICO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Informações do Cliente e Área
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 50)
    pdf.cell(0, 10, f"Produtor: {cliente} | Area: {area_ha} ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 10, f"Talhao: {talhao_id} | Cultura: {cultura}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Bloco de Análise e Níveis
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- ANALISE E NIVEIS ENCONTRADOS ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Fosforo (P): {p_laudo} - Nivel: {nivel_p}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Potassio (K): {k_laudo} - Nivel: {nivel_k}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"H+Al: {h_al_laudo} - Nivel: {nivel_h_al}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Bloco de Calagem
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- RECOMENDACAO DE CALAGEM ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Necessidade: {nc_ha:.2f} t/ha | Total Area: {total_calcario:.2f} toneladas".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Bloco de Adubação
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- RECOMENDACAO DE ADUBACAO ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Formulacao: {formula_escolhida}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Dose Sugerida: {dose_adubo} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Responsavel Tecnico: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), align="C")

    return bytes(pdf.output(dest='S'))

try:
    pdf_bytes = gerar_relatorio()
    st.download_button(
        label="⬇️ BAIXAR RELATÓRIO PDF COMPLETO",
        data=pdf_bytes,
        file_name=f"Relatorio_{talhao_id}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao gerar relatório. Verifique os campos.")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
