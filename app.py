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
    if arg > 35: 
        lim_p = [3, 6, 9, 12]
    else: 
        lim_p = [6, 12, 18, 30]
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
            st.warning(f"⚠️ ATENÇÃO - Gessagem reduzida para segurança: O cálculo original indicava {ng_base:.2f} t/ha, mas devido à alta saturação de alumínio ({sat_al:.1f}%), a dose foi limitada a 2.0 t/ha para evitar lixiviação de nutrientes.")
    
    if ca_solo > 3.0:
        ng = min(ng, 1.5)
        st.info(f"ℹ️ Gessagem ajustada: Solo com bom teor de cálcio ({ca_solo:.1f} cmolc/dm³). Dose reduzida para {ng:.2f} t/ha para evitar excesso.")

total_gesso = ng * area

# Recomendação de P e K com limite para solos com teores altos
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

# ---------------- PARCELAMENTO DO POTÁSSIO (MILHO) ----------------
# Limite seguro de K2O no plantio para solo argiloso
LIMITE_K2O_PLANTIO = 80  # kg/ha

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

# ---------------- FUNÇÃO PARA SUGERIR FONTES CONCENTRADAS COM PARCELAMENTO ----------------
def sugerir_fontes_concentradas(rec_p, rec_k, n_plantio, n_cobertura, area, cultura):
    """Sugere fontes comerciais concentradas com parcelamento do K"""
    
    if cultura == "Milho":
        k2o_plantio_sug = min(rec_k, LIMITE_K2O_PLANTIO)
        k2o_cobertura_sug = max(0, rec_k - k2o_plantio_sug)
    else:
        k2o_plantio_sug = rec_k
        k2o_cobertura_sug = 0
    
    # MAP (52% P2O5, 10% N) - Fonte de Fósforo
    map_kg = rec_p / 0.52 if rec_p > 0 else 0
    n_do_map = map_kg * 0.10
    
    # KCl plantio (60% K2O)
    kcl_plantio_kg = k2o_plantio_sug / 0.60 if k2o_plantio_sug > 0 else 0
    
    # KCl cobertura (60% K2O)
    kcl_cobertura_kg = k2o_cobertura_sug / 0.60 if k2o_cobertura_sug > 0 else 0
    
    # Ureia plantio (45% N) - complementa N
    n_faltante_plantio = max(0, n_plantio - n_do_map)
    ureia_plantio_kg = n_faltante_plantio / 0.45 if n_faltante_plantio > 0 else 0
    
    # Ureia cobertura (45% N) - para milho
    if cultura == "Milho":
        ureia_cobertura_kg = n_cobertura / 0.45 if n_cobertura > 0 else 0
    else:
        ureia_cobertura_kg = 0
    
    # Superfosfato Triplo (41% P2O5) - opção alternativa
    sft_kg = rec_p / 0.41 if rec_p > 0 else 0
    
    return {
        "MAP": map_kg,
        "SFT": sft_kg,
        "KCl_plantio": kcl_plantio_kg,
        "KCl_cobertura": kcl_cobertura_kg,
        "Ureia_plantio": ureia_plantio_kg,
        "Ureia_cobertura": ureia_cobertura_kg,
        "k2o_plantio": k2o_plantio_sug,
        "k2o_cobertura": k2o_cobertura_sug,
        "n_do_map": n_do_map
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
        
        # Exibe parcelamento do K
        if k2o_cobertura > 0:
            st.info(f"💡 **Parcelamento do Potássio:** {k2o_plantio:.0f} kg/ha de K2O no plantio + {k2o_cobertura:.0f} kg/ha de K2O em cobertura (V4-V6)")
        else:
            st.success(f"✅ Potássio: {k2o_plantio:.0f} kg/ha de K2O no plantio (dentro do limite seguro)")
    
    st.markdown("### 🛒 Formulação Comercial")
    st.caption("Digite a formulação do adubo que o cliente pretende usar (ex: 10-10-10, 04-14-08, 08-28-16)")
    cn, cp, ck = st.columns(3)
    f_n = cn.number_input("N%", 0, value=0 if cultura=="Soja" else 4)
    f_p = cp.number_input("P%", 0, value=20)
    f_k = ck.number_input("K%", 0, value=20)
    
    if f_p > 0 or f_k > 0:
        dose_p = (rec_p / f_p * 100) if f_p > 0 else 0
        dose_k = (k2o_plantio / f_k * 100) if f_k > 0 and k2o_plantio > 0 else 0
        dose_final = max(dose_p, dose_k)
        total_sacos = math.ceil((dose_final * area) / 50)
        
        # Verifica excesso de P
        p_fornecido = dose_final * f_p / 100
        if p_fornecido > rec_p * 1.2 and rec_p > 0:
            st.warning(f"⚠️ **EXCESSO DE FÓSFORO!** O formulado {f_n}-{f_p}-{f_k} fornece {p_fornecido:.0f} kg/ha de P2O5, mas a necessidade é de apenas {rec_p:.0f} kg/ha. Desperdício de {p_fornecido - rec_p:.0f} kg/ha.")
        
        # Exibe a recomendação original
        st.markdown("---")
        st.markdown("### 📋 RECOMENDAÇÃO ORIGINAL (conforme formulado escolhido)")
        
        if cultura == "Milho" and f_n > 0:
            n_fornecido = (dose_final * f_n) / 100
            if n_fornecido > n_plantio * 1.1:
                st.warning(f"⚠️ O formulado {f_n}-{f_p}-{f_k} fornece **{n_fornecido:.0f} kg/ha de N** no plantio, acima dos {n_plantio} kg/ha recomendados.")
            elif n_fornecido > n_plantio:
                st.info(f"ℹ️ O formulado fornece {n_fornecido:.0f} kg/ha de N no plantio. Ajuste a adubação de cobertura para {(rec_n - n_fornecido):.0f} kg/ha.")
        
        st.success(f"**Dose no plantio:** {dose_final:.0f} kg/ha | **Total de sacos (50kg):** {total_sacos} sacos para a área total")
        
        st.caption(f"""
        📊 **O que o formulado fornece no plantio:**
        - N: {dose_final * f_n / 100:.0f} kg/ha
        - P2O5: {dose_final * f_p / 100:.0f} kg/ha
        - K2O: {dose_final * f_k / 100:.0f} kg/ha
        """)
        
        # Sugestão de fontes concentradas com parcelamento
        st.markdown("---")
        st.markdown("### 💰 SUGESTÃO DE FONTES CONCENTRADAS (MAIS ECONÔMICAS E SEGURAS)")
        
        fontes = sugerir_fontes_concentradas(rec_p, rec_k, n_plantio, n_cobertura, area, cultura)
        
        st.markdown("**🌱 OPÇÃO 1: MAP + KCl + Ureia (Recomendada)**")
        
        col_op1a, col_op1b = st.columns(2)
        
        with col_op1a:
            st.markdown("**🌽 PLANTIO:**")
            if fontes["MAP"] > 0:
                st.write(f"📦 MAP (52% P2O5, 10% N): **{fontes['MAP']:.0f} kg/ha** ({math.ceil(fontes['MAP'] * area / 50)} sacos)")
                st.caption(f"  └─ Fornece: {fontes['n_do_map']:.0f} kg N + {rec_p:.0f} kg P2O5")
            if fontes["KCl_plantio"] > 0:
                st.write(f"📦 KCl (60% K2O): **{fontes['KCl_plantio']:.0f} kg/ha** ({math.ceil(fontes['KCl_plantio'] * area / 50)} sacos)")
                st.caption(f"  └─ Fornece: {fontes['k2o_plantio']:.0f} kg K2O (limite seguro)")
            if fontes["Ureia_plantio"] > 0:
                st.write(f"📦 Ureia (45% N): **{fontes['Ureia_plantio']:.0f} kg/ha** ({math.ceil(fontes['Ureia_plantio'] * area / 50)} sacos)")
                st.caption(f"  └─ Fornece: {fontes['Ureia_plantio'] * 0.45:.0f} kg N")
        
        with col_op1b:
            if cultura == "Milho" and (fontes["KCl_cobertura"] > 0 or fontes["Ureia_cobertura"] > 0):
                st.markdown("**🌿 COBERTURA (V4-V6):**")
                if fontes["KCl_cobertura"] > 0:
                    st.write(f"📦 KCl (60% K2O): **{fontes['KCl_cobertura']:.0f} kg/ha** ({math.ceil(fontes['KCl_cobertura'] * area / 50)} sacos)")
                    st.caption(f"  └─ Fornece: {fontes['k2o_cobertura']:.0f} kg K2O")
                if fontes["Ureia_cobertura"] > 0:
                    st.write(f"📦 Ureia (45% N): **{fontes['Ureia_cobertura']:.0f} kg/ha** ({math.ceil(fontes['Ureia_cobertura'] * area / 50)} sacos)")
                    st.caption(f"  └─ Fornece: {n_cobertura:.0f} kg N")
        
        total_sacos_op1 = math.ceil((fontes["MAP"] + fontes["KCl_plantio"] + fontes["Ureia_plantio"] + fontes["KCl_cobertura"] + fontes["Ureia_cobertura"]) * area / 50)
        st.success(f"💰 **Total de sacos Opção 1:** {total_sacos_op1} sacos")
        
        st.markdown("---")
        st.markdown("**🌽 OPÇÃO 2: Formulado 04-20-20 + Complementos**")
        
        col_op2a, col_op2b = st.columns(2)
        
        with col_op2a:
            dose_04_20_20 = max(rec_p / 0.20, k2o_plantio / 0.20) if rec_p > 0 or k2o_plantio > 0 else 0
            sacos_04_20_20 = math.ceil(dose_04_20_20 * area / 50)
            st.markdown("**🌽 PLANTIO:**")
            st.write(f"📦 04-20-20: **{dose_04_20_20:.0f} kg/ha** ({sacos_04_20_20} sacos)")
            st.caption(f"  └─ Fornece: {dose_04_20_20 * 0.04:.0f} kg N + {dose_04_20_20 * 0.20:.0f} kg P2O5 + {dose_04_20_20 * 0.20:.0f} kg K2O")
        
        with col_op2b:
            if cultura == "Milho" and (k2o_cobertura > 0 or n_cobertura > 0):
                st.markdown("**🌿 COBERTURA (V4-V6):**")
                if k2o_cobertura > 0:
                    kcl_extra = k2o_cobertura / 0.60
                    sacos_kcl_extra = math.ceil(kcl_extra * area / 50)
                    st.write(f"📦 KCl complementar: **{kcl_extra:.0f} kg/ha** ({sacos_kcl_extra} sacos)")
                    st.caption(f"  └─ Fornece: {k2o_cobertura:.0f} kg K2O")
                if n_cobertura > 0:
                    ureia_cobertura_op2 = n_cobertura / 0.45
                    sacos_ureia_op2 = math.ceil(ureia_cobertura_op2 * area / 50)
                    st.write(f"📦 Ureia: **{ureia_cobertura_op2:.0f} kg/ha** ({sacos_ureia_op2} sacos)")
                    st.caption(f"  └─ Fornece: {n_cobertura:.0f} kg N")
        
        total_sacos_op2 = sacos_04_20_20 + (sacos_kcl_extra if k2o_cobertura > 0 else 0) + (sacos_ureia_op2 if n_cobertura > 0 else 0)
        st.info(f"💰 **Total de sacos Opção 2:** {total_sacos_op2} sacos")
        
        # Comparativo de economia
        if total_sacos_op1 < total_sacos_op2:
            economia = total_sacos_op2 - total_sacos_op1
            st.success(f"💎 **ECONOMIA RECOMENDADA:** A Opção 1 economiza {economia} sacos ({(economia/total_sacos_op2)*100:.0f}% menos volume)!")
        elif total_sacos_op2 < total_sacos_op1:
            economia = total_sacos_op1 - total_sacos_op2
            st.info(f"💰 A Opção 2 economiza {economia} sacos ({(economia/total_sacos_op1)*100:.0f}% menos volume)")

# ---------------- CHECKLIST DE SEGURANÇA ----------------
st.divider()
st.subheader("✅ Checklist de Segurança para Aplicação")
col_check1, col_check2, col_check3 = st.columns(3)

with col_check1:
    st.markdown("**🪨 Calagem**")
    if nc > 5.0:
        st.error("[ATENÇÃO] Dose de calcário muito alta - parcelar aplicação")
    elif nc > 3.0:
        st.warning("[CUIDADO] Dose alta - aplicar com antecedência mínima de 90 dias")
    else:
        st.success("[OK] Dose dentro do recomendado")

with col_check2:
    st.markdown("**⚪ Gessagem**")
    if ng > 2.0:
        st.error("[ATENÇÃO] Gessagem elevada - risco de lixiviação de K e Mg")
    elif ng > 1.0:
        st.warning("[CUIDADO] Gessagem moderada - verificar necessidade de Ca e S")
    else:
        st.success("[OK] Dose segura")

with col_check3:
    if cultura == "Milho":
        st.markdown("**🌽 Nitrogênio (Milho)**")
        if n_cobertura > 120:
            st.warning("[CUIDADO] N em cobertura alto - parcelar em V4 e V6")
        else:
            st.success("[OK] N em cobertura adequado")
        
        if k2o_cobertura > 0:
            st.info(f"💡 Potássio parcelado: {k2o_plantio:.0f} kg/ha no plantio + {k2o_cobertura:.0f} kg/ha em cobertura")
        else:
            st.success(f"✅ Potássio: {k2o_plantio:.0f} kg/ha no plantio (dentro do limite)")
    else:
        st.markdown("**🌱 Nitrogênio (Soja)**")
        st.info("Soja - fixação biológica de N (não necessita adubação nitrogenada)")

# ---------------- 4️⃣ PDF RELATÓRIO ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix_txt(t): 
        t = t.replace('ç', 'ç')
        t = t.replace('ã', 'ã')
        t = t.replace('õ', 'õ')
        t = t.replace('á', 'á')
        t = t.replace('é', 'é')
        t = t.replace('í', 'í')
        t = t.replace('ó', 'ó')
        t = t.replace('ú', 'ú')
        t = t.replace('â', 'â')
        t = t.replace('ê', 'ê')
        t = t.replace('ô', 'ô')
        t = t.replace('à', 'à')
        t = t.replace('ç'.upper(), 'Ç')
        t = t.replace('ã'.upper(), 'Ã')
        t = t.replace('õ'.upper(), 'Õ')
        t = t.replace('á'.upper(), 'Á')
        t = t.replace('é'.upper(), 'É')
        t = t.replace('í'.upper(), 'Í')
        t = t.replace('ó'.upper(), 'Ó')
        t = t.replace('ú'.upper(), 'Ú')
        t = t.replace('â'.upper(), 'Â')
        t = t.replace('ê'.upper(), 'Ê')
        t = t.replace('ô'.upper(), 'Ô')
        return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    data_pdf = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 15, fix_txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 5, fix_txt(f"Consultor: Felipe Amorim | Data: {data_pdf}"), align="C", ln=True)
    
    # Dados Gerais
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 1. INFORMAÇÕES GERAIS E DIAGNÓSTICO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Cliente: {nome_cliente_input if nome_cliente_input else 'Não informado'} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Cultura: {cultura} | Área: {area:.2f} ha | Meta: {meta_ton} t/ha"), ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(f" Status Solo: pH ({ph_solo}) | Alumínio ({al_solo}) | Textura ({classe_txt})"), ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 6, fix_txt(f" Fósforo: {p_solo} mg/dm³ ({nivel_p}) | Potássio: {k_solo} cmolc/dm³ ({nivel_k})"), ln=True)
    
    # Prescrição Técnica
    pdf.ln(5)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 2. PRESCRIÇÃO TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Calagem: {nc:.2f} t/ha (Total para a área: {total_calc:.2f} t)"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Gessagem: {ng:.2f} t/ha (Total para a área: {total_gesso:.2f} t)"), ln=True)
    
    if ng_base > ng:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(190, 5, fix_txt(f"  *Observação: Dose original calculada de {ng_base:.2f} t/ha foi ajustada para segurança."), ln=True)
        pdf.set_text_color(0, 0, 0)
    
    if cultura == "Milho":
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 7, fix_txt(f" Recomendação de Nitrogênio (N): Total {rec_n:.0f} kg/ha"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(190, 6, fix_txt(f"  - Aplicação no Plantio: {n_plantio} kg/ha"), ln=True)
        pdf.cell(190, 6, fix_txt(f"  - Aplicação em Cobertura (V4-V6): {n_cobertura:.0f} kg/ha"), ln=True)
        
        # Parcelamento do K
        if k2o_cobertura > 0:
            pdf.cell(190, 6, fix_txt(f" Parcelamento do Potássio (K2O): {k2o_plantio:.0f} kg/ha no plantio + {k2o_cobertura:.0f} kg/ha em cobertura (V4-V6)"), ln=True)
        else:
            pdf.cell(190, 6, fix_txt(f" Potássio (K2O): {k2o_plantio:.0f} kg/ha no plantio (dentro do limite seguro)"), ln=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.ln(2)
    
    # Recomendação de nutrientes
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 6, fix_txt(" Recomendação de Nutrientes:"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 5, fix_txt(f" P2O5 recomendado: {rec_p:.0f} kg/ha"), ln=False)
    pdf.cell(95, 5, fix_txt(f" K2O recomendado: {rec_k:.0f} kg/ha"), ln=True)
    
    # Sugestão de fontes concentradas no PDF
    fontes = sugerir_fontes_concentradas(rec_p, rec_k, n_plantio, n_cobertura, area, cultura)
    
    pdf.ln(5)
    pdf.set_fill_color(200, 230, 200)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" SUGESTÃO DE FONTES CONCENTRADAS (MAIS ECONÔMICAS E SEGURAS)"), ln=True, fill=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 6, fix_txt(" Opção 1: MAP + KCl + Ureia (Recomendada)"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    
    pdf.cell(190, 5, fix_txt(" PLANTIO:"), ln=True)
    if fontes["MAP"] > 0:
        pdf.cell(190, 4, fix_txt(f"  - MAP (52% P2O5, 10% N): {fontes['MAP']:.0f} kg/ha ({math.ceil(fontes['MAP'] * area / 50)} sacos)"), ln=True)
        pdf.cell(190, 4, fix_txt(f"    Fornece: {fontes['n_do_map']:.0f} kg N + {rec_p:.0f} kg P2O5"), ln=True)
    if fontes["KCl_plantio"] > 0:
        pdf.cell(190, 4, fix_txt(f"  - KCl (60% K2O): {fontes['KCl_plantio']:.0f} kg/ha ({math.ceil(fontes['KCl_plantio'] * area / 50)} sacos)"), ln=True)
        pdf.cell(190, 4, fix_txt(f"    Fornece: {fontes['k2o_plantio']:.0f} kg K2O (limite seguro)"), ln=True)
    if fontes["Ureia_plantio"] > 0:
        pdf.cell(190, 4, fix_txt(f"  - Ureia (45% N): {fontes['Ureia_plantio']:.0f} kg/ha ({math.ceil(fontes['Ureia_plantio'] * area / 50)} sacos)"), ln=True)
        pdf.cell(190, 4, fix_txt(f"    Fornece: {fontes['Ureia_plantio'] * 0.45:.0f} kg N"), ln=True)
    
    if cultura == "Milho" and (fontes["KCl_cobertura"] > 0 or fontes["Ureia_cobertura"] > 0):
        pdf.cell(190, 5, fix_txt(" COBERTURA (V4-V6):"), ln=True)
        if fontes["KCl_cobertura"] > 0:
            pdf.cell(190, 4, fix_txt(f"  - KCl (60% K2O): {fontes['KCl_cobertura']:.0f} kg/ha ({math.ceil(fontes['KCl_cobertura'] * area / 50)} sacos)"), ln=True)
            pdf.cell(190, 4, fix_txt(f"    Fornece: {fontes['k2o_cobertura']:.0f} kg K2O"), ln=True)
        if fontes["Ureia_cobertura"] > 0:
            pdf.cell(190, 4, fix_txt(f"  - Ureia (45% N): {fontes['Ureia_cobertura']:.0f} kg/ha ({math.ceil(fontes['Ureia_cobertura'] * area / 50)} sacos)"), ln=True)
            pdf.cell(190, 4, fix_txt(f"    Fornece: {n_cobertura:.0f} kg N"), ln=True)
    
    total_sacos_op1 = math.ceil((fontes["MAP"] + fontes["KCl_plantio"] + fontes["Ureia_plantio"] + fontes["KCl_cobertura"] + fontes["Ureia_cobertura"]) * area / 50)
    pdf.cell(190, 5, fix_txt(f" Total de sacos Opção 1: {total_sacos_op1} sacos"), ln=True)
    
    # Opção 2
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 6, fix_txt(" Opção 2: Formulado 04-20-20 + Complementos"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    
    dose_04_20_20 = max(rec_p / 0.20, k2o_plantio / 0.20) if rec_p > 0 or k2o_plantio > 0 else 0
    sacos_04_20_20 = math.ceil(dose_04_20_20 * area / 50)
    pdf.cell(190, 4, fix_txt(f"  - 04-20-20 (plantio): {dose_04_20_20:.0f} kg/ha ({sacos_04_20_20} sacos)"), ln=True)
    pdf.cell(190, 4, fix_txt(f"    Fornece: {dose_04_20_20 * 0.04:.0f} kg N + {dose_04_20_20 * 0.20:.0f} kg P2O5 + {dose_04_20_20 * 0.20:.0f} kg K2O"), ln=True)
    
    if k2o_cobertura > 0:
        kcl_extra = k2o_cobertura / 0.60
        sacos_kcl_extra = math.ceil(kcl_extra * area / 50)
        pdf.cell(190, 4, fix_txt(f"  - KCl complementar (cobertura): {kcl_extra:.0f} kg/ha ({sacos_kcl_extra} sacos)"), ln=True)
        pdf.cell(190, 4, fix_txt(f"    Fornece: {k2o_cobertura:.0f} kg K2O"), ln=True)
    
    if n_cobertura > 0:
        ureia_cobertura_op2 = n_cobertura / 0.45
        sacos_ureia_op2 = math.ceil(ureia_cobertura_op2 * area / 50)
        pdf.cell(190, 4, fix_txt(f"  - Ureia (cobertura): {ureia_cobertura_op2:.0f} kg/ha ({sacos_ureia_op2} sacos)"), ln=True)
        pdf.cell(190, 4, fix_txt(f"    Fornece: {n_cobertura:.0f} kg N"), ln=True)
    
    total_sacos_op2 = sacos_04_20_20 + (sacos_kcl_extra if k2o_cobertura > 0 else 0) + (sacos_ureia_op2 if n_cobertura > 0 else 0)
    pdf.cell(190, 5, fix_txt(f" Total de sacos Opção 2: {total_sacos_op2} sacos"), ln=True)
    
    # Comparativo
    if total_sacos_op1 < total_sacos_op2:
        economia = total_sacos_op2 - total_sacos_op1
        pdf.cell(190, 5, fix_txt(f" ECONOMIA: A Opção 1 economiza {economia} sacos ({(economia/total_sacos_op2)*100:.0f}% menos volume)"), ln=True)
    
    # Checklist de segurança no PDF
    pdf.ln(5)
    pdf.set_fill_color(255, 235, 200)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(190, 7, fix_txt(" CHECKLIST DE SEGURANÇA PARA APLICAÇÃO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    
    if cultura == "Milho":
        if n_cobertura > 120:
            pdf.cell(190, 5, fix_txt(" [CUIDADO] Nitrogênio em cobertura elevado - parcelar em V4 e V6"), ln=True)
        else:
            pdf.cell(190, 5, fix_txt(" [OK] Nitrogênio em cobertura dentro do recomendado"), ln=True)
        
        if k2o_cobertura > 0:
            pdf.cell(190, 5, fix_txt(f" [INFO] Potássio parcelado: {k2o_plantio:.0f} kg/ha no plantio + {k2o_cobertura:.0f} kg/ha em cobertura (evita salinidade)"), ln=True)
    else:
        pdf.cell(190, 5, fix_txt(" [INFO] Soja - fixação biológica de N (não necessita adubação nitrogenada)"), ln=True)
    
    if ng > 2.0:
        pdf.cell(190, 5, fix_txt(" [ATENÇÃO] Gessagem elevada - risco de lixiviação de K e Mg"), ln=True)
    elif ng > 0:
        pdf.cell(190, 5, fix_txt(" [OK] Gessagem dentro da faixa segura"), ln=True)
    
    if nc > 3.0:
        pdf.cell(190, 5, fix_txt(" [CUIDADO] Calagem alta - aplicar com antecedência mínima de 90 dias"), ln=True)
    elif nc > 0:
        pdf.cell(190, 5, fix_txt(" [OK] Calagem dentro do recomendado"), ln=True)
    
    if nivel_p == "Bom" and rec_p > 0:
        pdf.cell(190, 5, fix_txt(" [INFO] Fósforo no solo já está BOM - adubação reduzida pela metade"), ln=True)
    if nivel_k == "Bom" and rec_k > 0:
        pdf.cell(190, 5, fix_txt(" [INFO] Potássio no solo já está BOM - adubação reduzida pela metade"), ln=True)

    # Nota de Responsabilidade
    pdf.ln(5)
    pdf.set_fill_color(255, 235, 235)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(190, 7, fix_txt(" NOTA DE RESPONSABILIDADE TÉCNICA"), ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 0, 0)
    pdf.multi_cell(190, 4, fix_txt("Esta recomendação baseia-se exclusivamente nos dados fornecidos pelo usuário. O sucesso da cultura depende de fatores climáticos, fitossanitários e do manejo correto no campo."))

    # Fontes
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(190, 8, fix_txt("FONTES E REFERÊNCIAS TÉCNICAS:"), ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(50, 50, 50)
    
    if cultura == "Soja":
        ref_texto = "- Interpretação de Solo: Embrapa Soja.\n- Exportação e Extração: Manual de Adubação e Calagem para o Estado do Paraná (SBCS).\n- Calagem: Método da Elevação da Saturação por Bases (V%)."
    else:
        ref_texto = "- Interpretação de Solo: Embrapa Milho e Sorgo.\n- Exportação e Extração: IPNI Brasil.\n- Calagem: Método da Elevação da Saturação por Bases (V%)."
        
    pdf.multi_cell(190, 5, fix_txt(ref_texto))
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO PARA GERAR PDF ----------------
st.divider()
st.warning("⚠️ **Aviso:** Esta ferramenta é um auxílio à decisão. Sempre consulte um engenheiro agrônomo antes da aplicação.")
if st.button("📄 GERAR RELATÓRIO PROFISSIONAL"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name=f"Relatorio_{nome_para_arquivo}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
