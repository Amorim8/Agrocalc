import streamlit as st
from fpdf import FPDF
import math
import pandas as pd
import pdfplumber

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")

area = st.sidebar.number_input("Área (ha):", min_value=0.01, value=1.0, step=0.1)
cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])

v_alvo = 70 if cultura == "Soja" else 60

# ---------------- UPLOAD ----------------
st.header("📂 Upload da Análise de Solo")

arquivo = st.file_uploader("Envie PDF, Excel ou CSV", type=["pdf", "xlsx", "csv"])

dados = None
linha = None

def extrair_pdf(uploaded):
    texto = ""
    with pdfplumber.open(uploaded) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() + "\n"
    return texto.lower()

if arquivo:
    try:
        if arquivo.name.endswith(".xlsx"):
            dados = pd.read_excel(arquivo)

        elif arquivo.name.endswith(".csv"):
            dados = pd.read_csv(arquivo)

        elif arquivo.name.endswith(".pdf"):
            texto = extrair_pdf(arquivo)

            # Extração simples (ajustável)
            import re
            p_val = re.findall(r"p\s*=?\s*(\d+[,\.]?\d*)", texto)
            k_val = re.findall(r"k\s*=?\s*(\d+[,\.]?\d*)", texto)
            v_val = re.findall(r"v%?\s*=?\s*(\d+[,\.]?\d*)", texto)
            arg_val = re.findall(r"argila\s*=?\s*(\d+[,\.]?\d*)", texto)

            linha = {
                "p": float(p_val[0].replace(",", ".")) if p_val else 0,
                "k": float(k_val[0].replace(",", ".")) if k_val else 0,
                "v": float(v_val[0].replace(",", ".")) if v_val else 0,
                "argila": float(arg_val[0].replace(",", ".")) if arg_val else 0
            }

            st.success("PDF lido automaticamente!")

        if dados is not None:
            st.success("Arquivo carregado!")
            st.dataframe(dados)

            coluna = st.selectbox("Coluna da amostra:", dados.columns)

            amostras = dados[coluna].astype(str).unique()
            escolha = st.selectbox("Escolha a amostra:", amostras)

            linha = dados[dados[coluna] == escolha].iloc[0]

    except:
        st.error("Erro ao processar arquivo")

# ---------------- FUNÇÃO AUTO ----------------
def get_val(nome, default=0.0):
    if linha is not None:
        if isinstance(linha, dict):
            return linha.get(nome, default)
        for col in linha.index:
            if nome.lower() in col.lower():
                return float(linha[col])
    return default

# ---------------- ANÁLISE ----------------
st.header("1️⃣ Análise de Solo")

col1, col2, col3 = st.columns(3)

with col1:
    p = st.number_input("Fósforo (mg/dm³)", value=get_val("p"))
    k = st.number_input("Potássio (cmolc/dm³)", value=get_val("k"))

with col2:
    argila = st.number_input("Argila", value=get_val("argila"))
    v_atual = st.number_input("V% Atual", value=get_val("v"))

with col3:
    ctc = st.number_input("CTC (cmolc/dm³)", value=get_val("ctc", 5.0))
    prnt = st.number_input("PRNT (%)", value=80.0)

# ---------------- CALAGEM ----------------
st.header("2️⃣ Calagem")

if v_atual >= v_alvo:
    nc = 0
    obs_calagem = "Não é necessário realizar calagem. Considerar uso de silício."
else:
    nc = ((v_alvo - v_atual) * ctc) / 100
    nc = nc / (prnt / 100) if prnt > 0 else 0
    obs_calagem = "Realizar calagem conforme recomendação."

total_calc = nc * area

colc1, colc2 = st.columns(2)
colc1.metric("Calcário (t/ha)", f"{nc:.2f}")
colc2.metric("Total (t)", f"{total_calc:.2f}")

st.info(obs_calagem)

# ---------------- INTERPRETAÇÃO ----------------
st.header("3️⃣ Interpretação do Solo")

niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]

col1, col2, col3 = st.columns(3)

nivel_n = col1.selectbox("Nitrogênio", niveis)
nivel_p = col2.selectbox("Fósforo", niveis)
nivel_k = col3.selectbox("Potássio", niveis)

