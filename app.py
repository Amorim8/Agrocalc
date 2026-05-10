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
    div[data-testid="stInfo"] {
        border-left-color: #17a2b8;
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

# ---------------- 1️⃣ ANÁLISE DE SOLO (COMPLETA) ----------------
st.subheader("1️⃣ Análise de Solo (Química e Física Completa)")

st.markdown("### 📊 Parâmetros Principais")
col1, col2, col3 = st.columns(3)
with col1:
    p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
    ph_solo = st.number_input("pH do Solo", 0.0, 14.0, value=5.5)
    ca_solo = st.number_input("Cálcio (cmolc/dm³)", 0.0, value=1.5)
with col2:
    argila = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
    v_atual = st.number_input("V% Atual (Saturação por Bases)", 0.0, 100.0, value=40.0)
    al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.0)
    mg_solo = st.number_input("Magnésio (cmolc/dm³)", 0.0, value=0.5)
with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
    mo_solo = st.number_input("Matéria Orgânica (g/dm³)", 0.0, value=20.0)
    prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)
    s_solo = st.number_input("Enxofre (mg/dm³)", 0.0, value=8.0)

st.markdown("### 🔬 Micronutrientes (Opcional)")
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    zn_solo = st.number_input("Zinco (mg/dm³)", 0.0, value=1.5, help="Ideal: 1.5-3.0 mg/dm³")
with col_m2:
    b_solo = st.number_input("Boro (mg/dm³)", 0.0, value=0.5, help="Ideal: 0.5-1.0 mg/dm³")
with col_m3:
    cu_solo = st.number_input("Cobre (mg/dm³)", 0.0, value=1.0, help="Ideal: 1.0-2.0 mg/dm³")

# ---------------- LÓGICA TÉCNICA ----------------
def interpretar_solo(p, k, arg, mo):
    if arg > 35: 
        lim_p = [3, 6, 9, 12]
    else: 
        lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    niv_mo = "Baixo" if mo < 20 else "Médio" if mo < 40 else "Bom"
    return "Argiloso" if arg > 35 else "Arenoso/Médio", niv_p, niv_k, niv_mo

classe_txt, nivel_p, nivel_k, nivel_mo = interpretar_solo(p_solo, k_solo, argila, mo_solo)

# Interpretação de micronutrientes
def interpretar_micronutriente(valor, ideal_min, ideal_max, nome):
    if valor < ideal_min:
        return f"{nome}: Baixo ({valor}) - Recomenda aplicação"
    elif valor > ideal_max:
        return f"{nome}: Alto ({valor}) - Sem necessidade"
    else:
        return f"{nome}: Adequado ({valor})"

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
            st.warning(f"⚠️ ATENÇÃO - Gessagem reduzida para segurança: O cálculo original indicava {ng_base:.2f} t/ha, mas devido à alta saturação de alumínio ({sat_al:.1f}%), a dose foi limitada a 2.0 t/ha para evitar lixiviação de nutrientes.")
    
    if ca_solo > 3.0:
        ng = min(ng, 1.5)
        st.info(f"ℹ️ Gessagem ajustada: Solo com bom teor de cálcio ({ca_solo:.1f} cmolc/dm³). Dose reduzida para {ng:.2f} t/ha para evitar excesso.")

total_gesso = ng * area

# Recomendação de P e K
n_plantio, n_cobertura = 0, 0
if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
    
    if nivel_p == "Bom":
        rec_p = rec_p * 0.5
        st.info(f"ℹ️ Fósforo reduzido: Nível atual de P é BOM ({p_solo} mg/dm³). Recomendação ajustada para {rec_p:.0f} kg/ha de P2O5.")
    
    if nivel_k == "Bom":
        rec_k = rec_k * 0.5
        st.info(f"ℹ️ Potássio reduzido: Nível atual de K é BOM ({k_solo} cmolc/dm³). Recomendação ajustada para {rec_k:.0f} kg/ha de K2O.")
        
