import streamlit as st
from fpdf import FPDF
from datetime import datetime

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR (COMO VOCÊ PREFERE) ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area = st.sidebar.number_input("Área (ha):", min_value=0.01, value=1.0, step=0.1)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# ---------------- 1. ANÁLISE DO SOLO ----------------
st.header("1️⃣ Análise de Solo (Química)")
col1, col2, col3 = st.columns(3)

with col1:
    p = st.number_input("Fósforo (mg/dm³)", value=0.0)
    k = st.number_input("Potássio (cmolc/dm³)", value=0.0)
with col2:
    argila = st.number_input("Argila (g/kg)", value=0.0)
    v_atual = st.number_input("V% Atual", value=0.0)
with col3:
    ctc = st.number_input("CTC", value=5.0)
    prnt = st.number_input("PRNT (%)", value=80.0)

# ---------------- 2. CALAGEM ----------------
st.header("2️⃣ Calagem")
v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0.0
total_calc = nc * area

colc1, colc2 = st.columns(2)
colc1.metric("Calcário (t/ha)", f"{nc:.2f}")
colc2.metric("Total para a Área (t)", f"{total_calc:.2f}")

# ---------------- 3. ADUBAÇÃO ----------------
st.header("3️⃣ Recomendação de Adubação")
niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]

col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    nivel_p = st.selectbox("Nível de Fósforo (P):", niveis)
    req_p = st.number_input("Necessidade de P₂O₅ (kg/ha):", value=0.0)
with col_a2:
    nivel_k = st.selectbox("Nível de Potássio (K):", niveis)
    f_p = st.number_input("% de P no Adubo (Ex: 14):", value=14.0)
with col_a3:
    formulado_nome = st.text_input("Nome do Adubo:", "04-14-08")
    dose = (req_p * 100) / f_p if f_p > 0 else 0.0

st.success(f"Dose Recomendada: {dose:.0f} kg/ha de {formulado_nome}")

# ---------------- 4. PDF (CORRIGIDO) ----------------
st.header("4️⃣ Gerar Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Função para tratar acentos no PDF
    def txt(t):
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    data_atual = datetime.now().strftime("%d/%m/%Y")

    # Título com acento
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(190, 8, txt(f"Emissão: {data_atual}"), ln=True, align="C")
    pdf.ln(10)

    # Identificação
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt(f"Produtor: {cliente}"), ln=True)
    pdf.cell(190, 8, txt(f"Talhão: {talhao}"), ln=True)
    pdf.cell(190, 8, txt(f"Área: {area} ha | Cultura: {cultura}"), ln=True)
    pdf.ln(5)

    # Calagem com acento
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("RECOMENDAÇÃO DE CALAGEM"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"Necessidade de Calcário: {nc:.2f} t/ha"), ln=True)
    pdf.cell(190, 7, txt(f"Total para a área: {total_calc:.2f} toneladas"), ln=True)
    pdf.ln(5)

    # Adubação com acento e Dose
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("RECOMENDAÇÃO DE ADUBAÇÃO"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"Nível P: {nivel_p} | Nível K: {nivel_k}"), ln=True)
    pdf.cell(190, 7, txt(f"Adubo Formulado: {formulado_nome}"), ln=True)
    
    # Quantidade de Adubo (Destaque)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, txt(f"QUANTIDADE DE ADUBO APLICAR: {dose:.0f} kg/ha"), ln=True)

    pdf.ln(20)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(190, 10, txt("Consultor Responsável: Felipe Amorim"), align="C")

    return pdf.output(dest='S').encode('latin-1')

try:
    if st.button("📄 Gerar PDF Final"):
        pdf_bytes = gerar_pdf()
        st.download_button(
            label="⬇️ Baixar Relatório Corrigido",
            data=pdf_bytes,
            file_name=f"Relatorio_{talhao}.pdf",
            mime="application/pdf"
        )
except Exception as e:
    st.error(f"Erro ao gerar o PDF. Verifique se os dados estão preenchidos.")

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
