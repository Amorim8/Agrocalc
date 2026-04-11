import streamlit as st
from fpdf import FPDF

# Configuração da Página - Felipe Amorim
st.set_page_config(page_title="AgroCalc", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: CONFIGURAÇÃO DA ÁREA ---
st.sidebar.header("📋 Configuração da Área") 
nome_area = st.sidebar.text_input("Nome da Área:", "Área Soja 01")
area_ha = st.sidebar.number_input("Tamanho (Hectares):", value=1.0, min_value=0.01)

# --- 1. RECOMENDAÇÃO DE CALAGEM ---
st.header("1. Recomendação de Calagem")
c1, c2, c3, c4 = st.columns(4)

with c1: ctc = st.number_input("CTC", value=13.87)
with c2: v1 = st.number_input("V1 atual (%)", value=78.40)
with c3: v2 = st.number_input("V2 desejada (%)", value=60.00)
with c4: prnt = st.number_input("PRNT (%)", value=89.00)

# Cálculo com trava para não dar valor negativo
nc_calculado = ((v2 - v1) * ctc) / prnt if prnt > 0 else 0
nc_ha = max(0.0, nc_calculado)
nc_total = nc_ha * area_ha

if nc_ha <= 0:
    st.success("✅ Solo equilibrado ou Saturação atual maior que a desejada. Recomendação: 0.00 t/ha")
else:
    st.info(f"👉 Recomendação: {nc_ha:.2f} t/ha | Total: {nc_total:.2f} Toneladas")

st.divider()

# --- 2. RECOMENDAÇÃO DE ADUBAÇÃO NPK ---
st.header("2. Adubação NPK de Precisão")
ce, cd = st.columns(2)

with ce:
    st.write("**Garantia do Adubo (%)**")
    f_n = st.number_input("N (%)", value=8, key="n_f")
    f_p = st.number_input("P2O5 (%)", value=20, key="p_f")
    f_k = st.number_input("K2O (%)", value=20, key="k_f")

with cd:
    st.write("**Necessidade (kg/ha)**")
    r_n = st.number_input("Meta N", value=0.0, key="n_r")
    r_p = st.number_input("Meta P", value=80.0, key="p_r")
    r_k = st.number_input("Meta K", value=60.0, key="k_r")

# Lógica da maior dose
doses = []
if f_n > 0: doses.append((r_n / f_n) * 100)
if f_p > 0: doses.append((r_p / f_p) * 100)
if f_k > 0: doses.append((r_k / f_k) * 100)

dose_final = max(doses) if doses else 0
total_kg = dose_final * area_ha
sacos = int(total_kg / 50) + 1

if dose_final > 0:
    res1, res2, res3 = st.columns(3)
    res1.metric("Dose/ha", f"{dose_final:.1f} kg")
    res2.metric("Total Área", f"{total_kg:.1f} kg")
    res3.metric("Sacos (50kg)", f"{sacos}")

st.divider()

# --- GERADOR DE PDF ---
if st.button("🚀 Gerar Relatório Final"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "RELATORIO TECNICO", ln=True, align="C")
        
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(190, 10, "Consultor: Felipe Amorim", ln=True)
        pdf.cell(190, 10, "Area: " + str(nome_area), ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "1. CALAGEM", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, "Recomendacao: " + str(round(nc_ha, 2)) + " t/ha", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "2. ADUBACAO NPK", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, "Dose: " + str(round(dose_final, 1)) + " kg/ha", ln=True)
        pdf.cell(190, 10, "Total: " + str(round(total_kg, 1)) + " kg", ln=True)

        # MÉTODO DE SAÍDA SEGURO PARA STREAMLIT
        pdf_out = pdf.output(dest='S')
        # Se o PDF vier como bytearray, não tentamos 'encode', apenas enviamos
        
        st.download_button(
            label="✅ Baixar Relatório PDF",
            data=bytes(pdf_out),
            file_name="Relatorio_Agro.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error("Erro técnico: " + str(e))

st.caption("© 2026 | Felipe Amorim")
