#!/usr/bin/env python3
"""Genera dashboard.html (genérico, plugin cod-ops) con data.json embebido.
Uso: python3 build_dashboard.py [ruta/al/data.json]"""
import json, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "data.json")
data = json.load(open(DATA_PATH, encoding="utf-8"))
TIENDA = data.get("tienda", "Tienda")

HTML = r"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard Operacional — __TIENDA__</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
:root{--bg:#0f1115;--card:#1a1d24;--card2:#222630;--muted:#8b8f99;--text:#e8eaed;--green:#1baf7a;--red:#e34948;--blue:#3987e5;--amber:#eda100;--border:#2a2e37}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding:28px;max-width:1080px;margin:0 auto}
h1{font-size:22px;font-weight:500}h2{font-size:15px;font-weight:500;color:var(--muted);margin:26px 0 12px}
.sub{color:var(--muted);font-size:13px;margin-bottom:20px}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.chip{background:var(--card);border:1px solid var(--border);color:var(--text);padding:7px 14px;border-radius:20px;font-size:13px;cursor:pointer;transition:.15s}
.chip:hover{border-color:#3d4350}.chip.on{background:var(--blue);border-color:var(--blue);color:#fff}
.flbl{font-size:12px;color:var(--muted);margin:0 8px 0 0;align-self:center}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:8px}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px}
.kpi .l{font-size:12px;color:var(--muted)}.kpi .v{font-size:23px;font-weight:500;margin:3px 0}.kpi .h{font-size:11px;color:var(--muted)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}}
.box{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:7px 8px;text-align:right;border-bottom:1px solid var(--border)}th:first-child,td:first-child{text-align:left}
th{color:var(--muted);font-weight:500}
.pos{color:var(--green)}.neg{color:var(--red)}.warn{color:var(--amber)}
.bar{height:8px;background:var(--card2);border-radius:4px;overflow:hidden;margin-top:5px}.bar>span{display:block;height:100%}
.prov{background:rgba(237,161,0,.12);border:1px solid var(--amber);color:var(--amber);font-size:12px;padding:8px 12px;border-radius:8px;margin-bottom:14px}
.casc td:first-child{color:var(--muted)}
.tabs{display:flex;gap:4px;margin-bottom:20px;border-bottom:1px solid var(--border)}
.tab{padding:10px 16px;cursor:pointer;color:var(--muted);font-size:14px;border-bottom:2px solid transparent;margin-bottom:-1px}
.tab.on{color:var(--text);border-bottom-color:var(--blue)}
.page{display:none}.page.on{display:block}
</style></head><body>
<h1>Dashboard · __TIENDA__</h1>
<div class="sub">fuente: data.json · actualizado por Claude bajo demanda</div>

<div class="tabs">
  <div class="tab on" data-pg="op">Operacional</div>
  <div class="tab" data-pg="log">Reporte logístico</div>
</div>

<div class="page on" id="pageOp">
  <div class="filters" id="fmes"><span class="flbl">Periodo</span></div>
  <div class="filters" id="fprod"><span class="flbl">Producto</span></div>
  <div id="provbox"></div>
  <div class="kpis" id="kpis"></div>
  <h2>Pérdidas y ganancias</h2>
  <div class="grid2">
    <div class="box"><table class="casc" id="pyg"></table></div>
    <div class="box"><div style="position:relative;height:230px"><canvas id="chMes"></canvas></div></div>
  </div>
  <h2>Logística (resumen del periodo)</h2>
  <div class="kpis" id="log"></div>
  <h2>Confirmación de pedidos · tendencia <span style="font-size:11px;color:var(--muted)">(despachadas / resueltas, dato Dropi)</span></h2>
  <div class="grid2">
    <div class="box"><div style="position:relative;height:230px"><canvas id="chConf"></canvas></div></div>
    <div class="box"><table id="tconf"></table></div>
  </div>
  <h2>Rentabilidad por producto</h2>
  <div class="box"><table id="tprod"></table></div>
</div>

