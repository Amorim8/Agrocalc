import streamlit as st

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide", page_icon="🌿")

# --- CABEÇALHO ---
st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor Responsável: Felipe Amorim")

# --- SIDEBAR: DADOS GERAIS ---
st.sidebar.header("📋 Configuração da Área")
talhao = st.sidebar.text_input("Identificação da Área:", "Área 01")
area_ha = st.sidebar.number_input("Tamanho da Área (Hectares):", value=1.0, min_value=0.01)
argila = st.sidebar.slider("Teor de Argila (%)", 0, 100, 40)

# --- 1. ENTRADA DA ANÁLISE DE SOLO ---
st.header("1. Dados da Análise de Solo")
col_an1, col_an2, col_an3, col_an4 = st.columns(4)

with col_an1:
    v_atual = st.number_input("V% Atual (da Análise)", value=0.0, step=1.0)
with col_an2:
    ctc = st.number_input("CTC (cmolc/dm³)", value=5.0, step=0.1)
with col_an3:
    p_solo = st.number_input("Fósforo (P) mg/dm³", value=0.0)
with col_an4:
    k_solo = st.number_input("Potássio (K) mg/dm³", value=0.0)

# --- 2. PLANEJAMENTO DA SAFRA ---
st.divider()
st.header("2. Planejamento da Safra")
cultura = st.selectbox("Selecione a Cultura Alvo:", ["Soja", "Milho"])

# Botões de Produtividade com Padrões Embrapa
st.write(f"Selecione a meta de produtividade para o {cultura}:")
c_btn1, c_btn2, c_btn3 = st.columns(3)

if c_btn1.button("📉 Baixa Produtividade"):
    meta_t = 5.0 if cultura == "Milho" else 2.5
elif c_btn2.button("📊 Média Produtividade"):
    meta_t = 9.0 if cultura == "Milho" else 3.8
elif c_btn3.button("🚀 Alta Produtividade"):
    meta_t = 13.0 if cultura == "Milho" else 5.5
else:
    # Valor padrão inicial caso nenhum botão seja clicado
    meta_t = 10.0 if cultura == "Milho" else 3.5

meta_final = st.number_input("Meta de Colheita Final (Toneladas/ha):", value=meta_t)

# --- LÓGICA DE RECOMENDAÇÃO (PADRÃO EMBRAPA) ---
v_alvo = 70 if cultura == "Soja" else 60

# Cálculos de Extração baseados na meta de produtividade
if cultura == "Milho":
    n_nec = meta_final * 22  # kg de N por tonelada
    p_nec = meta_final * 9   # kg de P2O5 por tonelada
    k_nec = meta_final * 18  # kg de K2O por tonelada
else: # Soja
    n_nec = 0  # Nitrogênio via inoculação
    p_nec = meta_final * 15
    k_nec = meta_final * 20

# --- 3. EXIBIÇÃO DAS RECOMENDAÇÕES ---
st.divider()
res1, res2 = st.columns(2)

with res1:
    st.subheader("🛠️ Recomendação de Calagem")
    prnt = st.number_input("PRNT do Calcário (%)", value=80.0)
    # NC (t/ha) = (V2 - V1) * CTC / PRNT
    nc = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual else 0
    
    if nc > 0:
        st.info(f"👉 Necessidade de Calagem: **{nc:.2f} t/ha**")
        st.write(f"Total para {area_ha} ha: **{nc * area_ha:.2f} Toneladas**")
    else:
        st.success("✅ Solo equilibrado. Calagem não necessária.")

with res2:
    st.subheader("🚜 Recomendação de Adubação")
    st.write(f"Para colher **{meta_final} t/ha**, a necessidade estimada é:")
    st.write(f"- **Nitrogênio (N):** {int(n_nec)} kg/ha")
    st.write(f"- **Fósforo (P₂O₅):** {int(p_nec)} kg/ha")
    st.write(f"- **Potássio (K₂O):** {int(k_nec)} kg/ha")
    if cultura == "Soja":
        st.caption("Nota: O Nitrogênio da soja deve ser suprido via inoculação (Bactérias).")

# --- 4. CÁLCULO PRÁTICO (TRANSFORMANDO EM SACOS) ---
st.divider()
st.header("3. Adubação Prática (Sacos)")
st.write("Insira a formulação do adubo disponível:")

col_f1, col_f2, col_f3 = st.columns(3)
fn = col_f1.number_input("N do Adubo (%)", value=5)
fp = col_f2.number_input("P₂O₅ do Adubo (%)", value=25)
fk = col_f3.number_input("K₂O do Adubo (%)", value=15)

if fp > 0:
    # Cálculo baseado no nutriente Fósforo (P)
    dose_ha = (p_nec / fp) * 100
    total_kg = dose_ha * area_ha
    total_sacos = total_kg / 50
    
    st.success(f"📦 Sugestão de aplicação: **{dose_ha:.1f} kg/ha** da formulação {fn}-{fp}-{fk}")
    st.metric(f"Total de Sacos para {area_ha} ha", f"{int(total_sacos)} un (50kg)")

st.divider()
st.caption("© 2026 | AgroCalc - Felipe Amorim | Dados baseados na Embrapa")
