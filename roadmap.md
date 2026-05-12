# Roadmap — suop-df/unad

---

## ✅ Concluído

- Estrutura do repositório (pastas, ETL, workflow)
- Query SQL de empenho (`empenho_volume.sql`) com `{SCHEMA_ANO}` dinâmico
- ETL (`etl.py`) com transform de empenho
- Dashboard de empenhos (`empenho/index.html`)
- GitHub Pages habilitado — https://suop-df.github.io/unad/
- Disparador automático às 06:00 integrado ao `disparar-etl.ps1` existente
- Runner self-hosted registrado na organização `suop-df` (atende todos os repos)
- Runner self-hosted registrado na organização `suop-df` (atende todos os repos)

---

## 🔄 Em andamento

---

## 📋 Pendente

### Dashboard com atualização a cada 1 hora

**Contexto:** um futuro dashboard precisará atualizar os dados de hora em hora.

**Solução recomendada:** agendador Windows chamando o ETL diretamente (sem GitHub Actions)

- Criar `E:\Actions-runner\etl-unad-local.ps1`:
  - Roda `py etl.py` em `E:\Projetos\unad`
  - Faz `git add`, `git commit --amend` e `git push --force` do JSON gerado
- Criar tarefa agendada `ETL-UNAD-Horario` com trigger a cada 1 hora
- **Motivo para não usar GitHub Actions:** o runner depende da estação logada;
  o agendador Windows é mais robusto para ciclos curtos e não passa pelo GitHub
- Runner separado para o unad pode ser avaliado se os ETLs precisarem rodar em paralelo

---

### Botão "Atualizar Dados" no dashboard

**Contexto:** ao clicar no botão, o ETL roda no Oracle e os dados são atualizados sem intervenção manual.

**Por que não é simples:** o navegador não consegue acessar o Oracle diretamente.
Alguém precisa fazer o meio-campo entre o clique e o banco.

**Solução recomendada: API na rede interna (GDF)**

- Servidor Python (Flask ou FastAPI) rodando na estação com IP fixo na rede GDF
- Botão no dashboard → `POST http://10.x.x.x:8000/atualizar` → servidor roda ETL → retorna JSON atualizado
- Qualquer dispositivo na rede GDF (PC, celular via Wi-Fi) alcança o endpoint
- **Pré-requisito:** estação com IP fixo ou reserva de DHCP
- **Dependência:** implementar junto com o dashboard de atualização horária (mesma API serve os dois casos)

**Limitação importante:**

| Cenário | Dashboard (visualizar) | Botão Atualizar |
|---------|----------------------|-----------------|
| Qualquer lugar (celular 4G, casa) | ✅ GitHub Pages | ❌ API interna inacessível |
| Rede GDF (Wi-Fi do trabalho) | ✅ GitHub Pages | ✅ API interna acessível |

O dashboard e os dados são sempre acessíveis de qualquer lugar via GitHub Pages.
O botão de atualizar só funciona dentro da rede GDF (ou via VPN).
Para funcionar de qualquer lugar seria necessário expor a API para a internet
(IP público ou tunnel como ngrok) — o que envolve questões de segurança da rede GDF.

**Opções descartadas:**
- Botão via GitHub Actions API — PAT ficaria exposto no HTML público; depende do runner ativo
- API local (`localhost`) — não alcançável por celular ou outros dispositivos

---

## 💡 Futuro

- Novos datasets além de empenho (ex.: receita, pessoal, projetos)
- Atualizar `index.html` raiz com menu de dashboards quando houver mais de um
