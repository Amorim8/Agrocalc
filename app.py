import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- 1. BLINDAGEM: SISTEMA DE ACESSO ----------------
def verificar_acesso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Sistema Felipe Amorim</h1>", unsafe_allow_html=True)
        senha = st.text_input("Digite a Senha de Consultor:", type="password")
        if st.button("Liberar Sistema"):
            if senha == "FELIPE2026": # Mude sua senha aqui se desejar
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Acesso Negado. Senha Incorreta.")
        return False
    return True

if verificar_acesso():
    # ---------------- CONFIGURAÇÃO VISUAL ----------------
    st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide")

    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        div[data-testid="stMetric"] {
            background-color: #1a1c23 !important;
            border-left: 5px solid #28a745 !important;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #28a745 !important;
            color: white !important;
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)

    # ---------------- SIDEBAR (CONFIGURAÇÕES) ----------------
    with st.sidebar:
        st.title("Configurações")
        cliente = st.text_input("👨‍🌾 Nome do Cliente:", "")
        fazenda = st.text_input("🏠 Fazenda:", "")
        area = st.number_input("📏 Área Total (ha):", min_value=0.1, value=1.0)
        cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"])
        meta = st.select_slider("🎯 Meta (t/ha):", options=[i for i in range(2, 20)], value=8 if cultura == "Milho" else 4)

    # ---------------- CÁLCULOS TÉCNICOS ----------------
    # Data corrigida para HOJE
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    
    # Simulação de lógica de solo (P e K)
    st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
    st.write(f"Consultor: **Felipe Amorim** | Data: **{data_hoje}**")

    col1, col2, col3 = st.columns(3)
    with col1: p_solo = st.number_input("Fósforo (mg/dm³)", value=8.0)
    with col2: k_solo = st.number_input("Potássio (cmolc/dm³)", value=0.15)
    with col3: v_atual = st.number_input("V% Atual", value=40.0)

    # Lógica de Recomendação (Simplificada para o exemplo)
    status_p = "Baixo" if p_solo < 10 else "Bom"
    status_k = "Baixo" if k_solo < 0.2 else "Bom"
    nc = max(0.0, (70 - v_atual) * 2 / 100) # Exemplo de calc calagem
    
    rec_n_total = meta * 22 if cultura == "Milho" else 0
    n_plantio = 30 if cultura == "Milho" else 0
    n_cobertura = rec_n_total - n_plantio

    # ---------------- EXIBIÇÃO NA TELA ----------------
    st.divider()
    st.subheader("2️⃣ Diagnóstico e Metas")
    m1, m2, m3 = st.columns(3)
    m1.metric("Status P", status_p)
    m2.metric("Status K", status_k)
    m3.metric("Calagem (t/ha)", f"{nc:.2f}")

    if cultura == "Milho":
        st.info(f"⚡ **Manejo de N:** {n_plantio}kg no Plantio | {n_cobertura}kg na Cobertura")

    # ---------------- GERAÇÃO DO PDF PROTEGIDO ----------------
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_fill_color(34, 139, 34)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 15, "RELATORIO DE RECOMENDACAO TECNICA", ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 5, f"Consultor: Felipe Amorim | Data: {data_hoje}", ln=True, align="C")

        # Corpo do Relatório
        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "1. INFORMACOES GERAIS", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, f"Cliente: {cliente if cliente else 'Nao informado'}", ln=True)
        pdf.cell(190, 7, f"Cultura: {cultura} | Meta: {meta} t/ha", ln=True)
        pdf.cell(190, 7, f"Status Solo: P ({status_p}) | K ({status_k})", ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "2. PRESCRICAO", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, f"Calagem: {nc:.2f} t/ha", ln=True)
        if cultura == "Milho":
            pdf.cell(190, 7, f"Nitrogenio Total: {rec_n_total} kg/ha", ln=True)
            pdf.cell(190, 7, f" - Plantio: {n_plantio} kg/ha | Cobertura: {n_cobertura} kg/ha", ln=True)

        # Fontes Técnicas
        pdf.ln(15)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, "FONTES TECNICAS:", ln=True)
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(190, 5, "Interpretacao: Embrapa Cerrados. Recomendacao: IPNI Brasil.")

        return pdf.output(dest='S').encode('latin-1')

    if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
        pdf_bytes = gerar_pdf()
        nome_arquivo = f"Relatorio_{cliente.replace(' ', '_')}.pdf" if cliente else "Relatorio_FelipeAmorim.pdf"
        st.download_button("⬇️ Baixar Agora", pdf_bytes, file_name=nome_arquivo)

    st.caption("Felipe Amorim | Consultoria Agronômica")
