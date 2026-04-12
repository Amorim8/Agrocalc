import streamlit as st

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide", page_icon="🌿")

# --- CABEÇALHO ---
st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor Responsável: Felipe Amorim")

# --- SIDEBAR: DADOS GERAIS ---
st.sidebar.header("📋 Configuração da Área")
talhao = st.sidebar.text_input("Identificação da Área/Talhão:", "Área 01")
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

# Botões de Produtividade
st.write(f"Selecione a meta de produtividade para o {cultura}:")
c_btn1, c_btn2, c_btn3 = st.columns(3)

if c_btn1.button("📉 Baixa Produtividade"):
    meta_t = 5.0 if cultura == "Milho" else 2.5
elif c_btn2.button("📊 Média Produtividade"):
    meta_t = 9.0 if cultura == "Milho" else 3.8
elif c_btn3.button("🚀 Alta Produtividade"):
    meta_t = 13.0 if cultura == "Milho" else 5.5
else:
    meta_t = 10.0 if cultura == "Milho" else 3.5

meta_final = st.number_input("Meta de Colheita Final (Toneladas/ha):", value=meta_t)

# --- LÓGICA DE RECOMENDAÇÃO (PADRÃO EMBRAPA) ---
v_alvo = 70 if cultura == "Soja" else 60

# Extração e Exportação estimada por Tonelada produzida
if cultura == "Milho":
    n_nec = meta_final * 22
    p_nec = meta_final * 9
    k_nec = meta_final * 18
else: # Soja
    n_nec = 0 # Inoculação via bactérias
    p_nec = meta_final * 15
    k_nec = meta_final * 20

# --- 3. RECOMENDAÇÕES FINAIS ---
st.divider()
res1, res2 = st.columns(2)

with res1:
    st.subheader("🛠️ Recomendação de Calagem")
    prnt = st.number_input("PRNT do Calcário (%)", value=80.0)
    # Fórmula de Calagem: NC = (V2 - V1) * CTC / PRNT
    nc = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual else 0
    
    if nc > 0:
        st.info(f"👉 Necessidade de Calagem: **{nc:.2f} t/ha**")
        st.write(f"Total para {area_ha} ha: **{nc * area_ha:.2f} Toneladas**")
    else:
        st.success("✅ Solo equilibrado ou já corrigido. Calagem não necessária.")

with res2:
    st.subheader("🚜 Necessidade de Adubação")
    st.write(f"Para colher **{meta_final} t/ha**, a extração estimada é:")
    st.write(f"- **Nitrogênio (N):** {int(n_nec)} kg/ha")
    st.write(f"- **Fósforo (P₂O₅):** {int(p_nec)} kg/ha")
    st.write(f"- **Potássio (K₂O):** {int(k_nec)} kg/ha")
    if cultura == "Soja":
        st.caption("Nota: O N da soja deve ser suprido via inoculação.")

# --- 4. CÁLCULO PRÁTICO DO ADUBO COMERCIAL ---
st.divider()
st.header("3. Adubação Prática (Sacos)")
col_f1, col_f2, col_f3 = st.columns(3)
fn = col_f1.number_input("N do Adubo (%)", value=5)
fp = col_f2.number_input("P₂O₅ do Adubo (%)", value=25)
fk = col_f3.number_input("K₂O do Adubo (%)", value=15)

if fp > 0:
    # Dose baseada no Fósforo (geralmente o limitante no plantio)
    dose_ha = (p_nec / fp) * 100
    total_kg = dose_ha * area_ha
    total_sacos = total_kg / 50
    
    st.success(f"📦 Aplicar **{dose_ha:.1f} kg/ha** da formulação {fn}-{fp}-{fk}")
    st.metric(f"Total para {area_ha} ha", f"{int(total_sacos)} sacos de 5
