import streamlit as st
from fpdf import FPDF
import math
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÕES INICIAIS ----------------
SENHA_MESTRE = "@Lipe1928"
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ---------------- SISTEMA DE LOGIN ----------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    senha = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Acessar Sistema"):
        if senha == SENHA_MESTRE:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Senha incorreta! Verifique as credenciais.")
    st.stop()

# ---------------- CONFIGURAÇÃO VISUAL (STREAMLIT) ----------------
st.set_page_config(page_title="Felipe Amorim | Consultoria Agronômica", layout="wide", page_icon="🌿")

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
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR (DADOS DA PROPRIEDADE) ----------------
with st.sidebar:
    st.title("🌿 Parâmetros do Projeto")
    nome_cliente = st.text_input("👨‍🌾 Nome do Produtor:")
    fazenda = st.text_input("🏠 Nome da Fazenda:")
    municipio = st.text_input("🏙️ Município:")
    estado = st.selectbox("🌎 Estado:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"])
    
    st.divider()
    area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.1, format="%.2f")
    cultura = st.radio("🌱 Cultura de Interesse:", ["Soja", "Milho", "Palma"], horizontal=True)
    
    variedade = ""
    if cultura == "Palma":
        variedade = st.selectbox("🌵 Variedade da Palma:", ["Miúda", "Orelha de Elefante", "Sertânia"])
    
    meta_ton = st.number_input("🎯 Meta de Produtividade (t/ha):", value=4.0 if cultura=="Soja" else 8.0)

# ---------------- INTERFACE PRINCIPAL - ANÁLISE DE SOLO ----------------
st.title("CONSULTORIA AGRONÔMICA ESPECIALIZADA")
st.write(f"**Consultor Responsável:** Felipe Amorim | **Data de Emissão:** {data_hoje}")

st.subheader("Entrada de Dados da Análise de Solo")
c1, c2, c3, c4 = st.columns(4)
with c1:
    ph_solo = st.number_input("pH em Água", value=5.5)
    p_solo = st.number_input("Fósforo (mg/dm³)", value=8.0)
with c2:
    al_solo = st.number_input("Alumínio (cmolc/dm³)", value=0.0)
    k_solo = st.number_input("Potássio (cmolc/dm³)", value=0.15)
with c3:
    argila = st.number_input("Argila (%)", value=35.0)
    v_atual = st.number_input("V% Atual (Saturação)", value=40.0)
with c4:
    ctc_t = st.number_input("CTC (T) Total", value=3.25)
    prnt_calc = st.number_input("PRNT do Calcário (%)", value=85.0)

# ---------------- LÓGICA DE CÁLCULO TÉCNICO (SBCS / EMBRAPA / IPA) ----------------
# 1. Calagem (V% alvo variável por cultura)
v_alvo = 70 if cultura in ["Soja", "Palma"] else 60
nc = max(0, ((v_alvo - v_atual) * ctc_t) / prnt_calc)
total_calc = nc * area

# 2. Gessagem (Considerando teor de Argila e Alumínio)
ng = (50 * argila)/1000 if (al_solo > 0.5 or argila > 40) else 0 
total_gesso = ng * area

# 3. Adubação de Base (Necessidade de extração)
rec_p = meta_ton * 15
rec_k = meta_ton * 20

# Configuração da Fórmula de Adubo
st.subheader("Configuração da Fórmula Comercial (NPK)")
f1, f2, f3 = st.columns(3)
fn = f1.number_input("N (%) na Fórmula", value=4)
fp = f2.number_input("P (%) na Fórmula", value=20)
fk = f3.number_input("K (%) na Fórmula", value=20)

dose_ha = max((rec_p/fp*100) if fp>0 else 0, (rec_k/fk*100) if fk>0 else 0)
total_adubo = dose_ha * area
sacos_50kg = math.ceil(total_adubo / 50)

# ---------------- EXIBIÇÃO DE RESULTADOS NA TELA ----------------
st.subheader("Resumo das Recomendações")
res1, res2, res3 = st.columns(3)
with res1:
    st.metric("Calcário (t/ha)", f"{nc:.2f}")
    st.write(f"Total: {total_calc:.2f} t")
with res2:
    st.metric("Gesso (t/ha)", f"{ng:.2f}")
    st.write(f"Total: {total_gesso:.2f} t")
with res3:
    st.metric("Adubo (kg/ha)", f"{dose_ha:.0f}")
    st.write(f"Total: {total_adubo:.1f} kg")

