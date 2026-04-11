import streamlit as st
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: IDENTIFICAÇÃO & ÁREA ---
st.sidebar.header("📋 Identificação & Área")
talhao = st.sidebar.text_input("Talhão/Lote:", "Gleba A1")
cultura = st.sidebar.selectbox("Cultura Alvo:", ["Soja", "Milho", "Feijão", "Algodão", "Hortaliças", "Outra"])

st.sidebar.markdown("---")
st.sidebar.write("### 📐 Tamanho da Área Total")
tipo_medida = st.sidebar.selectbox("Medir em:", ["Hectares (ha)", "Tarefas (Baianas - 4.356 m²)", "Metros Quadrados (m²)"])
tamanho_area = st.sidebar.number_input("Quantidade da área:", value=1.0, min_value=0.01)

# Conversão interna para Hectare
if tipo_medida == "Tarefas (Baianas - 4.356 m²)":
    area_ha = (tamanho_area * 4356) / 10000
elif tipo_medida == "Metros Quadrados (m²)":
    area_ha = tamanho_area / 10000
else:
    area_ha = tamanho_area

# --- 1. CALAGEM ---
st.header("1. Necessidade de Calagem")
col1, col2, col3 = st.columns(3)
with col1:
    ctc = st.number_input("CTC (cmolc/dm³)", value=5.0, step=0.1)
with col2:
    v1 = st.number_input("Saturação atual (V1 %)", value=30.0, step=1.0)
with col3:
    v2 = st.number_input("Saturação desejada (V2 %)", value=70.0, step=1.0)

prnt = st.number_input("PRNT do Calcário (%)", value=80.0, step=1.0)
nc_ha = ((v2 - v1) * ctc) / prnt
nc_total = nc_ha * area_ha

st.info(f"👉 **Recomendação:** {nc_ha:.2f} t/ha | **Total para sua área ({tamanho_area} {tipo_medida}):** {nc_total:.2f} toneladas")

st.markdown("---")

# --- 2. ADUBAÇÃO NPK (SIMPLES OU FORMULADO) ---
st.header("2. Recomendação de Adubação NPK")

metodo = st.radio("Como você vai adubar?", ["Usar Adubo Formulado (Ex: 00-20-20)", "Usar Adubos Simples (Ureia, Super, KCl)"])

if metodo == "Usar Adubo Formulado (Ex: 00-20-20)":
    st.write("### Configuração do Adubo")
    c1, c2, c3 = st.columns(3)
    with c1: f_n = st.number_input("N (%) no saco", value=0)
    with c2: f_p = st.number_input("P (%) no saco", value=20)
    with c3: f_k = st.number_input("K (%) no saco", value=20)
    
    st.write("### Qual nutriente manda no cálculo?")
    nutriente_base = st.selectbox("Calcular dose com base em:", ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)"])
    valor_rec = st.number_input(f"Quantidade recomendada de {nutriente_base} (kg/ha):", value=80.0)

    # Lógica de cálculo para formulado
    dose_ha = 0
    if nutriente_base == "Nitrogênio (N)" and f_n > 0: dose_ha = (valor_rec / f_n) * 100
    elif nutriente_base == "Fósforo (P)" and f_p > 0: dose_ha = (valor_rec / f_p) * 100
    elif nutriente_base == "Potássio (K)" and f_k > 0: dose_ha = (valor_rec / f_k) * 100

    if dose_ha > 0:
        dose_total_kg = dose_ha * area_ha
        st.success(f"🚜 **Dose por Hectare:** {dose_ha:.1f} kg/ha")
        st.metric(f"Total para {tamanho_area} {tipo_medida}", f"{dose_total_kg:.1f} kg")
        st.write(f"📦 **Quantidade de sacos (50kg):** {int(dose_total_kg/50) + 1} sacos")
    else:
        st.error("⚠️ O nutriente escolhido está com 0% na fórmula!")

else:
    st.write("### Recomendação para Adubos Simples")
    colN, colP, colK = st.columns(3)
    with colN:
        n_rec = st.number_input("N (kg/ha)", value=0.0)
        u_total = (n_rec / 0.45) * area_ha
        st.write(f"Ureia total: {u_total:.1f} kg")
    with colP:
        p_rec = st.number_input("P2O5 (kg/ha)", value=80.0)
        s_total = (p_rec / 0.18) * area_ha
        st.write(f"S. Simples total: {s_total:.1f} kg")
    with colK:
        k_rec = st.number_input("K2O (kg/ha)", value=60.0)
        k_total = (k_rec / 0.60) * area_ha
        st.write(f"KCl total: {k_total:.1f} kg")

# --- PDF ---
if st.button("🚀 Gerar PDF Profissional"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Relatorio de Recomendacao Agronomica", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Consultor: Felipe Amorim", ln=True)
    pdf.cell(200, 10, f"Area: {tamanho_area} {tipo_medida}", ln=True)
    pdf.cell(200, 10, f"Cultura: {cultura}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, f"Calcario Total: {nc_total:.2f} toneladas", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "Assinatura: _________________________________", ln=True)
    
    pdf_output = pdf.output(dest="S").encode("latin-1")
    st.download_button(label="📥 Baixar PDF", data=pdf_output, file_name=f"Recomendacao_{talhao}.pdf", mime="application/pdf")

st.markdown("---")
st.caption("© 2026 | Sistema de Consultoria Felipe Amorim")
