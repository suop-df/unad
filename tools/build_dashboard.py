import pandas as pd
import json

df = pd.read_excel(r'E:\empenho\exportar.xlsx', engine='openpyxl')
for col in ['NOUG', 'NUNE', 'NOEVENTO', 'DALANCAMENTO']:
    df[col] = df[col].str.strip()
df['VADOCUMENTO'] = df['VADOCUMENTO'].round(2)
df['MES'] = pd.to_datetime(df['DALANCAMENTO'], dayfirst=True).dt.month.astype(int)
df['FONTE_GRUPO'] = df['COFONTE'].apply(lambda x: str(x)[:4])

cols = ['COUG','NOUG','NUNE','COFONTE','INDESTINACAO','GND','MES','VADOCUMENTO']
data = df[cols].to_dict(orient='records')
dados_json = json.dumps(data, ensure_ascii=False, separators=(',',':'))

html_template = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard de Empenhos - GDF 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --azul:#1a3a5c; --azul2:#2563a8; --verde:#16a34a; --laranja:#d97706;
    --roxo:#7c3aed; --vermelho:#dc2626; --ciano:#0891b2;
    --cinza:#f1f5f9; --borda:#e2e8f0; --texto:#1e293b; --texto2:#64748b;
    --branco:#ffffff; --shadow:0 2px 8px rgba(0,0,0,0.08);
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Segoe UI',Arial,sans-serif;background:#eef2f7;color:var(--texto);}

  .header{background:linear-gradient(135deg,var(--azul) 0%,var(--azul2) 100%);
    color:#fff;padding:14px 28px;display:flex;align-items:center;
    justify-content:space-between;box-shadow:0 2px 12px rgba(0,0,0,0.2);flex-wrap:wrap;gap:8px;}
  .header h1{font-size:1.25rem;font-weight:700;}
  .header .sub{font-size:0.76rem;opacity:0.8;margin-top:2px;}
  .header-right{font-size:0.78rem;opacity:0.82;text-align:right;}

  .filtros-bar{background:var(--branco);border-bottom:1px solid var(--borda);
    padding:12px 28px;display:flex;flex-wrap:wrap;gap:12px;
    align-items:flex-end;box-shadow:var(--shadow);}
  .fg{display:flex;flex-direction:column;gap:3px;}
  .fg label{font-size:0.67rem;font-weight:700;color:var(--texto2);
    text-transform:uppercase;letter-spacing:0.5px;}
  .fg select{padding:5px 9px;border:1.5px solid var(--borda);border-radius:6px;
    font-size:0.8rem;color:var(--texto);background:var(--cinza);outline:none;
    transition:border-color 0.2s;min-width:140px;}
  .fg select:focus{border-color:var(--azul2);background:#fff;}
  .fg select[multiple]{min-height:68px;}
  .btn{padding:6px 16px;background:var(--azul2);color:#fff;border:none;
    border-radius:6px;font-size:0.8rem;font-weight:600;cursor:pointer;
    align-self:flex-end;transition:background 0.2s;}
  .btn:hover{background:var(--azul);}

  .main{padding:18px 28px;max-width:1600px;margin:0 auto;}

  .info-box{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
    padding:8px 13px;font-size:0.76rem;color:var(--azul2);margin-bottom:14px;}

  .cards-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:12px;margin-bottom:18px;}
  .card{background:var(--branco);border-radius:10px;padding:16px 18px;
    box-shadow:var(--shadow);border-top:4px solid var(--azul2);
    display:flex;flex-direction:column;gap:4px;
    transition:transform 0.15s,box-shadow 0.15s;}
  .card:hover{transform:translateY(-2px);box-shadow:0 5px 18px rgba(0,0,0,0.12);}
  .card.verde{border-top-color:var(--verde);}
  .card.laranja{border-top-color:var(--laranja);}
  .card.roxo{border-top-color:var(--roxo);}
  .card.verm{border-top-color:var(--vermelho);}
  .card.ciano{border-top-color:var(--ciano);}
  .card-label{font-size:0.66rem;font-weight:700;color:var(--texto2);
    text-transform:uppercase;letter-spacing:0.4px;}
  .card-value{font-size:1.45rem;font-weight:800;color:var(--texto);line-height:1;}
  .card-value.md{font-size:1.15rem;}
  .card-sub{font-size:0.7rem;color:var(--texto2);}
  .card-pct{font-size:0.72rem;color:var(--azul2);font-weight:600;}

  .stit{font-size:0.78rem;font-weight:700;color:var(--azul);text-transform:uppercase;
    letter-spacing:0.7px;margin-bottom:8px;padding-bottom:5px;
    border-bottom:2px solid var(--borda);display:flex;align-items:center;gap:8px;}
  .badge{background:var(--azul2);color:#fff;font-size:0.64rem;
    padding:2px 7px;border-radius:20px;font-weight:700;}

  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:18px;}
  .grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:18px;}
  @media(max-width:1000px){.grid2,.grid3{grid-template-columns:1fr;}}

  .painel{background:var(--branco);border-radius:10px;padding:16px 18px;
    box-shadow:var(--shadow);}

  .ctrl{display:flex;align-items:center;gap:9px;margin-bottom:8px;}
  .ctrl label{font-size:0.74rem;color:var(--texto2);font-weight:600;}
  .ctrl input[type=range]{width:90px;accent-color:var(--azul2);}
  .ctrl span{font-size:0.88rem;font-weight:700;color:var(--azul2);min-width:22px;}

  table{width:100%;border-collapse:collapse;font-size:0.77rem;}
  table th{background:var(--azul);color:#fff;padding:6px 8px;
    text-align:left;font-size:0.69rem;font-weight:600;}
  th.r,td.r{text-align:right;} th.c,td.c{text-align:center;}
  table tr:nth-child(even) td{background:var(--cinza);}
  table td{padding:5px 8px;border-bottom:1px solid var(--borda);}
  table tr:hover td{background:#dbeafe;}

  .rk{display:inline-flex;align-items:center;justify-content:center;
    background:var(--azul2);color:#fff;border-radius:50%;
    width:19px;height:19px;font-size:0.67rem;font-weight:700;}
  .rk.g{background:#d97706;} .rk.s{background:#94a3b8;} .rk.b{background:#b45309;}
  .bar-il{display:inline-block;height:6px;
    background:linear-gradient(90deg,var(--azul2),#60a5fa);
    border-radius:3px;vertical-align:middle;margin-left:5px;}

  .tabs{display:flex;gap:3px;margin-bottom:10px;}
  .tab{padding:5px 12px;border-radius:6px 6px 0 0;font-size:0.75rem;font-weight:600;
    cursor:pointer;border:1.5px solid var(--borda);border-bottom:none;
    background:var(--cinza);color:var(--texto2);transition:all 0.2s;}
  .tab.act{background:var(--azul2);color:#fff;border-color:var(--azul2);}
  .tbc{display:none;} .tbc.act{display:block;}

  .chart-wrap{position:relative;} .chart-wrap canvas{max-height:300px;}
  .chart-wrap.tall canvas{max-height:380px;}
  .pareto-info{font-size:0.72rem;color:var(--texto2);margin-top:6px;text-align:center;}

  .footer{text-align:center;padding:12px;font-size:0.69rem;color:var(--texto2);
    border-top:1px solid var(--borda);margin-top:10px;}

  /* TAG de mês ativo */
  .mes-tag{display:inline-block;background:var(--azul2);color:#fff;
    font-size:0.7rem;font-weight:700;padding:2px 10px;border-radius:12px;
    margin-left:8px;vertical-align:middle;}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>📊 Dashboard de Empenhos — GDF 2026</h1>
    <div class="sub">Acompanhamento por Mês · UG · Fonte de Recursos · GND</div>
  </div>
  <div class="header-right">
    <div id="hdr-val">—</div>
    <div id="hdr-qtd">—</div>
  </div>
</div>

<div class="filtros-bar">
  <div class="fg">
    <label>Mês</label>
    <select id="f-mes">
      <option value="">Todos os meses</option>
      <option value="1">Janeiro</option>
      <option value="2">Fevereiro</option>
      <option value="3">Março</option>
      <option value="4">Abril</option>
      <option value="5">Maio</option>
    </select>
  </div>
  <div class="fg">
    <label>Vinculação</label>
    <select id="f-tipo">
      <option value="">Todas</option>
      <option value="1">Não Vinculada</option>
      <option value="2">Vinculada</option>
    </select>
  </div>
  <div class="fg">
    <label>Fonte de Recurso</label>
    <select id="f-fonte" multiple title="Ctrl+clique para múltiplas">
      <option value="">— Todas —</option>
    </select>
  </div>
  <div class="fg">
    <label>GND</label>
    <select id="f-gnd" multiple title="Ctrl+clique para múltiplos">
      <option value="">— Todos —</option>
      <option value="1">Pessoal e Encargos Sociais</option>
      <option value="2">Juros e Encargos da Dívida</option>
      <option value="3">Outras Despesas Correntes</option>
      <option value="4">Investimentos</option>
      <option value="5">Inversões Financeiras</option>
      <option value="6">Amortização da Dívida</option>
    </select>
  </div>
  <button class="btn" onclick="limpar()">↺ Limpar</button>
</div>

<div class="main">
  <div class="info-box" id="infobox">ℹ️ Carregando dados...</div>

  <div class="cards-row">
    <div class="card">
      <div class="card-label">💰 Valor Total Empenhado</div>
      <div class="card-value md" id="c-val">—</div>
      <div class="card-pct" id="c-val-pct"></div>
    </div>
    <div class="card verde">
      <div class="card-label">📄 Qtd. Empenhos</div>
      <div class="card-value" id="c-qtd">—</div>
      <div class="card-pct" id="c-qtd-pct"></div>
    </div>
    <div class="card laranja">
      <div class="card-label">📊 Ticket Médio</div>
      <div class="card-value md" id="c-tick">—</div>
      <div class="card-sub">valor médio por empenho</div>
    </div>
    <div class="card roxo">
      <div class="card-label">🏢 UGs Ativas</div>
      <div class="card-value" id="c-ugs">—</div>
      <div class="card-sub" id="c-ugs-sub"></div>
    </div>
    <div class="card verm">
      <div class="card-label">🔗 Vinculada</div>
      <div class="card-value md" id="c-vinc">—</div>
      <div class="card-pct" id="c-vinc-pct"></div>
    </div>
    <div class="card ciano">
      <div class="card-label">⭕ Não Vinculada</div>
      <div class="card-value md" id="c-nvinc">—</div>
      <div class="card-pct" id="c-nvinc-pct"></div>
    </div>
  </div>

  <!-- TOP N -->
  <div class="grid2">
    <div class="painel">
      <div class="stit">🏆 Top UGs por Valor <span class="badge" id="b-tv">Top 10</span></div>
      <div class="ctrl">
        <label>Mostrar top:</label>
        <input type="range" min="5" max="30" value="10" id="sl-tv" oninput="renderTops()">
        <span id="lbl-tv">10</span>
      </div>
      <div style="overflow-x:auto">
        <table><thead><tr>
          <th class="c" style="width:28px">#</th><th>Unidade Gestora</th>
          <th class="r">Valor (R$)</th><th class="r">%</th><th class="r">Qtd</th>
        </tr></thead><tbody id="tb-tv"></tbody></table>
      </div>
    </div>
    <div class="painel">
      <div class="stit">📋 Top UGs por Qtd. de Empenhos <span class="badge" id="b-tq">Top 10</span></div>
      <div class="ctrl">
        <label>Mostrar top:</label>
        <input type="range" min="5" max="30" value="10" id="sl-tq" oninput="renderTops()">
        <span id="lbl-tq">10</span>
      </div>
      <div style="overflow-x:auto">
        <table><thead><tr>
          <th class="c" style="width:28px">#</th><th>Unidade Gestora</th>
          <th class="r">Qtd</th><th class="r">%</th><th class="r">Valor (R$)</th>
        </tr></thead><tbody id="tb-tq"></tbody></table>
      </div>
    </div>
  </div>

  <!-- PARETO -->
  <div class="painel" style="margin-bottom:18px">
    <div class="stit">📈 Análise de Pareto (80/20) — Concentração de Valor</div>
    <div class="tabs">
      <div class="tab act" onclick="switchTab('pt-ug',this)">Por Unidade Gestora</div>
      <div class="tab"     onclick="switchTab('pt-gnd',this)">Por GND</div>
    </div>
    <div id="pt-ug" class="tbc act">
      <div class="ctrl">
        <label>UGs no gráfico:</label>
        <input type="range" min="5" max="40" value="20" id="sl-pug" oninput="renderParetoUG()">
        <span id="lbl-pug">20</span>
      </div>
      <div class="chart-wrap tall"><canvas id="chPUG"></canvas></div>
      <div class="pareto-info" id="pi-ug"></div>
    </div>
    <div id="pt-gnd" class="tbc">
      <div class="chart-wrap"><canvas id="chPGND"></canvas></div>
      <div class="pareto-info" id="pi-gnd"></div>
    </div>
  </div>

  <!-- GRÁFICOS SECUNDÁRIOS -->
  <div class="grid3">
    <div class="painel">
      <div class="stit">🍩 Distribuição por GND (Valor)</div>
      <div class="chart-wrap"><canvas id="chGNDp"></canvas></div>
    </div>
    <div class="painel">
      <div class="stit">⚖️ Vinculada vs Não Vinculada</div>
      <div class="chart-wrap"><canvas id="chVinc"></canvas></div>
    </div>
    <div class="painel">
      <div class="stit">📊 Empenhos por Mês</div>
      <div class="chart-wrap"><canvas id="chMes"></canvas></div>
    </div>
  </div>

</div>

<div class="footer">
  Dashboard GDF 2026 — Dados: exportar.xlsx &nbsp;|&nbsp;
  Total de registros: <strong>TOTAL_COUNT</strong>
</div>

<script>
const DADOS = DADOS_PLACEHOLDER;

const GND_LABEL={1:'Pessoal e Encargos',2:'Juros e Encargos',
  3:'Outras Desp. Correntes',4:'Investimentos',
  5:'Inversões Financeiras',6:'Amortiz. da Dívida'};
const GND_COR={1:'#1d4ed8',2:'#dc2626',3:'#16a34a',
  4:'#d97706',5:'#7c3aed',6:'#0891b2'};
const MES_NOME={1:'Janeiro',2:'Fevereiro',3:'Março',
  4:'Abril',5:'Maio'};
const MES_COR=['#1d4ed8','#16a34a','#d97706','#7c3aed','#0891b2'];

let DF=[];
let cPUG=null,cPGND=null,cGNDp=null,cVinc=null,cMes=null;

function fv(v){
  if(v>=1e9) return 'R$ '+(v/1e9).toFixed(2).replace('.',',')+' Bi';
  if(v>=1e6) return 'R$ '+(v/1e6).toFixed(2).replace('.',',')+' Mi';
  if(v>=1e3) return 'R$ '+(v/1e3).toFixed(2).replace('.',',')+' Mil';
  return 'R$ '+v.toFixed(2).replace('.',',');
}
function fvf(v){return 'R$ '+v.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});}
function fn(n){return n.toLocaleString('pt-BR');}
function pct(a,b){return b===0?'0,0%':(a/b*100).toFixed(1).replace('.',',')+'%';}
function trunc(s,n){return s.length>n?s.substring(0,n)+'…':s;}
function _set(id,v){const el=document.getElementById(id);if(el)el.innerHTML=v;}

function init(){
  const fonteSet=new Set();
  DADOS.forEach(d=>fonteSet.add(String(d.COFONTE).substring(0,4)));
  const selF=document.getElementById('f-fonte');
  Array.from(fonteSet).sort().forEach(pre=>{
    const o=document.createElement('option');
    o.value=pre; o.textContent=pre; selF.appendChild(o);
  });
  ['f-mes','f-tipo','f-fonte','f-gnd'].forEach(id=>{
    document.getElementById(id).addEventListener('change',aplicar);
  });
  aplicar();
}

function getSel(id){
  return Array.from(document.getElementById(id).selectedOptions)
    .map(o=>o.value).filter(v=>v!=='');
}

function aplicar(){
  const mes=document.getElementById('f-mes').value,
        tipo=document.getElementById('f-tipo').value,
        prefixos=getSel('f-fonte'),
        gnds=getSel('f-gnd');

  DF=DADOS.filter(d=>{
    if(mes!==''       && String(d.MES)!==mes)                                return false;
    if(tipo!==''      && String(d.INDESTINACAO)!==tipo)                      return false;
    if(prefixos.length && !prefixos.some(p=>String(d.COFONTE).startsWith(p))) return false;
    if(gnds.length    && !gnds.includes(String(d.GND)))                      return false;
    return true;
  });

  const mesNome = mes!==''?MES_NOME[parseInt(mes)]:'';
  const ativos=[
    mesNome?mesNome:null,
    tipo!==''?(tipo==='1'?'Não Vinculada':'Vinculada'):null,
    prefixos.length?prefixos.length+' fonte(s)':null,
    gnds.length?'GND '+gnds.join(', '):null,
  ].filter(Boolean);

  document.getElementById('infobox').innerHTML = ativos.length===0
    ?'ℹ️ Exibindo todos os '+fn(DADOS.length)+' empenhos (Jan–Mai/2026). Use os filtros para segmentar.'
    :'🔍 Filtros: '+ativos.join(' | ')+
     ' — <strong>'+fn(DF.length)+'</strong> empenho(s) de '+fn(DADOS.length)+' total.';

  renderTudo();
}

function limpar(){
  document.getElementById('f-mes').value='';
  document.getElementById('f-tipo').value='';
  ['f-fonte','f-gnd'].forEach(id=>{
    Array.from(document.getElementById(id).options).forEach(o=>o.selected=false);
  });
  aplicar();
}

function renderTudo(){
  renderCards(); renderTops();
  renderParetoUG(); renderParetoGND();
  renderGNDp(); renderVinc(); renderMes();
}

function renderCards(){
  const tot=DADOS.reduce((s,x)=>s+x.VADOCUMENTO,0);
  const val=DF.reduce((s,x)=>s+x.VADOCUMENTO,0);
  const qtd=DF.length;
  const tick=qtd?val/qtd:0;
  const ugs=new Set(DF.map(x=>x.COUG));
  const ugAll=new Set(DADOS.map(x=>x.COUG));
  const vinc=DF.filter(x=>x.INDESTINACAO===2).reduce((s,x)=>s+x.VADOCUMENTO,0);
  const nvinc=DF.filter(x=>x.INDESTINACAO===1).reduce((s,x)=>s+x.VADOCUMENTO,0);

  _set('c-val',fv(val));       _set('c-val-pct',pct(val,tot)+' do total');
  _set('c-qtd',fn(qtd));       _set('c-qtd-pct',pct(qtd,DADOS.length)+' do total');
  _set('c-tick',fv(tick));
  _set('c-ugs',fn(ugs.size));  _set('c-ugs-sub','de '+ugAll.size+' UGs totais');
  _set('c-vinc',fv(vinc));     _set('c-vinc-pct',pct(vinc,val)+' do filtrado');
  _set('c-nvinc',fv(nvinc));   _set('c-nvinc-pct',pct(nvinc,val)+' do filtrado');
  _set('hdr-val','Total filtrado: '+fv(val));
  _set('hdr-qtd',fn(qtd)+' empenhos | '+fn(ugs.size)+' UGs');
}

function renderTops(){
  const nv=parseInt(document.getElementById('sl-tv').value);
  const nq=parseInt(document.getElementById('sl-tq').value);
  _set('lbl-tv',nv); _set('lbl-tq',nq);
  _set('b-tv','Top '+nv); _set('b-tq','Top '+nq);

  const ugMap=new Map();
  DF.forEach(d=>{
    if(!ugMap.has(d.COUG)) ugMap.set(d.COUG,{n:d.NOUG,v:0,q:0});
    const e=ugMap.get(d.COUG); e.v+=d.VADOCUMENTO; e.q++;
  });
  const lista=Array.from(ugMap.entries()).map(([c,e])=>({c,...e}));
  const totV=DF.reduce((s,x)=>s+x.VADOCUMENTO,0), totQ=DF.length;

  const topV=lista.slice().sort((a,b)=>b.v-a.v).slice(0,nv);
  document.getElementById('tb-tv').innerHTML=topV.map((e,i)=>{
    const bw=Math.round(e.v/topV[0].v*70);
    return `<tr><td class="c"><span class="rk ${i==0?'g':i==1?'s':i==2?'b':''}">${i+1}</span></td>
      <td title="${e.n}">${trunc(e.n,40)}<span class="bar-il" style="width:${bw}px"></span></td>
      <td class="r">${fvf(e.v)}</td><td class="r">${pct(e.v,totV)}</td><td class="r">${fn(e.q)}</td></tr>`;
  }).join('');

  const topQ=lista.slice().sort((a,b)=>b.q-a.q).slice(0,nq);
  document.getElementById('tb-tq').innerHTML=topQ.map((e,i)=>{
    const bw=Math.round(e.q/topQ[0].q*70);
    return `<tr><td class="c"><span class="rk ${i==0?'g':i==1?'s':i==2?'b':''}">${i+1}</span></td>
      <td title="${e.n}">${trunc(e.n,40)}<span class="bar-il" style="width:${bw}px"></span></td>
      <td class="r">${fn(e.q)}</td><td class="r">${pct(e.q,totQ)}</td><td class="r">${fvf(e.v)}</td></tr>`;
  }).join('');
}

function renderParetoUG(){
  const n=parseInt(document.getElementById('sl-pug').value);
  _set('lbl-pug',n);
  const ugMap=new Map();
  DF.forEach(d=>{
    if(!ugMap.has(d.COUG)) ugMap.set(d.COUG,{n:d.NOUG,v:0});
    ugMap.get(d.COUG).v+=d.VADOCUMENTO;
  });
  const sorted=Array.from(ugMap.values()).sort((a,b)=>b.v-a.v);
  const top=sorted.slice(0,n);
  const totAll=sorted.reduce((s,x)=>s+x.v,0);
  let cum=0;
  const labels=top.map(x=>trunc(x.n,22));
  const vals=top.map(x=>x.v);
  const acum=top.map(x=>{cum+=x.v;return parseFloat((cum/totAll*100).toFixed(2));});
  const idx80=acum.findIndex(v=>v>=80);
  const n80=idx80>=0?idx80+1:top.length;
  _set('pi-ug','📌 '+n80+' UG(s) concentram 80% do valor. Top '+n+' de '+sorted.length+
    ' UGs = '+pct(top.reduce((s,x)=>s+x.v,0),totAll));
  const ctx=document.getElementById('chPUG').getContext('2d');
  if(cPUG) cPUG.destroy();
  cPUG=new Chart(ctx,{
    data:{labels,datasets:[
      {type:'bar',label:'Valor',data:vals,
        backgroundColor:vals.map((_,i)=>i<n80?'#1d4ed8':'#93c5fd'),
        borderRadius:3,yAxisID:'y',order:2},
      {type:'line',label:'% Acumulado',data:acum,borderColor:'#dc2626',
        borderWidth:2.5,pointRadius:3,pointBackgroundColor:'#dc2626',
        yAxisID:'y2',order:1,tension:0.1,fill:false}
    ]},
    options:{responsive:true,interaction:{mode:'index',intersect:false},
      plugins:{legend:{position:'top',labels:{font:{size:10}}},
        tooltip:{callbacks:{label:c=>c.dataset.type==='bar'
          ?' Valor: '+fvf(c.raw):' Acum.: '+c.raw+'%'}}},
      scales:{
        x:{ticks:{font:{size:8},maxRotation:45,minRotation:30},grid:{display:false}},
        y:{position:'left',ticks:{callback:v=>fv(v),font:{size:9}},
          title:{display:true,text:'Valor (R$)',font:{size:9}}},
        y2:{position:'right',min:0,max:100,
          ticks:{callback:v=>v+'%',font:{size:9}},
          grid:{drawOnChartArea:false}}
      }}
  });
}

function renderParetoGND(){
  const gMap=new Map();
  DF.forEach(d=>gMap.set(d.GND,(gMap.get(d.GND)||0)+d.VADOCUMENTO));
  const sorted=Array.from(gMap.entries()).sort((a,b)=>b[1]-a[1]);
  const totAll=sorted.reduce((s,[,v])=>s+v,0);
  let cum=0;
  const labels=sorted.map(([k])=>GND_LABEL[k]||'GND '+k);
  const vals=sorted.map(([,v])=>v);
  const cores=sorted.map(([k])=>GND_COR[k]||'#94a3b8');
  const acum=sorted.map(([,v])=>{cum+=v;return parseFloat((cum/totAll*100).toFixed(2));});
  const idx80=acum.findIndex(v=>v>=80);
  _set('pi-gnd','📌 '+(idx80>=0?idx80+1:sorted.length)+' GND(s) concentram 80% do valor.');
  const ctx=document.getElementById('chPGND').getContext('2d');
  if(cPGND) cPGND.destroy();
  cPGND=new Chart(ctx,{
    data:{labels,datasets:[
      {type:'bar',label:'Valor',data:vals,backgroundColor:cores,borderRadius:5,yAxisID:'y',order:2},
      {type:'line',label:'% Acumulado',data:acum,borderColor:'#dc2626',
        borderWidth:2.5,pointRadius:5,pointBackgroundColor:'#dc2626',
        yAxisID:'y2',order:1,tension:0.1,fill:false}
    ]},
    options:{responsive:true,interaction:{mode:'index',intersect:false},
      plugins:{legend:{position:'top',labels:{font:{size:10}}},
        tooltip:{callbacks:{label:c=>c.dataset.type==='bar'
          ?' '+labels[c.dataIndex]+': '+fvf(c.raw):' Acum.: '+c.raw+'%'}}},
      scales:{
        x:{ticks:{font:{size:9}},grid:{display:false}},
        y:{position:'left',ticks:{callback:v=>fv(v),font:{size:9}}},
        y2:{position:'right',min:0,max:100,
          ticks:{callback:v=>v+'%',font:{size:9}},
          grid:{drawOnChartArea:false}}
      }}
  });
}

function renderGNDp(){
  const gMap=new Map();
  DF.forEach(d=>gMap.set(d.GND,(gMap.get(d.GND)||0)+d.VADOCUMENTO));
  const sorted=Array.from(gMap.entries()).sort((a,b)=>b[1]-a[1]);
  const tot=sorted.reduce((s,[,v])=>s+v,0);
  const ctx=document.getElementById('chGNDp').getContext('2d');
  if(cGNDp) cGNDp.destroy();
  cGNDp=new Chart(ctx,{type:'doughnut',
    data:{labels:sorted.map(([k])=>GND_LABEL[k]||'GND '+k),
      datasets:[{data:sorted.map(([,v])=>v),
        backgroundColor:sorted.map(([k])=>GND_COR[k]||'#94a3b8'),
        borderWidth:2,borderColor:'#fff'}]},
    options:{responsive:true,plugins:{
      legend:{position:'right',labels:{font:{size:9},boxWidth:10}},
      tooltip:{callbacks:{label:c=>' '+fv(c.raw)+' ('+pct(c.raw,tot)+')'}}}
    }
  });
}

function renderVinc(){
  const vinc=DF.filter(x=>x.INDESTINACAO===2).reduce((s,x)=>s+x.VADOCUMENTO,0);
  const nvinc=DF.filter(x=>x.INDESTINACAO===1).reduce((s,x)=>s+x.VADOCUMENTO,0);
  const tot=vinc+nvinc;
  const ctx=document.getElementById('chVinc').getContext('2d');
  if(cVinc) cVinc.destroy();
  cVinc=new Chart(ctx,{type:'doughnut',
    data:{labels:['Vinculada','Não Vinculada'],
      datasets:[{data:[vinc,nvinc],
        backgroundColor:['#1d4ed8','#0891b2'],borderWidth:2,borderColor:'#fff'}]},
    options:{responsive:true,plugins:{
      legend:{position:'right',labels:{font:{size:9}}},
      tooltip:{callbacks:{label:c=>' '+c.label+': '+fv(c.raw)+' ('+pct(c.raw,tot)+')'}}}
    }
  });
}

function renderMes(){
  const mMap=new Map();
  for(let m=1;m<=5;m++) mMap.set(m,{v:0,q:0});
  DF.forEach(d=>{
    if(mMap.has(d.MES)){mMap.get(d.MES).v+=d.VADOCUMENTO; mMap.get(d.MES).q++;}
  });
  const labels=[1,2,3,4,5].map(m=>MES_NOME[m]);
  const vals=[1,2,3,4,5].map(m=>mMap.get(m).v);
  const qtds=[1,2,3,4,5].map(m=>mMap.get(m).q);
  const ctx=document.getElementById('chMes').getContext('2d');
  if(cMes) cMes.destroy();
  cMes=new Chart(ctx,{
    data:{labels,datasets:[
      {type:'bar',label:'Valor',data:vals,
        backgroundColor:MES_COR,borderRadius:4,yAxisID:'y',order:2},
      {type:'line',label:'Qtd. Empenhos',data:qtds,
        borderColor:'#dc2626',borderWidth:2,pointRadius:4,
        pointBackgroundColor:'#dc2626',yAxisID:'y2',order:1,fill:false}
    ]},
    options:{responsive:true,interaction:{mode:'index',intersect:false},
      plugins:{legend:{position:'top',labels:{font:{size:10}}},
        tooltip:{callbacks:{label:c=>c.dataset.label==='Valor'
          ?' Valor: '+fvf(c.raw):' Empenhos: '+fn(c.raw)}}},
      scales:{
        x:{ticks:{font:{size:10}},grid:{display:false}},
        y:{position:'left',ticks:{callback:v=>fv(v),font:{size:9}},
          title:{display:true,text:'Valor',font:{size:9}}},
        y2:{position:'right',ticks:{callback:v=>fn(v),font:{size:9}},
          grid:{drawOnChartArea:false},
          title:{display:true,text:'Qtd.',font:{size:9}}}
      }}
  });
}

function switchTab(id,el){
  document.querySelectorAll('.tbc').forEach(t=>t.classList.remove('act'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('act'));
  document.getElementById(id).classList.add('act');
  el.classList.add('act');
  if(id==='pt-ug')  renderParetoUG();
  if(id==='pt-gnd') renderParetoGND();
}

init();
</script>
</body>
</html>'''

html_final = html_template.replace('DADOS_PLACEHOLDER', dados_json)
html_final = html_final.replace('TOTAL_COUNT', f'{len(data):,}'.replace(',','.'))

with open(r'E:\empenho\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

import os
size_kb = os.path.getsize(r'E:\empenho\dashboard.html') / 1024
print(f'Dashboard: {size_kb:.0f} KB | {len(data)} registros | meses 1-5')
