import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- SISTEMA DE ACESSO ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha para acessar o sistema:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# ---------------- ESTILO VISUAL ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6;
        padding: 15px;
        border-radius: 12px;
        border-left: 8px solid #28a745 !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #1a1c23 !important;
    }
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Ajustes de Campo")
    nome_cliente = st.text_input("👨‍🌾 Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    municipio = st.text_input("📍 Município:", "")
    estado = st.selectbox("🌎 Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    area_total = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01)
    
    st.divider()
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    var_palma = ""
    if cultura == "Palma Forrageira":
        var_palma = st.selectbox("🌵 Variedade:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

# ---------------- 1️⃣ ENTRADA DE DADOS ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Felipe Amorim** | Consultoria Agronômica")
st.write(f"Data de Emissão: {data_hoje}")

st.subheader("1️⃣ Dados da Análise de Solo")
col1, col2, col3 = st.columns(3)
with col1:
    p_s = st.number_input("Fósforo (P) - mg/dm³", 0.0, value=8.0)
    k_s = st.number_input("Potássio (K) - cmolc/dm³", 0.0, value=0.15)
    ph_s = st.number_input("pH em Água", 0.0, 14.0, value=5.5)
with col2:
    arg = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_at = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    al_s = st.number_input("Alumínio (Al)", 0.0, value=0.0)
with col3:
    ctc_s = st.number_input("CTC Total (T)", 0.0, value=3.25)
    prnt_s = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA DE ARGILA E CLASSIFICAÇÃO ----------------
if arg <= 15:
    classe_argila = "Arenosa"
    st_p = "Baixo" if p_s <= 20.0 else "Médio" if p_s <= 30.0 else "Alto"
elif arg <= 35:
    classe_argila = "Média"
    st_p = "Baixo" if p_s <= 12.0 else "Médio" if p_s <= 18.0 else "Alto"
elif arg <= 60:
    classe_argila = "Argilosa"
    st_p = "Baixo" if p_s <= 6.0 else "Médio" if p_s <= 9.0 else "Alto"
else:
    classe_argila = "Muito Argilosa"
    st_p = "Baixo" if p_s <= 4.0 else "Médio" if p_s <= 6.0 else "Alto"

st_k = "Baixo" if k_s <= 0.15 else "Médio" if k_s <= 0.30 else "Alto"

# ---------------- CÁLCULOS TÉCNICOS (MILHO COM N PARCELADO) ----------------
v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc_ha = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)
ng_ha = (arg * 50) / 1000 if (al_s > 0.5) else 0.0

n_plantio, n_cobertura = 0.0, 0.0

if cultura == "Soja":
    r_p, r_k = (meta_ton * 15), (meta_ton * 20)
elif cultura == "Milho":
    necessidade_n = meta_ton * 25 # kg de N por tonelada
    n_plantio = necessidade_n * 0.20 # 20% no plantio
    n_cobertura = necessidade_n * 0.80 # 80% em cobertura
    r_p, r_k = (meta_ton * 12), (meta_ton * 18)
else: # Palma Forrageira
    r_p = 100 * (1.5 if st_p == "Baixo" else 1.0)
    r_k = 180 * (1.5 if st_k == "Baixo" else 1.0)

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader(f"2️⃣ Diagnóstico e Corretivos ({area_total} ha)")
d1, d2, d3, d4 = st.columns(4)
d1.metric("Textura Solo", classe_argila)
d2.metric("Localidade", f"{municipio}-{estado}")
d3.metric("Status (P)", st_p)
d4.metric("Status (K)", st_k)

if cultura == "Milho":
    st.info(f"💡 **Sugestão de Nitrogênio (N):** {n_plantio:.0f} kg/ha no plantio e {n_cobertura:.0f} kg/ha em cobertura (V4 a V6).")

st.markdown("---")
c1, c2, g1, g2 = st.columns(4)
c1.metric("CALCÁRIO (t/ha)", f"{nc_ha:.2f}")
c2.metric("TOTAL CALCÁRIO (t)", f"{nc_ha * area_total:.2f}")
g1.metric("GESSO (t/ha)", f"{ng_ha:.2f}")
g2.metric("TOTAL GESSO (t)", f"{ng_ha * area_total:.2f}")

# ---------------- 3️⃣ ADUBAÇÃO COMERCIAL ----------------
st.write("---")
st.subheader("3️⃣ Planejamento de Adubação Comercial")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N%", 0, value=10 if cultura=="Palma Forrageira" else 0)
f_p = f2.number_input("P%", 0, value=10 if cultura=="Palma Forrageira" else 20)
f_k = f3.number_input("K%", 0, value=20)

if f_p > 0 or f_k > 0:
    dose_ha = max((r_p/f_p*100) if f_p>0 else 0, (r_k/f_k*100) if f_k>0 else 0)
    total_adubo_kg = dose_ha * area_total
    total_sacos = math.ceil(total_adubo_kg / 50)
    
    a1, a2, a3 = st.columns(3)
    a1.metric("DOSE (kg/ha)", f"{dose_ha:.0f}")
    a2.metric(f"TOTAL ({area_total} ha)", f"{total_adubo_kg:.0f} kg")
    a3.metric("COMPRA (SACOS)", f"{total_sacos}")

# ---------------- 4️⃣ PDF PERSONALIZADO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 15, fix("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 7, fix(f"Felipe Amorim | Consultoria Agronômica"), align="C", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, fix(f"Data: {data_hoje} | Localidade: {municipio} - {estado}"), align="C", ln=True)
    
    pdf.set_text_color(0, 0, 0); pdf.ln(15)
    
    # Seção 1: Diagnóstico
    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, fix(f" 1. IDENTIFICAÇÃO E DIAGNÓSTICO (TEXTURA: {classe_argila.upper()})"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, fix(f" Cliente: {nome_cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, fix(f" Cultura: {cultura} | Meta: {meta_ton} t/ha | Area Total: {area_total} ha"), ln=True)
    pdf.cell(190, 7, fix(f" Status Nutricional: Fosforo ({st_p}), Potassio ({st_k})"), ln=True)

    # Seção 2: Recomendações
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, fix(" 2. RECOMENDAÇÕES DE CORRETIVOS E ADUBAÇÃO"), ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, fix(f" > CALCÁRIO: {nc_ha:.2f} t/ha | TOTAL ÁREA: {nc_ha * area_total:.2f} t"), ln=True)
    pdf.cell(190, 8, fix(f" > GESSO: {ng_ha:.2f} t/ha | TOTAL ÁREA: {ng_ha * area_total:.2f} t"), ln=True)
    pdf.cell(190, 8, fix(f" > ADUBO ({f_n}-{f_p}-{f_k}): {dose_ha:.0f} kg/ha | TOTAL: {total_adubo_kg:.0f} kg"), ln=True)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(190, 8, fix(f" > NECESSIDADE DE COMPRA: {total_sacos} sacos de 50kg."), ln=True)
    pdf.set_text_color(0, 0, 0)

    # Seção 3: Manejo de Nitrogênio e Cultura
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, fix(" 3. MANEJO TÉCNICO E SUGESTÕES ESPECÍFICAS"), ln=True, fill=True)
    pdf.set_font("Arial", "I", 9); pdf.ln(2)
    pdf.multi_cell(190, 5, fix("Esta recomendação é EXCLUSIVA para os dados de solo e área informados. O sucesso da produção depende da correta execução das práticas culturais."))
    
    pdf.set_font("Arial", "", 10); pdf.ln(2)
    if cultura == "Milho":
        obs = [
            f"- PARCELAMENTO DE N: Aplicar {n_plantio:.1f} kg/ha de N no plantio.",
            f"- COBERTURA N: Aplicar {n_cobertura:.1f} kg/ha de N entre os estadios V4 e V6.",
            "- DISTRIBUIÇÃO: O parcelamento garante a disponibilidade de nitrogenio na fase de definicao do potencial produtivo.",
            "- MONITORAMENTO: Acompanhar presenca de cigarrinha e percevejo desde a emergencia.",
            "- UMIDADE: Aplicar adubação de cobertura preferencialmente com solo umido."
        ]
    elif cultura == "Palma Forrageira":
        obs = [
            f"- Variedade: {var_palma}.",
            "- ADUBAÇÃO ORGÂNICA: Aplicar 20-30 t/ha de esterco de curral bem curtido antes do plantio.",
            "- CORTE: PROIBIDO o corte na raquete mae para garantir a longevidade do palmal.",
            "- COBERTURA: Realizar o parcelamento de N e K durante o periodo chuvoso."
        ]
    else: # Soja
        obs = [
            "- INOCULAÇÃO: Inoculação e co-inoculação são essenciais para suprir o Nitrogenio via fixacao biologica.",
            "- PRAGAS: Monitorar percevejos e lagartas desde o inicio do desenvolvimento.",
            "- SEMEADURA: Garantir plantio em solo com umidade adequada."
        ]
    for item in obs: pdf.cell(190, 6, fix(item), ln=True)

    # Seção 4: Referências
    pdf.ln(8); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, fix(" 4. REFERÊNCIAS TÉCNICAS"), ln=True, fill=True)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(190, 5, fix("- Manual de Calagem e Adubação (Embrapa).\n- Boletins Técnicos Estaduais de Recomendação de Adubação.\n- Tabelas de Exigência Nutricional (Soja, Milho e Palma Forrageira)."))

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Recomendacao_{nome_cliente}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
