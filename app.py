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
    talhao_nome = st.text_input("Talhão/Gleba:", "Gleba 01")
    area_total = st.number_input("Área (ha):", value=1.0, min_value=0.01)
    cultura = st.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ANÁLISE DO SOLO ---
st.header("1️⃣ Análise do Solo")
col1, col2, col3 = st.columns(3)
with col1:
    v_atual = st.number_input("V% atual (Saturação):", 0.0)
    argila_valor = st.number_input("Argila (g/kg):", 0.0)
with col2:
    p_analise = st.number_input("Fósforo (P) no laudo:", 0.0)
    ctc_valor = st.number_input("CTC (cmolc/dm³):", 5.0)
with col3:
    k_analise = st.number_input("Potássio (K) no laudo:", 0.0)
    prnt_calcario = st.number_input("PRNT do Calcário (%):", 80.0)

# --- 2. CÁLCULO DE CALAGEM (VISÍVEL) ---
st.markdown("---")
st.header("2️⃣ Cálculo de Calagem")
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc_valor) / prnt_calcario if (v_atual < v_alvo and prnt_calcario > 0) else 0.0
total_ton = nc_ha * area_total

res_c1, res_c2 = st.columns(2)
res_c1.metric("Necessidade (t/ha)", f"{nc_ha:.2f}")
res_c2.metric(f"Total para {area_total} ha (Toneladas)", f"{total_ton:.2f}")

# --- 3. RECOMENDAÇÃO DE ADUBAÇÃO (MANUAL) ---
st.markdown("---")
st.header("3️⃣ Recomendação de Adubação")
st.write("Digite manualmente a formulação e a quantidade que deseja recomendar:")

col_ad1, col_ad2 = st.columns(2)
with col_ad1:
    formula_npk = st.text_input("Formulação NPK sugerida:", "04-14-08")
with col_ad2:
    qtd_adubo = st.number_input("Quantidade de Adubo (kg/ha):", value=0.0)

# --- 4. RELATÓRIO PDF ---
st.markdown("---")
st.header("4️⃣ Gerar Relatório Final")

def gerar_pdf_corrigido():
    pdf = FPDF()
    pdf.add_page()
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 22)
    pdf.set_xy(0, 15)
    pdf.cell(210, 10, "RELATORIO TECNICO".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    # Dados
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 50)
    pdf.cell(0, 10, f"Produtor: {cliente} | Gleba: {talhao_nome}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 10, f"Cultura: {cultura} | Area: {area_total} ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "DETALHES DA RECOMENDACAO:".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"- Calagem: {nc_ha:.2f} t/ha (Total: {total_ton:.2f} toneladas)".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"- Formulacao Sugerida: {formula_npk}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(0, 8, f"- Dose do Adubo: {qtd_adubo} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Rodapé
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Consultor Responsavel: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), align="C")
    
    return bytes(pdf.output(dest='S'))

try:
    pdf_final = gerar_pdf_corrigido()
    st.download_button(
        label="⬇️ BAIXAR RELATÓRIO EM PDF",
        data=pdf_final,
        file_name=f"Relatorio_{talhao_nome}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"Erro ao gerar PDF: {e}")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
