# CLAUDE.md — Dados Internos GDF

Documento de contexto para o Claude Code. Leia antes de qualquer intervenção.

---

## Visão Geral

Dashboards e relatórios unads do Governo do Distrito Federal, publicados via **GitHub Pages** e alimentados por ETL automatizado a partir do banco Oracle.

- **Organização GitHub:** suop-df
- **Repositório:** unad
- **URL:** https://suop-df.github.io/unad/
- **Responsável técnico:** James (james.coelho) — ContDF/SEEC

---

## Diferenças em relação ao repositório público (publico)

| Aspecto | publico | unad |
|---------|------------------|---------|
| Formato dos dados | `data/gz/*.json.gz` (comprimido) | `data/json/*.json` (puro) |
| Fallback | Supabase automático | Nenhum — GitHub Pages é fonte única |
| Público | Qualquer pessoa | URL não divulgada amplamente |
| Compressão | gzip nível 9 | Sem compressão |

---

## Arquitetura

```
Oracle (ORAPRD06)  →  etl.py (Python + oracledb)
                        └── data/json/*.json  →  git push  →  GitHub Pages
                                                                     ↓
                                                            Dashboards HTML
```

---

## ETL — etl.py

### Adicionar novo dataset

1. Criar query SQL em `data/queries/NOME.sql`
2. Adicionar entrada em `QUERIES` no `etl.py`:
   ```python
   {"file": "nome.json", "sql_file": "NOME.sql"},
   ```
3. Criar dashboard HTML que busca `data/json/nome.json`
4. Registrar link no `index.html`

### Executar manualmente

```cmd
cd E:\Projetos\unad
py etl.py
```

### Instalar dependências

```cmd
py -m pip install -r requirements.txt
```

---

## GitHub Actions — Workflow

Arquivo: `.github/workflows/etl.yml`

- `runs-on: self-hosted` — mesmo runner de `publico` (`DSK2035728`)
- Trigger: `workflow_dispatch` (manual ou via agendador Windows)
- Commita `data/json/` com padrão **amend + force push** — não acumula histórico de dados

### Adicionar ao disparador ETL (se necessário workflow separado)

Criar `E:\Actions-runner\disparar-etl-unad.ps1` seguindo o mesmo padrão de `disparar-etl.ps1`, apontando para o workflow `etl.yml` do repo `unad`.

---

## Runner Self-Hosted

- **Localização:** `E:\Actions-runner\`
- **Usuário:** seap\james.coelho
- **Inicialização:** Tarefa `GitHubActionsRunner` (AtLogOn, via run-hidden.vbs)
- Mesmo runner compartilhado com o repo `publico`

---

## GitHub Secrets — obrigatórios

Acessar: https://github.com/suop-df/unad/settings/secrets/actions

| Secret | Valor |
|--------|-------|
| `DB_USER` | usuário Oracle |
| `DB_PASSWORD` | senha Oracle |
| `DB_DSN` | `10.69.1.118:1521/oraprd06` |
| `ORACLE_CLIENT_PATH` | `C:\oracle\instantclient_19_30` |
| `DB_MIN_CONNECTIONS` | `1` |
| `DB_MAX_CONNECTIONS` | `5` |
| `DB_INCREMENT_CONNECTIONS` | `1` |

---

## Git — Padrão de commits

- Dados em `data/json/` → sempre **amend + force push** (nunca acumula histórico)
- Código/HTML → commit normal

## Contexto de Desenvolvimento

- Repositório local: `E:\Projetos\unad`
- Usar `py` em vez de `python` ou `python3` no Windows desta máquina.