# ---------------- TABELA ----------------
tabela = {
    "Soja": {
        "N": {n: 0 for n in niveis},
        "P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 50, "Muito Alto": 30},
        "K": {"Muito Baixo": 100, "Baixo": 90, "Médio": 70, "Alto": 50, "Muito Alto": 30}
    },
    "Milho": {
        "N": {"Muito Baixo": 140, "Baixo": 120, "Médio": 90, "Alto": 60, "Muito Alto": 40},
        "P": {"Muito Baixo": 120, "Baixo": 100, "Médio": 80, "Alto": 60, "Muito Alto": 40},
        "K": {"Muito Baixo": 100, "Baixo": 90, "Médio": 70, "Alto": 60, "Muito Alto": 40}
    }
}

req_n = tabela[cultura]["N"][nivel_n]
req_p = tabela[cultura]["P"][nivel_p]
req_k = tabela[cultura]["K"][nivel_k]

obs_n = "Nitrogênio dispensado. Focar na inoculação." if cultura == "Soja" else "Aplicar nitrogênio."

st.success(f"N: {req_n} | P2O5: {req_p} | K2O: {req_k} kg/ha")
st.warning(obs_n)

# ---------------- ADUBO ----------------
st.header("4️⃣ Adubo Formulado")

col1, col2, col3 = st.columns(3)

f_n = col1.number_input("N (%)", 0)
f_p = col2.number_input("P (%)", 20)
f_k = col3.number_input("K (%)", 20)

dose = 0
sacos = 0

if f_p > 0:
    dose = (req_p / f_p) * 100
    total_adubo = dose * area
    sacos = math.ceil(total_adubo / 50)

    st.success(f"Dose: {dose:.0f} kg/ha | Total: {sacos} sacos")

# ---------------- PDF ----------------
st.header("5️⃣ Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    def txt(t):
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_fill_color(230,255,230)
    pdf.rect(0,0,210,297,'F')

    pdf.set_fill_color(34,139,34)
    pdf.rect(0,0,210,35,'F')

    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial","B",18)
    pdf.cell(210,15, txt("CONSULTORIA AGRONÔMICA"), align="C")

    pdf.ln(10)
    pdf.set_font("Arial","B",12)
    pdf.cell(210,10, txt("Consultor: Felipe Amorim"), align="C")

    pdf.ln(25)
    pdf.set_text_color(0,0,0)

    pdf.set_fill_color(220,220,220)
    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("DADOS DA ÁREA"), ln=True, fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"Produtor: {cliente}"), ln=True)
    pdf.cell(190,8, txt(f"Área: {area} ha"), ln=True)
    pdf.cell(190,8, txt(f"Cultura: {cultura}"), ln=True)

    pdf.ln(5)

    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("ANÁLISE DO SOLO"), ln=True, fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"Fósforo: {p} mg/dm³"), ln=True)
    pdf.cell(190,8, txt(f"Potássio: {k} cmolc/dm³"), ln=True)
    pdf.cell(190,8, txt(f"Argila: {argila}"), ln=True)
    pdf.cell(190,8, txt(f"V%: {v_atual}"), ln=True)

    pdf.ln(5)

    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("CALAGEM"), ln=True, fill=True)

    pdf.set_font("Arial","",11)
    if nc == 0:
        pdf.multi_cell(190,8, txt(obs_calagem))
    else:
        pdf.cell(190,8, txt(f"Necessidade: {nc:.2f} t/ha"), ln=True)
        pdf.cell(190,8, txt(f"Total: {total_calc:.2f} t"), ln=True)

    pdf.ln(5)

    pdf.set_font("Arial","B",12)
    pdf.cell(190,8, txt("ADUBAÇÃO"), ln=True, fill=True)

    pdf.set_font("Arial","",11)
    pdf.cell(190,8, txt(f"N: {req_n} kg/ha"), ln=True)
    pdf.cell(190,8, txt(f"P2O5: {req_p} kg/ha"), ln=True)
    pdf.cell(190,8, txt(f"K2O: {req_k} kg/ha"), ln=True)
    pdf.cell(190,8, txt(obs_n), ln=True)

    if dose > 0:
        pdf.ln(5)
        pdf.set_font("Arial","B",12)
        pdf.cell(190,8, txt("ADUBO FORMULADO"), ln=True, fill=True)

        pdf.set_font("Arial","",11)
        pdf.cell(190,8, txt(f"Fórmula: {f_n}-{f_p}-{f_k}"), ln=True)
        pdf.cell(190,8, txt(f"Dose: {dose:.0f} kg/ha"), ln=True)
        pdf.cell(190,8, txt(f"Sacos: {sacos}"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar PDF"):
    try:
        pdf_bytes = gerar_pdf()
        st.download_button("⬇️ Baixar Relatório", pdf_bytes, file_name="relatorio.pdf")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")

st.caption("Sistema de Consultoria Agronômica | Felipe Amorim")
