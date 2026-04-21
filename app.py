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
st.set_page_config(page_title="Felipe Amorim | Consultoria", layout="wide", page_icon="🌿")

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
div[data-testid="stMetric"] label { color: #9ca3af !important; }
div[data-testid="stMetric"] div { color: #f9fafb !important; font-size: 26px; font-weight: bold; }
.stButton>button {
    background-color: #28a745 !important;
    color: white !important;
    font-weight: bold;
    width: 100%;
}
.warning-box {
    background-color: #332701;
    border-left: 5px solid #ffc107;
    padding: 10px;
    border-radius: 8px;
    margin: 10px 0;
}
.success-box {
    background-color: #052e16;
    border-left: 5px solid #22c55e;
    padding: 10px;
    border-radius: 8px;
    margin: 10px 0;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNÇÕES AUXILIARES ----------------
def remover_acentos(texto):
    """Remove acentos para o PDF"""
    import unicodedata
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

def sugerir_ajustes(cultura, dose_ha, fn, fp, fk, n_necessario, p_necessario, k_necessario):
    """Sugere fontes específicas para completar ou reduzir nutrientes"""
    
    # Calcula o que o adubo fornece
    n_fornecido = dose_ha * (fn / 100)
    p_fornecido = dose_ha * (fp / 100)
    k_fornecido = dose_ha * (fk / 100)
    
    # Calcula saldos
    saldo_n = n_fornecido - n_necessario
    saldo_p = p_fornecido - p_necessario
    saldo_k = k_fornecido - k_necessario
    
    sugestoes = []
    fontes = {}
    
    # Ajustes para N
    if saldo_n < -1:  # tolerância de 1 kg/ha
        falta_n = abs(saldo_n)
        ureia = falta_n / 0.45
        sulfato = falta_n / 0.20
        nitrato = falta_n / 0.15
        sugestoes.append(f"⚠️ **NITROGÊNIO**: faltam {falta_n:.1f} kg/ha")
        fontes['n'] = {
            'falta': falta_n,
            'ureia': ureia,
            'sulfato_amonio': sulfato,
            'nitrato_calcio': nitrato
        }
    elif saldo_n > 5:
        sugestoes.append(f"⚠️ **NITROGÊNIO**: excesso de {saldo_n:.1f} kg/ha → reduzir dose ou usar fórmula com menos N")
    
    # Ajustes para P (fósforo)
    if saldo_p < -1:
        falta_p = abs(saldo_p)
        map = falta_p / 0.48  # MAP tem 48% P₂O₅
        super_simples = falta_p / 0.18
        super_triplo = falta_p / 0.41
        sugestoes.append(f"⚠️ **FÓSFORO**: faltam {falta_p:.1f} kg/ha")
        fontes['p'] = {
            'falta': falta_p,
            'map': map,
            'super_simples': super_simples,
            'super_triplo': super_triplo
        }
    elif saldo_p > 20:
        sugestoes.append(f"⚠️ **FÓSFORO**: excesso de {saldo_p:.1f} kg/ha → usar fórmula com menos P ou reduzir dose")
    
    # Ajustes para K (potássio)
    if saldo_k < -1:
        falta_k = abs(saldo_k)
        kcl = falta_k / 0.60  # KCl tem 60% K₂O
        k2so4 = falta_k / 0.50  # Sulfato de Potássio tem 50% K₂O
        sugestoes.append(f"⚠️ **POTÁSSIO**: faltam {falta_k:.1f} kg/ha")
        fontes['k'] = {
            'falta': falta_k,
            'kcl': kcl,
            'k2so4': k2so4
        }
    elif saldo_k > 20:
        sugestoes.append(f"⚠️ **POTÁSSIO**: excesso de {saldo_k:.1f} kg/ha → usar fórmula com menos K ou reduzir dose")
    
    return sugestoes, fontes, n_fornecido, p_fornecido, k_fornecido, saldo_n, saldo_p, saldo_k

# ---------------- SIDEBAR (ENTRADAS) ----------------
with st.sidebar:
    st.title("🌿 Configurações")
    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:")
    fazenda = st.text_input("🏠 Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma"], horizontal=True)

    variedade = ""
    if cultura == "Palma":
        variedade = st.selectbox("🌵 Variedade:", ["Miúda", "Orelha de Elefante"])
    
    # Meta ajustada por cultura
    if cultura == "Soja":
        default_meta = 4.0
    elif cultura == "Milho":
        default_meta = 6.0
    else:
        default_meta = 40.0  # Palma em t/ha de matéria verde
    
    meta_ton = st.number_input("🎯 Meta (t/ha):", min_value=0.1, value=default_meta, step=0.5, format="%.1f")

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- ANÁLISE DE SOLO ----------------
st.title("🌱 SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"👨‍🔬 Consultor: Felipe Amorim | 📅 Data: {data_hoje}")

st.subheader("🔬 Análise de Solo")
c1, c2, c3 = st.columns(3)
with c1:
    p_solo = st.number_input("Fósforo (mg/dm³)", min_value=0.0, value=8.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", min_value=0.0, value=0.15)
with c2:
    argila = st.number_input("Argila (%)", min_value=0.0, value=35.0)
    v_atual = st.number_input("V% Atual", min_value=0.0, max_value=100.0, value=40.0)
with c3:
    ctc_t = st.number_input("CTC (T)", min_value=0.0, value=3.25)
    prnt_calc = st.number_input("PRNT do Calcário (%)", min_value=50.0, max_value=110.0, value=85.0)
    
    # Alumínio para gessagem
    aluminio = st.number_input("Alumínio (cmolc/dm³)", min_value=0.0, value=0.0, step=0.1)

# ---------------- LÓGICA DE CÁLCULO (REFERÊNCIAS TÉCNICAS) ----------------
# 1. Calagem (SBCS): V alvo 70% para Soja/Palma e 60% para Milho
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area

# 2. Gessagem (Embrapa): Baseado no teor de argila e alumínio
if argila > 40 or aluminio > 0.5:
    ng = (50 * argila) / 1000
else:
    ng = 0
total_gesso = ng * area

# 3. Adubação NPK (IPNI/Embrapa - exportação por cultura)
if cultura == "Soja":
    rec_p = meta_ton * 18   # Soja extrai mais P
    rec_k = meta_ton * 22
elif cultura == "Milho":
    rec_p = meta_ton * 14
    rec_k = meta_ton * 18
else:  # Palma
    rec_p = meta_ton * 10   # Palma em t de matéria verde
    rec_k = meta_ton * 25   # Palma é exigente em K

# 4. Nitrogênio (N) - Recomendação por cultura
if cultura == "Milho":
    # Embrapa Milho e Sorgo: 25kg N por tonelada de grão
    rec_n = meta_ton * 25
    n_plantio = rec_n * 0.2
    n_cobertura = rec_n * 0.8
    n_plantio_total = n_plantio * area
    n_cobertura_total = n_cobertura * area
elif cultura == "Soja":
    # Soja: pequena dose no plantio + inoculação
    rec_n = 20  # kg/ha no plantio
    n_plantio = rec_n
    n_cobertura = 0
    n_plantio_total = n_plantio * area
    n_cobertura_total = 0
else:  # Palma
    # Palma: N via esterco + complemento mineral
    rec_n = meta_ton * 12
    n_plantio = rec_n * 0.6
    n_cobertura = rec_n * 0.4
    n_plantio_total = n_plantio * area
    n_cobertura_total = n_cobertura * area

# Formulação de Adubo
st.subheader("🧪 Configuração da Adubação")
f1, f2, f3 = st.columns(3)
fn = f1.number_input("N (%) na Fórmula", min_value=0.0, value=4.0, step=1.0)
fp = f2.number_input("P (%) na Fórmula", min_value=0.0, value=20.0, step=1.0)
fk = f3.number_input("K (%) na Fórmula", min_value=0.0, value=20.0, step=1.0)

# Validação da fórmula
if fp <= 0 or fk <= 0:
    st.error("❌ Os percentuais de P e K na fórmula devem ser maiores que 0!")
    st.stop()

# ---------------- CÁLCULO DA DOSE DE ADUBO (CORRIGIDO COM N) ----------------
# Dose baseada no N do plantio (se for milho)
if cultura == "Milho" and fn > 0:
    dose_ha_n = n_plantio / (fn / 100)
else:
    dose_ha_n = 0

# Dose baseada no P
dose_ha_p = rec_p / (fp / 100) if fp > 0 else 0

# Dose baseada no K
dose_ha_k = rec_k / (fk / 100) if fk > 0 else 0

# Pega a maior dose para não faltar nenhum nutriente
doses_validas = [d for d in [dose_ha_n, dose_ha_p, dose_ha_k] if d > 0]
if doses_validas:
    dose_ha = max(doses_validas)
else:
    st.error("❌ Não foi possível calcular a dose. Verifique os percentuais da fórmula.")
    st.stop()

total_adubo = dose_ha * area
sacos_50kg = math.ceil(total_adubo / 50)

# ---------------- ANÁLISE DE BALANÇO E SUGESTÕES ----------------
# Definir necessidades por cultura
if cultura == "Milho":
    n_necessario = n_plantio
    p_necessario = rec_p
    k_necessario = rec_k
elif cultura == "Soja":
    n_necessario = n_plantio
    p_necessario = rec_p
    k_necessario = rec_k
else:  # Palma
    n_necessario = n_plantio
    p_necessario = rec_p
    k_necessario = rec_k

sugestoes, fontes, n_fornecido, p_fornecido, k_fornecido, saldo_n, saldo_p, saldo_k = sugerir_ajustes(
    cultura, dose_ha, fn, fp, fk, 
    n_necessario, p_necessario, k_necessario
)

# ---------------- RESULTADOS NA CALCULADORA ----------------
st.subheader("📊 Resultados da Recomendação")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Calcário (t/ha)", f"{nc:.2f}")
    st.metric("Total Calcário (t)", f"{total_calc:.2f}")
with col2:
    st.metric("Gesso (t/ha)", f"{ng:.2f}")
    st.metric("Total Gesso (t)", f"{total_gesso:.2f}")
with col3:
    st.metric("Adubo (kg/ha)", f"{dose_ha:.0f}")
    st.metric("Total Adubo (kg)", f"{total_adubo:.1f}")
    st.metric("Sacos 50kg", f"{sacos_50kg}")

# Balanço de Nutrientes
st.divider()
st.subheader("⚖️ Balanço de Nutrientes do Adubo")

colb1, colb2, colb3 = st.columns(3)
with colb1:
    cor_n = "normal" if abs(saldo_n) <= 2 else "inverse"
    st.metric("N fornecido (kg/ha)", f"{n_fornecido:.1f}", 
              delta=f"{saldo_n:+.1f} do necessário", delta_color=cor_n)
with colb2:
    cor_p = "normal" if abs(saldo_p) <= 5 else "inverse"
    st.metric("P₂O₅ fornecido (kg/ha)", f"{p_fornecido:.1f}", 
              delta=f"{saldo_p:+.1f} do necessário", delta_color=cor_p)
with colb3:
    cor_k = "normal" if abs(saldo_k) <= 5 else "inverse"
    st.metric("K₂O fornecido (kg/ha)", f"{k_fornecido:.1f}", 
              delta=f"{saldo_k:+.1f} do necessário", delta_color=cor_k)

# Sugestões de ajuste
if sugestoes:
    st.subheader("🔧 Sugestões de Ajuste Nutricional")
    
    for s in sugestoes:
        st.markdown(f'<div class="warning-box">{s}</div>', unsafe_allow_html=True)
    
    # Detalhamento das fontes
    if 'n' in fontes:
        with st.expander("📌 Fontes para NITROGÊNIO"):
            f_n = fontes['n']
            st.write(f"**Faltam {f_n['falta']:.1f} kg/ha de N**")
            st.write(f"• Ureia (45% N): **{f_n['ureia']:.1f} kg/ha**")
            st.write(f"• Sulfato de Amônio (20% N): **{f_n['sulfato_amonio']:.1f} kg/ha**")
            st.write(f"• Nitrato de Cálcio (15% N): **{f_n['nitrato_calcio']:.1f} kg/ha**")
    
    if 'p' in fontes:
        with st.expander("📌 Fontes para FÓSFORO"):
            f_p = fontes['p']
            st.write(f"**Faltam {f_p['falta']:.1f} kg/ha de P₂O₅**")
            st.write(f"• MAP (48% P₂O₅): **{f_p['map']:.1f} kg/ha**")
            st.write(f"• Superfosfato Triplo (41% P₂O₅): **{f_p['super_triplo']:.1f} kg/ha**")
            st.write(f"• Superfosfato Simples (18% P₂O₅): **{f_p['super_simples']:.1f} kg/ha**")
    
    if 'k' in fontes:
        with st.expander("📌 Fontes para POTÁSSIO"):
            f_k = fontes['k']
            st.write(f"**Faltam {f_k['falta']:.1f} kg/ha de K₂O**")
            st.write(f"• KCl (60% K₂O): **{f_k['kcl']:.1f} kg/ha**")
            st.write(f"• Sulfato de Potássio (50% K₂O): **{f_k['k2so4']:.1f} kg/ha**")
    
else:
    st.markdown('<div class="success-box">✅ Fórmula equilibrada! Todos os nutrientes atendidos dentro da faixa ideal.</div>', unsafe_allow_html=True)

# Detalhamento de Nitrogênio específico
if cultura == "Milho":
    st.divider()
    st.subheader("📊 Manejo Nitrogenado (Milho)")
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.metric("N no Plantio (kg/ha)", f"{n_plantio:.1f}")
        st.metric("Total N Plantio (kg)", f"{n_plantio_total:.1f}")
        # Sugestão de ureia para plantio se necessário
        if saldo_n < -1:
            ureia_plantio = abs(saldo_n) / 0.45
            st.info(f"🌱 Completar N no plantio: **{ureia_plantio:.1f} kg/ha de Ureia**")
    
    with col_n2:
        st.metric("N em Cobertura (kg/ha)", f"{n_cobertura:.1f}")
        st.metric("Total N Cobertura (kg)", f"{n_cobertura_total:.1f}")
        # Sugestão de ureia para cobertura
        ureia_cobertura = n_cobertura / 0.45
        st.info(f"🌽 Cobertura recomendada: **{ureia_cobertura:.1f} kg/ha de Ureia** (estádio V4-V6)")

elif cultura == "Soja":
    st.divider()
    st.subheader("📊 Manejo de Nitrogênio (Soja)")
    st.info("🌱 **Inoculação obrigatória com Bradyrhizobium** - Dispensa N mineral, exceto pequena dose no plantio.")
    st.metric("N no Plantio (kg/ha)", f"{n_plantio:.1f}")

elif cultura == "Palma":
    st.divider()
    st.subheader("📊 Manejo da Palma Forrageira")
    st.info(f"🌵 **Variedade: {variedade}**")
    st.write("• Adubação orgânica: 20-30 t/ha de esterco curtido")
    st.write(f"• N mineral: {n_plantio:.1f} kg/ha no plantio + {n_cobertura:.1f} kg/ha em cobertura")

st.success(f"📦 **Logística:** Necessários {sacos_50kg} sacos de 50kg do adubo {fn:.0f}-{fp:.0f}-{fk:.0f}")

# ---------------- GERAÇÃO DO PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho banner
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.ln(10)
    pdf.cell(190, 10, remover_acentos("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(190, 5, remover_acentos(f"Consultor: Felipe Amorim | Data: {data_hoje}"), 0, 1, "C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)

    # Identificação
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(235, 245, 235)
    pdf.cell(190, 8, remover_acentos("1. IDENTIFICAÇÃO"), 0, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, remover_acentos(f"Cliente: {nome_cliente_input} | Fazenda: {fazenda}"), 0, 1)
    area_format = f"{area:g}"
    pdf.cell(190, 7, remover_acentos(f"Local: {municipio}-{estado} | Área: {area_format} ha | Cultura: {cultura}"), 0, 1)
    if cultura == "Palma":
        pdf.cell(190, 7, remover_acentos(f"Variedade: {variedade} | Meta: {meta_ton} t/ha"), 0, 1)
    else:
        pdf.cell(190, 7, remover_acentos(f"Meta: {meta_ton} t/ha"), 0, 1)

    # Correção de solo
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, remover_acentos("2. CORREÇÃO DO SOLO"), 0, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, remover_acentos(f"Calcário (PRNT {prnt_calc:.0f}%): {nc:.2f} t/ha | Total: {total_calc:.2f} t"), 0, 1)
    if ng > 0:
        pdf.cell(190, 7, remover_acentos(f"Gesso Agrícola: {ng:.2f} t/ha | Total: {total_gesso:.2f} t"), 0, 1)

    # Adubação
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, remover_acentos("3. ADUBAÇÃO MINERAL"), 0, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, remover_acentos(f"Adubo formulado: {fn:.0f}-{fp:.0f}-{fk:.0f}"), 0, 1)
    pdf.cell(190, 7, remover_acentos(f"Dose: {dose_ha:.0f} kg/ha | Total: {total_adubo:.1f} kg ({sacos_50kg} sacos 50kg)"), 0, 1)

    # Balanço de nutrientes
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 7, remover_acentos("Balanço de Nutrientes (kg/ha):"), 0, 1)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(190, 6, remover_acentos(f"N: necessário {n_necessario:.1f} | fornecido {n_fornecido:.1f} | saldo {saldo_n:+.1f}"), 0, 1)
    pdf.cell(190, 6, remover_acentos(f"P₂O₅: necessário {p_necessario:.1f} | fornecido {p_fornecido:.1f} | saldo {saldo_p:+.1f}"), 0, 1)
    pdf.cell(190, 6, remover_acentos(f"K₂O: necessário {k_necessario:.1f} | fornecido {k_fornecido:.1f} | saldo {saldo_k:+.1f}"), 0, 1)

    # Manejo Nitrogenado
    if cultura == "Milho":
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(190, 7, remover_acentos("Manejo de Nitrogênio (Milho):"), 0, 1)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(190, 6, remover_acentos(f"- N no Plantio: {n_plantio:.1f} kg/ha (Total: {n_plantio_total:.1f} kg)"), 0, 1)
        pdf.cell(190, 6, remover_acentos(f"- N em Cobertura: {n_cobertura:.1f} kg/ha (Total: {n_cobertura_total:.1f} kg)"), 0, 1)
        pdf.cell(190, 6, remover_acentos(f"- Ureia em cobertura: {n_cobertura/0.45:.1f} kg/ha (estágio V4-V6)"), 0, 1)
        
        if saldo_n < -1:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(190, 6, remover_acentos(f"⚠️ Completar N no plantio com {abs(saldo_n)/0.45:.1f} kg/ha de Ureia"), 0, 1)
            pdf.set_text_color(0, 0, 0)

    # Observações
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, remover_acentos("4. OBSERVAÇÕES E RECOMENDAÇÕES"), 0, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    
    if cultura == "Palma":
        pdf.multi_cell(190, 5, remover_acentos(f"- Variedade: {variedade}\n- Adubação Orgânica: 20-30 t/ha de esterco curtido.\n- Evitar excesso de N mineral para não queimar a planta.\n- Colheita a partir de 18-24 meses."))
    elif cultura == "Milho":
        pdf.multi_cell(190, 5, remover_acentos("- Realizar cobertura nitrogenada com solo úmido (estágio V4-V6).\n- Monitorar lagarta-do-cartucho e percevejo.\n- Em caso de veranico, parcelar a cobertura de N.\n- Aplicar ureia com inibidor de urease se possível."))
    else:
        pdf.multi_cell(190, 5, remover_acentos("- Inoculação obrigatória com Bradyrhizobium (estirpes aprovadas).\n- Co-inoculação com Azospirillum para maior eficiência.\n- Monitorar ferrugem asiática e percevejo marrom."))

    # Sugestões de fontes complementares
    if fontes:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 6, remover_acentos("Fontes complementares sugeridas:"), 0, 1)
        pdf.set_font("Helvetica", "", 9)
        
        if 'n' in fontes:
            f_n = fontes['n']
            pdf.cell(190, 5, remover_acentos(f"N: Ureia ({f_n['ureia']:.0f} kg/ha) ou Sulfato ({f_n['sulfato_amonio']:.0f} kg/ha)"), 0, 1)
        if 'p' in fontes:
            f_p = fontes['p']
            pdf.cell(190, 5, remover_acentos(f"P: MAP ({f_p['map']:.0f} kg/ha) ou Super Triplo ({f_p['super_triplo']:.0f} kg/ha)"), 0, 1)
        if 'k' in fontes:
            f_k = fontes['k']
            pdf.cell(190, 5, remover_acentos(f"K: KCl ({f_k['kcl']:.0f} kg/ha) ou Sulfato K ({f_k['k2so4']:.0f} kg/ha)"), 0, 1)

    # Referências
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(190, 5, remover_acentos("Referências técnicas: SBCS (2023), Embrapa Cerrados, Embrapa Milho e Sorgo, IPA/PE, IPNI Brasil."), 0, 1)
    pdf.cell(190, 5, remover_acentos(f"Documento gerado em {data_hoje} - Consultor Responsável: Felipe Amorim"), 0, 1)

    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ---------------- BOTÃO DOWNLOAD ----------------
st.divider()
if st.button("📄 Gerar Relatório Final", type="primary"):
    with st.spinner("Gerando PDF..."):
        pdf_bytes = gerar_pdf()
        st.download_button(
            label="⬇️ Baixar PDF da Prescrição", 
            data=pdf_bytes, 
            file_name=f"Prescricao_{nome_para_arquivo}_{datetime.now().strftime('%Y%m%d')}.pdf", 
            mime="application/pdf"
        )

# Rodapé informativo
st.divider()
st.caption(f"👨‍🔬 Sistema de Prescrição Agronômica | Felipe Amorim Consultoria | {data_hoje}")
