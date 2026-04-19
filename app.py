import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
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

# ---------------- CONFIG VISUAL (CSS) ----------------
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

/* COR DO NÚMERO (Branco) */
div[data-testid="stMetricValue"] > div {
    color: #ffffff !important;
    font-size: 32px !important;
    font-weight: bold !important;
}

/* COR DO NOME/RÓTULO (Branco para visibilidade total) */
div[data-testid="stMetricLabel"] > div > p {
    color: #ffffff !important;
    font-size: 18px !important;
    font-weight: 500 !important;
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
    color: #cbd5e1;
    font-weight: 500;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR (PARÂMETROS) ----------------
with st.sidebar:
    st.title("🌿 Parâmetros")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura de Interesse:", ["Soja", "Milho", "Palma"], horizontal=True)
    
    # Seleção de Variedade para Palma
    variedade_palma = ""
    if cultura == "Palma":
        variedade_palma = st.selectbox("🌵 Variedade da Palma:", ["Orelha de Elefante", "Palma Miúda"])
    
    meta_padrao = 8.0 if cultura == "Milho" else (4.0 if cultura == "Soja" else 50.0)
    meta_ton = st.number_input("🎯 Meta de Produtividade (t/ha):", value=meta_padrao)

# ---------------- INTERFACE PRINCIPAL ----------------
st.title("SISTEMA DE PRESCRIÇÃO | FELIPE AMORIM")

st.markdown('<div class="aviso-dados">⚠️ NOTA IMPORTANTE: Todos os resultados e recomendações gerados são calculados estritamente de acordo com os dados técnicos inseridos nesta calculadora.</div>', unsafe_allow_html=True)

st.subheader("Entrada de Dados da Análise de Solo")
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

# ---------------- LÓGICA DE CÁLCULO ----------------
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area

ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 
total_gesso = ng * area

n_total_ha = meta_ton * 25 if cultura == "Milho" else 0
n_plantio_ha = n_total_ha * 0.20
n_cobertura_ha = n_total_ha * 0.80
total_n_plantio = n_plantio_ha * area
total_n_cobertura = n_cobertura_ha * area

st.subheader("Configuração da Fórmula Comercial (NPK)")
f1, f2, f3 = st.columns(3)
fn, fp, fk = f1.number_input("N %", 4), f2.number_input("P %", 20), f3.number_input("K %", 20)

dose_ha = max(((meta_ton * 15)/fp*100) if fp>0 else 0, ((meta_ton * 20)/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area

# ---------------- RESULTADOS NA TELA ----------------
st.divider()
st.header("Resumo das Recomendações")

res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc:.2f}")
st.write(f"**Total Área:** {total_calc:.2f} t")

res2.metric("Gesso (t/ha)", f"{ng:.2f}")
st.write(f"**Total Área:** {total_gesso:.2f} t")

res3.metric("Adubo Comercial (kg/ha)", f"{dose_ha:.0f}")
st.write(f"**Total Área:** {total_adubo:.1f} kg")

if cultura == "Milho":
    st.divider()
    st.header("📊 Detalhamento de Nitrogênio (N)")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.metric("N no Plantio (20%)", f"{n_plantio_ha:.1f} kg/ha")
        st.success(f"**Total:** {total_n_plantio:.1f} kg de N")
    with col_n2:
        st.metric("N na Cobertura (80%)", f"{n_cobertura_ha:.1f} kg/ha")
        st.success(f"**Total:** {total_n_cobertura:.1f} kg de N")

# ---------------- GERAÇÃO DO PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.ln(12)
    pdf.cell(190, 10, fix("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(190, 7, fix(f"Consultoria: Felipe Amorim | Data: {data_hoje}"), 0, 1, "C")
    
    # Aviso de Responsabilidade no PDF
    pdf.set_text_color(200, 0, 0)
    pdf.ln(18)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 8, fix("AVISO: Resultados baseados estritamente na colocacao dos dados na calculadora."), 0, 1, "C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, fix("1. IDENTIFICAÇÃO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"Produtor: {nome_cliente} | Fazenda: {fazenda}"), 0, 1)
    
    txt_cultura = f"Cultura: {cultura}"
    if cultura == "Palma": txt_cultura += f" ({variedade_palma})"
    pdf.cell(190, 7, fix(f"{txt_cultura} | Meta: {meta_ton} t/ha"), 0, 1)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("2. RECOMENDAÇÕES DE CORREÇÃO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"- Calcario: {nc:.2f} t/ha | Gesso: {ng:.2f} t/ha"), 0, 1)
    pdf.cell(190, 7, fix(f"- Adubo Comercial NPK: {dose_ha:.0f} kg/ha"), 0, 1)

    if cultura == "Palma":
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(210, 255, 210)
        pdf.cell(190, 8, fix(f"3. MANEJO TÉCNICO ({variedade_palma.upper()})"), 1, 1, "L", fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.multi_cell(190, 6, fix("- NAO CORTAR O CLADODIO MAE: Preservar para garantir a longevidade.\n- PRIMEIRO CORTE: Realizar entre 18 a 24 meses apos o plantio.\n- ADUBACAO: Baseada na meta de produtividade inserida."))

    # Referências Dinâmicas por Cultura
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix(f"REFERÊNCIAS TÉCNICAS ({cultura.upper()})"), 0, 1)
    pdf.set_font("Helvetica", "I", 9)
    if cultura == "Milho":
        pdf.multi_cell(190, 5, fix("- EMBRAPA Milho e Sorgo: Recomendacoes e Manejo de Nitrogenio."))
    elif cultura == "Soja":
        pdf.multi_cell(190, 5, fix("- SBCS: Manual de Calagem e Adubacao para Soja."))
    elif cultura == "Palma":
        pdf.multi_cell(190, 5, fix("- IPA: Manual de Cultivo e Recomendacao para variedades Miuda e Orelha de Elefante."))

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix("Consultoria Técnica: Felipe Amorim"), 0, 1, "R")
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- DOWNLOAD ----------------
st.divider()
if st.button("📄 GERAR RELATÓRIO PDF COMPLETO"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório PDF", pdf_bytes, file_name=f"Prescricao_{cultura}_{nome_cliente}.pdf", mime="application/pdf")
