import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"

# Ajuste de Fuso Horário (Brasília -3h em relação ao UTC)
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- SISTEMA DE ACESSO (SENHA) ----------------
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

# ---------------- CONFIG E ESTILO DARK PREMIUM ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1a1c23 !important;
        border: 1px solid #2e3139;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745 !important;
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }
    /* Estilo para alerts e warnings */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
    }
    div[data-testid="stWarning"] {
        border-left-color: #ffc107;
    }
    div[data-testid="stError"] {
        border-left-color: #dc3545;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Configurações")
    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    talhao = st.text_input("📍 Talhão:", "")
    municipio = st.text_input("🏙️ Município:", "")
    estado = st.selectbox("🌎 Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    
    meta_ton = st.select_slider(
        "🎯 Meta de Produtividade (t/ha):", 
        options=[float(i/2) for i in range(2, 31)], 
        value=4.0 if cultura == "Soja" else 8.0
    )

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- CABEÇALHO ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Consultor:** Felipe Amorim | **Data:** {data_hoje}")

# ---------------- 1️⃣ ANÁLISE DE SOLO ----------------
st.subheader("1️⃣ Análise de Solo (Química e Física)")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
    ph_solo = st.number_input("pH do Solo", 0.0, 14.0, value=5.5)
with col2:
    argila = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.0)
    ca_solo = st.number_input("Cálcio (cmolc/dm³)", 0.0, value=1.5, help="Importante para cálculo mais preciso da gessagem")
with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
    prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)
    s_solo = st.number_input("Enxofre (mg/dm³)", 0.0, value=8.0, help="Importante para necessidade de gesso")

# ---------------- LÓGICA TÉCNICA ----------------
def interpretar_solo(p, k, arg):
    if arg > 35: lim_p = [3, 6, 9, 12]
    else: lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return "Argiloso" if arg > 35 else "Arenoso/Médio", niv_p, niv_k

classe_txt, nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)

v_alvo = 70 if cultura == "Soja" else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

# Gessagem com limite de segurança
m_atual = (al_solo / (al_solo + (ctc - al_solo))) * 100 if (al_solo + (ctc - al_solo)) > 0 else 0
ng_base = (argila * 50) / 1000 if (m_atual > 20 or al_solo > 0.5) else 0.0

sat_al = al_solo / ctc * 100 if ctc > 0 else 0

ng = ng_base
if ng_base > 0:
    if sat_al > 20:
        ng = min(ng_base, 2.0)
        if ng_base > 2.0:
            st.warning(f"⚠️ ATENCAO - Gessagem reduzida para seguranca: O calculo original indicava {ng_base:.2f} t/ha, mas devido a alta saturacao de aluminio ({sat_al:.1f}%), a dose foi limitada a 2.0 t/ha para evitar lixiviacao de nutrientes.")
    
    if ca_solo > 3.0:
        ng = min(ng, 1.5)
        st.info(f"ℹ️ Gessagem ajustada: Solo com bom teor de calcio ({ca_solo:.1f} cmolc/dm³). Dose reduzida para {ng:.2f} t/ha para evitar excesso.")

total_gesso = ng * area

# Recomendação de P e K com limite para solos com teores altos
n_plantio, n_cobertura = 0, 0
if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    
    if nivel_p == "Bom":
        rec_p = rec_p * 0.5
        st.info(f"ℹ️ Fosforo reduzido: Nivel atual de P e BOM ({p_solo} mg/dm³). Recomendacao ajustada para {rec_p:.0f} kg/ha de P2O5.")
    
    if nivel_k == "Bom":
        rec_k = rec_k * 0.5
        st.info(f"ℹ️ Potassio reduzido: Nivel atual de K e BOM ({k_solo} cmolc/dm³). Recomendacao ajustada para {rec_k:.0f} kg/ha de K2O.")
        
