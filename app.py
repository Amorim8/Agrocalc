import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
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
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR (BARRA LATERAL) ----------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
    st.title("Configurações")
    nome_cliente_input = st.text_input("👨‍🌾 Nome do Cliente:", "")
    fazenda = st.text_input("🏠 Fazenda:", "")
    talhao = st.text_input("📍 Talhão:", "")
    municipio = st.text_input("🏙️ Município:", "Redenção do Gurguéia")
    estado = st.selectbox("🌎 Estado:", ["PI", "MA", "BA", "TO", "CE", "PE", "RN", "PB", "AL", "SE", "MG", "GO", "MT", "MS", "SP", "RJ", "ES", "PR", "SC", "RS", "AM", "RR", "AP", "PA", "AC", "RO", "DF"], index=0)
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    cultura = st.radio("🌱 Cultura:", ["Soja", "Milho", "Palma Forrageira"], horizontal=True)
    
    variedade_palma = ""
    if cultura == "Palma Forrageira":
        # Acréscimo das variedades conforme solicitado
        variedade_palma = st.selectbox("🌵 Variedade da Palma:", ["Orelha de Elefante (Gigante)", "Miúda (Doce)"])
        meta_ton = st.select_slider("🎯 Meta de Matéria Seca (t MS/ha):", options=[float(i) for i in range(5, 41)], value=20.0)
    else:
        meta_ton = st.select_slider("🎯 Meta de Produtividade (t/ha):", options=[float(i/2) for i in range(2, 31)], value=4.0 if cultura == "Soja" else 8.0)

nome_para_arquivo = nome_cliente_input.replace(" ", "_") if nome_cliente_input else "Cliente"

# ---------------- CABEÇALHO PRINCIPAL ----------------
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
with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
    prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)

# ---------------- LÓGICA TÉCNICA (CÁLCULOS) ----------------
def interpretar_solo(p, k, arg):
    if arg > 35: lim_p = [3, 6, 9, 12]
    else: lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    return "Argiloso" if arg > 35 else "Arenoso/Médio", niv_p, niv_k

classe_txt, nivel_p, nivel_k = interpretar_solo(p_solo, k_solo, argila)

v_alvo = 70 if cultura in ["Soja", "Palma Forrageira"] else 60
nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt)
total_calc = nc * area

m_atual = (al_solo / (al_solo + (ctc - al_solo))) * 100 if (al_solo + (ctc - al_solo)) > 0 else 0
ng = (argila * 50) / 1000 if (m_atual > 20 or al_solo > 0.5) else 0.0
total_gesso = ng * area

