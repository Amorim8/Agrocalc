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

# ---------------- CONFIG VISUAL (CSS DE ALTA VISIBILIDADE) ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria Agronômica", layout="wide", page_icon="🌿")

st.markdown("""
<style>
.main { background-color: #0e1117; }

/* Estilização das métricas para leitura clara no modo escuro */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1f2937, #111827) !important;
    border: 1px solid #374151;
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #22c55e !important;
}

/* Força a cor do valor da métrica para branco puro */
div[data-testid="stMetricValue"] > div {
    color: #ffffff !important;
    font-size: 32px !important;
    font-weight: bold !important;
}

/* Força a cor do rótulo para cinza claro */
div[data-testid="stMetricLabel"] > div > p {
    color: #e5e7eb !important;
    font-size: 16px !important;
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

# ---------------- SIDEBAR (PARÂMETROS DE ENTRADA) ----------------
with st.sidebar:
    st.title("🌿 Parâmetros")
    nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura de Interesse:", ["Soja", "Milho", "Palma"], horizontal=True)
    
    # Meta de produtividade ajustada por cultura
    meta_padrao = 8.0 if cultura == "Milho" else (4.0 if cultura == "Soja" else 50.0)
    meta_ton = st.number_input("🎯 Meta de Produtividade (t/ha):", value=meta_padrao)

# ---------------- INTERFACE PRINCIPAL ----------------
st.title("SISTEMA DE PRESCRIÇÃO | FELIPE AMORIM")

# Aviso obrigatório sobre a origem dos resultados
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

# ---------------- LÓGICA DE CÁLCULO AGRONÔMICO ----------------
# 1. Calagem
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area

# 2. Gessagem
ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 
total_gesso = ng * area

# 3. Manejo de Nitrogênio (N) - Específico para Milho (Embrapa)
n_total_ha = meta_ton * 25 if cultura == "Milho" else 0
n_plantio_ha = n_total_ha * 0.20
n_cobertura_ha = n_total_ha * 0.80
total_n_plantio = n_plantio_ha * area
total_n_cobertura = n_cobertura_ha * area

# 4. Adubação NPK Comercial
st.subheader("Configuração da Fórmula Comercial (NPK)")
f1, f2, f3 = st.columns(3)
fn, fp, fk = f1.number_input("N % na Fórmula", 4), f2.number_input("P % na Fórmula", 20), f3.number_input("K % na Fórmula", 20)

# Cálculo simplificado de dose baseado em exportação/meta
dose_ha = max(((meta_ton * 15)/fp*100) if fp>0 else 0, ((meta_ton * 20)/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area

# ---------------- EXIBIÇÃO DE RESULTADOS ----------------
st.divider()
st.header("Resumo das Recomendações")

res1, res2, res3 = st.columns(3)
res1.metric("Calcário (t/ha)", f"{nc:.2f}")
st.write(f"**Total para a Área:** {total_calc:.2f} t")

res2.metric("Gesso (t/ha)", f"{ng:.2f}")
st.write(f"**Total para a Área:** {total_gesso:.2f} t")

res3.metric("Adubo Comercial (kg/ha)", f"{dose_ha:.0f}")
st.write(f"**Total para a Área:** {total_adubo:.1f} kg")

# Seção de Nitrogênio para Milho
if cultura == "Milho":
    st.divider()
    st.header("📊 Manejo Detalhado de Nitrogênio (N)")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.metric("N no Plantio (20%)", f"{n_plantio_ha:.1f} kg/ha")
        st.success(f"**Total de N Puro:** {total_n_plantio:.1f} kg")
    with col_n2:
        st.metric("N na Cobertura (80%)", f"{n_cobertura_ha:.1f} kg/ha")
        st.success(f"**Total de N Puro:** {total_n_cobertura:.1f} kg")

# ---------------- GERAÇÃO DO PDF PROFISSIONAL ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Banner Superior
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.ln(12)
    pdf.cell(190, 10, fix("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(190, 7, fix(f"Consultoria: Felipe Amorim | Data: {data_hoje}"), 0, 1, "C")
    
    # Aviso de Dados e Identificação
    pdf.set_text_color(0, 0, 0)
    pdf.ln(18)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(200, 0, 0) # Vermelho para o aviso
    pdf.cell(190, 8, fix("AVISO: Resultados baseados estritamente nos dados inseridos na calculadora."), 0, 1, "C")
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, fix("1. DADOS DO CLIENTE E PROPRIEDADE"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"Produtor: {nome_cliente} | Fazenda: {fazenda}"), 0, 1)
    pdf.cell(190, 7, fix(f"Local: {municipio} - {estado} | Area: {area:g} ha"), 0, 1)
    pdf.cell(190, 7, fix(f"Cultura: {cultura} | Meta de Produtividade: {meta_ton} t/ha"), 0, 1)

    # Recomendações de Solo
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("2. RECOMENDAÇÕES DE CORREÇÃO E ADUBAÇÃO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"- Calcario: {nc:.2f} t/ha (Total area: {total_calc:.2f} t)"), 0, 1)
    pdf.cell(190, 7, fix(f"- Gesso: {ng:.2f} t/ha (Total area: {total_gesso:.2f} t)"), 0, 1)
    pdf.cell(190, 7, fix(f"- Adubo Comercial: {dose_ha:.0f} kg/ha (Total area: {total_adubo:.1f} kg)"), 0, 1)

    # Seção Milho
    if cultura == "Milho":
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(190, 8, fix("3. MANEJO ESPECÍFICO DE NITROGÊNIO (N)"), 1, 1, "L", fill=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.ln(2)
        pdf.cell(190, 7, fix(f"- N no Plantio (20%): {n_plantio_ha:.1f} kg/ha (Total: {total_n_plantio:.1f} kg)"), 0, 1)
        pdf.cell(190, 7, fix(f"- N na Cobertura (80%): {n_cobertura_ha:.1f} kg/ha (Total: {total_n_cobertura:.1f} kg)"), 0, 1)

    # Seção Palma (Manejo solicitado)
    if cultura == "Palma":
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(210, 255, 210)
        pdf.cell(190, 8, fix("3. RECOMENDAÇÕES TÉCNICAS PARA PALMA"), 1, 1, "L", fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)
        pdf.multi_cell(190, 6, fix("- MANEJO DO CLADODIO: Nao realizar o corte no cladodio-mae. Ele deve ser preservado para garantir a longevidade e o rebrote do palmal.\n- PRIMEIRO CORTE: Deve ser realizado entre 18 a 24 meses apos o plantio, conforme o vigor das raquetes.\n- ALTURA DE CORTE: Respeitar a arquitetura da planta para evitar estresse hidrico e pragas."))

    # Referências Dinâmicas
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix(f"REFERÊNCIAS TÉCNICAS UTILIZADAS ({cultura.upper()})"), 0, 1)
    pdf.set_font("Helvetica", "I", 9)
    if cultura == "Milho":
        pdf.multi_cell(190, 5, fix("- EMBRAPA Milho e Sorgo: Recomendacoes para o uso de corretivos e fertilizantes.\n- EMBRAPA: Sistema de producao de Milho (Manejo de N em cobertura).\n- Manual de Adubacao e Calagem (Tabelas de extracao por meta de produtividade)."))
    elif cultura == "Soja":
        pdf.multi_cell(190, 5, fix("- SBCS: Manual de Calagem e Adubacao para a cultura da Soja.\n- EMBRAPA Soja: Tecnologias de producao de soja (Critérios de V% e P/K).\n- Manual de Recomendacoes de Adubacao para o Cerrado."))
    elif cultura == "Palma":
        pdf.multi_cell(190, 5, fix("- IPA (Instituto Agronomico de Pernambuco): Manual de Cultivo e Recomendacao de Adubacao para Palma Forrageira.\n- IPA: Instrucoes sobre o manejo de cortes e preservacao de cladodios.\n- Pesquisas Regionais: Manejo de variedades Sertania, Miuda e Orelha de Elefante."))

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix("Responsável Técnico: Felipe Amorim"), 0, 1, "R")
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO DE DOWNLOAD ----------------
st.divider()
if st.button("📄 GERAR RELATÓRIO PDF COMPLETO"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Clique aqui para Baixar o PDF", pdf_bytes, file_name=f"Prescricao_{cultura}_{nome_cliente}.pdf", mime="application/pdf")