else:
    rec_n = meta_ton * 22
    n_plantio = 30
    n_cobertura = max(0.0, rec_n - n_plantio)
    rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
    
    if nivel_p == "Bom":
        rec_p = rec_p * 0.5
        st.info(f"ℹ️ Fosforo reduzido: Nivel atual de P e BOM ({p_solo} mg/dm³). Recomendacao ajustada para {rec_p:.0f} kg/ha de P2O5.")
    
    if nivel_k == "Bom":
        rec_k = rec_k * 0.5
        st.info(f"ℹ️ Potassio reduzido: Nivel atual de K e BOM ({k_solo} cmolc/dm³). Recomendacao ajustada para {rec_k:.0f} kg/ha de K2O.")

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Metas")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Textura Solo", classe_txt)
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Status P", nivel_p)
m4.metric("Status K", nivel_k)
m5.metric("Alumínio (m%)", f"{m_atual:.1f}%")

# ---------------- 3️⃣ PRESCRIÇÃO E ADUBO ----------------
st.write("---")
st.subheader("3️⃣ Planejamento de Fertilizantes e Corretivos")
r1, r2, r3 = st.columns([1, 1, 2])
with r1:
    st.markdown("### 🪨 Calagem")
    st.metric("Dose (t/ha)", f"{nc:.2f}")
    st.write(f"Total: **{total_calc:.2f} t**")
with r2:
    st.markdown("### ⚪ Gessagem")
    st.metric("Dose (t/ha)", f"{ng:.2f}")
    st.write(f"Total: **{total_gesso:.2f} t**")
    if ng_base > ng:
        st.caption(f"↪️ Calculo original: {ng_base:.2f} t/ha")
with r3:
    if cultura == "Milho":
        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Total N", f"{rec_n:.0f} kg")
        nc2.metric("Plantio", f"{n_plantio} kg")
        nc3.metric("Cobertura", f"{n_cobertura:.0f} kg")
    st.markdown("### 🛒 Formulação Comercial")
    cn, cp, ck = st.columns(3)
    f_n = cn.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
    f_p = cp.number_input("P%", 0, value=20)
    f_k = ck.number_input("K%", 0, value=20)
    if f_p > 0 or f_k > 0:
        dose_p = (rec_p / f_p * 100) if f_p > 0 else 0
        dose_k = (rec_k / f_k * 100) if f_k > 0 else 0
        dose_final = max(dose_p, dose_k)
        total_sacos = math.ceil((dose_final * area) / 50)
        
        if cultura == "Milho" and f_n > 0:
            n_fornecido = (dose_final * f_n) / 100
            if n_fornecido > n_plantio * 1.1:
                st.warning(f"⚠️ ATENCAO - NITROGENIO EXCESSIVO NO PLANTIO!\n\nO formulado {f_n}-{f_p}-{f_k} na dose de {dose_final:.0f} kg/ha fornece **{n_fornecido:.0f} kg/ha de N** no plantio, acima dos {n_plantio} kg/ha recomendados.\n\nSugestoes:\n• Reduza a dose do formulado e complemente com P/K separados\n• Troque para um formulado com menor teor de N (ex: 4-20-20)\n• Use ureia ou sulfato de amonio apenas em cobertura")
            elif n_fornecido > n_plantio:
                st.info(f"ℹ️ O formulado fornece {n_fornecido:.0f} kg/ha de N no plantio. Ajuste a adubacao de cobertura para {(rec_n - n_fornecido):.0f} kg/ha.")
        
        dose_max_recomendada = max(rec_p, rec_k) * 1.5 if (rec_p > 0 or rec_k > 0) else 500
        if dose_final > dose_max_recomendada and dose_max_recomendada > 0:
            st.error(f"⚠️ Dose muito elevada! A dose calculada ({dose_final:.0f} kg/ha) esta muito acima do necessario. Verifique os teores de P e K no solo ou ajuste a formulacao.")
        
        st.success(f"Dose: {dose_final:.0f} kg/ha | Total: {total_sacos} sacos")

