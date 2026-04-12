import streamlit as st
from fpdf import FPDF
import math

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Dados Gerais")
cliente = st.sidebar.text_input("Produtor:", "Nome do Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área (ha):", value=1.0, min_value=0.01)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# ---------------- 1. ANÁLISE DE SOLO ----------------
st.header("1️⃣ Dados da Análise")
with st.expander("📊 Digite aqui os valores do laudo (Opcional)"):
    col1, col2 = st.columns(2)
    with col1:
        argila = st.number_input("Argila (%):", 0.0)
        p_solo = st.number_input("Fósforo (P):", 0.0)
        v_atual = st.number_input("V% atual:", 0.0)
    with col2:
        k_solo = st.number_input("Potássio (K):", 0.0)
        ctc = st.number_input("CTC:", 5.0)
        prnt = st.number_input("PRNT (%):", 80.0)

# ---------------- 2. ESCOLHA DOS NÍVEIS (O QUE VOCÊ PEDIU) ----------------
st.header("2️⃣ Níveis de Fertilidade")
st.write("Selecione o nível de fertilidade indicado no seu laudo:")

c_n1, c_n2, c_n3 = st.columns(3)
with c_n1:
    nivel_n = st.selectbox("Nível de Nitrogênio (N):", ["Baixo", "Médio", "Alto"])
with c_n2:
    nivel_p = st.selectbox("Nível de Fósforo (P):", ["Baixo", "Médio", "Alto"])
with c_n3:
    nivel_k = st.selectbox("Nível de Potássio (K):", ["Baixo", "Médio", "Alto"])

# ---------------- 3. TABELA TÉCNICA ----------------
tabelas = {
    "Soja": {
        "N": {"Baixo": 20, "Médio": 10, "Alto": 0},
        "P": {"Baixo": 100, "Médio": 80, "Alto": 50},
        "K": {"Baixo": 90, "Médio": 70, "Alto": 50}
    },
    "Milho": {
        "N": {"Baixo": 120, "Médio": 80, "Alto": 40},
        "P": {"Baixo": 120, "Médio": 90, "Alto": 60},
        "K": {"Baixo": 100, "Médio": 80, "Alto": 60}
    }
}

# Puxando os valores baseados na sua escolha manual acima
req_n = tabelas[cultura]["N"][nivel_n]
req_p = tabelas[cultura]["P"][nivel_p]
req_k = tabelas[cultura]["K"][nivel_k]

# Cálculo de Calagem
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual and prnt > 0 else 0

# ---------------- 4. RESULTADOS NA TELA ----------------
st.header("3️⃣ Recomendação Final")
res1, res2, res3, res4 = st.columns(4)
res1.metric("Calcário (t/ha)", f"{nc_ha:.2f}")
res2.metric("N (kg/ha)", f"{req_n}")
res3.metric("P₂O₅ (kg/ha)", f"{req_p}")
res4.metric("K₂O (kg/ha)", f"{req_k}")

# ---------------- 5. PDF PROFISSIONAL ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(230, 255, 230)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.set_xy(0, 12)
    pdf.cell(210, 10, "RELATORIO TECNICO AGRONOMICO", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.set_xy(10, 45)
    pdf.cell(0, 10, f"Produtor: {cliente} | Cultura: {cultura}", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"- Calagem: {nc_ha:.2f} t/ha", ln=True)
    pdf.cell(0, 8, f"- Nitrogenio: {req_n} kg/ha ({nivel_n})", ln=True)
    pdf.cell(0, 8, f"- Fosforo: {req_p} kg/ha ({nivel_p})", ln=True)
    pdf.cell(0, 8, f"- Potassio: {req_k} kg/ha ({nivel_k})", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

st.markdown("---")
try:
    pdf_bytes = gerar_pdf()
    st.download_button(label="⬇️ BAIXAR RELATÓRIO PDF", data=pdf_bytes, file_name="Relatorio.pdf", mime="application/pdf")
except:
    st.error("Erro ao gerar PDF. Verifique os dados.")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
