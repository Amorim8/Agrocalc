import streamlit as st
from fpdf import FPDF
import fitz
import math

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Consultoria Agronômica", layout="wide")

st.title("🌿 Consultoria Agronômica")
st.subheader("Consultor: Felipe Amorim")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📋 Informações da Área")

cliente = st.sidebar.text_input("Produtor:", "Cliente")
talhao = st.sidebar.text_input("Talhão:", "Gleba 01")
area = st.sidebar.number_input("Área (ha):", 0.01, 1000.0, 1.0)

cultura = st.sidebar.selectbox("Cultura:", ["Soja", "Milho"])
v_alvo = 70 if cultura == "Soja" else 60

# ---------------- UPLOAD PDF ----------------
st.header("📂 Upload da Análise de Solo (PDF)")

arquivo = st.file_uploader("Envie PDF da análise", type=["pdf"])

p = k = v_atual = argila = 0

if arquivo:
    pdf = fitz.open(stream=arquivo.read(), filetype="pdf")

    texto = ""
    for page in pdf:
        texto += page.get_text()

    linhas = texto.split("\n")

    # Filtrar linhas que começam com número (amostras)
    amostras = [l for l in linhas if l.strip().startswith(tuple("0123456789"))]

    nomes = []
    dados = {}

    for linha in amostras:
        partes = linha.split()

        if len(partes) > 10:
            codigo = partes[0]
            nome = " ".join(partes[1:4])

            nomes.append(f"{codigo} - {nome}")
            dados[f"{codigo} - {nome}"] = partes

    escolha = st.selectbox("Escolha a amostra:", nomes)

    if escolha:
        dados_linha = dados[escolha]

        try:
            # POSIÇÕES BASEADAS NO SEU PDF
            p = float(dados_linha[10])   # P mg/dm³
            k = float(dados_linha[6])    # K cmolc/dm³
            v_atual = float(dados_linha[9])  # V%
            argila = float(dados_linha[-1])  # argila (última coluna)

            st.success("Dados extraídos automaticamente!")

        except:
            st.error("Erro ao ler os dados. PDF pode ter formato diferente.")

# ---------------- MANUAL (fallback) ----------------
if p == 0 and arquivo is None:
    st.header("1️⃣ Inserção Manual")

    col1, col2 = st.columns(2)

    with col1:
        p = st.number_input("Fósforo (mg/dm³)", 0.0)
        k = st.number_input("Potássio (cmolc/dm³)", 0.0)

    with col2:
        argila = st.number_input("Argila", 0.0)
        v_atual = st.number_input("V% Atual", 0.0)

# ---------------- CALAGEM ----------------
st.header("2️⃣ Calagem")

ctc = 5.0
prnt = 80.0

if v_atual >= v_alvo:
    nc = 0
    obs_calagem = "Não é necessário realizar calagem. Considerar uso de silício."
else:
    nc = ((v_alvo - v_atual) * ctc) / 100
    nc = nc / (prnt / 100)

total_calc = nc * area

st.metric("Calcário (t/ha)", f"{nc:.2f}")
st.metric("Total (t)", f"{total_calc:.2f}")

# ---------------- INTERPRETAÇÃO ----------------
st.header("3️⃣ Interpretação")

niveis = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]

nivel_p = st.selectbox("Nível de Fósforo", niveis)
nivel_k = st.selectbox("Nível de Potássio", niveis)

tabela = {
    "Soja": {
        "P": {"Muito Baixo":120,"Baixo":100,"Médio":80,"Alto":50,"Muito Alto":30},
        "K": {"Muito Baixo":100,"Baixo":90,"Médio":70,"Alto":50,"Muito Alto":30}
    },
    "Milho": {
        "P": {"Muito Baixo":120,"Baixo":100,"Médio":80,"Alto":60,"Muito Alto":40},
        "K": {"Muito Baixo":100,"Baixo":90,"Médio":70,"Alto":60,"Muito Alto":40}
    }
}

req_p = tabela[cultura]["P"][nivel_p]
req_k = tabela[cultura]["K"][nivel_k]

st.success(f"P2O5: {req_p} | K2O: {req_k} kg/ha")

# ---------------- PDF ----------------
st.header("4️⃣ Relatório")

def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()

    def txt(t):
        return str(t).encode('latin-1','replace').decode('latin-1')

    pdf.set_font("Arial","B",16)
    pdf.cell(0,10, txt("CONSULTORIA AGRONÔMICA"), ln=True)

    pdf.set_font("Arial","",12)
    pdf.cell(0,10, txt(f"Produtor: {cliente}"), ln=True)

    pdf.cell(0,10, txt(f"P: {p} | K: {k} | V%: {v_atual}"), ln=True)
    pdf.cell(0,10, txt(f"Calcário: {nc:.2f} t/ha"), ln=True)
    pdf.cell(0,10, txt(f"P2O5: {req_p} | K2O: {req_k}"), ln=True)

    return pdf.output(dest='S').encode('latin-1')

if st.button("📄 Gerar PDF"):
    st.download_button("⬇️ Baixar", gerar_pdf(), file_name="relatorio.pdf")