<div class="page" id="pageLog">
  <h2>Estado del piloto de ruteo</h2>
  <div class="box" id="ruteo"></div>
  <h2>Plan de acción por zona</h2>
  <div class="box"><table id="tplan"></table></div>
  <h2>Motivos de no-despacho <span style="font-size:11px;color:var(--muted)">(¿por qué no se confirma? ¿cobertura?)</span></h2>
  <div class="box" id="noDespacho"></div>
  <h2>Transportadoras (acumulado)</h2>
  <div class="box"><table id="ttransp"></table></div>
  <h2>Peores zonas — departamentos</h2>
  <div class="box"><table id="tdepto"></table></div>
  <h2>Matriz ciudad × transportadora (% entrega)</h2>
  <div class="box" style="overflow-x:auto"><table id="tmatriz"></table></div>
</div>

<script>
const DATA=__DATA__;
const MESES=Object.keys(DATA.meses).sort();
const NOM=DATA.meses_nombre||{};
const PRODS=DATA.productos||[];
let selMes='ALL', selProd='ALL';

const f0=v=>(v<0?'−$':'$')+Math.abs(Math.round(v)).toLocaleString('es-CO');
const fM=v=>(v<0?'−$':'$')+(Math.abs(v)/1e6).toFixed(2)+'M';
const pct=v=>(v==null?'—':v.toFixed(1)+'%');

function agg(){
  let ms = selMes==='ALL'?MESES:[selMes];
  ms = ms.filter(m=>!DATA.meses[m].provisional || selMes===m);
  let o={ingreso:0,cogs:0,flete:0,pauta:0,confirmaciones:0,comision:0,impuesto:0,apps:0,utilidad:0,
         ordenes:0,entregadas:0,devueltas:0,despachadas:0,shopify:0,prov:false};
  let prod={};
  ms.forEach(m=>{
    const M=DATA.meses[m]; if(M.provisional&&selMes===m)o.prov=true;
    o.shopify+=M.shopify_orders||0;
    const ps = selProd==='ALL'?Object.keys(M.productos):[selProd];
    ps.forEach(p=>{const d=M.productos[p];if(!d)return;
      ['ingreso','cogs','flete','pauta','confirmaciones','comision','impuesto','apps','utilidad','ordenes','entregadas','devueltas','despachadas'].forEach(k=>o[k]+=d[k]||0);
      prod[p]=prod[p]||{ingreso:0,pauta:0,utilidad:0,entregadas:0,devueltas:0,despachadas:0,total_entregado:0};
      ['ingreso','pauta','utilidad','entregadas','devueltas','despachadas','total_entregado'].forEach(k=>prod[p][k]+=d[k]||0);
    });
  });
  if(selProd==='ALL'){ms.forEach(m=>{const h=DATA.meses[m].pyg.pauta_huerfana||0;o.pauta+=h;o.utilidad-=h;});}
  o.tasa_entrega=o.despachadas?o.entregadas/o.despachadas*100:0;
  o.tasa_devol=o.despachadas?o.devueltas/o.despachadas*100:0;
  o.sincronizacion=o.shopify?o.ordenes/o.shopify*100:null;
  o.tasa_despacho=o.shopify?o.despachadas/o.ordenes*100:0;
  o.margen=o.ingreso?o.utilidad/o.ingreso*100:0;
  o.cpa=o.ordenes?o.pauta/o.ordenes:0;
  o.prods=prod;
  return o;
}

