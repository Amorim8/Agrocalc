import streamlit as st
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: CONFIGURAÇÃO DA ÁREA ---
st.sidebar.header("📋 Configuração da Área") 
nome_area = st.sidebar.text_input("Nome/Identificação da Área:", "Área Soja 01")
area_ha = st.sidebar.number_input("Tamanho da Área (Hectares):", value=1.0, min_value=0.01)

# --- 1. PROCESSO DE CALAGEM ---
st.header("1. Recomendação de Calagem")
st.write("Insira os dados da análise de solo.")

col_calc1, col_calc2, col_calc3, col_calc4 = st.columns(4)

with col_calc1:
    ctc = st.number_input("CTC (cmolc/dm³)", value=5.0, step=0.1)
with col_calc2:
    v1 = st.number_input("V1 (Saturação Atual %)", value=30.0, step=1.0)
with col_calc3:
    v2 = st.number_input("V2 (Saturação Desejada %)", value=70.0, step=1.0)
with col_calc4:
    prnt = st.number_input("PRNT do Calcário (%)", value=80.0, step=1.0)

# Cálculo com trava para zero/negativo
nc_calc = ((v2 - v1) * ctc) / prnt if prnt > 0 else 0
nc_ha = max(0.0, nc_calc)
nc_total = nc_ha * area_ha

if nc_ha <= 0:
    st.success("✅ Solo equilibrado. Recomendação: 0.00 t/ha")
else:
    st.info(f"👉 Recomendação: {nc_ha:.2f} t/ha | Total: {nc_total:.2f} Toneladas")

st.divider()

# --- 2. PROCESSO DE ADUBAÇÃO NPK ---
st.header("2. Adubação NPK de Precisão")
col_adubo, col_planta = st.columns(2)

with col_adubo:
    st.subheader("Garantia do Adubo (%)")
    f_n = st.number_input("N (%)", value=0, key="n_adubo")
    f_p = st.number_input("P2O5 (%)", value=20, key="p_adubo")
    f_k = st.number_input("K2O (%)", value=20, key="k_adubo")

with col_planta:
    st.subheader("Necessidade da Cultura (kg/ha)")
    req_n = st.number_input("Meta de N (kg/ha)", value=0.0, key="n_req")
    req_p = st.number_input("Meta de P2O5 (kg/ha)", value=80.0, key="p_req")
    req_k = st.number_input("Meta de K2O (kg/ha)", value=60.0, key="k_req")

# Lógica da maior dose
doses = []
if f_n > 0: doses.append((req_n / f_n) * 100)
if f_p > 0: doses.append((req_p / f_p) * 100)
if f_k > 0: doses.append((req_k / f_k) * 100)

dose_final_ha = max(doses) if doses else 0
total_kg = dose_final_ha * area_ha
sacos = int(total_kg / 50) + 1

if dose_final_ha > 0:
    res1, res2, res3 = st.columns(3)
    res1.metric("Dose por Hectare", f"{dose_final_ha:.1f} kg/ha")
    res2.metric("Total para a Área", f"{total_kg:.1f} kg")
    res3.metric("Sacos (50kg)", f"{sacos} un")

st.divider()

# --- GERADOR DE PDF ---
if st.button("🚀 Gerar Relatório Final"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(34, 139, 34)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_y(12)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 10, "RELATÓRIO DE RECOMENDAÇÃO TÉCNICA", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(190, 8, "Consultor Responsável: Felipe Amorim", ln=True, align='C')
        
        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(180, 10, f" CONFIGURAÇÃO DA ÁREA: {nome_area}", ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(180, 8, f" Tamanho Total: {area_ha} Hectares", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(180, 10, " 1. CALAGEM", ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        txt_cal = f" Recomendação: {nc_ha:.2f} t/ha | Total: {nc_total:.2f} Ton" if nc_ha > 0 else " Solo equilibrado. Calagem não necessária."
        pdf.cell(180, 8, txt_cal, ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(180, 10, " 2. ADUBAÇÃO NPK", ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(180, 8, f" Adubo: {f_n}-{f_p}-{f_k}\n Dose: {dose_final_ha:.1f} kg/ha\n Total Área: {total_kg:.1f} kg\n Logística: {sacos} sacos")
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("✅ Baixar PDF", data=pdf_bytes, file_name=f"Relatorio_{nome_area}.pdf")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("© 2026 | Felipe Amorim - Consultoria Agronômica")
