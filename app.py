import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime
import pytz # Necessário para travar a data no horário do Brasil

# ---------------- 1. BLINDAGEM E AJUSTE DE DATA (BRASÍLIA) ----------------
def obter_data_brasil():
    # Força o fuso horário de Brasília para o PDF não sair com a data de amanhã
    fuso_br = pytz.timezone('America/Sao_Paulo')
    return datetime.now(fuso_br).strftime('%d/%m/%Y')

def verificar_acesso():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Sistema Felipe Amorim</h1>", unsafe_allow_html=True)
        senha = st.text_input("Digite a Senha de Consultor:", type="password")
        if st.button("Liberar Sistema"):
            if senha == "@Lipe1928": # SENHA ATUALIZADA
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Acesso Negado. Senha Incorreta.")
        return False
    return True

if verificar_acesso():
    # Captura a data correta de hoje (Brasília)
    data_hoje = obter_data_brasil()

    # ---------------- CONFIGURAÇÃO VISUAL DARK ----------------
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

    # ---------------- SIDEBAR (CONFIGURAÇÕES) ----------------
    with st.sidebar:
        st.title("Configurações")
        cliente = st.text_input("👨‍🌾 Nome do Cliente:", "")
        fazenda = st.text_input("🏠 Fazenda:", "")
        talhao = st.text_input("📍 Talhão:", "")
        st.divider()
        area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0)
        cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"])
        meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[float(i/2) for i in range(2, 31)], value=8.0 if cultura == "Milho" else 4.0)

    # ---------------- 1️⃣ ANÁLISE DE SOLO (ENTRADA) ----------------
    st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
    st.write(f"**Consultor:** Felipe Amorim | **Data:** {data_hoje}")

    st.subheader("1️⃣ Análise de Solo (Química e Física)")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
        k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
    with col2:
        argila = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
        v_atual = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    with col3:
        ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
        prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

    # Lógica de Interpretação Técnica
    def interpretar_solo(p, k, arg):
        if arg > 35: lim_p = [3, 6, 9, 12]
        else: lim_p = [6, 12, 18, 30]
        niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
        niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
        return "Argiloso" if arg > 35 else "Arenoso/Médio", niv_p, niv_k

    classe_txt, nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)
    v_alvo = 70 if cultura == "Soja" else 60
    nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
    total_calc = nc * area

    # Lógica de Recomendação de Nutrientes
    if cultura == "Soja":
        rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
        rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    else: # Milho
        rec_n = meta_ton * 22
        n_plantio = 30
        n_cobertura = max(0.0, rec_n - n_plantio)
        rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
        rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)

    # ---------------- 2️⃣ DASHBOARD DE DIAGNÓSTICO ----------------
    st.divider()
    st.subheader("2️⃣ Diagnóstico e Metas")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Textura Solo", classe_txt)
    m2.metric("V% Alvo", f"{v_alvo}%")
    m3.metric("Status P", nivel_p)
    m4.metric("Status K", nivel_k)

    # ---------------- 3️⃣ PRESCRIÇÃO E FERTILIZANTES ----------------
    st.write("---")
    st.subheader("3️⃣ Planejamento de Fertilizantes")
    r1, r2 = st.columns([1, 2])
    with r1:
        st.markdown("### 🪨 Calagem")
        st.metric("Dose (t/ha)", f"{nc:.2f}")
        st.write(f"Total para a área: **{total_calc:.2f} t**")
    with r2:
        if cultura == "Milho":
            nc1, nc2, nc3 = st.columns(3)
            nc1.metric("Total N", f"{rec_n:.0f} kg")
            nc2.metric("N Plantio", f"{n_plantio} kg")
            nc3.metric("N Cobertura", f"{n_cobertura:.0f} kg")
        
        st.markdown("### 🛒 Formulação Comercial")
        cn, cp, ck = st.columns(3)
        f_n = cn.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
        f_p = cp.number_input("P%", 0, value=20)
        f_k = ck.number_input("K%", 0, value=20)
        
        if f_p > 0 or f_k > 0:
            dose_final = max((rec_p/f_p*100) if f_p>0 else 0, (rec_k/f_k*100) if f_k>0 else 0)
            total_sacos = math.ceil((dose_final * area) / 50)
            st.success(f"Dose Recomendada: **{dose_final:.0f} kg/ha** | Total: **{total_sacos} sacos (50kg)**")

    # ---------------- 4️⃣ PDF RELATÓRIO PROFISSIONAL ----------------
    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
        
        # Cabeçalho Verde
        pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
        pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 15, txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
        pdf.set_font("Arial", "", 10); pdf.cell(190, 5, txt(f"Consultor: Felipe Amorim | Data: {data_hoje}"), align="C", ln=True)
        
        # 1. Informações Gerais e Diagnóstico
        pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, txt(" 1. INFORMAÇÕES GERAIS E DIAGNÓSTICO"), ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, txt(f" Cliente: {cliente if cliente else 'Nao informado'} | Fazenda: {fazenda}"), ln=True)
        pdf.cell(190, 7, txt(f" Cultura: {cultura} | Area: {area:.2f} ha | Meta: {meta_ton} t/ha"), ln=True)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, txt(f" Status Solo: Fosforo ({nivel_p}) | Potassio ({nivel_k}) | Textura ({classe_txt})"), ln=True)
        
        # 2. Prescrição
        pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, txt(" 2. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, txt(f" Calagem: {nc:.2f} t/ha (Total para a area: {total_calc:.2f} t)"), ln=True)
        
        if cultura == "Milho":
            pdf.set_font("Arial", "B", 10)
            pdf.cell(190, 7, txt(f" Recomendacao de Nitrogenio (N): Total {rec_n:.0f} kg/ha"), ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(190, 6, txt(f"  - Aplicacao no Plantio: {n_plantio} kg/ha"), ln=True)
            pdf.cell(190, 6, txt(f"  - Aplicacao em Cobertura (V4-V6): {n_cobertura:.0f} kg/ha"), ln=True)
        else:
            pdf.cell(190, 7, txt(" Recomendacao de Nitrogenio: Via Inoculacao Bradyrhizobium."), ln=True)
        
        pdf.ln(2); pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, txt(f" Adubacao Sugerida: {dose_final:.0f} kg/ha do formulado {f_n}-{f_p}-{f_k}"), ln=True)
        pdf.cell(190, 7, txt(f" Necessidade de Compra: {total_sacos} sacos (50kg) para a area total."), ln=True)

        # Fontes
        pdf.ln(15); pdf.set_font("Arial", "B", 10); pdf.set_text_color(34, 139, 34)
        pdf.cell(190, 8, txt("FONTES E REFERÊNCIAS TÉCNICAS:"), ln=True)
        pdf.set_font("Arial", "I", 9); pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(190, 5, txt("- Interpretacao de Solo: Embrapa Cerrados / Embrapa Soja.\n- Exportacao e Extracao: IPNI Brasil.\n- Manejo N: Boletim 100 / Embrapa Milho e Sorgo.\n- Calagem: Metodo da Elevacao da Saturacao por Bases (V%)."))
        
        return pdf.output(dest='S').encode('latin-1')

    st.divider()
    if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
        pdf_bytes = gerar_pdf()
        # Nome do arquivo de download dinâmico e limpo
        nome_arquivo = f"Relatorio_{cliente.replace(' ', '_')}.pdf" if cliente else f"Relatorio_FelipeAmorim_{data_hoje.replace('/', '-')}.pdf"
        st.download_button("⬇️ Baixar Agora", pdf_bytes, file_name=nome_arquivo)

    st.caption(f"Felipe Amorim | Consultoria Agronômica | {data_hoje}")