function render(){
  const o=agg();
  document.getElementById('provbox').innerHTML = o.prov?'<div class="prov">⚠ Periodo provisional: las entregas aún maduran (parte en tránsito) mientras la pauta ya está cargada. No representa el resultado final.</div>':'';
  document.getElementById('kpis').innerHTML=`
    ${kpi('Ingreso neto',f0(o.ingreso))}
    ${kpi('Utilidad',f0(o.utilidad),o.utilidad<0?'neg':'pos')}
    ${kpi('Margen',o.margen.toFixed(1)+'%',o.margen<0?'neg':'pos')}
    ${kpi('Pauta',f0(o.pauta))}
    ${kpi('CPA',f0(o.cpa))}`;
  const rows=[['Ingreso neto',o.ingreso,'pos'],['− Pauta',-o.pauta],['− Confirmaciones',-o.confirmaciones],['− Comisión',-o.comision],['− Impuesto',-o.impuesto],['− Apps',-o.apps],['= Utilidad',o.utilidad,o.utilidad<0?'neg':'pos']];
  document.getElementById('pyg').innerHTML='<tr><th>Concepto</th><th>'+(DATA.moneda||'COP')+'</th></tr>'+rows.map(r=>`<tr><td>${r[0]}</td><td class="${r[2]||''}">${f0(r[1])}</td></tr>`).join('');
  document.getElementById('log').innerHTML=`
    ${gauge('Sincronización',o.sincronizacion)}
    ${gauge('Confirmación',o.tasa_despacho)}
    ${gauge('Entrega',o.tasa_entrega)}
    ${kpi('Devolución',pct(o.tasa_devol),o.tasa_devol>30?'neg':'')}`;
  const ps=Object.keys(o.prods).filter(p=>o.prods[p].ingreso!==0||o.prods[p].pauta!==0);
  document.getElementById('tprod').innerHTML='<tr><th>Producto</th><th>Ingreso</th><th>Pauta</th><th>Entreg.</th><th>Devol.</th><th>Tasa entr.</th><th>Utilidad</th></tr>'+
    ps.map(p=>{const d=o.prods[p];const te=d.despachadas?d.entregadas/d.despachadas*100:0;
      return `<tr><td>${p}</td><td>${f0(d.ingreso)}</td><td>${f0(d.pauta)}</td><td>${d.entregadas}</td><td>${d.devueltas}</td><td>${te.toFixed(1)}%</td><td class="${d.utilidad<0?'neg':'pos'}">${f0(d.utilidad)}</td></tr>`}).join('');
  drawChart();
}
function kpi(l,v,c){return `<div class="kpi"><div class="l">${l}</div><div class="v ${c||''}">${v}</div></div>`}
function gauge(l,v){const col=v==null?'#8b8f99':(v>=75?'#1baf7a':v>=60?'#eda100':'#e34948');
  return `<div class="kpi"><div class="l">${l}</div><div class="v">${pct(v)}</div><div class="bar"><span style="width:${v||0}%;background:${col}"></span></div></div>`}

let chart;
function drawChart(){
  const lab=MESES.map(m=>NOM[m]||m);
  const ing=MESES.map(m=>DATA.meses[m].pyg.ingreso);
  const ut=MESES.map(m=>DATA.meses[m].pyg.utilidad);
  if(chart)chart.destroy();
  chart=new Chart(document.getElementById('chMes'),{type:'bar',
    data:{labels:lab,datasets:[
      {label:'Ingreso',data:ing,backgroundColor:'#3987e5',borderRadius:4},
      {label:'Utilidad',data:ut,backgroundColor:ut.map(v=>v<0?'#e34948':'#1baf7a'),borderRadius:4}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{labels:{color:'#8b8f99',boxWidth:10}},tooltip:{callbacks:{label:c=>c.dataset.label+': '+fM(c.raw)}}},
      scales:{x:{ticks:{color:'#8b8f99'},grid:{display:false}},y:{ticks:{color:'#8b8f99',callback:fM},grid:{color:'#2a2e37'}}}}});
}

let chConf;
function drawConf(){
  const ms=MESES.filter(m=>DATA.meses[m].confirmacion);
  const lab=ms.map(m=>NOM[m]||m);
  const tasa=ms.map(m=>DATA.meses[m].confirmacion.tasa);
  const bg=ms.map(m=>DATA.meses[m].provisional?'#eda100':'#3987e5');
  if(chConf)chConf.destroy();
  chConf=new Chart(document.getElementById('chConf'),{type:'line',
    data:{labels:lab,datasets:[{label:'Tasa de confirmación %',data:tasa,borderColor:'#3987e5',
      backgroundColor:'rgba(57,135,229,.12)',fill:true,tension:.3,
      pointBackgroundColor:bg,pointRadius:5,pointBorderColor:bg}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>{const m=ms[c.dataIndex],cf=DATA.meses[m].confirmacion;
        return [c.raw+'%'+(DATA.meses[m].provisional?' (provisional)':''),'desp '+cf.despachadas+' / resueltas '+cf.resueltas]}}}},
      scales:{x:{ticks:{color:'#8b8f99'},grid:{display:false}},
        y:{suggestedMin:50,suggestedMax:100,ticks:{color:'#8b8f99',callback:v=>v+'%'},grid:{color:'#2a2e37'}}}}});
  let h='<tr><th>Mes</th><th>Confirm.</th><th>Despach.</th><th>Cancel.</th><th>Rechaz.</th><th>Pend.</th></tr>';
  h+=ms.map(m=>{const c=DATA.meses[m].confirmacion;const pv=DATA.meses[m].provisional?' <span class="warn" style="font-size:10px">prov</span>':'';
    const cls=c.tasa>=80?'pos':c.tasa>=70?'warn':'neg';
    return '<tr><td>'+(NOM[m]||m)+pv+'</td><td class="'+cls+'">'+c.tasa+'%</td><td>'+c.despachadas+'</td><td>'+c.canceladas+'</td><td>'+c.rechazadas+'</td><td>'+c.pend_conf+'</td></tr>'}).join('');
  document.getElementById('tconf').innerHTML=h;
}
function chips(id,items,sel,cb){const c=document.getElementById(id);
  items.forEach(it=>{const b=document.createElement('span');b.className='chip'+(it.v===sel?' on':'');b.textContent=it.l;
    b.onclick=()=>{cb(it.v);[...c.querySelectorAll('.chip')].forEach(x=>x.classList.remove('on'));b.classList.add('on');render()};c.appendChild(b)})}
