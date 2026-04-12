import streamlit as st

# Configuração da Interface
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide")

st.title("🌱 Consultoria Agronômica Digital")
st.subheader("Responsável Técnico: Felipe Amorim")
st.markdown("---")

# --- 1. ENTRADA DE DADOS: A NATA DA ANÁLISE ---
st.header("1️⃣ Dados da Análise de Solo")
st.write("Insira os resultados laboratoriais abaixo:")

col_an1, col_an2, col_an3, col_an4 = st.columns(4)
with col_an1:
    v_atual = st.number_input("V% Atual (Saturação por Bases)", value=0.0, step=1.0)
with col_an2:
    ctc = st.number_input("CTC Total (pH 7,0)", value=5.0, step=0.1)
with col_an3:
    p_solo = st.number_input("Fósforo (P) mg/dm³", value=0.0)
with col_an4:
    k_solo = st.number_input("Potássio (K) mg/dm³", value=0.0)

argila = st.slider("Teor de Argila (%)", 0, 100, 40)

# --- 2. PLANEJAMENTO DA SAFRA (BOTÕES DE PRODUTIVIDADE) ---
st.divider()
st.header("2️⃣ Planejamento e Metas")
cultura = st.selectbox("Selecione a Cultura Alvo:", ["Soja", "Milho"])

st.write(f"Escolha sua meta de produtividade (Baseado na Embrapa):")
c_btn1, c_btn2, c_btn3 = st.columns(3)

if c_btn1.button("📉 Baixa Produtividade"):
    meta_t = 5.0 if cultura == "Milho" else 2.5
elif c_btn2.button("📊 Média Produtividade"):
    meta_t = 9.0 if cultura == "Milho" else 3.8
elif c_btn3.button("🚀 Alta Produtividade"):
    meta_t = 13.0 if cultura == "Milho" else 5.5
else:
    meta_t = 10.0 if cultura == "Milho" else 3.5

meta_final = st.number_input("Meta de Colheita Ajustada (t/ha):", value=meta_t)

# --- LÓGICA TÉCNICA (CONFORME MANUAIS ENVIADOS) ---
v_alvo = 70 if cultura == "Soja" else 60

if cultura == "Milho":
    n_nec = meta_final * 22  # Extração N
    p_nec = meta_final * 9   # Extração P2O5
    k_nec = meta_final * 18  # Extração K2O
else:
    n_nec = 0  # Inoculação
    p_nec = meta_final * 15
    k_nec = meta_final * 20

# --- 3. RECOMENDAÇÃO DE CALAGEM ---
st.divider()
st.header("3️⃣ Recomendação de Calagem")
col_c1, col_c2 = st.columns([1, 2])

with col_c1:
    prnt = st.number_input("PRNT do Calcário (%)", value=80.0)

# Cálculo NC = (V2 - V1) * CTC / PRNT
nc = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual else 0

with col_c2:
    if nc > 0:
        st.warning(f"💡 **Necessidade de Calagem:** {nc:.2f} toneladas por hectare.")
        st.write(f"Objetivo: Elevar a saturação de **{v_atual}%** para **{v_alvo}%**.")
    else:
        st.success("✅ O solo já apresenta saturação por bases adequada para esta cultura.")

# --- 4. RECOMENDAÇÃO DE ADUBAÇÃO ---
st.divider()
st.header("4️⃣ Recomendação de Adubação")
st.write(f"Para atingir a meta de **{meta_final} t/ha**, a planta precisa de:")

res_n, res_p, res_k = st.columns(3)
res_n.metric("Nitrogênio (N)", f"{int(n_nec)} kg/ha")
res_p.metric("Fósforo (P₂O₅)", f"{int(p_nec)} kg/ha")
res_k.metric("Potássio (K₂O)", f"{int(k_nec)} kg/ha")

# Dica técnica final
if cultura == "Soja":
    st.info("📢 **Nota Técnica:** Para a Soja, garanta uma boa inoculação de sementes para suprir o Nitrogênio.")
else:
    st.info("📢 **Nota Técnica:** No Milho, aplique 30kg de N no plantio e o restante em cobertura (V4-V6).")

# --- RODAPÉ ---
st.sidebar.markdown("---")
area_total = st.sidebar.number_input("Área Total da Lavoura (ha):", value=1.0)
st.sidebar.write(f"**Calcário Total:** {nc * area_total:.2f} Ton")

st.divider()
st.caption("© 2026 | AgroCalc - Felipe Amorim | Dados baseados na Embrapa")
