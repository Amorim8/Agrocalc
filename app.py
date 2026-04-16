import streamlit as st
from fpdf import FPDF
from datetime import datetime

# ---------------- CONFIGURAÇÃO VISUAL ----------------
st.set_page_config(page_title="Consultoria Agronômica - Felipe Amorim", layout="wide")

# CSS para personalizar as cores (Fundo verde suave e subtítulos cinzas)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stHeader { color: #2e7d32; }
    .subtitle-box {
        background-color: #e0e0e0;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #2e7d32;
        font-weight: bold;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 Consultoria Agronômica")
st.markdown(f"<h2 style='color: #2e7d32;'>Consultor: Felipe Amorim</h2>", unsafe_allow_html=True)
st.write(f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Informações da Área")
cliente = st.sidebar.text_input("Produtor:", "Nome do Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area = st.sidebar.number_input("Área Total (ha):", min_value=0.0, value=1.0)
cultura = st.sidebar.selectbox("Cultura:", ["Milho", "Soja"])

# ---------------- 1️⃣ ANÁLISE DE SOLO (ESTILIZADA) ----------------
st.markdown('<div class="subtitle-box">1️⃣ ENTRADA DE DADOS DA ANÁLISE</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    argila = st.number_input("Teor de Argila (%)", 0.0, 100.0, 53.0)
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0)
with col2:
    v_atual = st.number_input("V% Atual", 0.0)
    ctc = st.number_input("CTC (T)", 0.0, 100.0, 5.0)
with col3:
    prnt = st.number_input("PRNT (%)", 0.1, 120.0, 80.0)
    prod_meta = st.number_input("Meta (sc/ha ou t/ha)", value=118.0)

# ---------------- 2️⃣ LÓGICA DE TABELA POR ARGILA ----------------
if argila > 60:
    classe, limites_p = "Classe 1 (> 60%)", [2.0, 4.0]
    rec_p = {"BAIXO": 120, "MÉDIO": 80, "BOM": 40}
elif 35 < argila <= 60:
    classe, limites_p = "Classe 2 (35-60%)", [3.0, 6.0]
    rec_p = {"BAIXO": 100, "MÉDIO": 70, "BOM": 30}
elif 15 < argila <= 35:
    classe, limites_p = "Classe 3 (15-35%)", [5.0, 10.0]
    rec_p = {"BAIXO": 80, "MÉDIO": 50, "BOM": 20}
else:
    classe, limites_p = "Classe 4 (< 15%)", [8.0, 16.0]
    rec_p = {"BAIXO": 60, "MÉDIO": 40, "BOM": 0}

# Diagnóstico de P e K
status_p = "BAIXO" if p_solo <= limites_p[0] else ("MÉDIO" if p_solo <= limites_p[1] else "BOM")
status_k = "BAIXO" if k_solo <= 0.15 else ("MÉDIO" if k_solo <= 0.30 else "BOM")

dose_p = rec_p[status_p]
dose_k = 90 if status_k == "BAIXO" else (60 if status_k == "MÉDIO" else 30)

# Calagem
v_alvo = 70 if cultura == "Soja" else 60
nc = ((v_alvo - v_atual) * ctc) / prnt if v_atual < v_alvo else 0

# ---------------- 3️⃣ ADUBO FORMULADO (QUALQUER FORMULAÇÃO) ----------------
st.markdown('<div class="subtitle-box">2️⃣ RECOMENDAÇÃO E FORMULADO</div>', unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    f_n = st.number_input("% N do Adubo", 0.0)
    f_p = st.number_input("% P do Adubo", 0.0)
    f_k = st.number_input("% K do Adubo", 0.0)

# Nitrogênio Parcelado (Milho)
if cultura == "Milho":
    n_total = 150 if prod_meta > 110 else 120
    n_plantio = 30
    n_cobertura = n_total - n_plantio
else:
    n_total = n_plantio = n_cobertura = 0

# Cálculo da Dose do Formulado
doses_calc = []
if f_n > 0: doses_calc.append((n_plantio / f_n) * 100)
if f_p > 0: doses_calc.append((dose_p / f_p) * 100)
if f_k > 0: doses_calc.append((dose_k / f_k) * 100)

dose_final = max(doses_calc) if doses_calc else 0

# Exibição dos resultados
st.success(f"Dose Recomendada: {dose_final:.0f} kg/ha | Calcário: {nc:.2f} t/ha")

# ---------------- 4️⃣ GERAÇÃO DE PDF PERSONALIZADO ----------------
def gerar_pdf_formatado():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Verde
    pdf.set_fill_color(46, 125, 50) 
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 15, "CONSULTORIA AGRONÔMICA", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 10, f"Consultor: Felipe Amorim", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    
    # Subtítulo Cinza no PDF
    pdf.set_fill_color(224, 224, 224)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "  DADOS DA ANÁLISE E DIAGNÓSTICO", ln=True, fill=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(95, 10, f"Produtor: {cliente}")
    pdf.cell(95, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(95, 10, f"Talhão: {talhao} | Área: {area} ha")
    pdf.cell(95, 10, f"Argila: {argila}% ({classe})", ln=True)
    
    pdf.ln(5)
    pdf.set_fill_color(224, 224, 224)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "  RECOMENDAÇÃO TÉCNICA", ln=True, fill=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 10, f"Cultura: {cultura} | Meta: {prod_meta}", ln=True)
    pdf.cell(190, 8, f"- Fósforo: {status_p} ({p_solo} mg/dm3) -> Aplicar {dose_p} kg/ha P2O5", ln=True)
    pdf.cell(190, 8, f"- Potássio: {status_k} ({k_solo} cmolc/dm3) -> Aplicar {dose_k} kg/ha K2O", ln=True)
    if cultura == "Milho":
        pdf.cell(190, 8, f"- Nitrogênio Total: {n_total} kg/ha (Plantio: {n_plantio} | Cobertura: {n_cobertura})", ln=True)
    
    pdf.ln(5)
    pdf.cell(190, 10, f"Calagem: Necessidade de {nc:.2f} t/ha de Calcário.", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 Gerar Relatório Profissional"):
    st.download_button("Clique aqui para baixar", gerar_pdf_formatado(), f"Consultoria_{talhao}.pdf")
