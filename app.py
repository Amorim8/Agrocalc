import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
# Senha e Data atualizada
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- SISTEMA DE LOGIN ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Acessar Sistema"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- CONFIG VISUAL (ALTA VISIBILIDADE) ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria Agronômica", layout="wide", page_icon="🌿")

st.markdown("""
<style>
.main { background-color: #0e1117; }

/* Estilização das caixas de métricas */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1f2937, #111827) !important;
    border: 1px solid #374151;
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #22c55e !important;
}

/* VALOR NUMÉRICO - BRANCO PURO */
div[data-testid="stMetricValue"] > div {
    color: #ffffff !important;
    font-size: 36px !important;
    font-weight: bold !important;
}

/* NOME DA MÉTRICA (RÓTULO) - BRANCO PURO E NEGRITO (PARA LEITURA TOTAL) */
div[data-testid="stMetricLabel"] > div > p {
    color: #ffffff !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    opacity: 1 !important;
    text-shadow: 1px 1px 2px #000;
}

.stButton>button {
    background-color: #28a745 !important;
    color: white !important;
    font-weight: bold;
    width: 100%;
}

.aviso-dados {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #f59e0b;
    color: #ffffff;
    font-weight: bold;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- BARRA LATERAL (PARÂMETROS) ----------------
with st.sidebar:
    st.title("🌿 Parâmetros")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura de Interesse:", ["Soja", "Milho", "Palma"], horizontal=True)
    
    # Seleção de Variedade específica para Palma
    variedade_palma = ""
    if cultura == "Palma":
        variedade_palma = st.selectbox("🌵 Variedade da Palma:", ["Orelha de Elefante", "Palma Miúda"])
    
    meta_padrao = 8.0 if cultura == "Milho" else (4.0 if cultura == "Soja" else 50.0)
    meta_ton = st.number_input("🎯 Meta de Produtividade (t/ha):", value=meta_padrao)

# ---------------- INTERFACE PRINCIPAL ----------------
st.title("SISTEMA DE PRESCRIÇÃO | FELIPE AMORIM")

st.markdown('<div class="aviso-dados">⚠️ NOTA IMPORTANTE: Todos os resultados gerados baseiam-se nos dados técnicos inseridos nesta calculadora.</div>', unsafe_allow_html=True)

st.subheader("Análise de Solo")
c1, c2, c3, c4 = st.columns(4)
with c1:
    ph_solo = st.number_input("pH (Água)", value=5.5)
    p_solo = st.number_input("Fósforo (mg/dm³)", value=8.0)
with c2:
    al_solo = st.number_input("Alumínio (cmolc/dm³)", value=0.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", value=0.15)
with c3:
    argila = st.number_input("Argila (%)", value=35.0)
    v_atual = st.number_input("V% Atual", value=40.0)
with c4:
    ctc_t = st.number_input("CTC (T)", value=3.25)
    prnt_calc = st.number_input("PRNT Calcário (%)", value=85.0)

# ---------------- LÓGICA DE CÁLCULOS ----------------
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area

ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 
total_gesso = ng * area

# Manejo de N para Milho
n_total_ha = meta_ton * 25 if cultura == "Milho" else 0
n_plantio_ha = n_total_ha * 0.20
n_cobertura_ha = n_total_ha * 0.80

st.subheader("Configuração da Adubação NPK")
f1, f2, f3 = st.columns(3)
fn, fp, fk = f1.number_input("N (%) na Fórmula", 4), f2.number_input("P (%) na Fórmula", 20), f3.number_input("K (%) na Fórmula", 20)

dose_ha = max(((meta_ton * 15)/fp*100) if fp>0 else 0, ((meta_ton * 20)/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area

# ---------------- EXIBIÇÃO DE RESULTADOS NA TELA ----------------
st.divider()
st.header("Resumo das Recomendações")

res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc:.2f}")
st.write(f"**Total Área:** {total_calc:.2f} t")

res2.metric("Gesso (t/ha)", f"{ng:.2f}")
st.write(f"**Total Área:** {total_gesso:.2f} t")

res3.metric("Adubo (kg/ha)", f"{dose_ha:.0f}")
st.write(f"**Total Área:** {total_adubo:.1f} kg")

if cultura == "Milho":
    st.divider()
    st.header("📊 Detalhamento de Nitrogênio (N)")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.metric("N no Plantio (20%)", f"{n_plantio_ha:.1f} kg/ha")
    with col_n2:
        st.metric("N na Cobertura (80%)", f"{n_cobertura_ha:.1f} kg/ha")

# ---------------- GERAÇÃO DO PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho Banner
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.ln(12)
    pdf.cell(190, 10, fix("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(190, 7, fix(f"Consultoria: Felipe Amorim | Data: {data_hoje}"), 0, 1, "C")
    
    # Aviso de Dados
    pdf.set_text_color(200, 0, 0)
    pdf.ln(18)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 8, fix("AVISO: Resultados baseados na colocacao dos dados na calculadora."), 0, 1, "C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, fix("1. IDENTIFICAÇÃO DO PROJETO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"Produtor: {nome_cliente} | Fazenda: {fazenda}"), 0, 1)
    
    info_cultura = f"Cultura: {cultura}"
    if cultura == "Palma": info_cultura += f" ({variedade_palma})"
    pdf.cell(190, 7, fix(f"{info_cultura} | Area: {area} ha | Meta: {meta_ton} t/ha"), 0, 1)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("2. RECOMENDAÇÕES DE CORREÇÃO E ADUBAÇÃO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"- Calcario: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), 0, 1)
    pdf.cell(190, 7, fix(f"- Gesso: {ng:.2f} t/ha (Total: {total_gesso:.2f} t)"), 0, 1)
    pdf.cell(190, 7, fix(f"- Adubo Comercial NPK: {dose_ha:.0f} kg/ha (Total: {total_adubo:.1f} kg)"), 0, 1)

    # Manejo da Palma
    if cultura == "Palma":
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(210, 255, 210)
        pdf.cell(190, 8, fix(f"3. MANEJO TÉCNICO ({variedade_palma.upper()})"), 1, 1, "L", fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.multi_cell(190, 6, fix("- NAO CORTAR O CLADODIO MAE: Essencial para o rebrote e longevidade.\n- PRIMEIRO CORTE: Realizar entre 18 a 24 meses apos o plantio.\n- VARIEDADE: Manejo focado nas caracteristicas da " + variedade_palma + "."))

    # Referências Técnicas
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix(f"REFERÊNCIAS ({cultura.upper()})"), 0, 1)
    pdf.set_font("Helvetica", "I", 9)
    if cultura == "Milho":
        pdf.multi_cell(190, 5, fix("- EMBRAPA Milho e Sorgo: Tecnologias de Producao e Manejo de Adubacao."))
    elif cultura == "Soja":
        pdf.multi_cell(190, 5, fix("- SBCS: Manual de Calagem e Adubacao para a Cultura da Soja."))
    elif cultura == "Palma":
        pdf.multi_cell(190, 5, fix("- IPA: Manual de Cultivo e Recomendacao para variedades Miuda e Orelha de Elefante."))

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix("Consultoria Técnica: Felipe Amorim"), 0, 1, "R")
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO DE DOWNLOAD ----------------
st.divider()
if st.button("📄 GERAR RELATÓRIO PDF COMPLETO"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF Agora", pdf_bytes, file_name=f"Prescricao_{cultura}.pdf", mime="application/pdf")
