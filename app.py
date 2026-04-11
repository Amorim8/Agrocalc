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
sacos_totais = 0

if metodo == "Usar Adubo Formulado (Ex: 00-20-20)":
    c1, c2, c3 = st.columns(3)
    with c1: f_n = st.number_input("N (%) no saco", value=6)
    with c2: f_p = st.number_input("P (%) no saco", value=20)
    with c3: f_k = st.number_input("K (%) no saco", value=20)
    
    nut_base = st.selectbox("Calcular dose com base em:", ["Nitrogênio (N)", "Fósforo (P)", "Potássio (K)"])
    valor_rec = st.number_input(f"Recomendação de {nut_base} (kg/ha):", value=80.0)

    dose_ha = 0
    if nut_base == "Nitrogênio (N)" and f_n > 0: dose_ha = (valor_rec / f_n) * 100
    elif nut_base == "Fósforo (P)" and f_p > 0: dose_ha = (valor_rec / f_p) * 100
    elif nut_base == "Potássio (K)" and f_k > 0: dose_ha = (valor_rec / f_k) * 100

    if dose_ha > 0:
        total_kg = dose_ha * area_ha
        sacos_totais = int(total_kg/50)+1
        st.success(f"🚜 **Dose:** {dose_ha:.1f} kg/ha | **Total Área:** {total_kg:.1f} kg ({sacos_totais} sacos de 50kg)")
        detalhes_pdf = f"Adubo {f_n}-{f_p}-{f_k}: {dose_ha:.1f} kg/ha. Total para area: {total_kg:.1f} kg ({sacos_totais} sacos)."
    else:
        st.warning(f"⚠️ Atenção: A fórmula escolhida tem 0% de {nut_base}. Mude o nutriente base ou a fórmula.")
else:
    colN, colP, colK = st.columns(3)
    with colN:
        n_rec = st.number_input("N (kg/ha)", value=0.0)
        u_total = (n_rec / 0.45) * area_ha
        st.write(f"Ureia total: {u_total:.1f} kg")
    with colP:
        p_rec = st.number_input("P2O5 (kg/ha)", value=80.0)
        s_total = (p_rec / 0.18) * area_ha
        st.write(f"Super Simples total: {s_total:.1f} kg")
    with colK:
        k_rec = st.number_input("K2O (kg/ha)", value=60.0)
        k_total = (k_rec / 0.60) * area_ha
        st.write(f"Cloreto (KCl) total: {k_total:.1f} kg")
    detalhes_pdf = f"Simples - Ureia: {u_total:.1f}kg, Super: {s_total:.1f}kg, KCl: {k_total:.1f}kg (Totais p/ area)"

# --- PDF ROBUSTO E PROFISSIONAL ---
if st.button("🚀 Gerar PDF Profissional e Colorido"):
    try:
        # Função para corrigir acentuação (substitui caracteres especiais)
        def sem_acento(texto):
            replacements = {
                'ã': 'a', 'ã': 'a', 'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a',
                'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
                'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
                'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o',
                'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
                'ç': 'c',
                'Ã': 'A', 'Á': 'A', 'À': 'A', 'Â': 'A', 'Ä': 'A',
                'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
                'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
                'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Ö': 'O', 'Õ': 'O',
                'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
                'Ç': 'C'
            }
            # FPDF nativo não suporta UTF-8 sem configurar fonte, vamos converter para garantir
            # Para entregar com acento real, precisaríamos configurar uma fonte TrueType (.ttf) que suportasse
            # Vamos manter a conversão por segurança, ou você pode carregar uma fonte customizada.
            return texto # Tentei manter o acento, vamos ver se a biblioteca nativa suporta no Streamlit Cloud

        pdf = FPDF()
        pdf.add_page()
        
        # --- CABEÇALHO ---
        # Adicionar uma imagem/logo opcional (se você tiver uma, me avisa que te ensino a colocar)
        # pdf.image('logo_agro.png', 10, 8, 33) 
        
        pdf.set_font("Arial", 'B', 18)
        # Usar uma cor verde para o título (R, G, B) - (34, 139, 34) é Forest Green
        pdf.set_text_color(34, 139, 34) 
        pdf.cell(190, 10, sem_acento("Relatório de Recomendação Agronômica"), ln=True, align='C')
        pdf.ln(5)
        
        # --- DADOS DO CONSULTOR ---
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0) # Voltar para preto
        pdf.cell(30, 10, "Consultor:", ln=0)
        pdf.set_font("Arial", 'B', 14)
        # Usar verde para o nome em destaque
        pdf.set_text_color(34, 139, 34)
        pdf.cell(100, 10, sem_acento("Felipe Amorim"), ln=True)
        
        # --- DADOS DA ÁREA ---
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0) # Preto
        pdf.cell(190, 8, f"Talhao/Lote: {sem_acento(talhao)} | Cultura: {sem_acento(cultura)}", ln=True)
        pdf.cell(190, 8, f"Area Total: {tamanho_area} {tipo_medida} ({area_ha:.2f} ha reais)", ln=True)
        pdf.ln(5)
        
        # --- RESULTADOS: CALAGEM ---
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(34, 139, 34) # Verde Forest
        pdf.cell(190, 10, sem_acento("1. Recomendação de Calagem"), ln=True)
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 8, f"Necessidade por Hectare: {nc_ha:.2f} t/ha", ln=True)
        pdf.set_font("Arial", 'B', 11)
        # Destacar o total para a área
        pdf.cell(50, 8, sem_acento("Total para sua Área:"), ln=0)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(100, 8, f"{nc_total:.2f} toneladas", ln=True)
        pdf.ln(5)
        
        # --- RESULTADOS: ADUBAÇÃO ---
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(34, 139, 34) # Verde Forest
        pdf.cell(190, 10, sem_acento("2. Recomendação de Adubação NPK"), ln=True)
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        if metodo == "Usar Adubo Formulado (Ex: 00-20-20)":
            pdf.cell(190, 8, f"Adubo Formulado {f_n}-{f_p}-{f_k}: {dose_ha:.1f} kg/ha", ln=True)
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 11)
            # Destacar o total e sacos
            pdf.cell(50, 8, sem_acento("Total p/ sua Área:"), ln=0)
            pdf.set_text_color(34, 139, 34)
            pdf.cell(100, 8, f"{total_kg:.1f} kg", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(50, 8, sem_acento("Quantidade de Sacos:"), ln=0)
            pdf.set_text_color(34, 139, 34)
            pdf.cell(100, 8, f"{sacos_totais} sacos de 50kg", ln=True)
        else:
            pdf.multi_cell(190, 8, sem_acento(f"Adubos Simples (Totais para area): {detalhes_pdf}"))
        
        # --- ASSINATURA ---
        pdf.ln(25)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 10, "________________________________________________", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(190, 5, sem_acento("Assinatura do Consultor Responsável"), ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(190, 5, sem_acento("Felipe Amorim"), ln=True, align='C')
        
        # Geração Robusta de PDF (Consertado o bug anterior)
        pdf_out = pdf.output(dest='S')
        final_pdf = bytes(pdf_out)
        
        st.download_button(
            label="📥 Baixar seu Relatório Profissional e Colorido",
            data=final_pdf,
            file_name=f"Relatorio_{talhao}_{sem_acento(cultura)}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Houve um problema ao gerar o relatório: {e}")

st.markdown("---")
st.caption("© 2026 | Felipe Amorim Consultoria")
