import streamlit as st
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: CONFIGURAÇÃO DA ÁREA ---
st.sidebar.header("📋 Configuração da Área") 
nome_da_area = st.sidebar.text_input("Nome/Identificação da Área:", "Área Soja 01")
area_total_ha = st.sidebar.number_input("Tamanho da Área (Hectares):", value=1.0, min_value=0.01)

# --- 1. PROCESSO DE CALAGEM ---
st.header("1. Recomendação de Calagem")
st.write("Insira os dados da análise de solo.")

c1, c2, c3, c4 = st.columns(4)
with c1: ctc_solo = st.number_input("CTC (cmolc/dm³)", value=5.0)
with c2: v1_atual = st.number_input("V1 (Saturação Atual %)", value=30.0)
with c3: v2_deseja = st.number_input("V2 (Saturação Desejada %)", value=70.0)
with c4: prnt_calc = st.number_input("PRNT do Calcário (%)", value=80.0)

# Cálculo com trava para zero
nc_bruto = ((v2_deseja - v1_atual) * ctc_solo) / prnt_calc if prnt_calc > 0 else 0
necessidade_ha = max(0.0, nc_bruto)
necessidade_total = necessidade_ha * area_total_ha

if necessidade_ha <= 0:
    st.success("✅ Solo equilibrado. Recomendação: 0.00 t/ha")
else:
    st.info(f"👉 Recomendação: {necessidade_ha:.2f} t/ha | Total: {necessidade_total:.2f} Toneladas")

st.divider()

# --- 2. PROCESSO DE ADUBAÇÃO NPK ---
st.header("2. Adubação NPK de Precisão")
col_e, col_d = st.columns(2)

with col_e:
    st.subheader("Garantia do Adubo (%)")
    f_n = st.number_input("N (%)", value=0, key="n_f")
    f_p = st.number_input("P2O5 (%)", value=20, key="p_f")
    f_k = st.number_input("K2O (%)", value=20, key="k_f")

with col_d:
    st.subheader("Necessidade da Cultura (kg/ha)")
    req_n = st.number_input("Meta de N (kg/ha)", value=0.0, key="n_r")
    req_p = st.number_input("Meta de P2O5 (kg/ha)", value=80.0, key="p_r")
    req_k = st.number_input("Meta de K2O (kg/ha)", value=60.0, key="k_r")

# Cálculo da maior dose necessária
lista_doses = []
if f_n > 0: lista_doses.append((req_n / f_n) * 100)
if f_p > 0: lista_doses.append((req_p / f_p) * 100)
if f_k > 0: lista_doses.append((req_k / f_k) * 100)

dose_final = max(lista_doses) if lista_doses else 0
kg_total = dose_final * area_total_ha
sacos_total = int(kg_total / 50) + 1

if dose_final > 0:
    r1, r2, r3 = st.columns(3)
    r1.metric("Dose por Hectare", f"{dose_final:.1f} kg/ha")
    r2.metric("Total para a Área", f"{kg_total:.1f} kg")
    r3.metric("Sacos (50kg)", f"{sacos_total} un")

st.divider()

# --- GERADOR DE PDF (CORRIGIDO) ---
if st.button("🚀 Gerar Relatório Final"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        # Cabeçalho
        pdf.cell(190, 10, "RELATORIO DE RECOMENDACAO TECNICA", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(190, 10, "Consultor: Felipe Amorim", ln=True, align='C')
        pdf.ln(10)
        
        # Área
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, f"CONFIGURACAO DA AREA: {nome_da_area}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(190, 8, f"Tamanho: {area_total_ha} Hectares", ln=True)
        pdf.ln(5)
        
        # Calagem
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, "1. CALAGEM", ln=True)
        pdf.set_font("Arial", '', 11)
        if necessidade_ha > 0:
            pdf.cell(190, 8, f"Recomendacao: {necessidade_ha:.2f} t/ha", ln=True)
            pdf.cell(190, 8, f"Total: {necessidade_total:.2f} Toneladas", ln=True)
        else:
            pdf.cell(190, 8, "Solo equilibrado. Calagem nao necessaria.", ln=True)
        pdf.ln(5)
        
        # NPK
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, "2. ADUBACAO NPK", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(190, 8, f"Adubo: {f_n}-{f_p}-{f_k}", ln=True)
        pdf.cell(190, 8, f"Dose: {dose_final:.1f} kg/ha", ln=True)
        pdf.cell(190, 8, f"Total Area: {kg_total:.1f} kg ({sacos_total} sacos)", ln=True)
        
        # Gerar o PDF como string de bytes
        pdf_out = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("✅ Baixar PDF", data=pdf_out, file_name="Relatorio.pdf", mime="application/pdf")
        
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("© 2026 | Felipe Amorim - Consultoria Agronômica")
