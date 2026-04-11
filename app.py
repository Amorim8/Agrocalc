import streamlit as st
from fpdf import FPDF

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# --- SIDEBAR: IDENTIFICAÇÃO & ÁREA ---
st.sidebar.header("📋 Identificação & Área")
talhao = st.sidebar.text_input("Talhão/Lote:", "Gleba A1")
cultura = st.sidebar.selectbox("Cultura Alvo:", ["Soja", "Milho", "Feijão", "Algodão", "Hortaliças", "Outra"])

st.sidebar.markdown("---")
st.sidebar.write("### 📐 Tamanho da Área Total")
tipo_medida = st.sidebar.selectbox("Medir em:", ["Hectares (ha)", "Tarefas (Baianas)", "Metros Quadrados (m²)"])
tamanho_area = st.sidebar.number_input("Quantidade da área:", value=1.0, min_value=0.01)

# Conversão para Hectare
if tipo_medida == "Tarefas (Baianas)":
    area_ha = (tamanho_area * 4356) / 10000
elif tipo_medida == "Metros Quadrados (m²)":
    area_ha = tamanho_area / 10000
else:
    area_ha = tamanho_area

# --- 1. CALAGEM ---
st.header("1. Necessidade de Calagem")
col1, col2, col3 = st.columns(3)
with col1:
    ctc = st.number_input("CTC (cmolc/dm³)", value=5.0, step=0.1)
with col2:
    v1 = st.number_input("Saturação atual (V1 %)", value=30.0, step=1.0)
with col3:
    v2 = st.number_input("Saturação desejada (V2 %)", value=70.0, step=1.0)

prnt = st.number_input("PRNT do Calcário (%)", value=80.0, step=1.0)
nc_ha = ((v2 - v1) * ctc) / prnt if prnt > 0 else 0
nc_total = nc_ha * area_ha

st.info(f"👉 **Recomendação:** {nc_ha:.2f} t/ha | **Quantidade p/ área:** {nc_total:.2f} toneladas")

st.markdown("---")

# --- 2. ADUBAÇÃO NPK ---
st.header("2. Recomendação de Adubação NPK")
metodo = st.radio("Como você vai adubar?", ["Usar Adubo Formulado", "Usar Adubos Simples"])

detalhes_pdf = ""
valor_final_kg = 0
sacos_calc = 0

if metodo == "Usar Adubo Formulado":
    c1, c2, c3 = st.columns(3)
    with c1: f_n = st.number_input("N (%)", value=6)
    with c2: f_p = st.number_input("P (%)", value=20)
    with c3: f_k = st.number_input("K (%)", value=20)
    
    nut_base = st.selectbox("Calcular dose com base em:", ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)"])
    valor_rec = st.number_input(f"Recomendação de {nut_base} (kg/ha):", value=80.0)

    dose_ha = 0
    if nut_base == "Nitrogênio (N)" and f_n > 0: dose_ha = (valor_rec / f_n) * 100
    elif nut_base == "Fósforo (P)" and f_p > 0: dose_ha = (valor_rec / f_p) * 100
    elif nut_base == "Potássio (K)" and f_k > 0: dose_ha = (valor_rec / f_k) * 100

    if dose_ha > 0:
        valor_final_kg = dose_ha * area_ha
        sacos_calc = int(valor_final_kg/50)+1
        st.success(f"🚜 **Dose:** {dose_ha:.1f} kg/ha | **Quantidade:** {valor_final_kg:.1f} kg")
        detalhes_pdf = f"Adubo {f_n}-{f_p}-{f_k}: {dose_ha:.1f} kg/ha (Total: {valor_final_kg:.1f} kg)"
else:
    colN, colP, colK = st.columns(3)
    with colN:
        n_rec = st.number_input("N (kg/ha)", value=0.0)
        u_total = (n_rec / 0.45) * area_ha
    with colP:
        p_rec = st.number_input("P2O5 (kg/ha)", value=80.0)
        s_total = (p_rec / 0.18) * area_ha
    with colK:
        k_rec = st.number_input("K2O (kg/ha)", value=60.0)
        k_total = (k_rec / 0.60) * area_ha
    detalhes_pdf = f"Ureia: {u_total:.1f}kg, Super: {s_total:.1f}kg, KCl: {k_total:.1f}kg"

# --- GERAÇÃO DO PDF ---
if st.button("🚀 Gerar PDF Profissional"):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho com fundo verde
        pdf.set_fill_color(34, 139, 34) 
        pdf.rect(0, 0, 210, 40, 'F')
        
        pdf.set_y(10)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 10, "RELATORIO DE CONSULTORIA".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        
        pdf.set_font("Arial", 'B', 15)
        pdf.cell(190, 10, "Felipe Amorim".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        pdf.ln(20)
        
        # Dados da Área
        pdf.set_fill_color(245, 245, 245)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, " IDENTIFICACAO DA AREA".encode('latin-1', 'replace').decode('latin-1'), ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(190, 8, f" Talhao: {talhao}  |  Cultura: {cultura}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.cell(190, 8, f" Area Total: {tamanho_area} {tipo_medida}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.ln(5)
        
        # Seções de Recomendação
        pdf.set_font("Arial", 'B', 13)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(190, 10, "1. RECOMENDACAO DE CALAGEM".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 7, f" Dose: {nc_ha:.2f} t/ha".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(235, 245, 235)
        pdf.cell(190, 9, f" TOTAL PARA A AREA: {nc_total:.2f} Toneladas".encode('latin-1', 'replace').decode('latin-1'), ln=True, fill=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 13)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(190, 10, "2. RECOMENDACAO DE ADUBACAO NPK".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(185, 8, f" Detalhes: {detalhes_pdf}".encode('latin-1', 'replace').decode('latin-1'))
        
        # Download sem erro de bytearray
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)

        st.download_button(
            label="✅ Baixar Relatório",
            data=pdf_bytes,
            file_name=f"Consultoria_{talhao}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro: {e}")

st.markdown("---")
st.caption("© 2026 | Felipe Amorim Consultoria Agronômica")
