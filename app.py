import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 AgroCalc Pro - Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- 1. IDENTIFICAÇÃO DA ÁREA (SUA ABINHA DE INFORMAÇÕES) ---
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

# --- 3. CALAGEM (CÁLCULO SEPARADO) ---
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

# --- 4. ADUBAÇÃO E NÍVEIS (CLASSIFICAÇÃO) ---
st.header("4️⃣ Recomendação de Adubação")
st.write("Classifique a fertilidade e escolha o formulado:")
col_ad1, col_ad2, col_ad3 = st.columns(3)

with col_ad1:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_ad2:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"])
with col_ad3:
    formulado = st.text_input("Adubo NPK Sugerido:", "04-14-08")

st.markdown("---")

# --- GERADOR DE PDF ---
def gerar_relatorio():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.set_xy(0, 15)
    pdf.cell(210, 10, "RELATORIO TECNICO AGRO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Identificação
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 50)
    pdf.cell(0, 10, f"Produtor: {cliente} | Gleba: {talhao_id}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 10, f"Area: {area_ha} ha | Cultura: {cultura}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Seção Calagem
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- CALAGEM ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Necessidade: {nc_ha:.2f} t/ha | Total Area: {total_calc:.2f} t".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Seção Adubação
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "--- ADUBACAO ---".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Nivel P: {nivel_p} | Nivel K: {nivel_k}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"Formulado Recomendado: {formulado}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Consultor Responsavel: Felipe Amorim", align="C")
    
    return pdf.output(dest='S').encode('latin-1')

try:
    if st.button("GERAR PDF"):
        pdf_bytes = gerar_relatorio()
        st.download_button(
            label="⬇️ Baixar Relatório",
            data=pdf_bytes,
            file_name=f"Relatorio_{talhao_id}.pdf",
            mime="application/pdf"
        )
except Exception as e:
    st.error(f"Erro ao preparar o arquivo. Verifique os dados.")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
