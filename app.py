import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- 1. SEGURANÇA E DATA (SEM PYTZ) ----------------
def verificar_acesso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Sistema Felipe Amorim</h1>", unsafe_allow_html=True)
        senha = st.text_input("Digite a Senha de Consultor:", type="password")
        if st.button("Liberar Sistema"):
            if senha == "@Lipe1928": 
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Acesso Negado. Senha Incorreta.")
        return False
    return True

if verificar_acesso():
    # Ajuste de data manual para evitar erro de servidor
    data_hoje = (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y')

    # ---------------- ESTILO VISUAL ----------------
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
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.title("Configurações")
        cliente = st.text_input("👨‍🌾 Nome do Cliente:", "")
        fazenda = st.text_input("🏠 Fazenda:", "")
        st.divider()
        area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0)
        cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"])
        meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[float(i/2) for i in range(2, 31)], value=8.0 if cultura == "Milho" else 4.0)

    # ---------------- ENTRADA DE DADOS ----------------
    st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
    st.write(f"**Consultor:** Felipe Amorim | **Data:** {data_hoje}")

    # (O restante dos cálculos de solo e adubação que você já tem no código...)
    # Mantendo a lógica de P, K, Argila e N que vimos nas imagens

    st.subheader("1️⃣ Análise de Solo")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=12.9)
        k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.06)
    with col2:
        argila = st.number_input("Argila (%)", 0.0, 100.0, value=54.0)
        v_atual = st.number_input("V% Atual", 0.0, 100.0, value=46.6)
    with col3:
        ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
        prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

    # Lógica de cálculo simplificada para garantir funcionamento
    v_alvo = 70 if cultura == "Soja" else 60
    nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
    
    # Exemplo de saída para o PDF
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 15, txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
        pdf.set_font("Arial", "", 10); pdf.cell(190, 5, txt(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
        
        pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, txt(" 1. INFORMAÇÕES GERAIS E DIAGNÓSTICO"), ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, txt(f" Cliente: {cliente} | Fazenda: {fazenda}"), ln=True)
        pdf.cell(190, 7, txt(f" Calagem Recomendada: {nc:.2f} t/ha"), ln=True)
        
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
        pdf_bytes = gerar_pdf()
        st.download_button("⬇️ Baixar Agora", pdf_bytes, file_name=f"Relatorio_{cliente}.pdf")
