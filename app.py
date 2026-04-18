import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- LOGIN ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- CONFIG VISUAL ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria Agronômica", layout="wide", page_icon="🌿")

st.markdown("""
<style>
.main { background-color: #0e1117; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1f2937, #111827) !important;
    border: 1px solid #374151;
    padding: 18px;
    border-radius: 12px;
    border-left: 6px solid #22c55e !important;
}
.stButton>button {
    background-color: #28a745 !important;
    color: white !important;
    font-weight: bold;
    width: 100%;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR (ENTRADAS) ----------------
with st.sidebar:
    st.title("🌿 Parâmetros")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma"], horizontal=True)
    
    variedade = ""
    if cultura == "Palma":
        variedade = st.selectbox("🌵 Variedade:", ["Miúda", "Orelha de Elefante", "Sertânia"])
    
    meta_ton = st.number_input("🎯 Meta (t/ha):", value=4.0 if cultura=="Soja" else 8.0)

# ---------------- ANÁLISE DE SOLO ----------------
st.title("CONSULTORIA AGRONÔMICA | FELIPE AMORIM")
st.write(f"Relatório Técnico Gerado em: {data_hoje}")

st.subheader("Entrada de Dados - Solo")
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

# ---------------- CÁLCULOS TÉCNICOS ----------------
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area

ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 
total_gesso = ng * area

rec_p = meta_ton * 15
rec_k = meta_ton * 20
rec_n = meta_ton * 25 if cultura == "Milho" else 0

# Configuração de Adubo
st.subheader("Configuração da Fórmula Comercial")
f1, f2, f3 = st.columns(3)
fn = f1.number_input("N %", value=4)
fp = f2.number_input("P %", value=20)
fk = f3.number_input("K %", value=20)

dose_ha = max((rec_p/fp*100) if fp>0 else 0, (rec_k/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area
sacos = math.ceil(total_adubo / 50)

# ---------------- RESULTADOS EM TELA ----------------
st.subheader("Resultados")
res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc:.2f}")
res2.metric("Gesso (t/ha)", f"{ng:.2f}")
res3.metric("Adubo (kg/ha)", f"{dose_ha:.0f}")

# ---------------- GERAÇÃO DO PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.ln(12)
    pdf.cell(190, 10, fix("PRESCRIÇÃO AGRONÔMICA ESPECIALIZADA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(190, 7, fix(f"Felipe Amorim - Consultoria Técnica | {data_hoje}"), 0, 1, "C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(18)

    # 1. Identificação
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, fix("1. DADOS DA PROPRIEDADE E ANÁLISE"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(95, 7, fix(f"Produtor: {nome_cliente}"), 0, 0)
    pdf.cell(95, 7, fix(f"Fazenda: {fazenda}"), 0, 1)
    pdf.cell(95, 7, fix(f"Cultura: {cultura} | Meta: {meta_ton} t/ha"), 0, 0)
    pdf.cell(95, 7, fix(f"Área: {area:g} ha | Local: {municipio}-{estado}"), 0, 1)

    # 2. Recomendação
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("2. RECOMENDAÇÃO TÉCNICA"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"- Calcário (t/ha): {nc:.2f} | Total para a área: {total_calc:.2f} t"), 0, 1)
    pdf.cell(190, 7, fix(f"- Gesso Agrícola (t/ha): {ng:.2f} | Total para a área: {total_gesso:.2f} t"), 0, 1)
    pdf.cell(190, 7, fix(f"- Adubação NPK (kg/ha): {dose_ha:.0f} | Total: {total_adubo:.1f} kg ({sacos} sacos)"), 0, 1)

    # 3. Manejo Detalhado
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("3. ORIENTAÇÕES DE MANEJO E CORTES"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    
    if cultura == "Palma":
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 6, fix("CUIDADOS NO CORTE DA PALMA (MUITO IMPORTANTE):"), 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(190, 5, fix("- É PROIBIDO realizar o corte na 'Planta-Mãe'. Deve-se preservar o primeiro cladódio (artigo) para garantir a rebrota e longevidade.\n- Realizar o corte a partir do segundo ou terceiro nível de raquetes.\n- Aplicar 20 a 30 t/ha de esterco bovino curtido para suprimento orgânico (Ref: IPA)."))
    elif cultura == "Milho":
        pdf.multi_cell(190, 5, fix("- Nitrogênio: 20% no plantio e 80% em cobertura entre V4 e V6.\n- Monitorar cigarrinha e percevejo nas fases iniciais (Ref: Embrapa)."))
    else:
        pdf.multi_cell(190, 5, fix("- Focar na inoculação com Bradyrhizobium para suprimento de N.\n- Realizar adubação de manutenção com Fósforo no plantio (Ref: SBCS)."))

    # 4. Referências Bibliográficas
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix("4. REFERÊNCIAS TÉCNICAS"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.ln(2)
    pdf.multi_cell(190, 4, fix("PALMA: IPA (Instituto Agronômico de Pernambuco) - Manejo de Palma Forrageira.\nMILHO: EMBRAPA Milho e Sorgo - Nutrição e Adubação Nitrogenada.\nSOJA: SBCS (Sociedade Brasileira de Ciência do Solo) - Manual de Calagem e Adubação."))

    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO DOWNLOAD ----------------
st.divider()
if st.button("📄 Gerar Relatório Profissional"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Consultoria_{nome_cliente}.pdf", mime="application/pdf")
