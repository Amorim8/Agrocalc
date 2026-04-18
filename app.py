import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

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

# ---------------- SIDEBAR (LOCALIZAÇÃO APENAS AQUI) ----------------
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

st.subheader("1️⃣ Dados da Análise de Solo")
col1, col2, col3 = st.columns(3)
with col1:
    p_s = st.number_input("Fósforo (P) - mg/dm³", 0.0, value=12.9)
    k_s = st.number_input("Potássio (K) - cmolc/dm³", 0.0, value=0.10)
    ph_s = st.number_input("pH em Água", 0.0, 14.0, value=5.5)
with col2:
    arg = st.number_input("Argila (%)", 0.0, 100.0, value=40.0)
    v_at = st.number_input("V% Atual", 0.0, 100.0, value=40.0)
    al_s = st.number_input("Alumínio (Al)", 0.0, value=0.0)
with col3:
    ctc_s = st.number_input("CTC Total (T)", 0.0, value=3.25)
    prnt_s = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA DE STATUS E FAIXAS ----------------
if arg > 60:
    classe_txt = "Argilosa (>60%)"
    st_p = "Baixo" if p_s < 4.0 else "Médio" if p_s < 9.0 else "Alto"
    r_p_base = 100 if p_s < 4.0 else 60 if p_s < 9.0 else 30
elif 35 < arg <= 60:
    classe_txt = "Argilosa (35-60%)"
    st_p = "Baixo" if p_s < 6.0 else "Médio" if p_s < 12.0 else "Alto"
    r_p_base = 90 if p_s < 6.0 else 50 if p_s < 12.0 else 25
elif 15 < arg <= 35:
    classe_txt = "Média (15-35%)"
    st_p = "Baixo" if p_s < 10.0 else "Médio" if p_s < 20.0 else "Alto"
    r_p_base = 80 if p_s < 10.0 else 40 if p_s < 20.0 else 20
else:
    classe_txt = "Arenosa (<15%)"
    st_p = "Baixo" if p_s < 15.0 else "Médio" if p_s < 30.0 else "Alto"
    r_p_base = 60 if p_s < 15.0 else 30 if p_s < 30.0 else 15

st_k = "Baixo" if k_s < 0.15 else "Médio" if k_s < 0.30 else "Alto"
r_k_base = 90 if k_s < 0.15 else 60 if k_s < 0.30 else 30

# Cálculos de doses
if cultura == "Milho":
    r_p, r_k = r_p_base * (meta_ton / 4), r_k_base * (meta_ton / 4)
    n_cobertura = (meta_ton * 25) * 0.8
elif cultura == "Soja":
    r_p, r_k = r_p_base * (meta_ton / 3.5), r_k_base * (meta_ton / 3.5)
    n_cobertura = 0
else: # Palma
    r_p = 100 if st_p == "Baixo" else 50
    r_k = 150 if st_k == "Baixo" else 80
    n_cobertura = 0

v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc_ha = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)
ng_ha = (arg * 50) / 1000 if (al_s > 0.5) else 0.0

# ---------------- 2️⃣ DASHBOARD COM STATUS (SEM MUNICÍPIO) ----------------
st.divider()
st.subheader(f"2️⃣ Diagnóstico da Recomendação")
res1, res2, res3, res4 = st.columns(4)
res1.metric("Classe de Argila", classe_txt)
res2.metric("Status Fósforo (P)", st_p)
res3.metric("Status Potássio (K)", st_k)
res4.metric("V% Alvo", f"{v_alvo}%")

st.markdown("---")
d1, d2, d3 = st.columns(3)
d1.metric("P₂O₅ (kg/ha)", f"{r_p:.0f}")
d2.metric("K₂O (kg/ha)", f"{r_k:.0f}")
d3.metric("CALCÁRIO (t/ha)", f"{nc_ha:.2f}")

# ---------------- 3️⃣ ADUBAÇÃO COMERCIAL ----------------
st.write("---")
st.subheader("3️⃣ Planejamento de Adubação Comercial")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N%", 0, value=5 if cultura=="Milho" else 0)
f_p = f2.number_input("P%", 0, value=20)
f_k = f3.number_input("K%", 0, value=20)

