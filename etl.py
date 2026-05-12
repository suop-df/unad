"""
ETL — Repositório UNAD (suop-df/unad)
Oracle (ORAPRD06) → JSON → GitHub Pages

Diferenças em relação ao externo/dashboard:
- Dados em data/json/ (JSON puro, sem compressão gz)
- Sem integração Supabase
- Sem fallback — GitHub Pages é a única fonte
"""

import os
import json
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# ── Variáveis de ambiente ────────────────────────────────────────────────────
DB_USER                  = os.getenv("DB_USER")
DB_PASSWORD              = os.getenv("DB_PASSWORD")
DB_DSN                   = os.getenv("DB_DSN", "10.69.1.118:1521/oraprd06")
ORACLE_CLIENT_PATH       = os.getenv("ORACLE_CLIENT_PATH", "")
DB_MIN_CONNECTIONS       = int(os.getenv("DB_MIN_CONNECTIONS", 1))
DB_MAX_CONNECTIONS       = int(os.getenv("DB_MAX_CONNECTIONS", 5))
DB_INCREMENT_CONNECTIONS = int(os.getenv("DB_INCREMENT_CONNECTIONS", 1))

SCHEMA_ANO = f"mil{datetime.now().year}"

# ── Queries ──────────────────────────────────────────────────────────────────
QUERIES = [
    {"file": "empenho.json", "sql_file": "empenho_volume.sql", "transform": "empenho"},
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "json")
SQL_DIR  = os.path.join(os.path.dirname(__file__), "data", "queries")

os.makedirs(DATA_DIR, exist_ok=True)


# ── Utilitários ──────────────────────────────────────────────────────────────

def serialize(value):
    """Converte tipos Oracle para tipos serializáveis em JSON."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def fetch(cursor, query):
    """Executa SQL e retorna lista de dicts com colunas em minúsculo."""
    cursor.execute(query)
    cols = [c[0].lower() for c in cursor.description]
    return [dict(zip(cols, (serialize(v) for v in row))) for row in cursor]


def save_json(filename, data):
    """Salva JSON em data/json/ com envelope padrão."""
    envelope = {
        "atualizado_em": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "total": len(data),
        "dados": data,
    }
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=False)
    print(f"  Salvo: {path} ({len(data)} registros)")


def read_sql(filename):
    """Lê arquivo SQL e substitui {SCHEMA_ANO}."""
    path = os.path.join(SQL_DIR, filename)
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    # Remove comentários de linha
    lines = [l for l in sql.splitlines() if not l.strip().startswith("--")]
    sql = "\n".join(lines)
    return sql.replace("{SCHEMA_ANO}", SCHEMA_ANO)


# ── Transformações ───────────────────────────────────────────────────────────

def build_empenho_data(rows):
    """
    Processa linhas brutas de empenho:
    - Extrai mês de dalancamento
    - Seleciona apenas as colunas usadas pelo dashboard
    - Arredonda valor para 2 casas
    - Remove espaços em campos de texto
    """
    resultado = []
    for r in rows:
        # Extrair mês da data de lançamento (formato ISO vindo do serialize)
        mes = None
        if r.get("dalancamento"):
            try:
                mes = int(r["dalancamento"][5:7])  # "YYYY-MM-DD..." → mês
            except (ValueError, IndexError):
                mes = None

        resultado.append({
            "coug":        r.get("coug"),
            "noug":        (r.get("noug") or "").strip(),
            "nune":        (r.get("nune") or "").strip(),
            "cofonte":     r.get("cofonte"),
            "indestinacao": r.get("indestinacao"),
            "gnd":         r.get("gnd"),
            "mes":         mes,
            "vadocumento": round(float(r.get("vadocumento") or 0), 2),
        })

    print(f"  Transformados: {len(resultado)} registros de empenho")
    return resultado


# ── Pipeline principal ───────────────────────────────────────────────────────

def run():
    import oracledb

    if ORACLE_CLIENT_PATH:
        oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_PATH)
        print(f"Oracle Instant Client: {ORACLE_CLIENT_PATH}")
    else:
        print("Oracle: thin mode")

    pool = oracledb.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        min=DB_MIN_CONNECTIONS,
        max=DB_MAX_CONNECTIONS,
        increment=DB_INCREMENT_CONNECTIONS,
    )

    with pool.acquire() as conn:
        with conn.cursor() as cur:
            for q in QUERIES:
                print(f"\n→ {q['sql_file']}")
                sql  = read_sql(q["sql_file"])
                rows = fetch(cur, sql)

                transform = q.get("transform")
                if transform == "empenho":
                    data = build_empenho_data(rows)
                else:
                    data = rows

                save_json(q["file"], data)

    pool.close()
    print("\nETL UNAD concluído.")


if __name__ == "__main__":
    run()
