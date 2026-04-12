import streamlit as st
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 AgroCalc Pro - Consultoria Técnica")
st.subheader("Consultor Responsável: Felipe Amorim")
st.markdown("---")

# --- BLOCO 1: DADOS TÉCNICOS DA ANÁLISE ---
st.header("1️⃣ Dados da Análise de Solo")
col1, col2, col3 = st.columns(3)

with col1:
    cliente = st.text_input("Nome do Produtor:", "Cliente Exemplo")
    talhao = st.text_input("Identificação do Talhão/Área:", "Gleba 01")
    area = st.number_input("Área Total (ha):", value=1.0, min_value=0.1)

with col2:
    v_atual = st.number_input("V% Atual (Saturação por Bases):", value=0.0)
    ctc = st.number_input("CTC Total (cmolc/dm³):", value=0.0)
    prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

with col3:
    cultura = st.selectbox("Cultura de Destino:", ["Soja", "Milho"])
    v_alvo = st.number_input("V% Alvo (Desejado):", value=70.0 if cultura == "Soja" else 60.0)
    argila = st.number_input("Teor de Argila (g/kg):", value=0.0)

# --- BLOCO 2: CÁLCULO DE CALAGEM ---
st.markdown("---")
st.header("2️⃣ Necessidade de Calagem")

# Fórmula da Necessidade de Calagem (NC = (V2 - V1) * CTC / PRNT)
if prnt > 0:
    nc_ton_ha = ((v_alvo - v_atual) * ctc) / prnt
    if nc_ton_ha < 0: nc_ton_ha = 0.0
    total_necessario = nc_ton_ha * area
else:
    nc_ton_ha = 0.0
    total_necessario = 0.0

res_col1, res_col2 = st.columns(2)
res_col1.metric("Necessidade (t/ha)", f"{nc_ha:.2f}")
res_col2.metric(f"Total para {area} ha (Toneladas)", f"{total_necessario:.2f}")

# --- BLOCO 3: RECOMENDAÇÃO DE ADUBAÇÃO (NPK) ---
st.markdown("---")
st.header("3️⃣ Recomendação de Adubação")

st.write("Determine os níveis para cálculo de NPK:")
n_col1, n_col2, n_col3 = st.columns(3)
with n_col1: nivel_p = st.selectbox("Nível de Fósforo (P):", ["Baixo", "Médio", "Alto"])
with n_col2: nivel_k = st.selectbox("Nível de Potássio (K):", ["Baixo", "Médio", "Alto"])
with n_col3: formula_escolhida = st.text_input("Formulação Sugerida (ex: 04-14-08):", "00-00-00")

# --- BLOCO 4: GERADOR DE PDF ---
st.markdown("---")
st.header("4️⃣ Relatório Final")

def gerar_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_fill_color(34, 139, 34) # Verde Agro
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 20)
        pdf.set_xy(0, 15)
        pdf.cell(210, 10, "RECOMENDACAO TECNICA".encode('latin-1', 'replace').decode('latin-1'), align="C")
        
        # Dados do Cliente
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 12)
        pdf.set_xy(10, 50)
        pdf.cell(0, 10, f"Produtor: {cliente} | Gleba: {talhao}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.cell(0, 10, f"Cultura: {cultura} | Area: {area} ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        # Tabela de Resultados
        pdf.ln(5)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, " RESULTADOS DA ANALISE E CALAGEM", 1, ln=True, fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(95, 8, f" V% Atual: {v_atual}%", 1)
        pdf.cell(95, 8, f" V% Alvo: {v_alvo}%", 1, ln=True)
        pdf.cell(95, 8, f" CTC Total: {ctc}", 1)
        pdf.cell(95, 8, f" PRNT: {prnt}%", 1, ln=True)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f" RECOMENDACAO: {nc_ton_ha:.2f} t/ha (Total: {total_necessario:.2f} toneladas)", 1, ln=True)
        
        # Rodapé
        pdf.ln(20)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Consultor Tecnico: Felipe Amorim", align="C")
        
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        return str(e)

if st.button("PREPARAR RELATÓRIO PDF"):
    pdf_saida = gerar_pdf()
    
    if isinstance(pdf_saida, str):
        st.error(f"Erro interno: {pdf_saida}")
    else:
        st.download_button(
            label="⬇️ BAIXAR RELATÓRIO AGORA",
            data=pdf_saida,
            file_name=f"Relatorio_{talhao}.pdf",
            mime="application/pdf"
        )

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
