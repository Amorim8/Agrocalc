import streamlit as st
from fpdf import FPDF
import math

# ---------------- CONFIG E PROTEÇÃO VISUAL ----------------
st.set_page_config(page_title="Consultoria Felipe Amorim", layout="wide")

hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

st.title("🌿 Consultoria Agronômica Inteligente")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR ----------------
st.sidebar.header("🎯 Planejamento da Safra")
cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area = st.sidebar.number_input("Área Total (ha):", min_value=0.1, value=1.0)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

meta_ton = st.sidebar.slider(
    f"Meta de Colheita ({cultura}) - Ton/ha:", 
    min_value=2.0, max_value=12.0, 
    value=4.0 if cultura == "Soja" else 8.0, step=0.5
)

# ---------------- 1️⃣ ENTRADA DE DADOS ----------------
st.header("1️⃣ Análise de Solo (Química e Física)")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
with col2:
    argila = st.number_input("Argila (%)", 0.0, max_value=100.0, value=35.0)
    v_atual = st.number_input("V% Atual", 0.0, value=40.0)
with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
    prnt = st.number_input("PRNT (%)", 0.0, value=85.0)

# ---------------- 2️⃣ LÓGICA TÉCNICA ----------------
def interpretar_solo(p, k, arg):
    if arg > 60: limits_p = [2.0, 4.0, 6.0, 9.0]
    elif arg > 35: limits_p = [3.0, 6.0, 9.0, 12.0]
    elif arg > 15: limits_p = [4.0, 8.0, 12.0, 18.0]
    else: limits_p = [6.0, 12.0, 18.0, 30.0]
    
    niv_p = "Baixo" if p <= limits_p[1] else "Médio" if p <= limits_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return niv_p, niv_k

nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)

# Calagem
v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

# Adubação
if cultura == "Soja":
    rec_n, obs_n = 0, "Nitrogênio via Fixação Biológica. Realizar inoculação."
    rec_p = (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
else:
    rec_n, obs_n = meta_ton * 22, "Dividir N: 20% no plantio e 80% em cobertura."
    rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)

# ---------------- 3️⃣ EXIBIÇÃO NA TELA ----------------
st.divider()
st.header(f"2️⃣ Diagnóstico e Recomendações")
st.info(f"**Calagem:** {nc:.2f} t/ha | **Adubação NPK:** {rec_n:.0f}-{rec_p:.0f}-{rec_k:.0f} kg/ha")

# ---------------- 4️⃣ FORMULADOS ----------------
st.header("3️⃣ Insumos e Sacaria")
f1, f2, f3 = st.columns(3)
fn, fp, fk = f1.number_input("N%", 0), f2.number_input("P%", 20), f3.number_input("K%", 20)
dose_ha = (rec_p / fp * 100) if fp > 0 else 0
total_sacos = math.ceil((dose_ha * area) / 50) if dose_ha > 0 else 0

if dose_ha > 0:
    st.success(f"Dose: {dose_ha:.0f} kg/ha | Total: {total_sacos} sacos de 50kg")

# ---------------- 5️⃣ PDF PROFISSIONAL ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Cores e Cabeçalho Verde Forte
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 20, txt("LAUDO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 5, txt(f"Consultor: Felipe Amorim"), align="C", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)

    # SUBTÍTULO: DADOS (FUNDO CINZA)
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(190, 8, txt("1. INFORMAÇÕES GERAIS"), ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"Produtor: {cliente} | Talhão: {talhao}"), ln=True)
    pdf.cell(190, 7, txt(f"Cultura: {cultura} | Área: {area} ha | Meta: {meta_ton} t/ha"), ln=True)
    
    pdf.ln(5)
    
    # SUBTÍTULO: ANALISE
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("2. DIAGNÓSTICO DO SOLO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 7, txt(f"P: {p_solo} mg/dm³ ({nivel_p}) | K: {k_solo} cmolc ({nivel_k}) | Argila: {argila}%"), ln=True)
    pdf.cell(190, 7, txt(f"V% Atual: {v_atual}% | CTC: {ctc} | PRNT: {prnt}%"), ln=True)

    pdf.ln(5)

    # SUBTÍTULO: RECOMENDAÇÃO
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, txt("3. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 7, txt(f"CALAGEM: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), ln=True)
    pdf.cell(190, 7, txt(f"ADUBAÇÃO NPK (kg/ha): {rec_n:.0f} - {rec_p:.0f} - {rec_k:.0f}"), ln=True)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(190, 6, txt(f"Obs: {obs_n}"))
    
    if dose_ha > 0:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 7, txt(f"FORMULADO: {fn}-{fp}-{fk} | Dose: {dose_ha:.0f} kg/ha | Total: {total_sacos} sacos"), ln=True)

    # RODAPÉ TÉCNICO (FONTES)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(190, 8, txt("FONTES E REFERÊNCIAS TÉCNICAS:"), ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(190, 5, txt("- Interpretação de P: Embrapa Cerrados (Sistemas de Produção).\n- Níveis Críticos de K: Embrapa Soja / Embrapa Milho.\n- Exportação de Nutrientes: IPNI Brasil (International Plant Nutrition Institute).\n- Cálculo de Calagem: Método da Elevação da Saturação por Bases (V%)."))

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar Relatório Profissional"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Laudo_{cliente}_{talhao}.pdf")

st.caption("Sistema de Consultoria Agronômica | Felipe Amorim")
