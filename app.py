import streamlit as st
from fpdf import FPDF

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgroCalc Pro", layout="wide")

st.title("🌿 AgroCalc Pro - Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR (AGORA COMO VOCÊ QUER) ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente Exemplo")
talhao_id = st.sidebar.text_input("Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área (ha):", 1.0)

cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

st.markdown("---")

# ---------------- ANÁLISE ----------------
st.header("1️⃣ Análise de Solo")

with st.expander("📊 Clique para inserir dados"):

    col1, col2, col3 = st.columns(3)

    with col1:
        v_atual = st.number_input("V% Atual", 0.0)
        ctc_total = st.number_input("CTC", 0.0)

    with col2:
        prnt_calc = st.number_input("PRNT (%)", 80.0)
        argila = st.number_input("Argila", 0.0)

    with col3:
        profundidade = st.selectbox("Profundidade", ["0-20 cm", "20-40 cm"])

# ---------------- CALAGEM ----------------
st.header("2️⃣ Calagem")

v_alvo = 70 if cultura == "Soja" else 60

if prnt_calc > 0:
    nc_base = ((v_alvo - v_atual) * ctc_total) / 100
    nc_ha = nc_base / (prnt_calc / 100)
    nc_ha = max(0, nc_ha)
else:
    nc_ha = 0

total_calc = nc_ha * area_ha

colc1, colc2 = st.columns(2)
colc1.metric("Calcário (t/ha)", f"{nc_ha:.2f}")
colc2.metric("Total (t)", f"{total_calc:.2f}")

st.markdown("---")

# ---------------- ADUBAÇÃO (MANUAL COMO VOCÊ PEDIU) ----------------
st.header("3️⃣ Adubação (Manual)")

col1, col2 = st.columns(2)

with col1:
    nivel_p = st.selectbox("Fósforo (P)", ["Baixo", "Médio", "Alto"])
    req_p = st.number_input("P2O5 (kg/ha)", 0.0)

with col2:
    nivel_k = st.selectbox("Potássio (K)", ["Baixo", "Médio", "Alto"])
    req_k = st.number_input("K2O (kg/ha)", 0.0)

formulado = st.text_input("Adubo (NPK)", "04-14-08")

st.success(f"Recomendação: P={req_p} kg/ha | K={req_k} kg/ha")

st.markdown("---")

# ---------------- PDF ----------------
st.header("4️⃣ Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    # FUNDO VERDE
    pdf.set_fill_color(230, 255, 230)
    pdf.rect(0, 0, 210, 297, 'F')

    # CABEÇALHO
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 35, 'F')

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, "RELATORIO AGRONOMICO", align="C")

    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(0, 22)
    pdf.cell(210, 10, "Felipe Amorim - Eng. Agronomo", align="C")

    pdf.ln(40)
    pdf.set_text_color(0, 0, 0)

    # BLOCO CINZA
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "DADOS DA AREA", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Produtor: {cliente}", ln=True)
    pdf.cell(190, 8, f"Talhao: {talhao_id}", ln=True)
    pdf.cell(190, 8, f"Area: {area_ha} ha", ln=True)
    pdf.cell(190, 8, f"Cultura: {cultura}", ln=True)
    pdf.cell(190, 8, f"Profundidade: {profundidade}", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "CALAGEM", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Necessidade: {nc_ha:.2f} t/ha", ln=True)
    pdf.cell(190, 8, f"Total: {total_calc:.2f} t", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "ADUBACAO", ln=True, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Nivel P: {nivel_p}", ln=True)
    pdf.cell(190, 8, f"Nivel K: {nivel_k}", ln=True)
    pdf.cell(190, 8, f"P2O5: {req_p} kg/ha", ln=True)
    pdf.cell(190, 8, f"K2O: {req_k} kg/ha", ln=True)
    pdf.cell(190, 8, f"Adubo: {formulado}", ln=True)

    return bytes(pdf.output(dest='S'))

if st.button("📄 Gerar PDF"):
    try:
        pdf_bytes = gerar_pdf()

        st.download_button(
            "⬇️ Baixar Relatório",
            pdf_bytes,
            file_name=f"Relatorio_{talhao_id}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("AgroCalc Pro | Felipe Amorim")
