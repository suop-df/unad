# Dashboards UNAD — SUOP/SEEC

Dashboards de acompanhamento interno produzidos pela UNAD/SUOP, publicados via GitHub Pages e alimentados por ETL automatizado a partir do banco Oracle.

🔗 **Acesso:** https://suop-df.github.io/unad/

---

## Arquitetura

```
Oracle (ORAPRD06)
    ↓ etl.py  (Python + oracledb)
    └── data/json/*.json  →  git push  →  GitHub Pages
                                               ↓
                                      Dashboards HTML
                              (browser busca JSON diretamente)
```

O ETL roda automaticamente todo dia às **06:00 (horário de Brasília)** via GitHub Actions com runner self-hosted instalado na estação da rede local do GDF.

> **Diferença em relação ao repositório `dashboard`:** sem Supabase (GitHub Pages é fonte única) e sem compressão gz — os dados são JSON puro, volume menor.

---

## Dashboards disponíveis

| Dashboard | URL |
|-----------|-----|
| Empenhos | https://suop-df.github.io/unad/empenho/ |

---

## Estrutura do projeto

```
├── index.html                    # Redireciona para empenho/
├── etl.py                        # ETL: Oracle → JSON
├── requirements.txt              # Dependências Python
├── .env                          # Credenciais (não versionado)
├── roadmap.md                    # Roadmap do projeto
├── .github/
│   └── workflows/
│       └── etl.yml               # Workflow de automação (Actions)
├── data/
│   ├── json/                     # JSONs gerados pelo ETL (commitados)
│   │   └── empenho.json
│   └── queries/                  # SQLs das extrações
│       └── empenho_volume.sql
├── empenho/
│   └── index.html                # Dashboard de Empenhos
└── tools/                        # Arquivos de referência (não versionados)
```

---

## Configuração do ambiente

### 1. Pré-requisitos

- Python 3.10+
- Acesso à rede do GDF (VPN ou máquina interna)
- Oracle Instant Client 19.x em `C:\oracle\instantclient_19_30`

### 2. Instalar dependências

```cmd
py -m pip install -r requirements.txt
```

### 3. Configurar credenciais

Crie o arquivo `.env` na raiz do projeto:

```env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_DSN=10.69.1.118:1521/oraprd06
ORACLE_CLIENT_PATH=C:\oracle\instantclient_19_30
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=5
DB_INCREMENT_CONNECTIONS=1
```

### 4. Executar o ETL manualmente

```cmd
cd E:\Projetos\unad
py etl.py
```

Os arquivos `.json` serão gerados em `data/json/`.

---

## GitHub Actions — Runner self-hosted

O workflow `etl.yml` roda via runner self-hosted registrado na organização `suop-df`, instalado em `E:\Actions-runner` na estação de trabalho do James (james.coelho). O runner é iniciado automaticamente via **Agendador de Tarefas do Windows** ao fazer login.

### Secrets necessários no repositório

Configure em Settings → Secrets → Actions:

| Secret | Descrição |
|--------|-----------|
| `DB_USER` | Usuário Oracle |
| `DB_PASSWORD` | Senha Oracle |
| `DB_DSN` | DSN de conexão (`10.69.1.118:1521/oraprd06`) |
| `ORACLE_CLIENT_PATH` | Caminho do Oracle Instant Client |
| `DB_MIN_CONNECTIONS` | Mínimo de conexões no pool |
| `DB_MAX_CONNECTIONS` | Máximo de conexões no pool |
| `DB_INCREMENT_CONNECTIONS` | Incremento do pool |

---

## Adicionar novo dataset

1. Criar query SQL em `data/queries/NOME.sql`
2. Adicionar entrada em `QUERIES` no `etl.py`:
   ```python
   {"file": "nome.json", "sql_file": "NOME.sql"},
   ```
3. Criar dashboard HTML em `nome/index.html`
4. Registrar link no `index.html` raiz

---

## Git — Padrão de commits de dados

Os arquivos em `data/json/` usam **amend + force push** — nunca acumulam histórico:

```
chore: atualiza dados ETL 2026-05-12 06:00 UTC  ← sempre 1 único commit de dados
```

Commits de código e HTML seguem o fluxo normal.

---

*suop-df/SUOP — Subsecretaria de Orçamento e Planejamento*
