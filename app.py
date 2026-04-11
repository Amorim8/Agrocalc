import streamlit as st
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: CONFIGURAÇÃO DA ÁREA ---
st.sidebar.header("📋 Configuração da Área") 
nome_area = st.sidebar.text_input("Nome da Área:", "Área Soja 01")
area_ha = st.sidebar.number_input("Tamanho (Hectares):", value=1.0, min_value=0.01)

# --- 1. RECOMENDAÇÃO DE CALAGEM ---
st.header("1. Recomendação de Calagem")
c1, c2, c3, c4 = st.columns(4)

with c1: ctc = st.number_input("CTC", value=5.0)
with c2: v1 = st.number_input("V1 atual (%)", value=30.0)
with c3: v2 = st.number_input("V2 desejada (%)", value=70.0)
with c4: prnt = st.number_input("PRNT (%)", value=80.0)

# Cálculo com trava para resultados negativos
calc_bruto = ((v2 - v1) * ctc) / prnt if prnt > 0 else 0
nc_ha = max(0.0, calc_bruto)
nc_total = nc_ha * area_ha

if nc_ha <= 0:
    st.success("✅ Solo equilibrado. Recomendação: 0.00 t/ha")
else:
    st.info(f"👉 Recomendação: {nc_ha:.2f} t/ha | Total: {nc_total:.2f} Toneladas")

st.divider()

# --- 2. RECOMENDAÇÃO DE ADUBAÇÃO NPK ---
st.header("2. Adubação NPK de Precisão")
ce, cd = st.columns(2)

with ce:
    st.write("**Garantia do Adubo (%)**")
    f_n = st.number_input("N (%)", value=0, key="n_ad")
    f_p = st.number_input("P2O5 (%)", value=20, key="p_ad")
    f_k = st.number_input("K2O (%)", value=20, key="k_ad")

with cd:
    st.write("**Necessidade (kg/ha)**")
    r_n = st.number_input("Meta N", value=0.0, key="n_re")
    r_p = st.number_input("Meta P", value=80.0, key="p_re")
    r_k = st.number_input("Meta K", value=60.0, key="k_re")

# Lógica da maior dose para cobrir todos os nutrientes
lista = []
if f_n > 0: lista.append((r_n / f_n) * 100)
if f_p > 0: lista.append((r_p / f_p) * 100)
if f_k > 0: lista.append((r_k / f_k) * 100)

dose_final = max(lista) if lista else 0
total_kg = dose_final * area_ha
sacos = int(total_kg / 50) + 1

if dose_final > 0:
    res1, res2, res3 = st.columns(3)
    res1.metric("Dose/ha", f"{dose_final:.1f} kg")
    res2.metric("Total Área", f"{total_kg:.1f} kg")
    res3.metric("Sacos (50kg)", f"{sacos}")

st.divider()

# --- GERADOR DE PDF (FORMATO COMPATÍVEL) ---
if st.button("🚀 Gerar Relatório Final"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "RELATORIO TECNICO", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, "Consultor: Felipe Amorim", ln=True, align="C")
        
        pdf.ln(10)
        pdf.cell(190, 10, "IDENTIFICACAO DA AREA: " + str(nome_area), ln=True)
        pdf.cell(190, 10, "TAMANHO: " + str(area_ha) + " Hectares", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "1. CALAGEM", ln=True)
        pdf.set_font("Arial", "", 11)
        if nc_ha > 0:
            pdf.cell(190, 8, "Dose: " + str(round(nc_ha, 2)) + " t/ha", ln=True)
            pdf.cell(190, 8, "Total: " + str(round(nc_total, 2)) + " Toneladas", ln=True)
        else:
            pdf.cell(190, 8, "Calagem nao necessaria. Solo equilibrado.", ln=True)
            
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "2. ADUBACAO NPK", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(190, 8, "Dose Recomendada: " + str(round(dose_final, 1)) + " kg/ha", ln=True)
        pdf.cell(190, 8, "Total para Area: " + str(round(total_kg, 1)) + " kg", ln=True)

        # Correção do erro de 'bytearray' e 'encode'
        pdf_binario = pdf.output(dest='S').encode('latin-1')
            
        st.download_button(
            label="✅ Baixar PDF",
            data=pdf_binario,
            file_name="Relatorio_Agro.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error("Erro ao gerar o documento: " + str(e))

st.caption("© 2026 | Felipe Amorim")
