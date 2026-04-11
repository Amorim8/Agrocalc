import streamlit as st
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: CONFIGURAÇÃO DA ÁREA ---
st.sidebar.header("📋 Configuração da Gleba")
talhao = st.sidebar.text_input("Identificação do Talhão:", "Área Soja 01")
area_ha = st.sidebar.number_input("Tamanho da Área (Hectares):", value=1.0, min_value=0.01)

# --- 1. PROCESSO DE CALAGEM ---
st.header("1. Recomendação de Calagem")
st.write("Insira os dados da análise de solo para calcular a necessidade de calcário.")

col_calc1, col_calc2, col_calc3, col_calc4 = st.columns(4)

with col_calc1:
    ctc = st.number_input("CTC (cmolc/dm³)", value=5.0, step=0.1)
with col_calc2:
    v1 = st.number_input("V1 (Saturação Atual %)", value=30.0, step=1.0)
with col_calc3:
    v2 = st.number_input("V2 (Saturação Desejada %)", value=70.0, step=1.0)
with col_calc4:
    prnt = st.number_input("PRNT do Calcário (%)", value=80.0, step=1.0)

# Lógica de Calagem com Trava para Negativos
nc_ha_calculado = ((v2 - v1) * ctc) / prnt if prnt > 0 else 0

if nc_ha_calculado <= 0:
    nc_ha = 0.0
    nc_total = 0.0
    status_calagem = "✅ Solo equilibrado. Não é necessário realizar a calagem."
    st.success(status_calagem)
else:
    nc_ha = nc_ha_calculado
    nc_total = nc_ha * area_ha
    status_calagem = f"👉 Recomendação: {nc_ha:.2f} t/ha | Total: {nc_total:.2f} Toneladas"
    st.info(status_calagem)

st.divider()

# --- 2. PROCESSO DE ADUBAÇÃO NPK ---
st.header("2. Adubação NPK de Precisão")
col_adubo, col_planta = st.columns(2)

with col_adubo:
    st.subheader("O que tem no seu Adubo? (%)")
    f_n = st.number_input("N (%)", value=0)
    f_p = st.number_input("P2O5 (%)", value=20)
    f_k = st.number_input("K2O (%)", value=20)

with col_planta:
    st.subheader("O que a Soja precisa? (kg/ha)")
    req_n = st.number_input("Meta de N (kg/ha)", value=0.0)
    req_p = st.number_input("Meta de P2O5 (kg/ha)", value=80.0)
    req_k = st.number_input("Meta de K2O (kg/ha)", value=60.0)

doses_teste = {}
if f_n > 0: doses_teste['Nitrogênio'] = (req_n / f_n) * 100
if f_p > 0: doses_teste['Fósforo'] = (req_p / f_p) * 100
if f_k > 0: doses_teste['Potássio'] = (req_k / f_k) * 100

if doses_teste:
    nutriente_base = max(doses_teste, key=doses_teste.get)
    dose_mestre_ha = doses_teste[nutriente_base]
    total_adubo_area = dose_mestre_ha * area_ha
    sacos_50kg = int(total_adubo_area / 50) + 1

    m1, m2, m3 = st.columns(3)
    m1.metric("Dose Recomendada", f"{dose_mestre_ha:.1f} kg/ha")
    m2.metric(f"Total para {area_ha} ha", f"{total_adubo_area:.1f} kg")
    m3.metric("Sacos (50kg)", f"{sacos_50kg} un")
else:
    dose_mestre_ha = 0
    total_adubo_area = 0
    sacos_50kg = 0

st.divider()

# --- GERADOR DE PDF ---
if st.button("🚀 Gerar Relatório Final"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(34, 139, 34)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_y(12)
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 10, "RELATÓRIO DE RECOMENDAÇÃO TÉCNICA".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(190, 8, f"Consultor: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        
        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)
        
        # Calagem no PDF
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(180, 10, " 1. RECOMENDAÇÃO DE CALAGEM".encode('latin-1', 'replace').decode('latin-1'), ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        if nc_ha == 0:
            pdf.cell(180, 8, " Não é necessário realizar a calagem para esta área.".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        else:
            pdf.cell(180, 8, f" Dose por Hectare: {nc_ha:.2f} t/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
            pdf.cell(180, 8, f" Total para a área: {nc_total:.2f} Toneladas".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.ln(5)
        
        # NPK no PDF
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(180, 10, " 2. RECOMENDAÇÃO DE ADUBAÇÃO NPK".encode('latin-1', 'replace').decode('latin-1'), ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(180, 8, f" Adubo: {f_n}-{f_p}-{f_k}\n Dose: {dose_mestre_ha:.1f} kg/ha\n Total Área: {total_adubo_area:.1f} kg ({sacos_50kg} sacos)".encode('latin-1', 'replace').decode('latin-1'))
        
        pdf_bytes = bytes(pdf.output(dest='S'))
        st.download_button("✅ Baixar PDF", data=pdf_bytes, file_name=f"Relatorio_{talhao}.pdf")
    except Exception as e:
        st.error(f"Erro: {e}")