if f_p > 0 or f_k > 0:
    dose_ha = max((r_p/f_p*100) if f_p>0 else 0, (r_k/f_k*100) if f_k>0 else 0)
    total_adubo = dose_ha * area_total
    st.info(f"🚜 **Recomendação:** Aplicar {dose_ha:.0f} kg/ha de {f_n}-{f_p}-{f_k}. Total: {total_adubo/50:.0f} sacos.")

# ---------------- 4️⃣ PDF COM ACENTOS CORRETOS ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def f(texto): return texto.encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 15, f("PRESCRIÇÃO TÉCNICA AGRONÔMICA"), align="C", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 7, f("Felipe Amorim | Consultoria Agronômica"), align="C", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, f(f"Data: {data_hoje} | Localidade: {municipio} - {estado}"), align="C", ln=True)
    
    pdf.set_text_color(0, 0, 0); pdf.ln(15)
    
    # Seção 1
    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, f(" 1. IDENTIFICAÇÃO E DIAGNÓSTICO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, f(f" Cliente: {nome_cliente} | Fazenda: {fazenda}"), ln=True)
    pdf.cell(190, 7, f(f" Cultura: {cultura} | Área: {area_total} ha | Classe Argila: {classe_txt}"), ln=True)
    pdf.cell(190, 7, f(f" Status: Fósforo ({st_p}) | Potássio ({st_k}) | V% Atual: {v_at}%"), ln=True)

    # Seção 2
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, f(" 2. RECOMENDAÇÕES DE ADUBAÇÃO E CORRETIVOS"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, f(f"- CALCÁRIO: {nc_ha:.2f} t/ha | GESSO: {ng_ha:.2f} t/ha"), ln=True)
    pdf.cell(190, 7, f(f"- ADUBAÇÃO NO PLANTIO: {dose_ha:.0f} kg/ha do formulado {f_n}-{f_p}-{f_k}"), ln=True)
    if cultura == "Milho":
        pdf.cell(190, 7, f(f"- NITROGÊNIO EM COBERTURA: Aplicar {n_cobertura:.1f} kg/ha de N entre V4 e V6."), ln=True)

    # Seção 3
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, f(" 3. SUGESTÕES DE MANEJO TÉCNICO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10); pdf.ln(2)
    
    if cultura == "Palma Forrageira":
        sugestoes = [
            f"- Variedade recomendada: {var_palma}.",
            "- Adubação Orgânica: Aplicar 20 a 30 t/ha de esterco bem curtido.",
            "- Corte: Proibido realizar o corte na raquete mãe.",
            "- Cobertura: Parcelar Nitrogênio e Potássio no período chuvoso."
        ]
    elif cultura == "Milho":
        sugestoes = [
            "- Realizar a adubação de cobertura rigorosamente entre V4 e V6.",
            "- Monitorar a presença de cigarrinha e percevejo desde a emergência.",
            "- Atentar para a umidade do solo no momento da aplicação."
        ]
    else: # Soja
        sugestoes = [
            "- A inoculação e a co-inoculação são essenciais para o suprimento de N.",
            "- Monitorar percevejos e lagartas no início do desenvolvimento vegetativo.",
            "- Garantir que a semeadura ocorra com umidade adequada no solo."
        ]
    for s in sugestoes: pdf.cell(190, 6, f(s), ln=True)

    # Seção 4
    pdf.ln(10); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, f(" 4. REFERÊNCIAS TÉCNICAS"), ln=True, fill=True)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(190, 5, f("- Manual de Calagem e Adubação (Embrapa Cerrados).\n- Boletins Técnicos de Recomendação de Adubação.\n- Tabela de Exigência Nutricional: Soja, Milho e Palma Forrageira."))

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    st.download_button("⬇️ Baixar PDF", gerar_pdf(), file_name=f"Recomendacao_{nome_cliente}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
