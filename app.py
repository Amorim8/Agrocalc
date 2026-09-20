import streamlit as st
import sqlite3
import hashlib
import secrets
import re
import os
import json
import math
import urllib.request
import pandas as pd
from datetime import datetime, timedelta
from contextlib import contextmanager
from fpdf import FPDF

# ============================================================
# CONFIGURAÇÕES INICIAIS
# ============================================================
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "usuarios.db")
PDF_DIR = os.path.join(DB_DIR, "pdfs")
FONT_DIR = os.path.join(DB_DIR, "fonts")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(FONT_DIR, exist_ok=True)

SENHA_MESTRE = "@Lipe1928"

# ============================================================
# BANCO DE DADOS
# ============================================================
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                telefone TEXT,
                crea TEXT,
                plano TEXT DEFAULT 'free',
                ativo INTEGER DEFAULT 1,
                aceitou_lgpd INTEGER DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                municipio TEXT,
                estado TEXT,
                contato TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS talhoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                area REAL,
                cultura_padrao TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS prescricoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                cliente_id INTEGER,
                talhao_id INTEGER,
                cliente TEXT,
                fazenda TEXT,
                talhao TEXT,
                municipio TEXT,
                estado TEXT,
                cultura TEXT,
                area REAL,
                meta_ton REAL,
                dados_solo TEXT,
                resultados TEXT,
                pdf_path TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                acao TEXT,
                detalhes TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


def registrar_log(user_id, acao, detalhes=""):
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO logs (user_id, acao, detalhes) VALUES (?, ?, ?)",
                (user_id, acao, detalhes)
            )
    except Exception:
        pass


# ============================================================
# AUTENTICAÇÃO
# ============================================================
def hash_senha(senha, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt.encode(), 100_000)
    return h.hex(), salt


def validar_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def validar_senha(senha):
    erros = []
    if len(senha) < 8:
        erros.append("mínimo 8 caracteres")
    if not re.search(r"[A-Za-z]", senha):
        erros.append("pelo menos uma letra")
    if not re.search(r"\d", senha):
        erros.append("pelo menos um número")
    return erros