else:  # Milho
    rec_n = meta_ton * 22
    n_plantio = 30
    n_cobertura = max(0.0, rec_n - n_plantio)
    rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
    
    if nivel_p == "Bom":
        rec_p = rec_p * 0.5
        st.info(f"ℹ️ Fósforo reduzido: Nível atual de P é BOM ({p_solo} mg/dm³). Recomendação ajustada para {rec_p:.0f} kg/ha de P2O5.")
    
    if nivel_k == "Bom":
        rec_k = rec_k * 0.5
        st.info(f"ℹ️ Potássio reduzido: Nível atual de K é BOM ({k_solo} cmolc/dm³). Recomendação ajustada para {rec_k:.0f} kg/ha de K2O.")

# Parcelamento do Potássio
LIMITE_K2O_PLANTIO = 80
k2o_plantio = min(rec_k, LIMITE_K2O_PLANTIO) if cultura == "Milho" else rec_k
k2o_cobertura = max(0, rec_k - k2o_plantio) if cultura == "Milho" else 0

# ---------------- 2️⃣ DASHBOARD ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Metas")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Textura Solo", classe_txt)
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Status P", nivel_p)
m4.metric("Status K", nivel_k)
m5.metric("Alumínio (m%)", f"{m_atual:.1f}%")

# ---------------- FUNÇÃO PARA SUGERIR FONTES ----------------
def sugerir_fontes_concentradas(rec_p, rec_k, n_plantio, n_cobertura, area, cultura):
    if cultura == "Milho":
        k2o_plantio_sug = min(rec_k, LIMITE_K2O_PLANTIO)
        k2o_cobertura_sug = max(0, rec_k - k2o_plantio_sug)
    else:
        k2o_plantio_sug = rec_k
        k2o_cobertura_sug = 0
    
    map_kg = rec_p / 0.52 if rec_p > 0 else 0
    n_do_map = map_kg * 0.10
    
    kcl_plantio_kg = k2o_plantio_sug / 0.60 if k2o_plantio_sug > 0 else 0
    kcl_cobertura_kg = k2o_cobertura_sug / 0.60 if k2o_cobertura_sug > 0 else 0
    
    n_faltante_plantio = max(0, n_plantio - n_do_map)
    ureia_plantio_kg = n_faltante_plantio / 0.45 if n_faltante_plantio > 0 else 0
    
    if cultura == "Milho":
        ureia_cobertura_kg = n_cobertura / 0.45 if n_cobertura > 0 else 0
    else:
        ureia_cobertura_kg = 0
    
    return {
        "MAP": map_kg,
        "KCl_plantio": kcl_plantio_kg,
        "KCl_cobertura": kcl_cobertura_kg,
        "Ureia_plantio": ureia_plantio_kg,
        "Ureia_cobertura": ureia_cobertura_kg,
        "k2o_plantio": k2o_plantio_sug,
        "k2o_cobertura": k2o_cobertura_sug
    }

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
        st.caption(f"↪️ Cálculo original: {ng_base:.2f} t/ha")