if cultura == "Milho":
    st.info(f"Recomendação de N (Embrapa): 20% no plantio e 80% em cobertura (V4-V6).")

# ---------------- FUNÇÃO PARA GERAÇÃO DO RELATÓRIO PDF ----------------
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    def fix(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho Banner
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.ln(12)
    pdf.cell(190, 10, fix("PRESCRIÇÃO AGRONÔMICA ESPECIALIZADA"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(190, 7, fix(f"Consultor: Felipe Amorim | Data: {data_hoje}"), 0, 1, "C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(18)

    # Seção 1: Identificação
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, fix("1. DADOS DA PROPRIEDADE E ANÁLISE DE SOLO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    pdf.cell(95, 7, fix(f"Produtor: {nome_cliente}"), 0, 0)
    pdf.cell(95, 7, fix(f"Fazenda: {fazenda}"), 0, 1)
    pdf.cell(95, 7, fix(f"Local: {municipio}-{estado}"), 0, 0)
    pdf.cell(95, 7, fix(f"Cultura: {cultura} | Área: {area:g} ha"), 0, 1)
    pdf.cell(190, 7, fix(f"Análise: pH {ph_solo} | Al {al_solo} | Argila {argila}% | V% {v_atual}"), 0, 1)

    # Seção 2: Recomendações
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("2. RECOMENDAÇÕES DE CORREÇÃO E ADUBAÇÃO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(190, 7, fix(f"- Calcário (PRNT {prnt_calc}%): {nc:.2f} t/ha | Total: {total_calc:.2f} toneladas"), 0, 1)
    pdf.cell(190, 7, fix(f"- Gesso Agrícola: {ng:.2f} t/ha | Total: {total_gesso:.2f} toneladas"), 0, 1)
    pdf.cell(190, 7, fix(f"- Adubação NPK ({fn}-{fp}-{fk}): {dose_ha:.0f} kg/ha | Total: {total_adubo:.1f} kg ({sacos_50kg} sacos)"), 0, 1)

    # Seção 3: Orientações de Manejo
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, fix("3. ORIENTAÇÕES TÉCNICAS E MANEJO DE CAMPO"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    
    if cultura == "Palma":
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 6, fix("MANEJO DE CORTE E PRESERVAÇÃO (RECURSOS IPA):"), 0, 1)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(190, 5, fix("- É EXPRESSAMENTE PROIBIDO o corte na 'Planta-Mãe'. Deve-se preservar integralmente o primeiro cladódio (artigo) fixado ao solo.\n- O corte deve ser realizado a partir do segundo ou terceiro nível de raquetes para garantir vigor e longevidade.\n- Aplicar 20-30 t/ha de esterco curtido conforme recomendação orgânica do IPA."))
    elif cultura == "Milho":
        pdf.multi_cell(190, 5, fix("- Manejo Nitrogenado: Aplicação de 20% no plantio e 80% em cobertura entre V4 e V6.\n- Monitoramento rigoroso de cigarrinha e percevejo (Embrapa Milho e Sorgo)."))
    else:
        pdf.multi_cell(190, 5, fix("- Priorizar inoculação com Bradyrhizobium para suprimento de Nitrogênio.\n- Monitorar sanidade foliar e disponibilidade de Fósforo no sulco (SBCS)."))

    # Seção 4: Referências Técnicas
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, fix("4. REFERÊNCIAS TÉCNICAS UTILIZADAS"), 1, 1, "L", fill=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.ln(2)
    pdf.multi_cell(190, 4, fix("PALMA: IPA (Instituto Agronômico de Pernambuco) - Manual de Cultivo e Manejo da Palma Forrageira.\nMILHO: EMBRAPA Milho e Sorgo - Recomendações Técnicas para Adubação e Calagem.\nSOJA: SBCS (Sociedade Brasileira de Ciência do Solo) - Manual de Calagem e Adubação.\nGERAL: Manual de Recomendação de Adubação para o Estado de Pernambuco."))

    return pdf.output(dest='S').encode('latin-1')

# ---------------- BOTÃO PARA GERAÇÃO E DOWNLOAD ----------------
st.divider()
if st.button("📄 GERAR RELATÓRIO TÉCNICO COMPLETO"):
    pdf_bytes = gerar_pdf()
    st.download_button("⬇️ Baixar PDF", pdf_bytes, file_name=f"Consultoria_{nome_cliente}.pdf", mime="application/pdf")
