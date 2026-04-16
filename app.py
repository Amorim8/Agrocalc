import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# ---------------- CONFIG E ESTILO PREMIUM ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

# CSS para customizar a aparência e dar cara de software pago
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #228B22; }
    div[data-testid="stExpander"] { background-color: #ffffff; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #228B22; color: white; font-weight: bold; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2510/2510250.png", width=80)
    st.title("Configurações")
    cliente = st.text_input("👨‍🌾 Cliente:", "Produtor Exemplo")
    fazenda = st.text_input("🏠 Fazenda:", "Nome da Propriedade")
    talhao = st.text_input("📍 Talhão:", "Gleba 01")
    municipio = st.text_input("🏙️ Município:", "Cidade")
    estado = st.selectbox("🌎 Estado:", ["GO", "MT", "MS", "MG", "PR", "SP", "BA", "TO", "RS", "SC", "PA"])
    
    st.divider()
    area = st.number_input("📏 Área (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    meta_ton = st.select_slider("🎯 Meta de Produção (t/ha):", options=[i/2 for i in range(2, 25)], value=4.0 if cultura == "Soja" else 8.0)

# ---------------- CABEÇALHO ----------------
col_tit, col_logo = st.columns([4, 1])
with col_tit:
    st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
    st.write(f"**Consultor responsável:** Felipe Amorim | **Data:** {datetime.now().strftime('%d/%m/%Y')}")

# ---------------- 1️⃣ ENTRADA DE DADOS (CARDS) ----------------
st.subheader("1️⃣ Dados da Análise de Solo")
with st.container():
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    p_solo = c1.number_input("P (mg/dm³)", 0.0, value=8.0)
    k_solo = c2.number_input("K (cmolc)", 0.0, value=0.15)
    argila = c3.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = c4.number_input("V% Atual", 0.0, 100.0, value=40.0)
    ctc = c5.number_input("CTC Total", 0.0, value=3.25)
    prnt = c6.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA TÉCNICA ----------------
def interpretar_solo(p, k, arg):
    if arg > 60: lim_p = [2, 4, 6, 9]
    elif arg > 35: lim_p = [3, 6, 9, 12]
    elif arg > 15: lim_p = [4, 8, 12, 18]
    else: lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return "Muito Argiloso" if arg > 60 else "Argiloso" if arg > 35 else "Médio" if arg > 15 else "Arenoso", niv_p, niv_k

classe_txt, nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)
v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    obs_n = "Inoculação via Bradyrhizobium."
else:
    rec_n, rec_p = meta_ton * 22, (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
    obs_n = "Dividir N em cobertura (V4-V6)."

# ---------------- 2️⃣ DASHBOARD DE RESULTADOS ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Prescrição")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Textura Solo", classe_txt)
m2.metric("Saturação Alvo", f"{v_alvo}%")
m3.metric("Status P", nivel_p)
m4.metric("Status K", nivel_k)

st.write("---")
r1, r2, r3 = st.columns([1, 1, 1])
with r1:
    st.markdown("### 🪨 Calagem")
    st.metric("Necessidade (t/ha)", f"{nc:.2f}")
    st.write(f"Total para {area} ha: **{total_calc:.2f} toneladas**")

with r2:
    st.markdown("### 🧪 Nutrientes (kg/ha)")
    st.write(f"**N:** {rec_n:.0f} | **P₂O₅:** {rec_p:.0f} | **K₂O:** {rec_k:.0f}")
    st.info(f"💡 {obs_n}")

with r3:
    st.markdown("### 🛒 Insumos Comercial")
    f_n = st.number_input("N% Adubo", 0)
    f_p = st.number_input("P% Adubo", 20)
    f_k = st.number_input("K% Adubo", 20)
    
    if f_p > 0:
        dose = (rec_p / f_p) * 100
        total_sacos = math.ceil((dose * area) / 50)
        st.success(f"Dose: **{dose:.0f} kg/ha**")
        st.write(f"Pedido: **{total_sacos} sacos de 50kg**")

# ---------------- 3️⃣ BOTÕES DE RELATÓRIO ----------------
st.divider()
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 20, txt("LAUDO TÉCNICO DE RECOMENDAÇÃO"), align="C", ln=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 5, txt(f"Emissor: Felipe Amorim | {datetime.now().strftime('%d/%m/%Y')}"), align="C", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 11); pdf.cell(190, 8, txt(f" CLIENTE: {cliente} | LOCAL: {municipio}-{estado}"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 8, txt(f" Área: {area} ha | Cultura: {cultura} | Meta: {meta_ton} t/ha"), ln=True)
    pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(190, 8, txt(" PRESCRIÇÃO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10); pdf.cell(190, 7, txt(f" Calcário: {nc:.2f} t/ha | NPK: {rec_n:.0f}-{rec_p:.0f}-{rec_k:.0f} kg/ha"), ln=True)
    pdf.cell(190, 7, txt(f" Adubo Sugerido: {fn}-{fp}-{fk} | Dose: {dose:.0f} kg/ha | Total Sacos: {total_sacos}"), ln=True)
    pdf.ln(10); pdf.set_font("Arial", "I", 8); pdf.cell(190, 5, txt("Fontes: Embrapa Cerrados, Embrapa Soja, IPNI Brasil."), align="C")
    return pdf.output(dest='S').encode('latin-1')

c_pdf1, c_pdf2, c_pdf3 = st.columns([1,1,1])
with c_pdf2:
    if st.button("📄 GERAR LAUDO PROFISSIONAL"):
        pdf_bytes = gerar_pdf()
        st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Laudo_{cliente}.pdf")

st.caption("Felipe Amorim | Consultoria de Solos & Nutrição de Plantas")