with r3:
    if cultura == "Milho":
        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Total N", f"{rec_n:.0f} kg")
        nc2.metric("Plantio", f"{n_plantio} kg")
        nc3.metric("Cobertura", f"{n_cobertura:.0f} kg")
        
        if k2o_cobertura > 0:
            st.info(f"💡 **Parcelamento do Potássio:** {k2o_plantio:.0f} kg/ha de K2O no plantio + {k2o_cobertura:.0f} kg/ha de K2O em cobertura (V4-V6)")
    
    st.markdown("### 🛒 Formulação Comercial")
    cn, cp, ck = st.columns(3)
    f_n = cn.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
    f_p = cp.number_input("P%", 0, value=20)
    f_k = ck.number_input("K%", 0, value=20)
    
    if f_p > 0 or f_k > 0:
        dose_p = (rec_p / f_p * 100) if f_p > 0 else 0
        dose_k = (k2o_plantio / f_k * 100) if f_k > 0 and k2o_plantio > 0 else 0
        dose_final = max(dose_p, dose_k)
        total_sacos = math.ceil((dose_final * area) / 50)
        
        p_fornecido = dose_final * f_p / 100
        if p_fornecido > rec_p * 1.2 and rec_p > 0:
            st.warning(f"⚠️ **EXCESSO DE FÓSFORO!** Desperdício de {p_fornecido - rec_p:.0f} kg/ha.")
        
        fontes = sugerir_fontes_concentradas(rec_p, rec_k, n_plantio, n_cobertura, area, cultura)
        
        st.markdown("---")
        st.markdown("### 💰 SUGESTÃO DE FONTES CONCENTRADAS (MAIS ECONÔMICAS)")
        st.markdown("**🌱 OPÇÃO RECOMENDADA: MAP + KCl + Ureia**")
        
        col_op1a, col_op1b = st.columns(2)
        with col_op1a:
            st.markdown("**PLANTIO:**")
            if fontes["MAP"] > 0:
                st.write(f"📦 MAP: **{fontes['MAP']:.0f} kg/ha** ({math.ceil(fontes['MAP'] * area / 50)} sacos)")
            if fontes["KCl_plantio"] > 0:
                st.write(f"📦 KCl: **{fontes['KCl_plantio']:.0f} kg/ha** ({math.ceil(fontes['KCl_plantio'] * area / 50)} sacos)")
            if fontes["Ureia_plantio"] > 0 and cultura == "Milho":
                st.write(f"📦 Ureia: **{fontes['Ureia_plantio']:.0f} kg/ha** ({math.ceil(fontes['Ureia_plantio'] * area / 50)} sacos)")
        
        with col_op1b:
            if cultura == "Milho" and (fontes["KCl_cobertura"] > 0 or fontes["Ureia_cobertura"] > 0):
                st.markdown("**COBERTURA (V4-V6):**")
                if fontes["KCl_cobertura"] > 0:
                    st.write(f"📦 KCl: **{fontes['KCl_cobertura']:.0f} kg/ha** ({math.ceil(fontes['KCl_cobertura'] * area / 50)} sacos)")
                if fontes["Ureia_cobertura"] > 0:
                    st.write(f"📦 Ureia: **{fontes['Ureia_cobertura']:.0f} kg/ha** ({math.ceil(fontes['Ureia_cobertura'] * area / 50)} sacos)")

