import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- 1. SEGURANÇA E DATA (SEM ERROS) ----------------
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
                st.error("Acesso Negado.")
        return False
    return True

if verificar_acesso():
    # Data corrigida para fuso de Brasília (sem bibliotecas extras)
    data_hoje = (datetime.utcnow() - timedelta(hours=3)).strftime('%d/%m/%Y')

    st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide")

    # ---------------- ENTRADAS (SIDEBAR) ----------------
    with st.sidebar:
        st.header("Configurações")
        cliente = st.text_input("👨‍🌾 Cliente:", "Produtor Exemplo")
        fazenda = st.text_input("🏠 Fazenda:", "Nome da Propriedade")
        area = st.number_input("📏 Área (ha):", min_value=0.01, value=1.0)
        cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"])
        meta = st.select_slider("🎯 Meta (t/ha):", options=[float(i) for i in range(2, 21)], value=8.0 if cultura == "Milho" else 4.0)

    st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
    st.write(f"Consultor: **Felipe Amorim** | Data: **{data_hoje}**")

    # ---------------- 1. ANÁLISE DE SOLO (ENTRADA) ----------------
    st.subheader("1️⃣ Análise de Solo")
    c1, c2, c3 = st.columns(3)
    with c1:
        p_solo = st.number_input("Fósforo (mg/dm³)", value=12.9)
        k_solo = st.number_input("Potássio (cmolc/dm³)", value=0.06)
    with c2:
        argila = st.number_input("Argila (%)", value=54.0)
        v_atual = st.number_input("V% Atual", value=46.6)
    with c3:
        ctc = st.number_input("CTC (cmolc/dm³)", value=3.25)
        prnt = st.number_input("PRNT (%)", value=85.0)

    # --- O "MOTOR" DE CÁLCULO (SUAS FÓRMULAS) ---
    v_alvo = 70 if cultura == "Soja" else 60
    nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
    
    # Interpretação P e K
    if argila > 35: status_p = "Baixo" if p_solo <= 6 else "Médio" if p_solo <= 9 else "Bom"
    else: status_p = "Baixo" if p_solo <= 12 else "Médio" if p_solo <= 18 else "Bom"
    status_k = "Baixo" if k_solo <= 0.15 else "Médio" if k_solo <= 0.30 else "Bom"

    # Recomendação de N, P, K
    if cultura == "Milho":
        rec_n = meta * 22
        n_plantio = 30
        n_cobertura = rec_n - n_plantio
        rec_p = (meta * 12) * (1.3 if status_p == "Baixo" else 1.0)
        rec_k = (meta * 18) * (1.2 if status_k == "Baixo" else 1.0)
    else: # Soja
        rec_n, n_plantio, n_cobertura = 0, 0, 0
        rec_p = (meta * 15) * (1.5 if status_p == "Baixo" else 1.0)
        rec_k = (meta * 20) * (1.4 if status_k == "Baixo" else 1.0)

    # ---------------- 2. DIAGNÓSTICO (EXIBIÇÃO) ----------------
    st.divider()
    st.subheader("2️⃣ Diagnóstico e Metas")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Textura", "Argiloso" if argila > 35 else "Médio/Arenoso")
    d2.metric("V% Alvo", f"{v_alvo}%")
    d3.metric("Status P", status_p)
    d4.metric("Status K", status_k)

    # ---------------- 3. PRESCRIÇÃO (EXIBIÇÃO) ----------------
    st.divider()
    st.subheader("3️⃣ Planejamento de Fertilizantes")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"🪨 **Calagem:** {nc:.2f} t/ha")
        if cultura == "Milho":
            st.warning(f"⚡ **Nitrogênio (N):** Total {rec_n:.0f}kg/ha\n- Plantio: 30kg | Cobertura: {n_cobertura:.0f}kg")

    with col_b:
        st.write("🛒 **Formulação Comercial**")
        f_n = st.number_input("N%", value=4 if cultura == "Milho" else 0)
        f_p = st.number_input("P%", value=20)
        f_k = st.number_input("K%", value=20)
        
        # Cálculo da dose pelo nutriente mais exigido
        dose = max((rec_p/f_p*100) if f_p>0 else 0, (rec_k/f_k*100) if f_k>0 else 0)
        sacos = math.ceil((dose * area) / 50)
        st.success(f"**Dose:** {dose:.0f} kg/ha | **Total:** {sacos} sacos")

    # ---------------- PDF ----------------
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        def t(texto): return str(texto).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 15, t("LAUDO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
        pdf.set_font("Arial", "", 10); pdf.cell(190, 5, t(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
        
        pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, t("1. INFORMAÇÕES GERAIS"), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 6, t(f"Cliente: {cliente} | Fazenda: {fazenda}"), ln=True)
        pdf.cell(190, 6, t(f"Cultura: {cultura} | Meta: {meta} t/ha"), ln=True)
        
        pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(190, 8, t("2. PRESCRIÇÃO TÉCNICA"), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 6, t(f"Calagem: {nc:.2f} t/ha"), ln=True)
        if cultura == "Milho":
            pdf.cell(190, 6, t(f"N Total: {rec_n:.0f}kg (Plantio: 30kg | Cobertura: {n_cobertura:.0f}kg)"), ln=True)
        pdf.cell(190, 6, t(f"Adubação: {dose:.0f} kg/ha do {f_n}-{f_p}-{f_k} ({sacos} sacos total)"), ln=True)
        
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
        st.download_button("⬇️ Baixar PDF", gerar_pdf(), file_name=f"Laudo_{cliente}.pdf")