chips('fmes',[{l:'Todo',v:'ALL'}].concat(MESES.map(m=>({l:NOM[m]||m,v:m}))),'ALL',v=>selMes=v);
chips('fprod',[{l:'Todos',v:'ALL'}].concat(PRODS.map(p=>({l:p,v:p}))),'ALL',v=>selProd=v);

const L=DATA.logistica;
function colpct(v){if(v==null)return '—';const c=v>=75?'pos':v>=65?'warn':'neg';return '<span class="'+c+'">'+v+'%</span>'}
function sumDesp(o){return Object.values(o).reduce((a,c)=>a+(c.desp||0),0)}
function renderLog(){
  const R=L.ruteo;
  document.getElementById('ruteo').innerHTML=
    '<div style="font-size:14px;margin-bottom:10px">'+R.objetivo+'</div>'+
    '<table><tr><td>Estado</td><td class="warn">'+R.estado+'</td></tr>'+
    '<tr><td>Baseline ('+R.baseline.zona+' / '+R.baseline.transportadora+')</td><td>'+R.baseline.entrega+'% entrega · '+R.baseline.devolucion+'% devol</td></tr>'+
    '<tr><td>Candidata</td><td>'+R.candidata+'</td></tr>'+
    '<tr><td>Gate para escalar</td><td>entrega ≥ '+R.gate_escalado+'%</td></tr></table>'+
    (R.semanas.length?'<table style="margin-top:12px"><tr><th>Semana</th><th>Transp.</th><th>Desp.</th><th>Entreg.</th><th>% entrega</th></tr>'+
      R.semanas.map(s=>'<tr><td>'+s.fecha+'</td><td>'+s.transportadora+'</td><td>'+s.despachadas+'</td><td>'+s.entregadas+'</td><td>'+colpct(s.tasa_entrega)+'</td></tr>').join('')+'</table>'
      :'<div style="color:var(--muted);font-size:13px;margin-top:12px">Sin semanas de seguimiento aún.</div>');
  const PZ=R.plan_zonas||[]; const cf={'ALTA':'pos','MEDIA':'warn'};
  document.getElementById('tplan').innerHTML = PZ.length? '<tr><th>Zona</th><th>Hoy</th><th>Entrega</th><th>Acción</th><th>Alternativa (datos propios)</th><th>Confianza</th></tr>'+
    PZ.map(z=>'<tr><td>'+z.zona+'</td><td>'+z.actual+'</td><td>'+colpct(z.tasa)+'</td><td>'+
      (z.accion.indexOf('CAMBIAR')===0?'<span class="pos">':z.accion.indexOf('PROBAR')===0?'<span class="warn">':'<span style="color:var(--muted)">')+z.accion+'</span></td>'+
      '<td>'+(z.alt&&z.alt!=='—'?z.alt+(z.tasa_alt?' <span style="color:var(--muted);font-size:11px">('+z.tasa_alt+'%·n='+z.n+')</span>':''):'—')+'</td>'+
      '<td><span class="'+(cf[z.confianza]||'')+'" style="font-size:12px">'+z.confianza+'</span></td></tr>').join('')
    : '<tr><td style="color:var(--muted)">Sin plan de zonas configurado.</td></tr>';
  const ND=L.no_despacho;
  if(ND){
    const tl={'CANCELADO':'Canceló','RECHAZADO':'Rechazó (puerta / no estaba)','PENDIENTE/CONF':'Nunca confirmó (fantasma)'};
    const cinv=v=>'<span class="'+(v>=35?'neg':v>=25?'warn':'')+'">'+v+'%</span>';
    const via=Object.entries(ND.rescate_via||{}).map(([k,v])=>v+' '+k).join(', ');
    let h='<div style="font-size:13px;margin-bottom:12px;line-height:1.5">De <b>'+ND.total+'</b> no despachados, <b class="pos">'+ND.rescatados+'</b> fueron <b>re-ruteados</b> (recreados, no perdidos'+(via?': '+via:'')+'). <b class="neg">Pérdida real: '+ND.perdidos+'</b>.<br>El <b>'+ND.con_transportadora_pct+'%</b> tenía transportadora → <b>no es cobertura</b>, es confirmación.</div>';
    h+='<table><tr><th>Tipo de caída</th><th>Total</th><th>Re-ruteado</th><th>Pérdida real</th></tr>';
    Object.entries(ND.tipo).sort((a,b)=>b[1].total-a[1].total).forEach(([t,x])=>h+='<tr><td>'+(tl[t]||t)+'</td><td>'+x.total+'</td><td class="pos">'+x.rescatado+'</td><td class="neg">'+x.perdido+'</td></tr>');
    h+='</table><div style="font-size:13px;margin:14px 0 6px;color:var(--muted)">Departamentos con mayor tasa de PÉRDIDA REAL (foco geográfico):</div>';
    h+='<table><tr><th>Departamento</th><th>Perdidos</th><th>Total</th><th>Tasa</th></tr>';
    ND.top_departamentos.forEach(d=>h+='<tr><td>'+d.depto+'</td><td>'+d.perdido+'</td><td>'+d.total+'</td><td>'+cinv(d.tasa)+'</td></tr>');
    document.getElementById('noDespacho').innerHTML=h+'</table>';
  }
  const T=L.transportadoras;
  document.getElementById('ttransp').innerHTML='<tr><th>Transportadora</th><th>Desp.</th><th>Entreg.</th><th>Devol.</th><th>% entrega</th><th>% devol</th><th>Costo devol.</th></tr>'+
    Object.entries(T).sort((a,b)=>b[1].despachadas-a[1].despachadas).map(([t,x])=>'<tr><td>'+t+'</td><td>'+x.despachadas+'</td><td>'+x.entregadas+'</td><td>'+x.devueltas+'</td><td>'+colpct(x.tasa_entrega)+'</td><td class="'+(x.tasa_devolucion>30?'neg':'')+'">'+x.tasa_devolucion+'%</td><td>'+f0(x.costo_devoluciones)+'</td></tr>').join('');
  const D=L.departamentos;
  document.getElementById('tdepto').innerHTML='<tr><th>Departamento</th><th>Desp.</th><th>% entrega</th><th>% devol</th></tr>'+
    Object.entries(D).sort((a,b)=>a[1].tasa_entrega-b[1].tasa_entrega).map(([dp,x])=>'<tr><td>'+dp+'</td><td>'+x.despachadas+'</td><td>'+colpct(x.tasa_entrega)+'</td><td class="'+(x.tasa_devolucion>30?'neg':'')+'">'+x.tasa_devolucion+'%</td></tr>').join('');
  const Mx=L.matriz_ciudad_transp;
  const trs=[...new Set(Object.values(Mx).flatMap(o=>Object.keys(o)))];
  let h='<tr><th>Ciudad</th>'+trs.map(t=>'<th>'+t.slice(0,8)+'</th>').join('')+'</tr>';
  h+=Object.entries(Mx).sort((a,b)=>sumDesp(b[1])-sumDesp(a[1])).map(([ci,o])=>'<tr><td>'+ci+'</td>'+trs.map(t=>{const c=o[t];return '<td>'+(c?colpct(c.entrega)+' <span style="color:var(--muted);font-size:11px">('+c.desp+')</span>':'—')+'</td>'}).join('')+'</tr>').join('');
  document.getElementById('tmatriz').innerHTML=h;
}
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));t.classList.add('on');
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('on'));
  document.getElementById(t.dataset.pg==='op'?'pageOp':'pageLog').classList.add('on');
  if(t.dataset.pg==='log')renderLog();
});
render();
drawConf();
</script></body></html>"""

html = HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__TIENDA__", TIENDA)
out = os.path.join(os.path.dirname(DATA_PATH), "dashboard.html")
open(out, "w", encoding="utf-8").write(html)
print("OK ->", out)