# Checklist de seguranca (apenas texto, sem emojis)
st.divider()
st.subheader("✅ Checklist de Seguranca para Aplicacao")
col_check1, col_check2, col_check3 = st.columns(3)

with col_check1:
    st.markdown("**Calagem**")
    if nc > 5.0:
        st.error("[ATENCAO] Dose de calcario muito alta - parcelar aplicacao")
    elif nc > 3.0:
        st.warning("[CUIDADO] Dose alta - aplicar com antecedencia minima de 90 dias")
    else:
        st.success("[OK] Dose dentro do recomendado")

with col_check2:
    st.markdown("**Gessagem**")
    if ng > 2.0:
        st.error("[ATENCAO] Gessagem elevada - risco de lixiviacao de K e Mg")
    elif ng > 1.0:
        st.warning("[CUIDADO] Gessagem moderada - verificar necessidade de Ca e S")
    else:
        st.success("[OK] Dose segura")

with col_check3:
    st.markdown("**Nitrojenio (Milho)**")
    if cultura == "Milho":
        if n_cobertura > 120:
            st.warning("[CUIDADO] N em cobertura alto - parcelar em V4 e V6")
        else:
            st.success("[OK] N em cobertura adequado")
    else:
        st.info("Soja - fixacao biologica de N")

# ---------------- 4️⃣ PDF RELATÓRIO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix_txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    data_pdf = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')
    
    # Cabecalho
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 15, fix_txt("RELATORIO DE RECOMENDACAO TECNICA"), align="C", ln=True)
    pdf.set_font("Helvetica", "", 10); pdf.cell(190, 5, fix_txt(f"Consultor: Felipe Amorim | Data: {data_pdf}"), align="C", ln=True)
    
    # Dados Gerais
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 1. INFORMACOES GERAIS E DIAGNOSTICO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Cliente: {nome_cliente_input if nome_cliente_input else 'Nao informado'} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Cultura: {cultura} | Area: {area:.2f} ha | Meta: {meta_ton} t/ha"), ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(f" Status Solo: pH ({ph_solo}) | Aluminio ({al_solo}) | Textura ({classe_txt})"), ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 6, fix_txt(f" Fosforo: {p_solo} mg/dm³ ({nivel_p}) | Potassio: {k_solo} cmolc/dm³ ({nivel_k})"), ln=True)
    
    # Prescricao Tecnica
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 2. PRESCRICAO TECNICA"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Calagem: {nc:.2f} t/ha (Total para a area: {total_calc:.2f} t)"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Gessagem: {ng:.2f} t/ha (Total para a area: {total_gesso:.2f} t)"), ln=True)
    
    if ng_base > ng:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(190, 5, fix_txt(f"  *Observacao: Dose original calculada de {ng_base:.2f} t/ha foi ajustada para seguranca."), ln=True)
        pdf.set_text_color(0, 0, 0)
    
    if cultura == "Milho":
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 7, fix_txt(f" Recomendacao de Nitrogenio (N): Total {rec_n:.0f} kg/ha"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(190, 6, fix_txt(f"  - Aplicacao no Plantio: {n_plantio} kg/ha"), ln=True)
        pdf.cell(190, 6, fix_txt(f"  - Aplicacao em Cobertura (V4-V6): {n_cobertura:.0f} kg/ha"), ln=True)
    
    pdf.set_font("Helvetica", "B", 10); pdf.ln(2)
    d_p = (rec_p / f_p * 100) if f_p > 0 else 0
    d_k = (rec_k / f_k * 100) if f_k > 0 else 0
    d_final_pdf = max(d_p, d_k)
    t_sacos_pdf = math.ceil((d_final_pdf * area) / 50)
    
    pdf.cell(190, 7, fix_txt(f" Adubacao Sugerida: {d_final_pdf:.0f} kg/ha do formulado {f_n}-{f_p}-{f_k}"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Necessidade de Compra: {t_sacos_pdf} sacos (50kg) para a area total."), ln=True)
    
    # Recomendacao de nutrientes
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 6, fix_txt(" Recomendacao de Nutrientes:"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 5, fix_txt(f" P2O5 recomendado: {rec_p:.0f} kg/ha"), ln=False)
    pdf.cell(95, 5, fix_txt(f" K2O recomendado: {rec_k:.0f} kg/ha"), ln=True)

    # Checklist de seguranca no PDF (sem emojis, usando texto simples)
    pdf.ln(5)
    pdf.set_fill_color(255, 235, 200)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" CHECKLIST DE SEGURANCA PARA APLICACAO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    
    if cultura == "Milho":
        if n_cobertura > 120:
            pdf.cell(190, 5, fix_txt(" [CUIDADO] Nitrogenio em cobertura elevado - parcelar em V4 e V6"), ln=True)
        else:
            pdf.cell(190, 5, fix_txt(" [OK] Nitrogenio em cobertura dentro do recomendado"), ln=True)
    
    if ng > 2.0:
        pdf.cell(190, 5, fix_txt(" [ATENCAO] Gessagem elevada - risco de lixiviacao de K e Mg"), ln=True)
    elif ng > 0:
        pdf.cell(190, 5, fix_txt(" [OK] Gessagem dentro da faixa segura"), ln=True)
    
    if nc > 3.0:
        pdf.cell(190, 5, fix_txt(" [CUIDADO] Calagem alta - aplicar com antecedencia minima de 90 dias"), ln=True)
    elif nc > 0:
        pdf.cell(190, 5, fix_txt(" [OK] Calagem dentro do recomendado"), ln=True)
    
    # Verificacao adicional para P e K altos
    if nivel_p == "Bom" and rec_p > 0:
        pdf.cell(190, 5, fix_txt(" [INFO] Fosforo no solo ja esta BOM - adubacao reduzida pela metade"), ln=True)
    if nivel_k == "Bom" and rec_k > 0:
        pdf.cell(190, 5, fix_txt(" [INFO] Potassio no solo ja esta BOM - adubacao reduzida pela metade"), ln=True)

    # Nota de Responsabilidade
    pdf.ln(5); pdf.set_fill_color(255, 235, 235); pdf.set_font("Helvetica", "B", 9)
    pdf.cell(190, 7, fix_txt(" NOTA DE RESPONSABILIDADE TECNICA"), ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 8); pdf.set_text_color(100, 0, 0)
    pdf.multi_cell(190, 4, fix_txt("Esta recomendacao baseia-se exclusivamente nos dados fornecidos pelo usuario. O sucesso da cultura depende de fatores climaticos, fitossanitarios e do manejo correto no campo."))

    # Fontes
    pdf.ln(5); pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(34, 139, 34)
    pdf.cell(190, 8, fix_txt("FONTES E REFERENCIAS TECNICAS:"), ln=True)
    pdf.set_font("Helvetica", "I", 9); pdf.set_text_color(50, 50, 50)
    
    if cultura == "Soja":
        ref_texto = "- Interpretacao de Solo: Embrapa Soja.\n- Exportacao e Extracao: Manual de Adubacao e Calagem para o Estado do Parana (SBCS).\n- Calagem: Metodo da Elevacao da Saturaco por Bases (V%)."
    else:
        ref_texto = "- Interpretacao de Solo: Embrapa Milho e Sorgo.\n- Exportacao e Extracao: IPNI Brasil.\n- Calagem: Metodo da Elevacao da Saturaco por Bases (V%)."
        
    pdf.multi_cell(190, 5, fix_txt(ref_texto))
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
st.warning("⚠️ **Aviso:** Esta ferramenta é um auxílio à decisão. Sempre consulte um engenheiro agrônomo antes da aplicação.")
if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name=f"Relatorio_{nome_para_arquivo}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
