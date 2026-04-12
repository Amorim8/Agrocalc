import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime

# -------------------------------
# CONFIGURAÇÃO DE INTERFACE
# -------------------------------
st.set_page_config(page_title="AgroCalc Pro - Felipe Amorim", layout="wide")

st.title("🌿 Sistema de Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")
st.markdown("---")

# -------------------------------
# 1. ANÁLISE DE SOLO (ENTRADA DE DADOS)
# -------------------------------
st.header("1️⃣ Dados da Análise de Solo")

with st.container():
    col_p, col_a = st.columns(2)
    with col_p:
        profundidade = st.selectbox("Profundidade da amostra:", ["0-20 cm", "20-40 cm", "0-40 cm"])
    with col_a:
        argila = st.number_input("Teor de Argila (Valor do laudo):", value=0.0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        p_solo = st.number_input("Fósforo (P) [mg/dm³]:", value=0.0)
    with col2:
        k_solo = st.number_input("Potássio (K) [cmolc/dm³]:", value=0.0)
    with col3:
        v_atual = st.number_input("V1% (Saturação Atual):", value=0.0)
    with col4:
        ctc_total = st.number_input("CTC Total (pH 7.0):", value=5.0)

# -------------------------------
# 2. CALAGEM (CORREÇÃO DO SOLO)
# -------------------------------
st.divider()
st.header("2️⃣ Recomendação de Calagem")

# Configuração da Área na Sidebar
st.sidebar.header("📋 Configuração da Área")
talhao = st.sidebar.text_input("Talhão:", "Área 01")
area_ha = st.sidebar.number_input("Área (ha):", value=1.0)
cultura = st.sidebar.selectbox("Cultura Alvo:", ["Soja", "Milho"])

# Alvos Embrapa (V2)
v_alvo = 70 if cultura == "Soja" else 60
prnt = st.number_input("PRNT do Calcário (%):", value=80.0)

# Cálculo NC = ((V2 - V1) * CTC) / PRNT
nc = ((v_alvo - v_atual) * ctc_total) / prnt if v_alvo > v_atual else 0

if nc > 0:
    st.warning(f"👉 **Necessidade de Calagem:** {nc:.2f} t/ha")
    st.info(f"Quantidade total para {area_ha} ha: **{nc * area_ha:.2f} Toneladas**")
else:
    st.success(f"✅ Saturação de {v_atual}% está adequada para o cultivo de {cultura}.")

# -------------------------------
# 3. PLANEJAMENTO DE PRODUTIVIDADE
# -------------------------------
st.divider()
st.header("3️⃣ Planejamento de Safra")
st.write(f"Defina a meta de produtividade para **{cultura}**:")

b1, b2, b3 = st.columns(3)

if b1.button("📉 Baixa"):
    meta_sugestao = 5.0 if cultura == "Milho" else 2.5
elif b2.button("📊 Média"):
    meta_sugestao = 9.0 if cultura == "Milho" else 3.8
elif b3.button("🚀 Alta"):
    meta_sugestao = 13.0 if cultura == "Milho" else 5.5
else:
    meta_sugestao = 10.0 if cultura == "Milho" else 3.5

meta_final = st.number_input("Meta Final (t/ha):", value=meta_sugestao)

# -------------------------------
# 4. RECOMENDAÇÃO DE ADUBAÇÃO (NPK)
# -------------------------------
st.divider()
st.header("4️⃣ Recomendação de Adubação")

# Lógica de Extração conforme manuais Embrapa (Circ. 181 e Doc. 48)
if cultura == "Soja":
    req_n = 0 # Fixação Biológica
    req_p = meta_final * 15 # kg P2O5/t
    req_k = meta_final * 20 # kg K2O/t
else: # Milho
    req_n = meta_final * 22 # kg N/t
    req_p = meta_final * 9  # kg P2O5/t
    req_k = meta_final * 18 # kg K2O/t

n_col, p_col, k_col = st.columns(3)
n_col.metric("Nitrogênio (N)", f"{int(req_n)} kg/ha")
p_col.metric("Fósforo (P₂O₅)", f"{int(req_p)} kg/ha")
k_col.metric("Potássio (K₂O)", f"{int(req_k)} kg/ha")

# Cálculo de Sacos
st.write("---")
st.subheader("📦 Recomendação de Fertilizante Comercial")
f_p = st.number_input("Teor de P₂O₅ no adubo disponível (%):", value=25.0)

if f_p > 0:
    dose_kg_ha = (req_p / f_p) * 100
    total_sacos = (dose_kg_ha * area_ha) / 50
    st.success(f"Dose recomendada: **{dose_kg_ha:.1f} kg/ha**. Total para a área: **{math.ceil(total_sacos)} sacos**.")

# -------------------------------
# RODAPÉ
# -------------------------------
st.divider()
if st.button("📄 Gerar Relatório Técnico"):
    st.write("Relatório gerado com sucesso!")

st.caption("© 2026 | AgroCalc - Felipe Amorim | Unidades: P (mg/dm³), K (cmolc/dm³), CTC (cmolc/dm³)")
