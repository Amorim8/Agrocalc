import streamlit as st
from fpdf import FPDF

# Configuração da Página para o Link Online
st.set_page_config(page_title="AgroCalc | Felipe Amorim", layout="wide", page_icon="🌿")

# Identidade do Especialista
autor = "Felipe Amorim"

st.title("🌿 AgroCalc: Consultoria Inteligente")
st.subheader(f"Responsável Técnico: {autor}")
st.markdown("---")

# Entradas de Dados
st.sidebar.header("📋 Identificação")
nome_area = st.sidebar.text_input("Talhão/Lote:", "Gleba A1")
cultura = st.sidebar.selectbox("Cultura Alvo:", ["Soja", "Milho", "Feijão", "Hortaliças", "Frutíferas"])

col1, col2 = st.columns(2)

with col1:
    st.header("🛡️ Correção (Calagem)")
    ctc = st.number_input("CTC (cmolc/dm³)", min_value=0.1, value=5.0)
    v1 = st.number_input("Saturação atual (V1 %)", min_value=0.0, value=30.0)
    v2 = st.number_input("Saturação desejada (V2 %)", min_value=0.0, value=70.0)
    prnt = st.number_input("PRNT do Calcário (%)", min_value=1.0, value=80.0)
    
    nc = ((v2 - v1) * ctc) / prnt
    nc = max(0.0, nc)
    st.info(f"👉 **Necessidade de Calcário:** {nc:.2f} t/ha")

with col2:
    st.header("🧪 Nutrição (NPK Individual)")
    st.write("Fórmula do Adubo:")
    c1, c2, c3 = st.columns(3)
    f_n = c1.number_input("N (%)", min_value=0, value=20)
    f_p = c2.number_input("P (%)", min_value=0, value=0)
    f_k = c3.number_input("K (%)", min_value=0, value=20)
    
    rec_n = st.number_input("Recomendação de N (kg/ha)", min_value=0.0, value=100.0)
    
    qtd_adubo = (rec_n * 100) / f_n if f_n > 0 else 0
    ent_p = (qtd_adubo * f_p) / 100
    ent_k = (qtd_adubo * f_k) / 100
    
    st.success(f"🚜 **Dose do Adubo:** {qtd_adubo:.1f} kg/ha")
    st.write(f"🔹 **N:** {rec_n:.1f} kg | **P:** {ent_p:.1f} kg | **K:** {ent_k:.1f} kg")

# Classe de PDF Profissional com Acentos
class PDF_Agro(FPDF):
    def header(self):
        self.set_fill_color(34, 139, 34) 
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 18)
        self.cell(0, 20, "RECOMENDAÇÃO TÉCNICA AGRONÔMICA", border=0, ln=1, align="C")
        self.set_font("helvetica", "I", 12)
        self.cell(0, 10, f"Consultoria: {autor}", border=0, ln=1, align="C")
        self.ln(15)

def exportar_pdf():
    pdf = PDF_Agro()
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(240, 255, 240) 
    pdf.cell(0, 10, f"DADOS DA ÁREA: {nome_area}", ln=1, fill=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Cultura: {cultura}", ln=1)
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "1. CORREÇÃO DE SOLO", ln=1, fill=True)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"- Necessidade de Calcário: {nc:.2f} t/ha", ln=1)
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "2. PLANO DE NUTRIÇÃO (NPK)", ln=1, fill=True)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f"- DOSE TOTAL: {qtd_adubo:.1f} kg/ha (Fórmula {f_n}-{f_p}-{f_k})", ln=1)
    pdf.set_font("helvetica", "I", 11)
    pdf.cell(0, 8, f"Aporte Individual: N: {rec_n:.1f}kg | P: {ent_p:.1f}kg | K: {ent_k:.1f}kg", ln=1)
    return pdf.output()

st.markdown("---")
if st.button("🚀 Gerar PDF Profissional"):
    dados_pdf = exportar_pdf()
    st.download_button(
        label="📥 Baixar PDF para Enviar ao Cliente",
        data=bytes(dados_pdf),
        file_name=f"Recomendacao_{nome_area}.pdf",
        mime="application/pdf"
    )

st.write("---")
st.caption(f"© 2026 | Sistema de Consultoria {autor}")
