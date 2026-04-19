import streamlit as st
from fpdf import FPDF # Importante: Utilize a biblioteca fpdf2 (pip install fpdf2)
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- SISTEMA DE LOGIN ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Acessar Sistema"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- LÓGICA DE INTERPRETAÇÃO TÉCNICA ----------------
def interpretar_fosforo(p, argila):
    if argila > 60: limites = [2.0, 4.0]
    elif argila > 35: limites = [3.0, 6.0]
    elif argila > 15: limites = [4.0, 9.0]
    else: limites = [6.0, 12.0]
    if p <= limites[0]: return "Baixo"
    if p <= limites[1]: return "Médio"
    return "Alto"

def interpretar_potassio(k):
    if k <= 0.15: return "Baixo"
    if k <= 0.30: return "Médio"
    return "Alto"

# ---------------- CONFIG VISUAL (CONTRASTE MÁXIMO) ----------------
st.set_page_config(page_title="Sistema de Prescrição Agronômica", layout="wide")

st.markdown("""
<style>
/* Estilização das métricas conforme imagem (Fundo Escuro) */
div[data-testid="stMetric"] {
    background-color: #1e293b !important;
    border-radius: 15px;
    padding: 25px;
    border-left: 10px solid #22c55e !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}
/* Valores e Rótulos */
div[data-testid="stMetricValue"] > div { color: #ffffff !important; font-size: 42px !important; font-weight: 800 !important; }
div[data-testid="stMetricLabel"] > div > p { color: #94a3b8 !important; font-size: 18px !important; font-weight: bold !important; text-transform: uppercase; }

.stButton>button {
    background-color: #16a34a !important;
    color: white !important;
    font-weight: bold;
    height: 3.5em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR (PARÂMETROS) ----------------
with st.sidebar:
    st.title("🌿 Parâmetros")
    nome_cliente = st.text_input("Produtor:")
    fazenda = st.text_input("Fazenda:")
    municipio = st.text_input("Município:")
    estado = st.selectbox("Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("Área Total (ha):", min_value=0.01, value=1.0, step=0.1)
    cultura = st.radio("Cultura de Interesse:", ["Soja", "Milho", "Palma"], horizontal=True)
    
    variedade_palma = ""
    if cultura == "Palma":
        variedade_palma = st.selectbox("Variedade da Palma:", ["Orelha de Elefante", "Palma Miúda"])
    
    meta_padrao = 50.0 if cultura == "Palma" else (8.0 if cultura == "Milho" else 4.0)
    meta_ton = st.number_input("Meta de Produtividade (t/ha):", value=meta_padrao)

# ---------------- ENTRADA DE DADOS DA ANÁLISE ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")

st.subheader("Entrada de Dados da Análise de Solo")
c1, c2, c3, c4 = st.columns(4)
with c1:
    ph_solo = st.number_input("pH (Água)", value=5.5)
    p_solo = st.number_input("Fósforo (mg/dm³)", value=8.0)
with c2:
    al_solo = st.number_input("Alumínio (cmolc/dm³)", value=0.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", value=0.15)
with c3:
    argila = st.number_input("Argila (%)", value=35.0)
    v_atual = st.number_input("V% Atual", value=40.0)
with c4:
    ctc_t = st.number_input("CTC (T)", value=3.25)
    prnt_calc = st.number_input("PRNT Calcário (%)", value=85.0)

# ---------------- CÁLCULOS TÉCNICOS ----------------
status_p = interpretar_fosforo(p_solo, argila)
status_k = interpretar_potassio(k_solo)

v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 

st.subheader("Configuração da Fórmula Comercial (NPK)")
f1, f2, f3 = st.columns(3)
fn, fp, fk = f1.number_input("N (%)", 4), f2.number_input("P (%)", 20), f3.number_input("K (%)", 20)
dose_ha = max(((meta_ton * 15)/fp*100) if fp>0 else 0, ((meta_ton * 20)/fk*100) if fk>0 else 0)

# ---------------- EXIBIÇÃO DE RESULTADOS NA TELA ----------------
st.divider()
st.header("Resumo das Recomendações")
r1, r2, r3 = st.columns(3)
r1.metric("CALCÁRIO (T/HA)", f"{nc:.2f}")
r2.metric("GESSO (T/HA)", f"{ng:.2f}")
r3.metric("ADUBO (KG/HA)", f"{dose_ha:.0f}")

# ---------------- GERAÇÃO DO PDF (COM ACENTOS E LAYOUT DE BLOCOS) ----------------
def gerar_pdf():
    # fpdf2 suporta acentos UTF-8 nativamente
    pdf = FPDF()
    pdf.add_page()
    
    # 1. DADOS DO CLIENTE (BLOCO CINZA)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 10, " 1. DADOS DO CLIENTE E PROPRIEDADE", border=1, ln=1, fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, f"Produtor: {nome_cliente} | Fazenda: {fazenda}", ln=1)
    pdf.cell(190, 7, f"Local: {municipio} - {estado} | Área: {area} ha", ln=1)
    pdf.cell(190, 7, f"Cultura: {cultura} | Meta de Produtividade: {meta_ton} t/ha", ln=1)
    pdf.ln(5)

    # 2. RECOMENDAÇÕES (BLOCO CINZA)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(190, 10, " 2. RECOMENDAÇÕES DE CORREÇÃO E ADUBAÇÃO", border=1, ln=1, fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, f"- Calcário: {nc:.2f} t/ha (Total área: {nc*area:.2f} t)", ln=1)
    pdf.cell(190, 7, f"- Gesso: {ng:.2f} t/ha (Total área: {ng*area:.2f} t)", ln=1)
    pdf.cell(190, 7, f"- Adubo Comercial: {dose_ha:.0f} kg/ha (Total área: {dose_ha*area:.1f} kg)", ln=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, f"  Status Químico do Solo: Fósforo ({status_p}) | Potássio ({status_k})", ln=1)
    pdf.ln(5)

    # 3. RECOMENDAÇÕES TÉCNICAS (VERDE CLARO)
    if cultura == "Palma":
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(210, 255, 210) 
        pdf.cell(190, 10, " 3. RECOMENDAÇÕES TÉCNICAS PARA PALMA", border=1, ln=1, fill=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.ln(2)
        pdf.multi_cell(190, 7, "- MANEJO DO CLADÓDIO: Não realizar o corte no cladódio-mãe. Ele deve ser preservado para garantir a longevidade e o rebrote do palmal.\n- PRIMEIRO CORTE: Deve ser realizado entre 18 a 24 meses após o plantio, conforme o vigor das raquetes.\n- ALTURA DE CORTE: Respeitar a arquitetura da planta para evitar estresse hídrico e pragas.")
        pdf.ln(10)

        # Referências
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(190, 7, "REFERÊNCIAS TÉCNICAS UTILIZADAS (PALMA)", ln=1)
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(190, 6, "- IPA (Instituto Agronômico de Pernambuco): Manual de Cultivo e Recomendação de Adubação.", ln=1)
        pdf.cell(190, 6, "- IPA: Instruções sobre o manejo de cortes e preservação de cladódios.", ln=1)

    # Assinatura Final
    pdf.ln(20)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, f"Responsável Técnico: Felipe Amorim", border=0, ln=1, align="R")
    
    return pdf.output()

# ---------------- BOTÃO DE GERAÇÃO ----------------
st.divider()
if st.button("📄 GERAR RELATÓRIO PDF COMPLETO"):
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="⬇️ Clique para Baixar o Relatório (Com Acentos)",
        data=pdf_bytes,
        file_name=f"Prescricao_{nome_cliente}.pdf",
        mime="application/pdf"
    )
