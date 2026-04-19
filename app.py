import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
# Mantendo a senha de acesso solicitada
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

# ---------------- CONFIG VISUAL (CONTRASTE MÁXIMO) ----------------
st.set_page_config(page_title="Sistema de Prescrição Agronômica", layout="wide", page_icon="🌿")

st.markdown("""
<style>
.main { background-color: #f8fafc; }

/* Estilização das caixas de métricas - FUNDO CLARO E TEXTO PRETO */
div[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    padding: 20px;
    border-radius: 12px;
    border-left: 10px solid #16a34a !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* VALOR NUMÉRICO - PRETO INTENSO */
div[data-testid="stMetricValue"] > div {
    color: #000000 !important;
    font-size: 38px !important;
    font-weight: 800 !important;
}

/* RÓTULO DA MÉTRICA - PRETO E NEGRITO (LEITURA TOTAL) */
div[data-testid="stMetricLabel"] > div > p {
    color: #000000 !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    text-transform: uppercase;
}

.stButton>button {
    background-color: #16a34a !important;
    color: white !important;
    font-weight: bold;
    height: 3.5em;
    width: 100%;
}

.aviso-dados {
    background-color: #fffbeb;
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #d97706;
    color: #92400e;
    font-weight: bold;
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
    
    variedade_palma = ""
    if cultura == "Palma":
        variedade_palma = st.selectbox("🌵 Variedade da Palma:", ["Orelha de Elefante", "Palma Miúda"])
    
    meta_padrao = 8.0 if cultura == "Milho" else (4.0 if cultura == "Soja" else 50.0)
    meta_ton = st.number_input("🎯 Meta de Produtividade (t/ha):", value=meta_padrao)

# ---------------- INTERFACE PRINCIPAL ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA") # Título profissional sem nome próprio

st.markdown('<div class="aviso-dados">⚠️ NOTA IMPORTANTE: Todos os resultados e recomendações são baseados nos dados técnicos inseridos.</div>', unsafe_allow_html=True)

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

# ---------------- CÁLCULOS ----------------
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area
ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 
total_gesso = ng * area

n_total_ha = meta_ton * 25 if cultura == "Milho" else 0
n_plantio_ha = n_total_ha * 0.20
n_cobertura_ha = n_total_ha * 0.80

st.subheader("Configuração da Fórmula Comercial (NPK)")
f1, f2, f3 = st.columns(3)
fn, fp, fk = f1.number_input("N (%)", 4), f2.number_input("P (%)", 20), f3.number_input("K (%)", 20)
dose_ha = max(((meta_ton * 15)/fp*100) if fp>0 else 0, ((meta_ton * 20)/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area

# ---------------- EXIBIÇÃO DE RESULTADOS NA TELA ----------------
st.divider()
st.header("Resumo das Recomendações")
r1, r2, r3 = st.columns(3)
r1.metric("CALCÁRIO (T/HA)", f"{nc:.2f}")
st.write(f"Total: **{total_calc:.2f} t**")
r2.metric("GESSO (T/HA)", f"{ng:.2f}")
st.write(f"Total: **{total_gesso:.2f} t**")
r3.metric("ADUBO (KG/HA)", f"{dose_ha:.0f}")
st.write(f"Total: **{total_adubo:.1f} kg**")

if cultura == "Milho":
    st.divider()
    st.header("📊 Detalhamento de Nitrogênio (N)")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.metric("N NO PLANTIO (20%)", f"{n_plantio_ha:.1f} kg/ha")
    with col_n2:
        st.metric("N NA COBERTURA (80%)", f"{n_cobertura_ha:.1f} kg/ha")

# ---------------- GERAÇÃO DO PDF (COM CORREÇÃO DE ACENTOS) ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Função interna para tratar os acentos corretamente no PDF (Padrão Windows-1252)
    def txt(texto):
        return str(texto).encode('cp1252', 'replace').decode('cp1252')

    # Banner Superior
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.ln(12)
    pdf.cell(190, 10, txt("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(190, 7, txt(f"Data de Emissão: {data_hoje}"), 0, 1, "C")
    
    # Aviso Legal
    pdf.set_text_color(200, 0, 0)
    pdf.ln(18)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 8, txt("AVISO: Recomendações baseadas estritamente nos dados técnicos inseridos."), 0, 1, "C")
    
    # Dados Gerais
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, txt("1. INFORMAÇÕES DA PROPRIEDADE"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, txt(f"Cliente: {nome_cliente} | Fazenda: {fazenda}"), 0, 1)
    
    txt_cultura = f"Cultura: {cultura}"
    if cultura == "Palma": txt_cultura += f" ({variedade_palma})"
    pdf.cell(190, 7, txt(f"{txt_cultura} | Área: {area} ha | Produtividade: {meta_ton} t/ha"), 0, 1)

    # Recomendações Técnicas
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, txt("2. PRESCRIÇÃO TÉCNICA DE MANEJO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, txt(f"- Calcário: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), 0, 1)
    pdf.cell(190, 7, txt(f"- Gesso: {ng:.2f} t/ha (Total: {total_gesso:.2f} t)"), 0, 1)
    pdf.cell(190, 7, txt(f"- Adubo NPK: {dose_ha:.0f} kg/ha (Total: {total_adubo:.1f} kg)"), 0, 1)

    # Observações de Manejo Especial para Palma
    if cultura == "Palma":
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(210, 255, 210)
        pdf.cell(190, 8, txt(f"3. ORIENTAÇÕES DE MANEJO ({variedade_palma.upper()})"), 1, 1, "L", fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.multi_cell(190, 6, txt("- NÃO CORTAR O CLADÓDIO MÃE: Prática essencial para manter o vigor e a produção contínua.\n- CICLO DE COLHEITA: O primeiro corte deve ser realizado entre 18 a 24 meses pós-plantio."))

    # Referências Técnicas Dinâmicas
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, txt(f"REFERÊNCIAS TÉCNICAS ({cultura.upper()})"), 0, 1)
    pdf.set_font("Helvetica", "I", 9)
    if cultura == "Milho":
        pdf.multi_cell(190, 5, txt("- EMBRAPA Milho e Sorgo: Tecnologias de Produção e Manejo de Solo."))
    elif cultura == "Soja":
        pdf.multi_cell(190, 5, txt("- SBCS: Manual de Calagem e Adubação para a Cultura da Soja."))
    elif cultura == "Palma":
        pdf.multi_cell(190, 5, txt("- IPA: Manual de Cultivo para variedades Miúda e Orelha de Elefante."))

    # Assinatura Final
    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, txt(f"Responsável Técnico: Felipe Amorim"), 0, 1, "R")
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO DE DOWNLOAD ----------------
st.divider()
if st.button("📄 GERAR RELATÓRIO PDF COMPLETO"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Clique para Baixar o Relatório", pdf_bytes, file_name=f"Prescricao_{nome_cliente}.pdf", mime="application/pdf")
