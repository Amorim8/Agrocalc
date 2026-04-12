import streamlit as st

# Configuração da Página
st.set_page_config(page_title="AgroCalc - Felipe Amorim", layout="wide", page_icon="🌱")

st.title("🌿 Consultoria Agronômica Digital")
st.subheader("Responsável Técnico: Felipe Amorim")
st.markdown("---")

# --- ETAPA 1: DADOS DA ANÁLISE DE SOLO ---
st.header("1️⃣ Análise de Solo")
st.write("Insira abaixo os dados extraídos do laudo do laboratório:")

col1, col2, col3, col4 = st.columns(4)
with col1:
    v_atual = st.number_input("V% Atual (%)", value=0.0, help="Saturação por bases atual")
with col2:
    ctc = st.number_input("CTC Total (pH 7,0)", value=5.0, step=0.1)
with col3:
    p_solo = st.number_input("Fósforo (P) mg/dm³", value=0.0)
with col4:
    k_solo = st.number_input("Potássio (K) mg/dm³", value=0.0)

argila = st.slider("Teor de Argila no solo (%)", 0, 100, 40)

# --- ETAPA 2: PLANEJAMENTO DA SAFRA ---
st.divider()
st.header("2️⃣ Planejamento e Metas")
cultura = st.selectbox("Selecione a Cultura Alvo:", ["Soja", "Milho"])

st.write(f"Defina a meta de produtividade (Padrões Embrapa):")
c_btn1, c_btn2, c_btn3 = st.columns(3)

if c_btn1.button("📉 Baixa Produtividade"):
    meta_t = 5.0 if cultura == "Milho" else 2.5
elif c_btn2.button("📊 Média Produtividade"):
    meta_t = 9.0 if cultura == "Milho" else 3.8
elif c_btn3.button("🚀 Alta Produtividade"):
    meta_t = 13.0 if cultura == "Milho" else 5.5
else:
    meta_t = 10.0 if cultura == "Milho" else 3.5

meta_final = st.number_input("Meta Final Ajustada (t/ha):", value=meta_t)

# --- CÁLCULOS TÉCNICOS (REFERÊNCIA EMBRAPA) ---
# V% Alvo
v_alvo = 70 if cultura == "Soja" else 60

# Extração de Nutrientes (Baseado nos PDFs enviados)
if cultura == "Milho":
    n_nec = meta_final * 22
    p_nec = meta_final * 9
    k_nec = meta_final * 18
else: # Soja
    n_nec = 0 # FBN - Inoculação
    p_nec = meta_final * 15
    k_nec = meta_final * 20

# --- ETAPA 3: RECOMENDAÇÃO DE CALAGEM ---
st.divider()
st.header("3️⃣ Recomendação de Calagem")
prnt = st.number_input("PRNT do Calcário disponível (%)", value=80.0)

# NC (t/ha) = (V2 - V1) * CTC / PRNT
nc = ((v_alvo - v_atual) * ctc) / prnt if v_alvo > v_atual else 0

if nc > 0:
    st.warning(f"**Necessidade de Calagem:** {nc:.2f} toneladas por hectare.")
    st.write(f"Objetivo: Elevar o V% de {v_atual}% para {v_alvo}%.")
else:
    st.success("✅ Calagem não necessária. O V% atual atende aos requisitos da Embrapa.")

# --- ETAPA 4: RECOMENDAÇÃO DE ADUBAÇÃO ---
st.divider()
st.header("4️⃣ Recomendação de Adubação")
st.write(f"Com base na meta de **{meta_final} t/ha**, a necessidade de nutrientes é:")

res_n, res_p, res_k = st.columns(3)
res_n.metric("Nitrogênio (N)", f"{int(n_nec)} kg/ha")
res_p.metric("Fósforo (P₂O₅)", f"{int(p_nec)} kg/ha")
res_k.metric("Potássio (K₂O)", f"{int(k_nec)} kg/ha")

if cultura == "Soja":
    st.info("💡 Para a Soja, o Nitrogênio deve ser fornecido via Inoculação.")

# --- FECHAMENTO ---
st.sidebar.markdown("---")
st.sidebar.write(f"**Área Total:** {
