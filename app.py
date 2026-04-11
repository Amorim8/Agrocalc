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
tipo_medida = st.sidebar.selectbox("Medir em:", ["Hectares (ha)", "Tarefas (Baianas - 4.356 m²)", "Metros Quadrados (m²)"])
tamanho_area = st.sidebar.number_input("Quantidade da área:", value=1.0, min_value=0.01)

# Conversão interna para Hectare
if tipo_medida == "Tarefas (Baianas - 4.356 m²)":
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

st.info(f"👉 **Recomendação:** {nc_ha:.2f} t/ha | **Total para sua área:** {nc_total:.2f} toneladas")

st.markdown("---")

# --- 2. ADUBAÇÃO NPK ---
st.header("2. Recomendação de Adubação NPK")
metodo = st.radio("Como você vai adubar?", ["Usar Adubo Formulado (Ex: 00-20-20)", "Usar Adubos Simples (Ureia, Super, KCl)"])

detalhes_pdf = ""
total_kg = 0
sacos_totais = 0
dose_ha = 0

if metodo == "Usar Adubo Formulado (Ex: 00-20-20)":
    c1, c2, c3 = st.columns(3)
    with c1: f_n = st.number_input("N (%) no saco", value=6)
    with c2: f_p = st.number_input("P (%) no saco", value=20)
    with c3: f_k = st.number_input("K (%) no saco", value=20)
    
    nut_base = st.selectbox("Calcular dose com base em:", ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)"])
    valor_rec = st.number_input(f"Recomendação de {nut_base} (kg/ha):", value=80.0)

    if nut_base == "Nitrogênio (N)" and f_n > 0: dose_ha = (valor_rec / f_n) * 100
    elif nut_base == "Fósforo (P)" and f_p > 0: dose_ha = (valor_rec / f_p) * 100
    elif nut_base == "Potássio (K)" and f_k > 0: dose_ha = (valor_rec / f_k) * 100

    if dose_ha > 0:
        total_kg = dose_ha * area_ha
        sacos_totais = int(total_kg/50)+1
        st.success(f"🚜 **Dose:** {dose_ha:.1f} kg/ha | **Total Área:** {total_kg:.1f} kg ({sacos_totais} sacos)")
        detalhes_pdf = f"Adubo {f_n}-{f_p}-{f_k}: {dose_ha:.1f} kg/ha (Total: {total_kg:.1f} kg)"
    else:
        st.warning("⚠️ Verifique a fórmula!")
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

# --- CLASSE PARA O PDF COM MARCA D'ÁGUA ---
class PDF(FPDF):
    def header(self):
        # Marca d'água cinza bem clara
        self.set_font('Arial', 'B', 40)
        self.set_text_color(240, 240, 240)
        # Rotação de 45 graus no centro
        with self.rotation(45, 105, 148):
            self.text(35, 190, "FELIPE AMORIM - CONSULTORIA")

# --- BOTÃO E GERAÇÃO DO PDF ---
if st.button("Gerar Relatório"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Título Verde
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(34, 139, 34) 
        pdf.cell(190, 15, "Relatorio de Recomendacao Agronomica", ln=True, align='C')
        pdf.ln(5)
        
        # Consultor em destaque
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(30, 10, "Consultor:", ln=0)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(100, 10, "Felipe Amorim", ln=True)
        
        # Dados da Área com fundo suave
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 10, f"  Talhao: {talhao}  |  Cultura: {cultura}", ln=True, fill=True)
        pdf.cell(190, 10, f"  Area: {tamanho_area} {tipo_medida} ({area_ha:.2f} ha)", ln=True, fill=True)
        pdf.ln(5)
        
        # Calagem
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(190, 10, "1. Recomendacao de Calagem", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 8, f"Necessidade por hectare: {nc_ha:.2f} t/ha", ln=True)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(190, 10, f"TOTAL PARA A AREA: {nc_total:.2f} Toneladas", ln=True, fill=True)
        pdf.ln(5)
        
        # NPK
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(190, 10, "2. Recomendacao de Adubacao NPK", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(190, 8, f"Detalhamento: {detalhes_pdf}")
        
        if metodo == "Usar Adubo Formulado (Ex: 00-20-20)":
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(190, 10, f"TOTAL: {total_kg:.1f} kg ({sacos_totais} sacos de 50kg)", ln=True, fill=True)
        
        # Assinatura centralizada
        pdf.ln(25)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 10, "________________________________________________", ln=True, align='C')
        pdf.cell(190, 5, "Felipe Amorim - Consultor Responsavel", ln=True, align='C')
        
        pdf_output = bytes(pdf.output(dest='S'))
        
        st.download_button(
            label="📥 Baixar Recomendação",
            data=pdf_output,
            file_name=f"Recomendacao_{talhao}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.markdown("---")
st.caption("© 2026 | Felipe Amorim Consultoria")
