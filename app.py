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

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Ajustes de Campo")
    nome_cliente = st.text_input("👨‍🌾 Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    municipio = st.text_input("📍 Município:", "")
    estado = st.selectbox("🌎 Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    area_total = st.number_input("📏 Área da Gleba (ha):", min_value=0.001, value=1.0, step=0.1, format="%.3f")
    
    st.divider()
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    if cultura == "Palma Forrageira":
        var_palma = st.selectbox("🌵 Variedade:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

# ---------------- 1️⃣ ENTRADA DE DADOS E LÓGICA TÉCNICA ----------------
st.title("SISTEMA DE PRESCRIÇÃO AGRONÔMICA")
st.write(f"**Felipe Amorim** | Consultoria Agronômica")

# Dados da Análise (Valores da imagem enviada anteriormente como base)
p_s = 12.90; k_s = 0.10; ph_s = 5.5; arg = 40.0; v_at = 40.0; al_s = 0.0; ctc_s = 3.25; prnt_s = 85.0

# Lógica de Faixas de Argila
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

# Ajustes de Meta e Nitrogênio
if cultura == "Milho":
    r_p, r_k = r_p_base * (meta_ton / 4), r_k_base * (meta_ton / 4)
    n_total = meta_ton * 25
    n_plantio = n_total * 0.20
    n_cobertura = n_total * 0.80
elif cultura == "Soja":
    r_p, r_k = r_p_base * (meta_ton / 3.5), r_k_base * (meta_ton / 3.5)
    n_plantio = 0; n_cobertura = 0
else: # Palma
    r_p = 100 if st_p == "Baixo" else 50
    r_k = 150 if st_k == "Baixo" else 80
    n_plantio = 0; n_cobertura = 0

# Calcário e Gesso
v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc_ha = max(0.0, ((v_alvo - v_at) * ctc_s) / prnt_s)
ng_ha = (arg * 50) / 1000 if (al_s > 0.5 or arg > 40) else 0.0

# ---------------- 2️⃣ DASHBOARD COMPLETO ----------------
st.subheader(f"📊 Diagnóstico e Recomendações ({area_total} ha)")
d1, d2, d3, d4 = st.columns(4)
d1.metric("Argila", classe_txt)
d2.metric("P Status", st_p)
d3.metric("K Status", st_k)
d4.metric("V% Alvo", f"{v_alvo}%")

st.markdown("---")
col_ca, col_ge, col_p2, col_k2 = st.columns(4)
col_ca.metric("Calcário (t/ha)", f"{nc_ha:.2f}")
col_ge.metric("Gesso (t/ha)", f"{ng_ha:.2f}")
col_p2.metric("P₂O₅ (kg/ha)", f"{r_p:.0f}")
col_k2.metric("K₂O (kg/ha)", f"{r_k:.0f}")

if cultura == "Milho":
    st.warning(f"🌽 **MANEJO DE NITROGÊNIO:** Aplicar **{n_plantio:.1f} kg/ha de N** no plantio e **{n_cobertura:.1f} kg/ha de N** em cobertura (V4 a V6).")

# ---------------- 3️⃣ ADUBAÇÃO COMERCIAL POR ÁREA REAL ----------------
st.write("---")
st.subheader("🛒 Cálculo de Insumos para a Área Total")
f1, f2, f3 = st.columns(3)
f_n = f1.number_input("N% do Adubo", 0, value=5 if cultura=="Milho" else 0)
f_p = f2.number_input("P% do Adubo", 0, value=20)
f_k = f3.number_input("K% do Adubo", 0, value=20)

if f_p > 0 or f_k > 0:
    dose_ha = max((r_p/f_p*100) if f_p>0 else 0, (r_k/f_k*100) if f_k>0 else 0)
    total_adubo_kg = dose_ha * area_total
    total_sacos = math.ceil(total_adubo_kg / 50)
    
    st.success(f"✅ **Recomendação para {area_total} ha:**")
    res_a, res_b, res_c = st.columns(3)
    res_a.metric("Dose Recomendada", f"{dose_ha:.0f} kg/ha")
    res_b.metric("Total em Quilos", f"{total_adubo_kg:.1f} kg")
    res_c.metric("Total em Sacos", f"{total_sacos} un")

# ---------------- 4️⃣ PDF COM ACENTOS E INFOS TÉCNICAS ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def f(texto): return str(texto).encode('latin-1', 'replace').decode('latin-1')
    
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
    pdf.cell(190, 9, f(" 1. IDENTIFICAÇÃO E DIAGNÓSTICO DA ÁREA"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 7, f(f" Cliente: {nome_cliente} | Fazenda: {fazenda} | Gleba: {area_total} ha"), ln=True)
    pdf.cell(190, 7, f(f" Cultura: {cultura} | Classe Argila: {classe_txt}"), ln=True)
    pdf.cell(190, 7, f(f" Status Solo: Fósforo ({st_p}) | Potássio ({st_k})"), ln=True)

    # Seção 2
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, f(" 2. RECOMENDAÇÃO DE CORRETIVOS E ADUBAÇÃO"), ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, f(f"> CALCÁRIO: {nc_ha:.2f} t/ha | TOTAL ÁREA: {nc_ha * area_total:.2f} t"), ln=True)
    pdf.cell(190, 8, f(f"> GESSO: {ng_ha:.2f} t/ha | TOTAL ÁREA: {ng_ha * area_total:.2f} t"), ln=True)
    pdf.cell(190, 8, f(f"> ADUBO ({f_n}-{f_p}-{f_k}): {dose_ha:.0f} kg/ha | TOTAL ÁREA: {total_adubo_kg:.1f} kg"), ln=True)
    
    if cultura == "Milho":
        pdf.set_text_color(0, 100, 0)
        pdf.cell(190, 8, f(f"> NITROGÊNIO NO PLANTIO: Aplicar {n_plantio:.1f} kg/ha de N."), ln=True)
        pdf.cell(190, 8, f(f"> NITROGÊNIO EM COBERTURA: Aplicar {n_cobertura:.1f} kg/ha de N (V4-V6)."), ln=True)
        pdf.set_text_color(0, 0, 0)

    # Seção 3
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 9, f(" 3. SUGESTÕES DE MANEJO TÉCNICO"), ln=True, fill=True)
    pdf.set_font("Arial", "", 10); pdf.ln(2)
    
    if cultura == "Milho":
        sugestoes = [
            "- Aplicar adubação de cobertura rigorosamente entre os estádios V4 e V6.",
            "- O parcelamento de Nitrogênio é vital para atingir o potencial produtivo.",
            "- Gesso agrícola: aplicação recomendada para melhoria do perfil do solo.",
            "- Monitorar pragas iniciais (Cigarrinha e Percevejo) desde a emergência."
        ]
    elif cultura == "Palma Forrageira":
        sugestoes = [
            "- Aplicar 20 a 30 t/ha de esterco bem curtido antes do plantio.",
            "- Proibido realizar o corte na raquete mãe para manter a longevidade.",
            "- Realizar cobertura de N e K durante o período das chuvas."
        ]
    else:
        sugestoes = [
            "- Inoculação e co-inoculação são essenciais para o suprimento de Nitrogênio.",
            "- Monitorar percevejos e lagartas desde o início do ciclo.",
            "- Realizar semeadura com solo em condições ideais de umidade."
        ]
    for s in sugestoes: pdf.cell(190, 6, f(s), ln=True)

    pdf.ln(10); pdf.set_font("Arial", "I", 8); pdf.cell(190, 5, f("Referências: Embrapa Cerrados / Manual de Calagem e Adubação."), align="C", ln=True)

    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📄 GERAR RELATÓRIO PDF"):
    st.download_button("⬇️ Baixar PDF", gerar_pdf(), file_name=f"Recomendacao_{nome_cliente}.pdf")

st.caption("Felipe Amorim | Consultoria Agronômica")
