import streamlit as st
from fpdf import FPDF

# 1. Configuração Principal
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: CONFIGURAÇÃO DA ÁREA ---
st.sidebar.header("📋 Configuração da Área") 
nome_area = st.sidebar.text_input("Nome da Área:", "Gleba Soja 01")
area_ha = st.sidebar.number_input("Tamanho (Hectares):", value=1.0, min_value=0.01)

# --- 1. RECOMENDAÇÃO DE CALAGEM ---
st.header("1. Recomendação de Calagem")
col1, col2, col3, col4 = st.columns(4)

with col1: ctc = st.number_input("CTC", value=5.0)
with col2: v1 = st.number_input("V1 atual (%)", value=30.0)
with col3: v2 = st.number_input("V2 desejada (%)", value=70.0)
with col4: prnt = st.number_input("PRNT (%)", value=80.0)

# Trava para calagem negativa
calc_nc = ((v2 - v1) * ctc) / prnt if prnt > 0 else 0
nc_final = max(0.0, calc_nc)
nc_total = nc_final * area_ha

if nc_final <= 0:
    st.success("✅ Solo equilibrado. Calagem: 0.00 t/ha")
else:
    st.info(f"👉 Recomendação: {nc_final:.2f} t/ha | Total: {nc_total:.2f} Toneladas")

st.divider()

# --- 2. RECOMENDAÇÃO DE ADUBAÇÃO NPK ---
st.header("2. Adubação NPK de Precisão")
c_esq, c_dir = st.columns(2)

with c_esq:
    st.write("**Garantia do Adubo (%)**")
    fn = st.number_input("N", value=0, key="n1")
    fp = st.number_input("P2O5", value=20, key="p1")
    fk = st.number_input("K2O", value=20, key="k1")

with c_dir:
    st.write("**Necessidade (kg/ha)**")
    rn = st.number_input("Meta N", value=0.0, key="n2")
    rp = st.number_input("Meta P", value=80.0, key="p2")
    rk = st.number_input("Meta K", value=60.0, key="k2")

# Cálculo da maior dose
doses = []
if fn > 0: doses.append((rn / fn) * 100)
if fp > 0: doses.append((rp / fp) * 100)
if fk > 0: doses.append((rk / fk) * 100)

dose_ha = max(doses) if doses else 0
total_adubo = dose_ha * area_ha
qtd_sacos = int(total_adubo / 50) + 1

if dose_ha > 0:
    res1, res2, res3 = st.columns(3)
    res1.metric("Dose/ha", f"{dose_ha:.1f} kg")
    res2.metric("Total Área", f"{total_adubo:.1f} kg")
    res3.metric("Sacos (50kg)", f"{qtd_sacos}")

st.divider()

# --- GERADOR DE PDF (CORREÇÃO DE FORMATO BINÁRIO) ---
if st.button("🚀 Gerar Relatório Final"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "RELATORIO TECNICO", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 10, "Consultor: Felipe Amorim", ln=True, align="C")
        
        pdf.ln(10)
        pdf.cell(190, 10, "AREA: " + nome_area, ln=True)
        pdf.cell(190, 10, "TAMANHO: " + str(area_ha) + " Hectares", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "1. CALAGEM", ln=True)
        pdf.set_font("Arial", "", 11)
        if nc_final > 0:
            pdf.cell(190, 10, "Dose: " + str(round(nc_final, 2)) + " t/ha", ln=True)
        else:
            pdf.cell(190, 10, "Calagem nao necessaria", ln=True)
            
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "2. ADUBACAO NPK", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(190, 10, "Dose: " + str(round(dose_ha, 1)) + " kg/ha", ln=True)
        pdf.cell(190, 10, "Total Area: " + str(round(total_adubo, 1)) + " kg", ln=True)

        # A solução para o erro de 'bytearray': converter para bytes puras
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
        st.download_button(
            label="✅ Baixar PDF",
            data=pdf_bytes,
            file_name="Relatorio_Agro.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error("Erro ao gerar PDF: " + str(e))

st.caption("© 2026 | Felipe Amorim")