def cadastrar_usuario(nome, email, senha, telefone="", crea="", aceitou_lgpd=False):
    if not nome or len(nome.strip()) < 3:
        return False, "Nome inválido."
    if not validar_email(email):
        return False, "E-mail inválido."
    erros = validar_senha(senha)
    if erros:
        return False, "Senha fraca: " + ", ".join(erros)
    if not aceitou_lgpd:
        return False, "Você precisa aceitar os termos da LGPD."

    senha_hash, salt = hash_senha(senha)
    try:
        with get_conn() as conn:
            conn.execute(
                """INSERT INTO usuarios (nome, email, senha_hash, salt, telefone, crea, aceitou_lgpd)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (nome.strip(), email.lower().strip(), senha_hash, salt, telefone, crea, int(aceitou_lgpd))
            )
        return True, "Cadastro realizado com sucesso!"
    except Exception as e:
        if "UNIQUE" in str(e):
            return False, "Este e-mail já está cadastrado."
        return False, f"Erro ao cadastrar: {e}"


def autenticar(email, senha):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, nome, email, senha_hash, salt, plano, ativo FROM usuarios WHERE email = ?",
            (email.lower().strip(),)
        ).fetchone()

    if not row:
        return None, "E-mail ou senha incorretos."
    if not row['ativo']:
        return None, "Conta desativada."

    senha_hash_input, _ = hash_senha(senha, row['salt'])
    if senha_hash_input != row['senha_hash']:
        return None, "E-mail ou senha incorretos."

    with get_conn() as conn:
        conn.execute("UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?",
                     (datetime.now(), row['id']))

    registrar_log(row['id'], "login", f"Login de {row['email']}")
    return {
        "id": row['id'], "nome": row['nome'],
        "email": row['email'], "plano": row['plano'],
    }, None


def alterar_senha(user_id, senha_atual, nova_senha):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT senha_hash, salt FROM usuarios WHERE id = ?", (user_id,)
        ).fetchone()
    if not row:
        return False, "Usuário não encontrado."
    hash_atual, _ = hash_senha(senha_atual, row['salt'])
    if hash_atual != row['senha_hash']:
        return False, "Senha atual incorreta."
    erros = validar_senha(nova_senha)
    if erros:
        return False, "Nova senha fraca: " + ", ".join(erros)
    novo_hash, novo_salt = hash_senha(nova_senha)
    with get_conn() as conn:
        conn.execute("UPDATE usuarios SET senha_hash = ?, salt = ? WHERE id = ?",
                     (novo_hash, novo_salt, user_id))
    return True, "Senha alterada com sucesso!"


def atualizar_perfil(user_id, nome, telefone, crea):
    with get_conn() as conn:
        conn.execute(
            "UPDATE usuarios SET nome = ?, telefone = ?, crea = ? WHERE id = ?",
            (nome, telefone, crea, user_id)
        )


def obter_usuario(user_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, nome, email, telefone, crea, plano, criado_em FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


def excluir_conta(user_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT pdf_path FROM prescricoes WHERE user_id = ?", (user_id,)
        ).fetchall()
        for r in rows:
            if r['pdf_path'] and os.path.exists(r['pdf_path']):
                try:
                    os.remove(r['pdf_path'])
                except OSError:
                    pass
        conn.execute('''DELETE FROM talhoes WHERE cliente_id IN
                        (SELECT id FROM clientes WHERE user_id = ?)''', (user_id,))
        conn.execute("DELETE FROM clientes WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM prescricoes WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM logs WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))


# ============================================================
# PAINEL ADMIN - FUNÇÕES
# ============================================================
def admin_listar_usuarios():
    """Retorna lista completa de usuários com estatísticas."""
    with get_conn() as conn:
        rows = conn.execute('''
            SELECT
                u.id,
                u.nome,
                u.email,
                u.telefone,
                u.crea,
                u.plano,
                u.ativo,
                u.criado_em,
                u.ultimo_acesso,
                COUNT(p.id) as total_prescricoes,
                COALESCE(SUM(p.area), 0) as area_total
            FROM usuarios u
            LEFT JOIN prescricoes p ON p.user_id = u.id
            GROUP BY u.id
            ORDER BY u.criado_em DESC
        ''').fetchall()
        return [dict(r) for r in rows]


def admin_estatisticas():
    """Estatísticas gerais do sistema."""
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        ativos = conn.execute("SELECT COUNT(*) FROM usuarios WHERE ativo = 1").fetchone()[0]
        inativos = total_users - ativos
        total_presc = conn.execute("SELECT COUNT(*) FROM prescricoes").fetchone()[0]
        area_total = conn.execute("SELECT COALESCE(SUM(area), 0) FROM prescricoes").fetchone()[0]
        total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        total_talhoes = conn.execute("SELECT COUNT(*) FROM talhoes").fetchone()[0]

        # Cadastros nos últimos 30 dias
        novos_30 = conn.execute('''
            SELECT COUNT(*) FROM usuarios
            WHERE criado_em >= datetime('now', '-30 days')
        ''').fetchone()[0]

        return {
            "total_users": total_users,
            "ativos": ativos,
            "inativos": inativos,
            "total_presc": total_presc,
            "area_total": area_total,
            "total_clientes": total_clientes,
            "total_talhoes": total_talhoes,
            "novos_30": novos_30,
        }


def admin_detalhes_usuario(user_id):
    """Detalhes de um usuário específico."""
    with get_conn() as conn:
        user = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (user_id,)
        ).fetchone()

        clientes = conn.execute(
            "SELECT COUNT(*) FROM clientes WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

        talhoes = conn.execute('''
            SELECT COUNT(*) FROM talhoes
            WHERE cliente_id IN (SELECT id FROM clientes WHERE user_id = ?)
        ''', (user_id,)).fetchone()[0]

        prescricoes = conn.execute('''
            SELECT id, cliente, cultura, area, criado_em
            FROM prescricoes WHERE user_id = ?
            ORDER BY criado_em DESC LIMIT 20
        ''', (user_id,)).fetchall()

        return {
            "usuario": dict(user) if user else None,
            "total_clientes": clientes,
            "total_talhoes": talhoes,
            "prescricoes": [dict(p) for p in prescricoes],
        }


def admin_toggle_ativo(user_id):
    """Ativa/desativa um usuário."""
    with get_conn() as conn:
        row = conn.execute("SELECT ativo FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        if row:
            novo = 0 if row['ativo'] else 1
            conn.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (novo, user_id))
            return novo
    return None


def admin_excluir_usuario(user_id):
    """Exclui um usuário e todos os seus dados."""
    excluir_conta(user_id)


def admin_logs_recentes(limite=50):
    """Últimos logs do sistema."""
    with get_conn() as conn:
        rows = conn.execute('''
            SELECT l.id, l.acao, l.detalhes, l.criado_em,
                   u.nome as usuario_nome, u.email as usuario_email
            FROM logs l
            LEFT JOIN usuarios u ON u.id = l.user_id
            ORDER BY l.criado_em DESC LIMIT ?
        ''', (limite,)).fetchall()
        return [dict(r) for r in rows]


# ============================================================
# CLIENTES E TALHÕES
# ============================================================
def criar_cliente(user_id, nome, municipio, estado, contato):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO clientes (user_id, nome, municipio, estado, contato) VALUES (?, ?, ?, ?, ?)",
            (user_id, nome, municipio, estado, contato)
        )
        return c.lastrowid


def listar_clientes(user_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM clientes WHERE user_id = ? ORDER BY nome", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def deletar_cliente(cliente_id, user_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM talhoes WHERE cliente_id IN (SELECT id FROM clientes WHERE id = ? AND user_id = ?)",
                     (cliente_id, user_id))
        conn.execute("DELETE FROM clientes WHERE id = ? AND user_id = ?", (cliente_id, user_id))


def criar_talhao(cliente_id, nome, area, cultura_padrao):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO talhoes (cliente_id, nome, area, cultura_padrao) VALUES (?, ?, ?, ?)",
            (cliente_id, nome, area, cultura_padrao)
        )
        return c.lastrowid


def listar_talhoes(cliente_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM talhoes WHERE cliente_id = ? ORDER BY nome", (cliente_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ============================================================
# PRESCRIÇÕES
# ============================================================
def salvar_prescricao(user_id, dados, resultados, pdf_bytes=None, cliente_id=None, talhao_id=None):
    pdf_path = None
    if pdf_bytes:
        nome_arquivo = f"user{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(PDF_DIR, nome_arquivo)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

    with get_conn() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO prescricoes
            (user_id, cliente_id, talhao_id, cliente, fazenda, talhao, municipio,
             estado, cultura, area, meta_ton, dados_solo, resultados, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, cliente_id, talhao_id,
            dados.get('cliente', ''), dados.get('fazenda', ''), dados.get('talhao', ''),
            dados.get('municipio', ''), dados.get('estado', ''),
            dados.get('cultura', ''), dados.get('area', 0), dados.get('meta_ton', 0),
            json.dumps(dados.get('solo', {})),
            json.dumps(resultados, default=str),
            pdf_path
        ))
        return c.lastrowid


def listar_prescricoes(user_id, limite=100):
    with get_conn() as conn:
        rows = conn.execute('''
            SELECT id, cliente, fazenda, talhao, cultura, area, meta_ton, criado_em, pdf_path,
                   municipio, estado, dados_solo, resultados
            FROM prescricoes WHERE user_id = ?
            ORDER BY criado_em DESC LIMIT ?
        ''', (user_id, limite)).fetchall()
        return [dict(r) for r in rows]


def obter_prescricao(prescricao_id, user_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM prescricoes WHERE id = ? AND user_id = ?",
            (prescricao_id, user_id)
        ).fetchone()
        return dict(row) if row else None


def deletar_prescricao(prescricao_id, user_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT pdf_path FROM prescricoes WHERE id = ? AND user_id = ?",
            (prescricao_id, user_id)
        ).fetchone()
        if row and row['pdf_path'] and os.path.exists(row['pdf_path']):
            try:
                os.remove(row['pdf_path'])
            except OSError:
                pass
        conn.execute("DELETE FROM prescricoes WHERE id = ? AND user_id = ?",
                     (prescricao_id, user_id))


def estatisticas_usuario(user_id):
    with get_conn() as conn:
        row = conn.execute('''
            SELECT COUNT(*) as total,
                   COALESCE(SUM(area), 0) as area_total,
                   MAX(criado_em) as ultima
            FROM prescricoes WHERE user_id = ?
        ''', (user_id,)).fetchone()
        return dict(row) if row else {'total': 0, 'area_total': 0, 'ultima': None}


# ============================================================
# CÁLCULOS AGRONÔMICOS
# ============================================================
LIMITE_K2O_PLANTIO = 80


def interpretar_solo(p, k, arg, mo):
    if arg > 35:
        lim_p = [3, 6, 9, 12]
    else:
        lim_p = [6, 12, 18, 30]
    niv_p = "Baixo" if p <= lim_p[1] else "Médio" if p <= lim_p[2] else "Bom"
    niv_k = "Baixo" if k <= 0.15 else "Médio" if k <= 0.30 else "Bom"
    niv_mo = "Baixo" if mo < 20 else "Médio" if mo < 40 else "Bom"
    classe = "Argiloso" if arg > 35 else "Arenoso/Médio"
    return classe, niv_p, niv_k, niv_mo


def sugerir_fontes(rec_p, rec_k, n_plantio, n_cobertura, cultura):
    if cultura == "Milho":
        k2o_plantio = min(rec_k, LIMITE_K2O_PLANTIO)
        k2o_cobertura = max(0, rec_k - k2o_plantio)
    else:
        k2o_plantio = rec_k
        k2o_cobertura = 0

    map_kg = rec_p / 0.52 if rec_p > 0 else 0
    n_do_map = map_kg * 0.10

    kcl_plantio = k2o_plantio / 0.60 if k2o_plantio > 0 else 0
    kcl_cobertura = k2o_cobertura / 0.60 if k2o_cobertura > 0 else 0

    n_faltante = max(0, n_plantio - n_do_map)
    ureia_plantio = n_faltante / 0.45 if n_faltante > 0 else 0
    ureia_cobertura = n_cobertura / 0.45 if cultura == "Milho" and n_cobertura > 0 else 0

    return {
        "MAP": map_kg, "KCl_plantio": kcl_plantio,
        "KCl_cobertura": kcl_cobertura,
        "Ureia_plantio": ureia_plantio,
        "Ureia_cobertura": ureia_cobertura,
        "n_do_map": n_do_map,
    }


def calcular_tudo(dados):
    p_solo = dados['p_solo']
    k_solo = dados['k_solo']
    ca_solo = dados['ca_solo']
    argila = dados['argila']
    v_atual = dados['v_atual']
    al_solo = dados['al_solo']
    mg_solo = dados['mg_solo']
    ctc = dados['ctc']
    mo_solo = dados['mo_solo']
    prnt = dados['prnt']
    s_solo = dados['s_solo']
    zn_solo = dados['zn_solo']
    b_solo = dados['b_solo']
    cu_solo = dados['cu_solo']
    area = dados['area']
    cultura = dados['cultura']
    meta_ton = dados['meta_ton']

    classe_txt, nivel_p, nivel_k, nivel_mo = interpretar_solo(p_solo, k_solo, argila, mo_solo)
    alertas = []

    # Calagem
    v_alvo = 70 if cultura == "Soja" else 60
    nc = max(0.0, ((v_alvo - v_atual) * ctc) / prnt) if prnt > 0 else 0
    total_calc = nc * area

    # Gessagem
    m_atual = (al_solo / ctc) * 100 if ctc > 0 else 0
    ng_base = (argila * 50) / 1000 if (m_atual > 20 or al_solo > 0.5) else 0.0
    sat_al = (al_solo / ctc) * 100 if ctc > 0 else 0

    ng = ng_base
    if ng_base > 0:
        if sat_al > 20:
            ng = min(ng_base, 2.0)
            if ng_base > 2.0:
                alertas.append({
                    "tipo": "warning",
                    "msg": f"Gessagem reduzida por segurança: cálculo original {ng_base:.2f} t/ha, "
                           f"mas saturação de Al alta ({sat_al:.1f}%). Limitado a 2.0 t/ha."
                })
        if ca_solo > 3.0:
            ng = min(ng, 1.5)
            alertas.append({
                "tipo": "info",
                "msg": f"Gessagem ajustada: solo com bom Ca ({ca_solo:.1f}). Dose reduzida para {ng:.2f} t/ha."
            })
    total_gesso = ng * area

    # N, P, K
    rec_n, n_plantio, n_cobertura = 0, 0, 0
    if cultura == "Soja":
        rec_n = 0
        rec_p = (meta_ton * 15) * (1.5 if nivel_p == "Baixo" else 1.0)
        rec_k = (meta_ton * 20) * (1.4 if nivel_k == "Baixo" else 1.0)
        if nivel_p == "Bom":
            rec_p *= 0.5
            alertas.append({"tipo": "info", "msg": f"Fósforo reduzido: P BOM ({p_solo} mg/dm³). Ajustado para {rec_p:.0f} kg/ha."})
        if nivel_k == "Bom":
            rec_k *= 0.5
            alertas.append({"tipo": "info", "msg": f"Potássio reduzido: K BOM ({k_solo} cmolc/dm³). Ajustado para {rec_k:.0f} kg/ha."})
    else:
        rec_n = meta_ton * 22
        n_plantio = 30
        n_cobertura = max(0.0, rec_n - n_plantio)
        rec_p = (meta_ton * 12) * (1.3 if nivel_p == "Baixo" else 1.0)
        rec_k = (meta_ton * 18) * (1.2 if nivel_k == "Baixo" else 1.0)
        if nivel_p == "Bom":
            rec_p *= 0.5
            alertas.append({"tipo": "info", "msg": f"Fósforo reduzido: P BOM ({p_solo} mg/dm³). Ajustado para {rec_p:.0f} kg/ha."})
        if nivel_k == "Bom":
            rec_k *= 0.5
            alertas.append({"tipo": "info", "msg": f"Potássio reduzido: K BOM ({k_solo} cmolc/dm³). Ajustado para {rec_k:.0f} kg/ha."})

    if cultura == "Milho":
        k2o_plantio = min(rec_k, LIMITE_K2O_PLANTIO)
        k2o_cobertura = max(0, rec_k - k2o_plantio)
    else:
        k2o_plantio = rec_k
        k2o_cobertura = 0

    fontes = sugerir_fontes(rec_p, rec_k, n_plantio, n_cobertura, cultura)

    return {
        "classe_txt": classe_txt, "nivel_p": nivel_p, "nivel_k": nivel_k,
        "nivel_mo": nivel_mo, "v_alvo": v_alvo, "m_atual": m_atual,
        "sat_al": sat_al, "nc": nc, "total_calc": total_calc,
        "ng": ng, "ng_base": ng_base, "total_gesso": total_gesso,
        "rec_n": rec_n, "n_plantio": n_plantio, "n_cobertura": n_cobertura,
        "rec_p": rec_p, "rec_k": rec_k,
        "k2o_plantio": k2o_plantio, "k2o_cobertura": k2o_cobertura,
        "fontes": fontes, "alertas": alertas,
    }


# ============================================================
# FONTES PARA PDF
# ============================================================
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def baixar_fontes():
    urls = {
        FONT_REGULAR: "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
        FONT_BOLD: "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf",
    }
    for path, url in urls.items():
        if not os.path.exists(path):
            try:
                urllib.request.urlretrieve(url, path)
            except Exception:
                pass


try:
    baixar_fontes()
except Exception:
    pass


class PDFComAcentos(FPDF):
    def __init__(self):
        super().__init__()
        self.tem_dejavu = os.path.exists(FONT_REGULAR)
        if self.tem_dejavu:
            self.add_font('DejaVu', '', FONT_REGULAR, uni=True)
            if os.path.exists(FONT_BOLD):
                self.add_font('DejaVu', 'B', FONT_BOLD, uni=True)


# ============================================================
# GERAÇÃO DE PDF
# ============================================================
def gerar_pdf(entrada, calc, usuario_nome="", usuario_crea=""):
    pdf = PDFComAcentos()
    fonte = 'DejaVu' if pdf.tem_dejavu else 'Helvetica'
    bold = 'B' if pdf.tem_dejavu else ''
    pdf.add_page()

    data_pdf = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(fonte, bold, 16)
    pdf.cell(190, 15, "RELATÓRIO DE RECOMENDAÇÃO TÉCNICA", align="C", ln=True)
    pdf.set_font(fonte, '', 10)
    consultor_info = f"Consultor: {usuario_nome or 'Felipe Amorim'}"
    if usuario_crea:
        consultor_info += f" | CREA: {usuario_crea}"
    pdf.cell(190, 5, f"{consultor_info} | Data: {data_pdf}", align="C", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font(fonte, bold, 11)
    pdf.cell(190, 8, " 1. INFORMAÇÕES GERAIS E DIAGNÓSTICO", ln=True, fill=True)
    pdf.set_font(fonte, '', 10)
    pdf.cell(190, 7, f" Cliente: {entrada.get('cliente', '')} | Fazenda: {entrada.get('fazenda', '')}", ln=True)
    pdf.cell(190, 7, f" Município: {entrada.get('municipio', '')} - {entrada.get('estado', '')} | Talhão: {entrada.get('talhao', '')}", ln=True)
    pdf.cell(190, 7, f" Cultura: {entrada.get('cultura', '')} | Área: {entrada.get('area', 0):.2f} ha | Meta: {entrada.get('meta_ton', 0)} t/ha", ln=True)

    solo = entrada.get('solo', {})
    pdf.set_font(fonte, bold, 10)
    pdf.cell(190, 7, " Análise do Solo:", ln=True)
    pdf.set_font(fonte, '', 9)
    pdf.cell(190, 5, f" - pH: {solo.get('ph_solo', 0)} | Al: {solo.get('al_solo', 0)} cmolc/dm³ | V%: {solo.get('v_atual', 0):.1f}% (Alvo: {calc['v_alvo']}%)", ln=True)
    pdf.cell(190, 5, f" - CTC: {solo.get('ctc', 0):.2f} | MO: {solo.get('mo_solo', 0):.1f} g/dm³ ({calc['nivel_mo']}) | Argila: {solo.get('argila', 0):.1f}%", ln=True)
    pdf.cell(190, 5, f" - Ca: {solo.get('ca_solo', 0):.2f} | Mg: {solo.get('mg_solo', 0):.2f} | S: {solo.get('s_solo', 0):.1f} mg/dm³", ln=True)
    pdf.cell(190, 5, f" - P: {solo.get('p_solo', 0)} mg/dm³ ({calc['nivel_p']}) | K: {solo.get('k_solo', 0)} cmolc/dm³ ({calc['nivel_k']})", ln=True)
    pdf.cell(190, 5, f" - Zn: {solo.get('zn_solo', 0):.1f} | B: {solo.get('b_solo', 0):.1f} | Cu: {solo.get('cu_solo', 0):.1f} mg/dm³", ln=True)

    pdf.ln(5)
    pdf.set_fill_color(200, 230, 200)
    pdf.set_font(fonte, bold, 10)
    pdf.cell(190, 7, " 2. JUSTIFICATIVA TÉCNICA", ln=True, fill=True)
    pdf.set_font(fonte, '', 9)

    cultura = entrada.get('cultura', '')
    meta_ton = entrada.get('meta_ton', 0)
    if cultura == "Milho":
        pdf.multi_cell(190, 5, f" - N: Ajustado para meta de {meta_ton} t/ha. Parcelamento 30 kg/ha no plantio + {calc['n_cobertura']:.0f} kg/ha em cobertura.")
        pdf.multi_cell(190, 5, f" - P2O5: {calc['rec_p']:.0f} kg/ha (nível {calc['nivel_p'].lower()}).")
        pdf.multi_cell(190, 5, f" - K2O: {calc['k2o_plantio']:.0f} kg/ha no plantio + {calc['k2o_cobertura']:.0f} kg/ha em cobertura.")
    else:
        pdf.multi_cell(190, 5, " - N: Soja utiliza fixação biológica (Bradyrhizobium). NÃO necessita adubação nitrogenada.")
        pdf.multi_cell(190, 5, f" - P2O5: {calc['rec_p']:.0f} kg/ha (nível {calc['nivel_p'].lower()}).")
        pdf.multi_cell(190, 5, f" - K2O: {calc['rec_k']:.0f} kg/ha para reposição.")

    pdf.ln(5)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font(fonte, bold, 11)
    pdf.cell(190, 8, " 3. PRESCRIÇÃO TÉCNICA", ln=True, fill=True)
    pdf.set_font(fonte, '', 10)
    pdf.cell(190, 7, f" Calagem: {calc['nc']:.2f} t/ha (Total: {calc['total_calc']:.2f} t)", ln=True)
    pdf.cell(190, 7, f" Gessagem: {calc['ng']:.2f} t/ha (Total: {calc['total_gesso']:.2f} t)", ln=True)
    if cultura == "Milho":
        pdf.cell(190, 7, f" N: {calc['rec_n']:.0f} kg/ha (Plantio: {calc['n_plantio']} | Cobertura: {calc['n_cobertura']:.0f})", ln=True)
    pdf.cell(190, 7, f" P2O5: {calc['rec_p']:.0f} kg/ha | K2O: {calc['rec_k']:.0f} kg/ha", ln=True)

    pdf.ln(5)
    pdf.set_fill_color(200, 230, 200)
    pdf.set_font(fonte, bold, 10)
    pdf.cell(190, 7, " 4. SUGESTÃO DE FONTES CONCENTRADAS", ln=True, fill=True)
    pdf.set_font(fonte, '', 9)

    fontes = calc['fontes']
    area = entrada.get('area', 0)

    pdf.cell(190, 5, " PLANTIO:", ln=True)
    if fontes['MAP'] > 0:
        pdf.cell(190, 4, f"  - MAP (52% P2O5): {fontes['MAP']:.0f} kg/ha ({math.ceil(fontes['MAP'] * area / 50)} sacos)", ln=True)
    if fontes['KCl_plantio'] > 0:
        pdf.cell(190, 4, f"  - KCl (60% K2O): {fontes['KCl_plantio']:.0f} kg/ha ({math.ceil(fontes['KCl_plantio'] * area / 50)} sacos)", ln=True)
    if fontes['Ureia_plantio'] > 0 and cultura == "Milho":
        pdf.cell(190, 4, f"  - Ureia (45% N): {fontes['Ureia_plantio']:.0f} kg/ha ({math.ceil(fontes['Ureia_plantio'] * area / 50)} sacos)", ln=True)

    if cultura == "Milho" and (fontes['KCl_cobertura'] > 0 or fontes['Ureia_cobertura'] > 0):
        pdf.cell(190, 5, " COBERTURA (V4-V6):", ln=True)
        if fontes['KCl_cobertura'] > 0:
            pdf.cell(190, 4, f"  - KCl: {fontes['KCl_cobertura']:.0f} kg/ha ({math.ceil(fontes['KCl_cobertura'] * area / 50)} sacos)", ln=True)
        if fontes['Ureia_cobertura'] > 0:
            pdf.cell(190, 4, f"  - Ureia: {fontes['Ureia_cobertura']:.0f} kg/ha ({math.ceil(fontes['Ureia_cobertura'] * area / 50)} sacos)", ln=True)

    total_sacos = math.ceil(
        (fontes['MAP'] + fontes['KCl_plantio'] + fontes['Ureia_plantio'] +
         fontes['KCl_cobertura'] + fontes['Ureia_cobertura']) * area / 50
    )
    pdf.cell(190, 5, f" Total de sacos: {total_sacos} sacos", ln=True)

    pdf.ln(5)
    pdf.set_fill_color(230, 230, 250)
    pdf.set_font(fonte, bold, 10)
    pdf.cell(190, 7, " 5. RECOMENDAÇÃO DE MICRONUTRIENTES", ln=True, fill=True)
    pdf.set_font(fonte, '', 9)
    if cultura == "Milho":
        pdf.multi_cell(190, 5, " - Zinco (Zn): Alta exigência. Aplicar 3-5 kg/ha de Zn via sulfato de zinco se necessário.")
        pdf.multi_cell(190, 5, " - Boro (B): Aplicação foliar (0.5-1.0 kg/ha) no pré-florescimento.")
    else:
        pdf.multi_cell(190, 5, " - Zinco (Zn): Essencial para fixação de N. Aplicar 2-3 kg/ha de Zn se nível estiver baixo.")
        pdf.multi_cell(190, 5, " - Boro (B): Crítico na floração. Aplicar 0.5-1.0 kg/ha via foliar no início do florescimento.")
    pdf.multi_cell(190, 5, " - Enxofre (S): Essencial para proteínas. Aplicar 20-30 kg/ha de S se necessário.")

    pdf.ln(5)
    pdf.set_fill_color(255, 235, 200)
    pdf.set_font(fonte, bold, 10)
    pdf.cell(190, 7, " 6. CRONOGRAMA OPERACIONAL", ln=True, fill=True)
    pdf.set_font(fonte, '', 9)
    if cultura == "Milho":
        pdf.cell(190, 5, " 30-60 dias antes: Aplicação de calcário (incorporar 0-20cm)", ln=True)
        pdf.cell(190, 5, " Plantio: MAP + KCl + Ureia (sulco)", ln=True)
        pdf.cell(190, 5, " V4-V6: Cobertura nitrogenada + K restante", ln=True)
        pdf.cell(190, 5, " VT-R1: Monitoramento e aplicação foliar de micronutrientes", ln=True)
    else:
        pdf.cell(190, 5, " 30-60 dias antes: Aplicação de calcário (incorporar 0-20cm)", ln=True)
        pdf.cell(190, 5, " Plantio: MAP + KCl (sulco) + inoculação das sementes", ln=True)
        pdf.cell(190, 5, " R1 (início floração): Aplicação foliar de Boro", ln=True)

    pdf.ln(5)
    pdf.set_fill_color(255, 220, 220)
    pdf.set_font(fonte, bold, 10)
    pdf.cell(190, 7, " 7. RECOMENDAÇÕES COMPLEMENTARES", ln=True, fill=True)
    pdf.set_font(fonte, '', 9)
    for rec in [
        "- Monitorar compactação do solo (penetrômetro)",
        "- Verificar emergência uniforme aos 15-20 dias",
        "- Atenção ao déficit hídrico no florescimento",
        "- Evitar aplicação em solo seco (salinidade)",
        "- Realizar monitoramento fitossanitário",
        "- Coleta de solo pós-safra para avaliação",
    ]:
        pdf.cell(190, 5, rec, ln=True)

    pdf.ln(5)
    pdf.set_fill_color(255, 235, 235)
    pdf.set_font(fonte, bold, 9)
    pdf.cell(190, 7, " NOTA DE RESPONSABILIDADE TÉCNICA", ln=True, fill=True)
    pdf.set_font(fonte, 'I' if pdf.tem_dejavu else '', 8)
    pdf.set_text_color(100, 0, 0)
    pdf.multi_cell(190, 4, "Esta recomendação baseia-se exclusivamente nos dados fornecidos. "
                            "O sucesso da cultura depende de fatores climáticos, fitossanitários e do manejo correto no campo.")

    pdf.ln(5)
    pdf.set_font(fonte, bold, 10)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(190, 8, "FONTES E REFERÊNCIAS:", ln=True)
    pdf.set_font(fonte, 'I' if pdf.tem_dejavu else '', 9)
    pdf.set_text_color(50, 50, 50)
    if cultura == "Soja":
        ref = "- Embrapa Soja\n- Manual de Adubação e Calagem (SBCS)\n- IPNI Brasil"
    else:
        ref = "- Embrapa Milho e Sorgo\n- IPNI Brasil\n- Manual de Adubação e Calagem (SBCS)"
    pdf.multi_cell(190, 5, ref)

    return pdf.output(dest='S').encode('latin-1')


# ============================================================
# INTERFACE STREAMLIT
# ============================================================
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
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div { color: #ffffff !important; }
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

init_db()
data_hoje = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

# ============================================================
# LOGIN / CADASTRO
# ============================================================
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None
if 'admin_autenticado' not in st.session_state:
    st.session_state['admin_autenticado'] = False


def tela_login():
    st.markdown("<h1 style='text-align:center;'>🌿 Sistema de Prescrição Agronômica</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Felipe Amorim | Consultoria Agronômica</p>", unsafe_allow_html=True)
    st.divider()

    tab_login, tab_cadastro = st.tabs(["🔐 Login", "📝 Criar Conta"])

    # ==================== LOGIN ====================
    with tab_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("Acesse sua conta")
            email = st.text_input("E-mail", key="login_email")
            senha = st.text_input("Senha", type="password", key="login_senha")

            if st.button("Entrar", key="btn_login", use_container_width=True):
                if not email or not senha:
                    st.error("Preencha e-mail e senha.")
                else:
                    user, erro = autenticar(email, senha)
                    if user:
                        st.session_state['usuario'] = user
                        st.rerun()
                    else:
                        st.error(erro)

    # ==================== CADASTRO ====================
    with tab_cadastro:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("Criar nova conta")

            nome = st.text_input("Nome completo *", key="cad_nome")
            email_c = st.text_input("E-mail *", key="cad_email")

            col_a, col_b = st.columns(2)
            with col_a:
                telefone = st.text_input("Telefone (opcional)", key="cad_tel")
            with col_b:
                crea = st.text_input("CREA (opcional)", key="cad_crea")

            senha_c = st.text_input(
                "Senha * (mín. 8 caracteres, 1 letra e 1 número)",
                type="password", key="cad_senha"
            )
            senha_c2 = st.text_input(
                "Confirme a senha *",
                type="password", key="cad_senha2"
            )

            aceite = st.checkbox(
                "Li e aceito a **Política de Privacidade** e o tratamento dos meus dados conforme a **LGPD**.",
                key="aceite_lgpd"
            )

            with st.expander("📄 Ver Política de Privacidade completa"):
                st.markdown("""
### 🔒 Política de Privacidade e Termos de Uso

**Última atualização:** """ + (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y') + """

#### 1. Quem somos
Este sistema é uma ferramenta de auxílio à decisão agronômica, desenvolvida para engenheiros agrônomos e consultores do setor agrícola.

#### 2. Quais dados coletamos
- **Dados de identificação:** nome, e-mail, telefone, CREA (opcional)
- **Dados de uso:** clientes cadastrados, talhões, análises de solo, prescrições geradas
- **Dados técnicos:** data e hora de acesso, ações realizadas no sistema (logs de auditoria)

#### 3. Como usamos seus dados
- Exclusivamente para o funcionamento do sistema
- Para gerar relatórios técnicos personalizados
- Para manter seu histórico de prescrições
- **NÃO compartilhamos seus dados com terceiros**
- **NÃO usamos seus dados para publicidade**

#### 4. Onde os dados ficam armazenados
Todos os dados ficam armazenados **localmente no servidor onde o sistema roda**. Não enviamos dados para nuvem ou terceiros.

#### 5. Seus direitos (LGPD - Lei 13.709/2018)
Você tem direito a:
- ✅ **Acessar** todos os seus dados a qualquer momento
- ✅ **Corrigir** informações incorretas no seu perfil
- ✅ **Excluir** sua conta e todos os dados associados (irreversível)
- ✅ **Portabilidade:** baixar seus dados em formato PDF/Excel
- ✅ **Revogar consentimento** a qualquer momento

#### 6. Segurança
- Senhas são criptografadas com **PBKDF2 + SHA-256** (100.000 iterações)
- Sessões são protegidas por token
- Logs de auditoria registram todas as ações importantes

#### 7. Como exercer seus direitos
- **Acessar dados:** pela página "Meu Perfil"
- **Alterar dados:** pela página "Meu Perfil"
- **Excluir conta:** em "Meu Perfil" → aba "LGPD"
- **Dúvidas:** entre em contato com o administrador do sistema

#### 8. Retenção de dados
Seus dados são mantidos enquanto sua conta estiver ativa. Ao excluir a conta, **todos os dados são permanentemente removidos** em até 24 horas.

#### 9. Alterações nesta política
Podemos atualizar esta política. Mudanças significativas serão comunicadas por e-mail.

---

**Ao marcar a caixa de aceite, você declara que leu, entendeu e concorda com os termos acima.**
                """)

            st.write("")

            if st.button("✅ Criar conta", key="btn_cadastro", use_container_width=True):
                if not nome or not email_c or not senha_c:
                    st.error("⚠️ Preencha todos os campos obrigatórios (*).")
                elif senha_c != senha_c2:
                    st.error("⚠️ As senhas não coincidem.")
                elif not aceite:
                    st.error("⚠️ Você precisa aceitar a Política de Privacidade e a LGPD.")
                else:
                    ok, msg = cadastrar_usuario(nome, email_c, senha_c, telefone, crea, aceite)
                    if ok:
                        user, erro_login = autenticar(email_c, senha_c)
                        if user:
                            st.session_state['usuario'] = user
                            st.success("✅ Conta criada! Bem-vindo(a)!")
                            st.rerun()
                        else:
                            st.success(msg)
                            st.info("👉 Faça login na aba **🔐 Login** para continuar.")
                    else:
                        st.error(msg)


if st.session_state['usuario'] is None:
    tela_login()
    st.stop()


# ============================================================
# APP PRINCIPAL
# ============================================================
usuario = st.session_state['usuario']

with st.sidebar:
    st.markdown(f"<h3 style='text-align:center;'>👤 {usuario['nome']}</h3>", unsafe_allow_html=True)
    st.caption(f"Plano: **{usuario['plano'].upper()}**")
    st.divider()

    pagina = st.radio(
        "📂 Navegação",
        ["🧮 Nova Prescrição", "📊 Meu Histórico", "👥 Clientes e Talhões", "⚙️ Meu Perfil", "👑 Painel Admin"]
    )

    st.divider()
    if st.button("🚪 Sair"):
        registrar_log(usuario['id'], "logout", "")
        st.session_state['usuario'] = None
        st.session_state['admin_autenticado'] = False
        st.rerun()


# ============================================================
# PÁGINA: NOVA PRESCRIÇÃO
# ============================================================
if pagina == "🧮 Nova Prescrição":
    st.title("🧮 Nova Prescrição Agronômica")
    st.caption(f"**Consultor:** {usuario['nome']} | **Data:** {data_hoje}")

    clientes = listar_clientes(usuario['id'])
    cliente_sel_id = None
    talhao_sel_id = None

    if clientes:
        with st.expander("⚡ Preenchimento Rápido (usar cliente/talhão cadastrado)", expanded=False):
            nomes_clientes = ["-- Novo cliente --"] + [c['nome'] for c in clientes]
            cliente_escolhido = st.selectbox("Cliente cadastrado:", nomes_clientes)
            if cliente_escolhido != "-- Novo cliente --":
                cliente_sel_id = next(c['id'] for c in clientes if c['nome'] == cliente_escolhido)
                talhoes = listar_talhoes(cliente_sel_id)
                if talhoes:
                    nomes_talhoes = ["-- Novo talhão --"] + [t['nome'] for t in talhoes]
                    talhao_escolhido = st.selectbox("Talhão cadastrado:", nomes_talhoes)
                    if talhao_escolhido != "-- Novo talhão --":
                        talhao_sel_id = next(t['id'] for t in talhoes if t['nome'] == talhao_escolhido)

    st.subheader("📍 Dados do Cliente e Área")
    c1, c2, c3 = st.columns(3)
    with c1:
        nome_cliente = st.text_input("👨‍🌾 Nome do Cliente:", key="nc")
        fazenda = st.text_input("🏠 Fazenda:", key="faz")
    with c2:
        talhao = st.text_input("📍 Talhão:", key="tal")
        municipio = st.text_input("🏙️ Município:", key="mun")
    with c3:
        estado = st.selectbox("🌎 Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
                                             "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                                             "RS", "RO", "RR", "SC", "SP", "SE", "TO"], key="est")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        area = st.number_input("📏 Área Total (ha):", min_value=0.01, value=1.0, step=0.01, format="%.2f")
    with c2:
        cultura = st.radio("🌱 Cultura:", ["Soja", "Milho"], horizontal=True)
    with c3:
        meta_ton = st.select_slider(
            "🎯 Meta de Produtividade (t/ha):",
            options=[float(i / 2) for i in range(2, 31)],
            value=4.0 if cultura == "Soja" else 8.0
        )

    nome_para_arquivo = nome_cliente.replace(" ", "_") if nome_cliente else "Cliente"

    st.divider()
    st.subheader("1️⃣ Análise de Solo (Química e Física Completa)")

    st.markdown("### 📊 Parâmetros Principais")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_solo = st.number_input("Fósforo (mg/dm³)", 0.0, value=8.0)
        k_solo = st.number_input("Potássio (cmolc/dm³)", 0.0, value=0.15)
        ph_solo = st.number_input("pH do Solo", 0.0, 14.0, value=5.5)
        ca_solo = st.number_input("Cálcio (cmolc/dm³)", 0.0, value=1.5)
    with col2:
        argila = st.number_input("Argila (%)", 0.0, 100.0, value=35.0)
        v_atual = st.number_input("V% Atual (Saturação por Bases)", 0.0, 100.0, value=40.0)
        al_solo = st.number_input("Alumínio (cmolc/dm³)", 0.0, value=0.0)
        mg_solo = st.number_input("Magnésio (cmolc/dm³)", 0.0, value=0.5)
    with col3:
        ctc = st.number_input("CTC (cmolc/dm³)", 0.0, value=3.25)
        mo_solo = st.number_input("Matéria Orgânica (g/dm³)", 0.0, value=20.0)
        prnt = st.number_input("PRNT (%)", 0.0, 100.0, value=85.0)
        s_solo = st.number_input("Enxofre (mg/dm³)", 0.0, value=8.0)

    st.markdown("### 🔬 Micronutrientes (Opcional)")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        zn_solo = st.number_input("Zinco (mg/dm³)", 0.0, value=1.5)
    with col_m2:
        b_solo = st.number_input("Boro (mg/dm³)", 0.0, value=0.5)
    with col_m3:
        cu_solo = st.number_input("Cobre (mg/dm³)", 0.0, value=1.0)

    dados_entrada = {
        "cliente": nome_cliente, "fazenda": fazenda, "talhao": talhao,
        "municipio": municipio, "estado": estado,
        "area": area, "cultura": cultura, "meta_ton": meta_ton,
        "solo": {
            "p_solo": p_solo, "k_solo": k_solo, "ph_solo": ph_solo,
            "ca_solo": ca_solo, "argila": argila, "v_atual": v_atual,
            "al_solo": al_solo, "mg_solo": mg_solo, "ctc": ctc,
            "mo_solo": mo_solo, "prnt": prnt, "s_solo": s_solo,
            "zn_solo": zn_solo, "b_solo": b_solo, "cu_solo": cu_solo,
        },
    }

    calc_input = {
        "p_solo": p_solo, "k_solo": k_solo, "ph_solo": ph_solo,
        "ca_solo": ca_solo, "argila": argila, "v_atual": v_atual,
        "al_solo": al_solo, "mg_solo": mg_solo, "ctc": ctc,
        "mo_solo": mo_solo, "prnt": prnt, "s_solo": s_solo,
        "zn_solo": zn_solo, "b_solo": b_solo, "cu_solo": cu_solo,
        "area": area, "cultura": cultura, "meta_ton": meta_ton,
    }

    calc = calcular_tudo(calc_input)

    for a in calc['alertas']:
        if a['tipo'] == 'warning':
            st.warning(a['msg'])
        elif a['tipo'] == 'info':
            st.info(a['msg'])

    st.divider()
    st.subheader("2️⃣ Diagnóstico e Metas")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Textura Solo", calc['classe_txt'])
    m2.metric("V% Alvo", f"{calc['v_alvo']}%")
    m3.metric("Status P", calc['nivel_p'])
    m4.metric("Status K", calc['nivel_k'])
    m5.metric("Alumínio (m%)", f"{calc['m_atual']:.1f}%")

    st.divider()
    st.subheader("3️⃣ Planejamento de Fertilizantes e Corretivos")

    r1, r2, r3 = st.columns([1, 1, 2])
    with r1:
        st.markdown("### 🪨 Calagem")
        st.metric("Dose (t/ha)", f"{calc['nc']:.2f}")
        st.write(f"Total: **{calc['total_calc']:.2f} t**")
    with r2:
        st.markdown("### ⚪ Gessagem")
        st.metric("Dose (t/ha)", f"{calc['ng']:.2f}")
        st.write(f"Total: **{calc['total_gesso']:.2f} t**")
        if calc['ng_base'] > calc['ng']:
            st.caption(f"↪️ Cálculo original: {calc['ng_base']:.2f} t/ha")
    with r3:
        if cultura == "Milho":
            nc1, nc2, nc3 = st.columns(3)
            nc1.metric("Total N", f"{calc['rec_n']:.0f} kg")
            nc2.metric("Plantio", f"{calc['n_plantio']} kg")
            nc3.metric("Cobertura", f"{calc['n_cobertura']:.0f} kg")
            if calc['k2o_cobertura'] > 0:
                st.info(f"💡 **Parcelamento do Potássio:** {calc['k2o_plantio']:.0f} kg/ha no plantio + "
                        f"{calc['k2o_cobertura']:.0f} kg/ha em cobertura (V4-V6)")

        st.markdown("### 🛒 Formulação Comercial")
        cn, cp, ck = st.columns(3)
        f_n = cn.number_input("N%", 0, value=0 if cultura == "Soja" else 4)
        f_p = cp.number_input("P%", 0, value=20)
        f_k = ck.number_input("K%", 0, value=20)

        if f_p > 0 or f_k > 0:
            dose_p = (calc['rec_p'] / f_p * 100) if f_p > 0 else 0
            dose_k = (calc['k2o_plantio'] / f_k * 100) if f_k > 0 and calc['k2o_plantio'] > 0 else 0
            dose_final = max(dose_p, dose_k)
            total_sacos = math.ceil((dose_final * area) / 50)

            p_fornecido = dose_final * f_p / 100
            if p_fornecido > calc['rec_p'] * 1.2 and calc['rec_p'] > 0:
                st.warning(f"⚠️ **EXCESSO DE P!** Formulado fornece {p_fornecido:.0f} kg/ha, "
                           f"necessidade: {calc['rec_p']:.0f} kg/ha.")

            st.success(f"**Dose plantio:** {dose_final:.0f} kg/ha | **Total:** {total_sacos} sacos (50kg)")

    st.markdown("---")
    st.markdown("### 💰 Sugestão de Fontes Concentradas")
    fontes = calc['fontes']
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🌱 PLANTIO:**")
        if fontes['MAP'] > 0:
            st.write(f"📦 MAP (52% P2O5, 10% N): **{fontes['MAP']:.0f} kg/ha** "
                     f"({math.ceil(fontes['MAP'] * area / 50)} sacos)")
        if fontes['KCl_plantio'] > 0:
            st.write(f"📦 KCl (60% K2O): **{fontes['KCl_plantio']:.0f} kg/ha** "
                     f"({math.ceil(fontes['KCl_plantio'] * area / 50)} sacos)")
        if fontes['Ureia_plantio'] > 0 and cultura == "Milho":
            st.write(f"📦 Ureia (45% N): **{fontes['Ureia_plantio']:.0f} kg/ha** "
                     f"({math.ceil(fontes['Ureia_plantio'] * area / 50)} sacos)")
    with col_b:
        if cultura == "Milho" and (fontes['KCl_cobertura'] > 0 or fontes['Ureia_cobertura'] > 0):
            st.markdown("**🌿 COBERTURA (V4-V6):**")
            if fontes['KCl_cobertura'] > 0:
                st.write(f"📦 KCl: **{fontes['KCl_cobertura']:.0f} kg/ha** "
                         f"({math.ceil(fontes['KCl_cobertura'] * area / 50)} sacos)")
            if fontes['Ureia_cobertura'] > 0:
                st.write(f"📦 Ureia: **{fontes['Ureia_cobertura']:.0f} kg/ha** "
                         f"({math.ceil(fontes['Ureia_cobertura'] * area / 50)} sacos)")

    total_sacos_op1 = math.ceil(
        (fontes['MAP'] + fontes['KCl_plantio'] + fontes['Ureia_plantio'] +
         fontes['KCl_cobertura'] + fontes['Ureia_cobertura']) * area / 50
    )
    st.success(f"💰 **Total de sacos (Opção recomendada):** {total_sacos_op1} sacos")

    st.divider()
    st.subheader("✅ Checklist de Segurança")
    ck1, ck2, ck3 = st.columns(3)
    with ck1:
        st.markdown("**🪨 Calagem**")
        if calc['nc'] > 5.0:
            st.error("[ATENÇÃO] Dose muito alta - parcelar")
        elif calc['nc'] > 3.0:
            st.warning("[CUIDADO] Aplicar com 90 dias de antecedência")
        else:
            st.success("[OK] Dentro do recomendado")
    with ck2:
        st.markdown("**⚪ Gessagem**")
        if calc['ng'] > 2.0:
            st.error("[ATENÇÃO] Risco de lixiviação")
        elif calc['ng'] > 1.0:
            st.warning("[CUIDADO] Verificar necessidade de Ca e S")
        else:
            st.success("[OK] Dose segura")
    with ck3:
        if cultura == "Milho":
            st.markdown("**🌽 Nitrogênio**")
            if calc['n_cobertura'] > 120:
                st.warning("[CUIDADO] Parcelar em V4 e V6")
            else:
                st.success("[OK] Adequado")
        else:
            st.info("🌱 Soja: fixação biológica (sem N)")

    st.divider()
    st.warning("⚠️ Esta ferramenta é um auxílio à decisão. Consulte um engenheiro agrônomo antes da aplicação.")

    if st.button("📄 GERAR E SALVAR RELATÓRIO"):
        perfil = obter_usuario(usuario['id'])
        pdf_bytes = gerar_pdf(
            dados_entrada, calc,
            usuario_nome=perfil['nome'],
            usuario_crea=perfil.get('crea') or ""
        )

        presc_id = salvar_prescricao(
            usuario['id'], dados_entrada, calc, pdf_bytes,
            cliente_id=cliente_sel_id, talhao_id=talhao_sel_id
        )
        registrar_log(usuario['id'], "gerar_prescricao", f"ID {presc_id}")

        st.success(f"✅ Relatório gerado e salvo no histórico! (ID: {presc_id})")
        st.download_button(
            "⬇️ Baixar Relatório PDF",
            pdf_bytes,
            file_name=f"Relatorio_{nome_para_arquivo}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )


# ============================================================
# PÁGINA: HISTÓRICO
# ============================================================
elif pagina == "📊 Meu Histórico":
    st.title("📊 Meu Histórico de Prescrições")

    stats = estatisticas_usuario(usuario['id'])
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Prescrições", stats['total'])
    c2.metric("Área Total Atendida", f"{stats['area_total']:.1f} ha")
    c3.metric("Última Prescrição", (stats['ultima'] or "—")[:10] if stats['ultima'] else "—")

    st.divider()

    prescricoes = listar_prescricoes(usuario['id'])
    if not prescricoes:
        st.info("Você ainda não gerou nenhuma prescrição.")
    else:
        df = pd.DataFrame(prescricoes)
        df_display = df[['id', 'cliente', 'fazenda', 'talhao', 'cultura', 'area', 'meta_ton', 'criado_em']].copy()
        df_display.columns = ['ID', 'Cliente', 'Fazenda', 'Talhão', 'Cultura', 'Área (ha)', 'Meta (t/ha)', 'Data']
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("🔍 Detalhes de uma Prescrição")
        id_sel = st.selectbox("Selecione o ID:", df['id'].tolist())

        if id_sel:
            p = obter_prescricao(id_sel, usuario['id'])
            if p:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Cliente:** {p['cliente']} | **Fazenda:** {p['fazenda']}")
                    st.markdown(f"**Talhão:** {p['talhao']} | **Cultura:** {p['cultura']}")
                    st.markdown(f"**Área:** {p['area']} ha | **Meta:** {p['meta_ton']} t/ha")
                    st.markdown(f"**Data:** {p['criado_em']}")

                    with st.expander("📋 Ver dados do solo"):
                        try:
                            st.json(json.loads(p['dados_solo']) if isinstance(p['dados_solo'], str) else p['dados_solo'])
                        except Exception:
                            st.write(p['dados_solo'])
                    with st.expander("📊 Ver resultados calculados"):
                        try:
                            st.json(json.loads(p['resultados']) if isinstance(p['resultados'], str) else p['resultados'])
                        except Exception:
                            st.write(p['resultados'])

                with col2:
                    if p['pdf_path'] and os.path.exists(p['pdf_path']):
                        with open(p['pdf_path'], "rb") as f:
                            st.download_button(
                                "⬇️ Baixar PDF original",
                                f.read(),
                                file_name=f"Relatorio_{id_sel}.pdf",
                                mime="application/pdf",
                                key=f"dl_{id_sel}"
                            )
                    else:
                        st.warning("PDF não encontrado.")

                if st.button(f"🗑️ Excluir prescrição #{id_sel}"):
                    deletar_prescricao(id_sel, usuario['id'])
                    registrar_log(usuario['id'], "deletar_prescricao", f"ID {id_sel}")
                    st.success("Prescrição excluída!")
                    st.rerun()


# ============================================================
# PÁGINA: CLIENTES
# ============================================================
elif pagina == "👥 Clientes e Talhões":
    st.title("👥 Gerenciar Clientes e Talhões")

    tab1, tab2 = st.tabs(["📋 Meus Clientes", "➕ Novo Cliente"])

    with tab2:
        st.subheader("Cadastrar Novo Cliente")
        c1, c2 = st.columns(2)
        with c1:
            nome_c = st.text_input("Nome do cliente/fazenda:")
            municipio_c = st.text_input("Município:")
        with c2:
            estado_c = st.selectbox("Estado:", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
                                                "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                                                "RS", "RO", "RR", "SC", "SP", "SE", "TO"], key="est_c")
            contato_c = st.text_input("Contato (telefone/e-mail):")

        if st.button("✅ Cadastrar Cliente"):
            if nome_c.strip():
                criar_cliente(usuario['id'], nome_c, municipio_c, estado_c, contato_c)
                registrar_log(usuario['id'], "criar_cliente", nome_c)
                st.success(f"Cliente '{nome_c}' cadastrado!")
                st.rerun()
            else:
                st.error("Informe o nome.")

    with tab1:
        clientes = listar_clientes(usuario['id'])
        if not clientes:
            st.info("Nenhum cliente cadastrado ainda.")
        else:
            for cli in clientes:
                with st.expander(f"🏠 {cli['nome']} — {cli['municipio']}/{cli['estado']}"):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**Contato:** {cli['contato'] or '—'}")
                        st.write(f"**Cadastrado em:** {cli['criado_em']}")

                        talhoes = listar_talhoes(cli['id'])
                        if talhoes:
                            st.markdown("**Talhões cadastrados:**")
                            for t in talhoes:
                                st.write(f"- 📍 {t['nome']} ({t['area']} ha) — {t['cultura_padrao']}")
                        else:
                            st.caption("Nenhum talhão cadastrado.")

                        st.markdown("**➕ Adicionar talhão:**")
                        t1, t2, t3, t4 = st.columns([2, 1, 1, 1])
                        nome_t = t1.text_input("Nome talhão", key=f"tn_{cli['id']}")
                        area_t = t2.number_input("Área (ha)", min_value=0.01, value=1.0, key=f"ta_{cli['id']}")
                        cultura_t = t3.selectbox("Cultura", ["Soja", "Milho"], key=f"tc_{cli['id']}")
                        if t4.button("Adicionar", key=f"tb_{cli['id']}"):
                            if nome_t.strip():
                                criar_talhao(cli['id'], nome_t, area_t, cultura_t)
                                st.success(f"Talhão '{nome_t}' adicionado!")
                                st.rerun()

                    with col_b:
                        if st.button(f"🗑️ Excluir cliente", key=f"del_{cli['id']}"):
                            deletar_cliente(cli['id'], usuario['id'])
                            registrar_log(usuario['id'], "deletar_cliente", cli['nome'])
                            st.success("Cliente excluído!")
                            st.rerun()


# ============================================================
# PÁGINA: PERFIL
# ============================================================
elif pagina == "⚙️ Meu Perfil":
    st.title("⚙️ Meu Perfil")

    perfil = obter_usuario(usuario['id'])

    tab_perfil, tab_senha, tab_lgpd = st.tabs(["📝 Dados", "🔑 Alterar Senha", "🛡️ LGPD"])

    with tab_perfil:
        st.subheader("Dados Pessoais")
        nome_p = st.text_input("Nome:", value=perfil['nome'])
        email_p = st.text_input("E-mail:", value=perfil['email'], disabled=True)
        tel_p = st.text_input("Telefone:", value=perfil.get('telefone') or "")
        crea_p = st.text_input("CREA:", value=perfil.get('crea') or "")

        if st.button("💾 Salvar Alterações"):
            atualizar_perfil(usuario['id'], nome_p, tel_p, crea_p)
            st.session_state['usuario']['nome'] = nome_p
            st.success("Perfil atualizado!")
            st.rerun()

        st.divider()
        st.caption(f"Conta criada em: {perfil['criado_em']}")
        st.caption(f"Plano: **{perfil['plano'].upper()}**")

    with tab_senha:
        st.subheader("Alterar Senha")
        s_atual = st.text_input("Senha atual:", type="password")
        s_nova = st.text_input("Nova senha:", type="password")
        s_nova2 = st.text_input("Confirme a nova senha:", type="password")

        if st.button("🔑 Alterar Senha"):
            if s_nova != s_nova2:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = alterar_senha(usuario['id'], s_atual, s_nova)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    with tab_lgpd:
        st.subheader("🛡️ Privacidade e LGPD")
        st.markdown("""
        **Seus direitos conforme a LGPD:**
        - Você pode acessar, corrigir ou excluir seus dados a qualquer momento.
        - Seus dados são armazenados localmente e não são compartilhados com terceiros.
        - Os relatórios gerados ficam armazenados apenas na sua conta.
        """)

        st.warning("⚠️ **Atenção:** A exclusão da conta é **permanente** e apagará TODOS os seus dados, "
                   "incluindo clientes, talhões, prescrições e PDFs gerados.")

        confirmar = st.text_input("Digite **EXCLUIR** para confirmar:")
        if st.button("🗑️ Excluir minha conta permanentemente"):
            if confirmar == "EXCLUIR":
                excluir_conta(usuario['id'])
                st.session_state['usuario'] = None
                st.success("Conta excluída. Até logo!")
                st.rerun()
            else:
                st.error("Digite EXCLUIR para confirmar.")


# ============================================================
# PÁGINA: PAINEL ADMIN
# ============================================================
elif pagina == "👑 Painel Admin":
    st.title("👑 Painel Administrativo")

    # Autenticação do admin
    if not st.session_state['admin_autenticado']:
        st.info("🔒 Esta área é restrita ao administrador do sistema.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            senha_admin = st.text_input("Digite a senha mestra:", type="password", key="admin_senha")
            if st.button("🔓 Desbloquear Painel", use_container_width=True):
                if senha_admin == SENHA_MESTRE:
                    st.session_state['admin_autenticado'] = True
                    registrar_log(usuario['id'], "admin_acesso", "Painel Admin acessado")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta.")
        st.stop()

    # Botão para bloquear novamente
    col_top1, col_top2 = st.columns([3, 1])
    with col_top2:
        if st.button("🔒 Bloquear"):
            st.session_state['admin_autenticado'] = False
            st.rerun()

    st.success("✅ Acesso liberado ao Painel Administrativo")

    # ============ MÉTRICAS GERAIS ============
    stats = admin_estatisticas()

    st.subheader("📊 Visão Geral do Sistema")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Total de Usuários", stats['total_users'])
    m2.metric("🟢 Ativos", stats['ativos'])
    m3.metric("🔴 Inativos", stats['inativos'])
    m4.metric("🆕 Novos (30 dias)", stats['novos_30'])

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("📄 Prescrições", stats['total_presc'])
    m6.metric("📏 Área Total", f"{stats['area_total']:.1f} ha")
    m7.metric("👨‍🌾 Clientes", stats['total_clientes'])
    m8.metric("📍 Talhões", stats['total_talhoes'])

    st.divider()

    # ============ TABS ============
    tab_users, tab_logs = st.tabs(["👥 Usuários Cadastrados", "📋 Logs de Atividade"])

    with tab_users:
        st.subheader("👥 Lista de Usuários")

        usuarios_lista = admin_listar_usuarios()

        if not usuarios_lista:
            st.info("Nenhum usuário cadastrado ainda.")
        else:
            # Preparar DataFrame
            df_admin = pd.DataFrame(usuarios_lista)
            df_display = df_admin[[
                'id', 'nome', 'email', 'telefone', 'crea',
                'plano', 'ativo', 'criado_em', 'ultimo_acesso',
                'total_prescricoes', 'area_total'
            ]].copy()
            df_display['ativo'] = df_display['ativo'].apply(lambda x: '🟢 Ativo' if x else '🔴 Inativo')
            df_display.columns = [
                'ID', 'Nome', 'E-mail', 'Telefone', 'CREA',
                'Plano', 'Status', 'Cadastro', 'Último Acesso',
                'Nº Prescrições', 'Área Total (ha)'
            ]

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Exportar Excel
            st.divider()
            st.markdown("### 📥 Exportar Dados")
            col_exp1, col_exp2 = st.columns(2)

            with col_exp1:
                csv = df_display.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    "📄 Baixar CSV",
                    csv,
                    file_name=f"usuarios_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col_exp2:
                try:
                    buffer = io.BytesIO()
                    df_display.to_excel(buffer, index=False, engine='openpyxl')
                    buffer.seek(0)
                    st.download_button(
                        "📊 Baixar Excel",
                        buffer.getvalue(),
                        file_name=f"usuarios_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception:
                    st.caption("(Instale `openpyxl` para exportar Excel)")

            # ============ DETALHES DE UM USUÁRIO ============
            st.divider()
            st.subheader("🔍 Detalhes de um Usuário")
            user_id_sel = st.selectbox(
                "Selecione o ID do usuário:",
                [u['id'] for u in usuarios_lista]
            )

            if user_id_sel:
                detalhes = admin_detalhes_usuario(user_id_sel)
                u = detalhes['usuario']

                if u:
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"**Nome:** {u['nome']}")
                        st.markdown(f"**E-mail:** {u['email']}")
                        st.markdown(f"**Telefone:** {u.get('telefone') or '—'}")
                        st.markdown(f"**CREA:** {u.get('crea') or '—'}")
                        st.markdown(f"**Plano:** {u['plano'].upper()}")
                        st.markdown(f"**Status:** {'🟢 Ativo' if u['ativo'] else '🔴 Inativo'}")
                        st.markdown(f"**Cadastro:** {u['criado_em']}")
                        st.markdown(f"**Último acesso:** {u.get('ultimo_acesso') or '—'}")

                    with col_b:
                        st.metric("Clientes", detalhes['total_clientes'])
                        st.metric("Talhões", detalhes['total_talhoes'])
                        st.metric("Prescrições", len(detalhes['prescricoes']))

                    # Ações
                    st.markdown("### ⚙️ Ações")
                    col_ac1, col_ac2 = st.columns(2)

                    with col_ac1:
                        if st.button("🔄 Ativar/Desativar conta", key=f"toggle_{user_id_sel}", use_container_width=True):
                            novo_status = admin_toggle_ativo(user_id_sel)
                            if novo_status is not None:
                                acao = "ativado" if novo_status else "desativado"
                                registrar_log(usuario['id'], "admin_toggle", f"Usuário {user_id_sel} {acao}")
                                st.success(f"Usuário {'ativado' if novo_status else 'desativado'}!")
                                st.rerun()

                    with col_ac2:
                        if st.button("🗑️ Excluir conta", key=f"del_user_{user_id_sel}", use_container_width=True):
                            st.session_state[f'confirmar_exclusao_{user_id_sel}'] = True

                    # Confirmação de exclusão
                    if st.session_state.get(f'confirmar_exclusao_{user_id_sel}'):
                        st.error(f"⚠️ **Tem certeza?** Isso apagará TODOS os dados de **{u['nome']}** permanentemente!")
                        col_conf1, col_conf2 = st.columns(2)
                        with col_conf1:
                            if st.button("✅ Sim, excluir", key=f"conf_del_{user_id_sel}", use_container_width=True):
                                admin_excluir_usuario(user_id_sel)
                                registrar_log(usuario['id'], "admin_excluir", f"Usuário {user_id_sel} - {u['email']}")
                                st.session_state[f'confirmar_exclusao_{user_id_sel}'] = False
                                st.success("Usuário excluído!")
                                st.rerun()
                        with col_conf2:
                            if st.button("❌ Cancelar", key=f"cancel_del_{user_id_sel}", use_container_width=True):
                                st.session_state[f'confirmar_exclusao_{user_id_sel}'] = False
                                st.rerun()

                    # Prescrições do usuário
                    if detalhes['prescricoes']:
                        st.markdown("### 📄 Prescrições recentes deste usuário")
                        df_presc = pd.DataFrame(detalhes['prescricoes'])
                        df_presc.columns = ['ID', 'Cliente', 'Cultura', 'Área (ha)', 'Data']
                        st.dataframe(df_presc, use_container_width=True, hide_index=True)

    with tab_logs:
        st.subheader("📋 Últimas Atividades no Sistema")
        st.caption("Registros de login, prescrições geradas, clientes cadastrados e outras ações.")

        logs = admin_logs_recentes(limite=100)
        if not logs:
            st.info("Nenhuma atividade registrada ainda.")
        else:
            df_logs = pd.DataFrame(logs)
            df_logs = df_logs[['criado_em', 'usuario_nome', 'usuario_email', 'acao', 'detalhes']]
            df_logs.columns = ['Data/Hora', 'Usuário', 'E-mail', 'Ação', 'Detalhes']
            st.dataframe(df_logs, use_container_width=True, hide_index=True)


st.divider()
st.caption(f"🌿 Felipe Amorim | Consultoria Agronômica — © {datetime.now().year}")
