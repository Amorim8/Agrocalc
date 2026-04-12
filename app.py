import streamlit as st
from fpdf import FPDF
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# --- SIDEBAR FIXA ---
st.sidebar.header("📋 Dados Gerais")
cliente = st.sidebar.text_input("Produtor:", "Nome do Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area_ha = st.sidebar.number_input("Área Total (Hectares):", value=1.0, min_value=0.01)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

# --- 1. ENTRADA DE DADOS ORGANIZADA (EXPANDER) ---
st.header("1️⃣ Entrada de Dados")

# Lugar de apertar para aparecer os campos, como você pediu
with st.expander("📊 CLIQUE AQUI PARA INSERIR DADOS DA ANÁLISE DE SOLO", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        argila = st.number_input("Teor de Argila (%):", value=0.0)
        p_solo = st.number_input("Fósforo (P) [mg/dm³]:", value=0.0)
        v_atual = st.number_input("V% Atual (Saturação):", value=0.0)
    with col2:
        k_solo = st.number_input("Potássio (K) [cmolc/dm³]:", value=0.0)
        ctc = st.number_input("CTC Total (pH 7.0):", value=5.0)
        prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# --- 2. CLASSIFICAÇÃO AUTOMÁTICA DOS NÍVEIS ---
# Lógica baseada nos manuais de solo para Cerrado
if p_solo < 10: nivel_p = "Baixo"
elif p_solo < 20: nivel_p = "Médio"
else: nivel_p = "Alto"

if k_solo < 0.15: nivel_k = "Baixo"
elif k_solo < 0.30: nivel_k = "Médio"
else: nivel_k = "Alto"

st.info(f"✅ Níveis Identificados: Fósforo **{nivel_p}** | Potássio **{nivel_k}**")

# --- 3. CÁLCULOS TÉCNICOS ---
# Calagem
v_alvo = 70 if cultura == "Soja" else 60
nc_ha = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual else 0
total_calcario = nc_ha * area_ha

# Adubação (kg/ha de P2O5 e K2O conforme nível)
tabela = {
    "Soja": {"Baixo": (100, 80), "Médio": (70, 60), "Alto": (40, 30)},
    "Milho": {"Baixo": (120, 100), "Médio": (90, 80), "Alto": (60, 50)}
}
req_p, req_k = tabela[cultura][nivel_p][0], tabela[cultura][nivel_k][1]

# --- 4. EXIBIÇÃO DOS RESULTADOS ---
st.divider()
st.header("2️⃣ Recomendação de Correção e Adubação")

res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc_ha:.2f}")
res2.metric(f"P₂O₅ para {nivel_p} (kg/ha)", f"{req_p}")
res3.metric(f"K₂O para {nivel_k} (kg/ha)", f"{req_k}")

# Cálculo do Formulado
st.write("---")
st.subheader("📦 Fechamento com Adubo Formulado")
f_col1, f_col2, f_col3 = st.columns(3)
f_n = f_col1.number_input("N no adubo:", value=0)
f_p = f_col2.number_input("P no adubo:", value=20)
f_k = f_col3.number_input("K no adubo:", value=20)

if f_p > 0:
    dose_adubo = (req_p / f_p) * 100
    sacos_total = (dose_adubo * area_ha) / 50
    st.warning(f"Dose Final: **{int(dose_adubo)} kg/ha** | Total para a área: **{math.ceil(sacos_total)} sacos**")

# --- 5. GERAÇÃO DO PDF (CORREÇÃO DE ABERTURA) ---
st.divider()
st.header("3️⃣ Relatório Final")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    # Fundo verde suave
    pdf.set_fill_color(240, 255, 240)
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(200, 10, "RELATORIO TECNICO - AGROCALC".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 11)
    pdf.ln(10)
    pdf.cell(200, 8, f"Consultor: Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(200, 8, f"Produtor: {cliente} | Area: {area_ha} ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(200, 8, f"Cultura: {cultura} | Talhao: {talhao}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, "RECOMENDACOES".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 8, f"Calcario: {nc_ha:.2f} t/ha (Total: {total_calcario:.2f} Ton)".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(200, 8, f"Adubacao: {int(dose_adubo)} kg/ha de {f_n}-{f_p}-{f_k}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.cell(200, 8, f"Total de Sacos: {math.ceil(sacos_total)}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    return pdf.output(dest='S')

# Botão de download direto para evitar erros de renderização
if st.button("📝 Criar Arquivo PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="⬇️ CLIQUE AQUI PARA BAIXAR O PDF",
        data=pdf_bytes,
        file_name=f"Recomendacao_{talhao}.pdf",
        mime="application/pdf"
    )

st.caption("Sistema AgroCalc Pro | Felipe Amorim")
