import streamlit as st
from fpdf import FPDF
import math

# -------------------------------
# CONFIGURAÇÃO DE INTERFACE
# -------------------------------
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# -------------------------------
# SIDEBAR - CONFIGURAÇÕES
# -------------------------------
st.sidebar.header("📋 Dados da Área")
cliente = st.sidebar.text_input("Produtor:", "Nome do Cliente")
talhao = st.sidebar.text_input("Talhão:", "Área 01")
area_total = st.sidebar.number_input("Área Total (Hectares):", value=1.0, min_value=0.01, step=0.1)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# -------------------------------
# 1. ANÁLISE E CLASSIFICAÇÃO DO SOLO
# -------------------------------
st.header("1️⃣ Diagnóstico e Níveis do Solo")

col_d1, col_d2 = st.columns(2)

with col_d1:
    argila = st.number_input("Argila (%):", value=0.0)
    p_solo = st.number_input("Fósforo (P) [mg/dm³]:", value=0.0)
    k_solo = st.number_input("Potássio (K) [cmolc/dm³]:", value=0.0)

with col_d2:
    # Classificação Automática baseada nos manuais (Cerrado/Embrapa)
    # Fósforo
    if p_solo < 10: nivel_p = "Baixo"
    elif p_solo < 20: nivel_p = "Médio"
    else: nivel_p = "Alto"
    
    # Potássio
    if k_solo < 0.15: nivel_k = "Baixo"
    elif k_solo < 0.30: nivel_k = "Médio"
    else: nivel_k = "Alto"

    st.info(f"Interpretação: Fósforo **{nivel_p}** | Potássio **{nivel_k}**")
    v_atual = st.number_input("V1% (Saturação Atual):", value=0.0)
    ctc = st.number_input("CTC Total:", value=5.0)

# -------------------------------
# 2. CALAGEM
# -------------------------------
st.divider()
st.header("2️⃣ Correção (Calagem)")
v_alvo = 70 if cultura == "Soja" else 60
prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

nc_ha = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual else 0
total_calcario = nc_ha * area_total

st.success(f"Dose: **{nc_ha:.2f} t/ha** | Total para a área: **{total_calcario:.2f} Toneladas**")

# -------------------------------
# 3. ADUBAÇÃO COM FORMULADOS (NPK)
# -------------------------------
st.divider()
st.header("3️⃣ Recomendação de Adubação NPK")

# Guardando na memória as recomendações padrão por nível
# Exemplo simplificado para Soja (P2O5 / K2O)
tabela_soja = {"Baixo": (100, 80), "Médio": (70, 60), "Alto": (40, 30)}
tabela_milho = {"Baixo": (120, 100), "Médio": (90, 80), "Alto": (60, 50)}

dados = tabela_soja if cultura == "Soja" else tabela_milho
req_p_ha, req_k_ha = dados[nivel_p][0], dados[nivel_k][1]

st.write(f"Recomendação técnica para nível **{nivel_p}/{nivel_k}**: {req_p_ha}kg P₂O₅ e {req_k_ha}kg K₂O por ha.")

st.subheader("Calcular com Adubo Formulado")
c_f1, c_f2, c_f3 = st.columns(3)
f_n = c_f1.number_input("N no formulado:", value=0)
f_p = c_f2.number_input("P no formulado:", value=20)
f_k = c_f3.number_input("K no formulado:", value=20)

# Cálculo baseado no nutriente limitante (geralmente Fósforo no plantio)
if f_p > 0:
    dose_formulado = (req_p_ha / f_p) * 100
    total_adubo = (dose_formulado * area_total) / 50 # em sacos de 50kg
    
    st.metric("Dose do Adubo", f"{dose_formulado:.0f} kg/ha")
    st.metric(f"Total para {area_total} ha", f"{math.ceil(total_adubo)} sacos (50kg)")

# -------------------------------
# 4. PDF COM FUNDO VERDE
# -------------------------------
st.divider()

def gerar_pdf_verde():
    pdf = FPDF()
    pdf.add_page()
    
    # Fundo Verde Suave
    pdf.set_fill_color(240, 255, 240)
    pdf.rect(0, 0, 210, 297, 'F')
    
    # Cabeçalho discreto
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(200, 10, "RECOMENDACAO TECNICA AGRONOMICA".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.cell(200, 8, f"Consultor: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(200, 8, f"Produtor: {cliente} | Area: {area_total} ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(200, 8, f"Cultura: {cultura} | Talhao: {talhao}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, "RESULTADOS E NIVEIS".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 8, f"Fosforo: {p_solo} mg/dm3 ({nivel_p}) | Potassio: {k_solo} cmolc/dm3 ({nivel_k})".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, "CORRECAO E ADUBACAO".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 8, f"Calcario: {nc_ha:.2f} t/ha (Total: {total_calcario:.2f} Ton)".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(200, 8, f"Adubo Formulado ({f_n}-{f_p}-{f_k}): {dose_formulado:.0f} kg/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    return pdf.output(dest='S')

if st.button("📄 Gerar Relatório PDF Profissional"):
    pdf_out = gerar_pdf_verde()
    st.download_button("⬇️ Baixar PDF com Fundo Verde", data=pdf_out, file_name=f"Relatorio_{talhao}.pdf", mime="application/pdf")

st.caption("Sistema AgroCalc | Felipe Amorim")