# ---------------- 4️⃣ PDF RELATÓRIO COMPLETO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix_txt(t): 
        t = t.replace('ç', 'ç').replace('ã', 'ã').replace('õ', 'õ')
        t = t.replace('á', 'á').replace('é', 'é').replace('í', 'í').replace('ó', 'ó').replace('ú', 'ú')
        t = t.replace('â', 'â').replace('ê', 'ê').replace('ô', 'ô').replace('à', 'à')
        t = t.replace('ç'.upper(), 'Ç').replace('ã'.upper(), 'Ã').replace('õ'.upper(), 'Õ')
        t = t.replace('á'.upper(), 'Á').replace('é'.upper(), 'É').replace('í'.upper(), 'Í')
        t = t.replace('ó'.upper(), 'Ó').replace('ú'.upper(), 'Ú')
        return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    data_pdf = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')
    fontes = sugerir_fontes_concentradas(rec_p, rec_k, n_plantio, n_cobertura, area, cultura)
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 15, fix_txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 5, fix_txt(f"Consultor: Felipe Amorim | Data: {data_pdf}"), align="C", ln=True)
    
    # INFORMAÇÕES GERAIS
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 1. INFORMAÇÕES GERAIS E DIAGNÓSTICO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Cliente: {nome_cliente_input if nome_cliente_input else 'Não informado'} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Cultura: {cultura} | Área: {area:.2f} ha | Meta: {meta_ton} t/ha"), ln=True)
    
    # ANÁLISE COMPLETA DO SOLO
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" Análise Completa do Solo:"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(190, 5, fix_txt(f" • pH: {ph_solo} | Alumínio: {al_solo} cmolc/dm³ | V%: {v_atual:.1f}% (Alvo: {v_alvo}%)"), ln=True)
    pdf.cell(190, 5, fix_txt(f" • CTC: {ctc:.2f} cmolc/dm³ | Matéria Orgânica: {mo_solo:.1f} g/dm³ ({nivel_mo})"), ln=True)
    pdf.cell(190, 5, fix_txt(f" • Cálcio: {ca_solo:.2f} cmolc/dm³ | Magnésio: {mg_solo:.2f} cmolc/dm³ | Enxofre: {s_solo:.1f} mg/dm³"), ln=True)
    pdf.cell(190, 5, fix_txt(f" • Fósforo: {p_solo} mg/dm³ ({nivel_p}) | Potássio: {k_solo} cmolc/dm³ ({nivel_k})"), ln=True)
    pdf.cell(190, 5, fix_txt(f" • Textura: {classe_txt} | Argila: {argila:.1f}%"), ln=True)
    
    # Micronutrientes
    pdf.cell(190, 5, fix_txt(f" • Zinco: {zn_solo:.1f} mg/dm³ | Boro: {b_solo:.1f} mg/dm³ | Cobre: {cu_solo:.1f} mg/dm³"), ln=True)
    
    # JUSTIFICATIVA TÉCNICA
    pdf.ln(5)
    pdf.set_fill_color(200, 230, 200)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" 2. JUSTIFICATIVA TÉCNICA DAS DOSES"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    
    if cultura == "Milho":
        pdf.multi_cell(190, 5, fix_txt(f" • Nitrogênio (N): Dose ajustada para meta produtiva de {meta_ton} t/ha. Adoção do parcelamento 30 kg/ha no plantio + {n_cobertura:.0f} kg/ha em cobertura visando maior eficiência e redução de perdas por lixiviação."))
        pdf.multi_cell(190, 5, fix_txt(f" • Fósforo (P2O5): Necessidade de {rec_p:.0f} kg/ha considerando nível {'baixo' if nivel_p=='Baixo' else 'médio' if nivel_p=='Médio' else 'bom'} do solo e fator de correção específico para a cultura."))
        pdf.multi_cell(190, 5, fix_txt(f" • Potássio (K2O): Parcelamento de {k2o_plantio:.0f} kg/ha no plantio e {k2o_cobertura:.0f} kg/ha em cobertura para reduzir risco de salinidade em solo {classe_txt.lower()} e melhorar aproveitamento."))
    else:
        pdf.multi_cell(190, 5, fix_txt(f" • Nitrogênio (N): Soja utiliza fixação biológica com Bradyrhizobium. Recomenda-se inoculação das sementes."))
        pdf.multi_cell(190, 5, fix_txt(f" • Fósforo (P2O5): Dose de {rec_p:.0f} kg/ha considerando nível {'baixo' if nivel_p=='Baixo' else 'médio' if nivel_p=='Médio' else 'bom'} do solo."))
        pdf.multi_cell(190, 5, fix_txt(f" • Potássio (K2O): Dose de {rec_k:.0f} kg/ha para reposição da exportação pela cultura."))
    
    # PRESCRIÇÃO TÉCNICA
    pdf.ln(5)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 3. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Calagem: {nc:.2f} t/ha (Total: {total_calc:.2f} t) - Método V%"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Gessagem: {ng:.2f} t/ha (Total: {total_gesso:.2f} t)"), ln=True)
    
    if cultura == "Milho":
        pdf.cell(190, 7, fix_txt(f" Nitrogênio (N): {rec_n:.0f} kg/ha (Plantio: {n_plantio} kg | Cobertura: {n_cobertura:.0f} kg)"), ln=True)
    
    pdf.cell(190, 7, fix_txt(f" P2O5: {rec_p:.0f} kg/ha | K2O: {rec_k:.0f} kg/ha"), ln=True)
    
    # SUGESTÃO DE FONTES
    pdf.ln(5)
    pdf.set_fill_color(200, 230, 200)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" 4. SUGESTÃO DE FONTES CONCENTRADAS (MAIS ECONÔMICAS)"), ln=True, fill=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 6, fix_txt(" Opção Recomendada: MAP + KCl + Ureia"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    
    pdf.cell(190, 5, fix_txt(" PLANTIO:"), ln=True)
    if fontes["MAP"] > 0:
        pdf.cell(190, 4, fix_txt(f"  • MAP (52% P2O5, 10% N): {fontes['MAP']:.0f} kg/ha ({math.ceil(fontes['MAP'] * area / 50)} sacos)"), ln=True)
    if fontes["KCl_plantio"] > 0:
        pdf.cell(190, 4, fix_txt(f"  • KCl (60% K2O): {fontes['KCl_plantio']:.0f} kg/ha ({math.ceil(fontes['KCl_plantio'] * area / 50)} sacos)"), ln=True)
    if fontes["Ureia_plantio"] > 0 and cultura == "Milho":
        pdf.cell(190, 4, fix_txt(f"  • Ureia (45% N): {fontes['Ureia_plantio']:.0f} kg/ha ({math.ceil(fontes['Ureia_plantio'] * area / 50)} sacos)"), ln=True)
    
    if cultura == "Milho" and (fontes["KCl_cobertura"] > 0 or fontes["Ureia_cobertura"] > 0):
        pdf.cell(190, 5, fix_txt(" COBERTURA (V4-V6):"), ln=True)
        if fontes["KCl_cobertura"] > 0:
            pdf.cell(190, 4, fix_txt(f"  • KCl: {fontes['KCl_cobertura']:.0f} kg/ha ({math.ceil(fontes['KCl_cobertura'] * area / 50)} sacos)"), ln=True)
        if fontes["Ureia_cobertura"] > 0:
            pdf.cell(190, 4, fix_txt(f"  • Ureia: {fontes['Ureia_cobertura']:.0f} kg/ha ({math.ceil(fontes['Ureia_cobertura'] * area / 50)} sacos)"), ln=True)
    
    # MICRONUTRIENTES
    pdf.ln(5)
    pdf.set_fill_color(230, 230, 250)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" 5. RECOMENDAÇÃO DE MICRONUTRIENTES"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    
    if cultura == "Milho":
        pdf.multi_cell(190, 5, fix_txt(" • Zinco (Zn): Alta exigência para milho. Recomenda-se monitoramento e aplicação de 3-5 kg/ha de Zn via sulfato de zinco se necessário."))
        pdf.multi_cell(190, 5, fix_txt(" • Boro (B): Importante para formação de grãos. Aplicação via foliar (0.5-1.0 kg/ha) no pré-florescimento."))
    else:
        pdf.multi_cell(190, 5, fix_txt(" • Zinco (Zn): Essencial para fixação de nitrogênio. Aplicar 2-3 kg/ha de Zn se nível estiver baixo."))
        pdf.multi_cell(190, 5, fix_txt(" • Boro (B): Crítico na floração. Recomenda-se 0.5-1.0 kg/ha via foliar no início do florescimento."))
    
    pdf.multi_cell(190, 5, fix_txt(" • Enxofre (S): Essencial para síntese de proteínas. Monitorar e aplicar 20-30 kg/ha de S se necessário."))
    
    # CRONOGRAMA OPERACIONAL
    pdf.ln(5)
    pdf.set_fill_color(255, 235, 200)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" 6. CRONOGRAMA OPERACIONAL SUGERIDO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    
    if cultura == "Milho":
        pdf.cell(190, 5, fix_txt(" 30-60 dias antes do plantio: Aplicação de calcário (incorporar 0-20cm)"), ln=True)
        pdf.cell(190, 5, fix_txt(" Plantio: MAP + KCl + Ureia (sulco de plantio)"), ln=True)
        pdf.cell(190, 5, fix_txt(" V4-V6 (30-40 dias): Cobertura nitrogenada + K restante"), ln=True)
        pdf.cell(190, 5, fix_txt(" VT-R1 (60-70 dias): Monitoramento nutricional e aplicação foliar de micronutrientes"), ln=True)
    else:
        pdf.cell(190, 5, fix_txt(" 30-60 dias antes do plantio: Aplicação de calcário (incorporar 0-20cm)"), ln=True)
        pdf.cell(190, 5, fix_txt(" Plantio: MAP + KCl (sulco de plantio) + inoculação das sementes"), ln=True)
        pdf.cell(190, 5, fix_txt(" R1 (início da floração): Aplicação foliar de Boro (0.5-1.0 kg/ha)"), ln=True)
    
    # MANEJO DE PERDAS
    pdf.ln(5)
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" 7. MANEJO DE PERDAS DE NITROGÊNIO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(190, 5, fix_txt(" • Ureia: Aplicar antes de chuva leve (5-15mm) ou incorporar ao solo para evitar perdas por volatilização."))
    pdf.multi_cell(190, 5, fix_txt(" • Parcelamento: Divisão da adubação nitrogenada reduz perdas e aumenta eficiência do fertilizante."))
    pdf.multi_cell(190, 5, fix_txt(" • Condições: Evitar aplicar em solo seco ou com temperatura muito alta (acima de 30°C)."))
    
    # RECOMENDAÇÕES COMPLEMENTARES
    pdf.ln(5)
    pdf.set_fill_color(255, 220, 220)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" 8. RECOMENDAÇÕES AGRONÔMICAS COMPLEMENTARES"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    
    recomendacoes = [
        "• Monitorar compactação do solo: Realizar teste de penetrômetro antes do plantio",
        "• Verificar emergência uniforme: Avaliar estande nos primeiros 15-20 dias",
        "• Atenção ao déficit hídrico: Especialmente no florescimento e enchimento de grãos",
        "• Evitar aplicação de fertilizantes em solo seco: Pode causar salinidade e queima",
        "• Realizar monitoramento fitossanitário: Pragas e doenças podem reduzir produtividade",
        "• Coleta de solo pós-safra: Avaliar eficiência da adubação e necessidade de correção"
    ]
    
    for rec in recomendacoes:
        pdf.cell(190, 5, fix_txt(rec), ln=True)
    
    # CHECKLIST DE SEGURANÇA
    pdf.ln(5)
    pdf.set_fill_color(255, 235, 200)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" 9. CHECKLIST DE SEGURANÇA PARA APLICAÇÃO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    
    if cultura == "Milho":
        if n_cobertura > 120:
            pdf.cell(190, 5, fix_txt(" [CUIDADO] Nitrogênio em cobertura elevado - parcelar em V4 e V6"), ln=True)
        else:
            pdf.cell(190, 5, fix_txt(" [OK] Nitrogênio em cobertura dentro do recomendado"), ln=True)
        
        if k2o_cobertura > 0:
            pdf.cell(190, 5, fix_txt(f" [INFO] Potássio parcelado: {k2o_plantio:.0f} kg/ha no plantio + {k2o_cobertura:.0f} kg/ha em cobertura"), ln=True)
    else:
        pdf.cell(190, 5, fix_txt(" [INFO] Soja - fixação biológica de N (inoculação obrigatória)"), ln=True)
    
    if ng > 0:
        pdf.cell(190, 5, fix_txt(" [OK] Gessagem dentro da faixa segura" if ng <= 2.0 else " [ATENÇÃO] Gessagem elevada - risco de lixiviação"), ln=True)
    
    if nivel_p == "Bom" and rec_p > 0:
        pdf.cell(190, 5, fix_txt(" [INFO] Fósforo no solo já está BOM - adubação reduzida pela metade"), ln=True)
    
    pdf.cell(190, 5, fix_txt(" [INFO] Evite aplicação em solo seco ou temperaturas elevadas"), ln=True)
    
    # NOTA DE RESPONSABILIDADE
    pdf.ln(5)
    pdf.set_fill_color(255, 235, 235)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(190, 7, fix_txt(" NOTA DE RESPONSABILIDADE TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 0, 0)
    pdf.multi_cell(190, 4, fix_txt("Esta recomendação baseia-se exclusivamente nos dados fornecidos pelo usuário. O sucesso da cultura depende de fatores climáticos, fitossanitários e do manejo correto no campo."))
    
    # FONTES
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(190, 8, fix_txt("FONTES E REFERÊNCIAS TÉCNICAS:"), ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(50, 50, 50)
    
    if cultura == "Soja":
        ref_texto = "- Interpretação de Solo: Embrapa Soja.\n- Exportação e Extração: Manual de Adubação e Calagem para o Estado do Paraná (SBCS).\n- Calagem: Método da Elevação da Saturação por Bases (V%).\n- Micronutrientes: IPNI Brasil.\n- Manejo de Perdas: Embrapa Milho e Sorgo."
    else:
        ref_texto = "- Interpretação de Solo: Embrapa Milho e Sorgo.\n- Exportação e Extração: IPNI Brasil.\n- Calagem: Método da Elevação da Saturação por Bases (V%).\n- Micronutrientes: IPNI Brasil.\n- Manejo de Perdas: Embrapa Milho e Sorgo."
    
    pdf.multi_cell(190, 5, fix_txt(ref_texto))
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO ----------------
st.divider()
st.warning("⚠️ **Aviso:** Esta ferramenta é um auxílio à decisão. Sempre consulte um engenheiro agrônomo antes da aplicação.")
if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name=f"Relatorio_{nome_para_arquivo}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
