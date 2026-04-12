import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# -------------------------------
# CONFIGURAÇÃO
# -------------------------------
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# -------------------------------
# CULTURAS
# -------------------------------
culturas = {
    "Soja": {"N": 0, "P": 80, "K": 60, "V": 60},
    "Milho": {"N": 120, "P": 90, "K": 80, "V": 70},
    "Pastagem": {"N": 80, "P": 60, "K": 50, "V": 50}
}

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.header("📋 Configuração da Área")

talhao = st.sidebar.text_input("Identificação do Talhão:", "Área Soja 01")
area_ha = st.sidebar.number_input("Tamanho da Área (ha):", value=1.0, min_value=0.01)

cultura = st.sidebar.selectbox("Cultura", list(culturas.keys()))

# -------------------------------
# CALAGEM
# -------------------------------
st.header("1. Recomendação de Calagem")

ctc = st.number_input("CTC (cmolc/dm³)", value=5.0)
v1 = st.number_input("V1 (%)", value=30.0)
v2 = culturas[cultura]["V"]
prnt = st.number_input("PRNT (%)", value=80.0)

st.caption(f"V2 automático para {cultura}: {v2}%")

interpretacao = ""

if v2 <= v1:
    st.warning("⚠️ V2 deve ser maior que V1 para haver necessidade de calagem.")
    nc_ha = 0
else:
    if prnt > 0:
        nc_base = ((v2 - v1) * ctc) / 100
        nc_ha = nc_base / (prnt / 100)
    else:
        nc_ha = 0

nc_total = nc_ha * area_ha

if nc_ha == 0:
    interpretacao = "Solo equilibrado. Não necessita calagem."
    st.success(interpretacao)
else:
    if nc_ha < 2:
        interpretacao = "Baixa necessidade de calagem"
    elif nc_ha <= 4:
        interpretacao = "Média necessidade de calagem"
    else:
        interpretacao = "Alta necessidade de calagem"

    st.info(f"👉 {nc_ha:.2f} t/ha | Total: {nc_total:.2f} t")
    st.caption(interpretacao)

    if nc_ha > 3:
        st.warning("⚠️ Recomenda-se parcelamento da aplicação")

# -------------------------------
# GESSAGEM
# -------------------------------
st.header("2. Gessagem")

gesso = ctc * 0.5 if nc_ha > 0 else 0
st.info(f"👉 Aplicar aproximadamente {gesso:.2f} t/ha de gesso agrícola")

# -------------------------------
# ADUBAÇÃO
# -------------------------------
st.header("3. Adubação NPK")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Adubo (%)")
    f_n = st.number_input("N (%)", value=0.0)
    f_p = st.number_input("P2O5 (%)", value=20.0)
    f_k = st.number_input("K2O (%)", value=20.0)

with col2:
    st.subheader("Necessidade da cultura (kg/ha)")
    req_n = culturas[cultura]["N"]
    req_p = culturas[cultura]["P"]
    req_k = culturas[cultura]["K"]

    st.markdown(f"""
- **N:** {req_n} kg/ha  
- **P₂O₅:** {req_p} kg/ha  
- **K₂O:** {req_k} kg/ha  
""")

doses = {}

if f_n > 0:
    doses["Nitrogênio"] = (req_n / f_n) * 100
if f_p > 0:
    doses["Fósforo"] = (req_p / f_p) * 100
if f_k > 0:
    doses["Potássio"] = (req_k / f_k) * 100

if doses:
    nutriente_base = max(doses, key=doses.get)
    dose_ha = doses[nutriente_base]

    total = dose_ha * area_ha
    sacos = math.ceil(total / 50)

    c1, c2, c3 = st.columns(3)
    c1.metric("Dose (kg/ha)", f"{dose_ha:.1f}")
    c2.metric("Total (kg)", f"{total:.1f}")
    c3.metric("Sacos (50kg)", f"{sacos}")

    st.caption(f"Nutriente limitante: {nutriente_base}")
else:
    dose_ha = 0
    total = 0
    sacos = 0
    nutriente_base = "-"

# -------------------------------
# CUSTOS
# -------------------------------
st.header("4. Custos")

preco_calcario = st.number_input("Preço calcário (R$/t)", value=150.0)
preco_adubo = st.number_input("Preço adubo (R$/ton)", value=2500.0)

custo_calcario = nc_total * preco_calcario
custo_adubo = (total / 1000) * preco_adubo

st.metric("Custo Calagem", f"R$ {custo_calcario:.2f}")
st.metric("Custo Adubação", f"R$ {custo_adubo:.2f}")

# -------------------------------
# PDF
# -------------------------------
if st.button("📄 Gerar Relatório"):
    pdf = FPDF()
    pdf.add_page()

    data = datetime.today().strftime('%d/%m/%Y')

    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "RELATÓRIO AGRONÔMICO", ln=True, align="C")

    pdf.set_font("Arial", size=11)
    pdf.cell(190, 8, f"Data: {data}", ln=True)
    pdf.cell(190, 8, f"Talhão: {talhao}", ln=True)
    pdf.cell(190, 8, f"Área: {area_ha} ha", ln=True)
    pdf.cell(190, 8, f"Cultura: {cultura}", ln=True)

    pdf.ln(5)

    pdf.cell(190, 8, f"Calagem: {nc_ha:.2f} t/ha", ln=True)
    pdf.cell(190, 8, f"Interpretação: {interpretacao}", ln=True)

    pdf.ln(5)

    pdf.cell(190, 8, f"Gessagem: {gesso:.2f} t/ha", ln=True)

    pdf.ln(5)

    pdf.cell(190, 8, f"Adubo: {f_n}-{f_p}-{f_k}", ln=True)
    pdf.cell(190, 8, f"Dose: {dose_ha:.1f} kg/ha", ln=True)
    pdf.cell(190, 8, f"Nutriente limitante: {nutriente_base}", ln=True)

    pdf.ln(5)

    pdf.cell(190, 8, f"Custo Calagem: R$ {custo_calcario:.2f}", ln=True)
    pdf.cell(190, 8, f"Custo Adubação: R$ {custo_adubo:.2f}", ln=True)

    pdf_bytes = bytes(pdf.output(dest="S"))

    st.download_button(
        "⬇️ Baixar PDF",
        pdf_bytes,
        file_name=f"Relatorio_{talhao}.pdf"
    )