# Recomendação de NPK baseada na cultura
if cultura == "Soja":
    rec_n, rec_p = 0, (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
elif cultura == "Milho":
    rec_n = meta_ton * 22
    n_plantio = 30
    n_cobertura = max(0.0, rec_n - n_plantio)
    rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
    rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
else: # Palma Forrageira (Ref: Embrapa Meio-Norte)
    rec_n = meta_ton * 10 
    rec_p = 90 * (1.5 if nivel_p == "Baixo" else 1.0) 
    rec_k = 120 * (1.5 if nivel_k == "Baixo" else 1.0) 

# ---------------- 2️⃣ DASHBOARD DE DIAGNÓSTICO ----------------
st.divider()
st.subheader("2️⃣ Diagnóstico e Metas")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Textura Solo", classe_txt)
m2.metric("V% Alvo", f"{v_alvo}%")
m3.metric("Status P", nivel_p)
m4.metric("Status K", nivel_k)
m5.metric("Alumínio (m%)", f"{m_atual:.1f}%")

# ---------------- 3️⃣ PRESCRIÇÃO E FERTILIZANTES ----------------
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
with r3:
    if cultura in ["Milho", "Palma Forrageira"]:
        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Total N", f"{rec_n:.0f} kg")
        if cultura == "Milho":
            nc2.metric("Plantio N", f"{n_plantio} kg")
            nc3.metric("Cobertura N", f"{n_cobertura:.0f} kg")
        else:
            nc2.metric("P2O5 Recom.", f"{rec_p:.0f} kg")
            nc3.metric("K2O Recom.", f"{rec_k:.0f} kg")
            
    st.markdown("### 🛒 Formulação Comercial")
    cn, cp, ck = st.columns(3)
    # Valores padrão inteligentes baseados na cultura
    f_n = cn.number_input("N%", 0, value=0 if cultura=="Soja" else 10 if cultura=="Palma Forrageira" else 4)
    f_p = cp.number_input("P%", 0, value=10 if cultura=="Palma Forrageira" else 20)
    f_k = ck.number_input("K%", 0, value=20)
    
    if f_p > 0 or f_k > 0:
        dose_p = (rec_p / f_p * 100) if f_p > 0 else 0
        dose_k = (rec_k / f_k * 100) if f_k > 0 else 0
        dose_final = max(dose_p, dose_k)
        total_sacos = math.ceil((dose_final * area) / 50)
        st.success(f"Dose: {dose_final:.0f} kg/ha | Total: {total_sacos} sacos")

# ---------------- 4️⃣ GERAÇÃO DO PDF PROFISSIONAL ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix_txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    data_pdf = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')
    
    # Cabeçalho Estilizado
    pdf.set_fill_color(34, 139, 34); pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 15, fix_txt("RELATÓRIO DE RECOMENDAÇÃO TÉCNICA"), align="C", ln=True)
    pdf.set_font("Helvetica", "", 10); pdf.cell(190, 5, fix_txt(f"Consultor: Felipe Amorim | Consultoria Agronômica"), align="C", ln=True)
    pdf.cell(190, 5, fix_txt(f"Data de Emissão: {data_pdf}"), align="C", ln=True)
    
    # Seção 1: Identificação
    pdf.set_text_color(0, 0, 0); pdf.ln(15); pdf.set_fill_color(230, 230, 230); pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 1. INFORMAÇÕES GERAIS E DIAGNÓSTICO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Cliente: {nome_cliente_input if nome_cliente_input else 'Não informado'} | Fazenda: {fazenda}"), ln=True)
    
    c_final = f"{cultura} ({variedade_palma})" if cultura == "Palma Forrageira" else cultura
    pdf.cell(190, 7, fix_txt(f" Cultura: {c_final} | Área: {area:.2f} ha | Meta: {meta_ton} t/ha"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Local: {municipio} - {estado}"), ln=True)
    
    # Seção 2: Prescrição
    pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 2. PRESCRIÇÃO TÉCNICA DE CORRETIVOS E FERTILIZANTES"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(190, 7, fix_txt(f" Calagem: {nc:.2f} t/ha (Total: {total_calc:.2f} t)"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Gessagem: {ng:.2f} t/ha (Total: {total_gesso:.2f} t)"), ln=True)
    
    d_p_pdf = (rec_p / f_p * 100) if f_p > 0 else 0
    d_k_pdf = (rec_k / f_k * 100) if f_k > 0 else 0
    d_final_pdf = max(d_p_pdf, d_k_pdf)
    t_sacos_pdf = math.ceil((d_final_pdf * area) / 50)
    
    pdf.cell(190, 7, fix_txt(f" Adubação: {d_final_pdf:.0f} kg/ha do formulado comercial {f_n}-{f_p}-{f_k}"), ln=True)
    pdf.cell(190, 7, fix_txt(f" Necessidade de Aquisição: {t_sacos_pdf} sacos de 50kg para a área total."), ln=True)

    # Seção 3: Observações de Manejo (Destaque para a Palma)
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix_txt(" 3. ORIENTAÇÕES TÉCNICAS E MANEJO"), ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 9); pdf.set_text_color(30, 30, 30)
    
    if cultura == "Palma Forrageira":
        obs_especifica = "- Variedade Miúda: Alta palatabilidade, mas exige maior fertilidade e drenagem." if "Miúda" in variedade_palma else "- Variedade Orelha de Elefante: Grande resistência e alta produção de biomassa seca."
        obs = [
            f"  RECOMENDAÇÕES PARA {variedade_palma.upper()}:",
            obs_especifica,
            "⚠️ REGRA DE OURO DO CORTE: JAMAIS cortar o cladódio inicial (RAQUETE MÃE).",
            "- A preservação da raquete mãe é vital para a longevidade e rebrote do palmal.",
            "- O corte deve ser feito apenas nos cladódios de ordens superiores (filhos/netos).",
            "- Primeiro Corte: Realizar entre 18 a 24 meses após o plantio.",
            "- Adubação Orgânica: Essencial aplicar 20-30 t/ha de esterco bovino curtido.",
            "- Pragas: Monitorar rigorosamente a Cochonilha-do-Carmim."
        ]
    elif cultura == "Milho":
        obs = [
            "- Nitrogênio: Aplicar 1/3 no plantio e os 2/3 restantes em cobertura entre V4 e V6.",
            "- Monitorar incidência de cigarrinha e lagarta-do-cartucho."
        ]
    else: # Soja
        obs = [
            "- Realizar inoculação com Bradyrhizobium de alta qualidade.",
            "- Monitorar percevejos e ferrugem asiática desde o início do florescimento."
        ]

    for linha in obs:
        pdf.cell(190, 5, fix_txt(linha), ln=True)

    # Rodapé com Fontes
    pdf.ln(10); pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(34, 139, 34)
    pdf.cell(190, 8, fix_txt("FONTES E REFERÊNCIAS TÉCNICAS:"), ln=True)
    pdf.set_font("Helvetica", "I", 9); pdf.set_text_color(50, 50, 50)
    fonte_ref = "Embrapa Meio-Norte e IPA (Palma)" if cultura == "Palma Forrageira" else "Embrapa Soja / Embrapa Milho e Sorgo."
    pdf.multi_cell(190, 5, fix_txt(f"- {fonte_ref}\n- Manual de Adubação e Calagem Regional.\n- Tabelas de exportação nutricional (IPNI Brasil)."))
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- FINALIZAÇÃO DA INTERFACE ----------------
st.divider()
st.warning(f"💡 Felipe, o sistema está configurado para a cultura: **{cultura}**.")

if st.button("📄 GERAR RELATÓRIO PROFISSIONAL (PDF)"):
    try:
        pdf_bytes = gerar_pdf()
        st.download_button("⬇️ Clique aqui para Baixar", pdf_bytes, file_name=f"Prescricao_{nome_para_arquivo}.pdf")
        st.balloons()
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("Felipe Amorim | Consultoria Agronômica")
