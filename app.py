import streamlit as st
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: ÁREA REAL ---
st.sidebar.header("📋 Configuração da Gleba")
talhao = st.sidebar.text_input("Identificação do Talhão:", "Área Soja 01")
area_ha = st.sidebar.number_input("Tamanho da Área (Hectares):", value=1.0, min_value=0.01)

st.header("🎯 Definição da Recomendação Desejada")
st.write("Insira abaixo as necessidades que você pesquisou para a cultura e as garantias do seu adubo.")

col_adubo, col_planta = st.columns(2)

with col_adubo:
    st.subheader("1. O que tem no seu Adubo? (%)")
    f_n = st.number_input("Garantia de N (%)", value=6)
    f_p = st.number_input("Garantia de P2O5 (%)", value=24)
    f_k = st.number_input("Garantia de K2O (%)", value=12)

with col_planta:
    st.subheader("2. O que a Cultura exige? (kg/ha)")
    req_n = st.number_input("Meta de N (kg/ha)", value=20.0)
    req_p = st.number_input("Meta de P2O5 (kg/ha)", value=80.0)
    req_k = st.number_input("Meta de K2O (kg/ha)", value=60.0)

st.divider()

# --- LÓGICA DE SEGURANÇA NPK ---
st.header("🚜 Resultado Final para sua Área")

# Calculando quanto de adubo precisaria para cada nutriente isolado
doses_teste = {}
if f_n > 0: doses_teste['Nitrogênio'] = (req_n / f_n) * 100
if f_p > 0: doses_teste['Fósforo'] = (req_p / f_p) * 100
if f_k > 0: doses_teste['Potássio'] = (req_k / f_k) * 100

if doses_teste:
    # Seleciona a maior dose para garantir que nenhum nutriente falte
    nutriente_base = max(doses_teste, key=doses_teste.get)
    dose_mestre_ha = doses_teste[nutriente_base]
    
    # Cálculo para a área total do Felipe
    total_area_kg = dose_mestre_ha * area_ha
    sacos_50kg = int(total_area_kg / 50) + 1

    # Exibição de Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("Dose Recomendada", f"{dose_mestre_ha:.1f} kg/ha")
    m2.metric(f"Total para {area_ha} ha", f"{total_area_kg:.1f} kg")
    m3.metric("Total de Sacos", f"{sacos_50kg} un")

    st.success(f"✅ **Segurança Garantida:** Esta dose supre 100% da necessidade de **{nutriente_base}**, que era o item mais exigente.")
    
    # Detalhamento do que está sendo entregue
    st.write("### 📝 O que essa aplicação entrega por Hectare:")
    e_n = (dose_mestre_ha * f_n) / 100
    e_p = (dose_mestre_ha * f_p) / 100
    e_k = (dose_mestre_ha * f_k) / 100
    st.info(f"N: {e_n:.1f} kg/ha | P2O5: {e_p:.1f} kg/ha | K2O: {e_k:.1f} kg/ha")

# --- GERADOR DE PDF ---
if st.button("🚀 Gerar PDF"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(34, 139, 34)
        pdf.rect(0, 0, 210, 40, 'F')
        
        pdf.set_y(12)
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 10, "RELATÓRIO DE RECOMENDAÇÃO TÉCNICA".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        pdf.set_font("Arial", '', 13)
        pdf.cell(190, 8, f"Consultor Responsável: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        
        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(180, 10, f" PROJETO: {talhao} | ÁREA TOTAL: {area_ha} Hectares".encode('latin-1', 'replace').decode('latin-1'), ln=True, fill=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(180, 10, " DETALHAMENTO DA ADUBAÇÃO".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(180, 8, f"- Adubo Formulado: {f_n}-{f_p}-{f_k}\n- Dose Aplicada: {dose_mestre_ha:.1f} kg/ha\n- Quantidade Total: {total_area_kg:.1f} kg\n- Logística: {sacos_50kg} sacos de 50kg".encode('latin-1', 'replace').decode('latin-1'))
        
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(180, 10, "Relatório gerado via AgroCalc Sistema de Precisão.".encode('latin-1', 'replace').decode('latin-1'), align='C')

        pdf_bytes = bytes(pdf.output(dest='S'))
        st.download_button("✅ Baixar PDF do Relatório", data=pdf_bytes, file_name=f"Recomendacao_{talhao}.pdf")
    except Exception as e:
        st.error(f"Erro ao gerar documento: {e}")

st.markdown("---")
st.caption("© 2026 | Felipe Amorim Consultoria Agronômica")
