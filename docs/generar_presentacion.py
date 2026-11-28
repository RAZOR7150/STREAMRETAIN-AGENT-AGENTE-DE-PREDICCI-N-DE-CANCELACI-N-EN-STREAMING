import html
import json
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
slides = json.loads((raiz / 'docs' / 'presentacion_contenido.json').read_text(encoding='utf-8-sig'))
css = '''
@page { size: 13.333in 7.5in; margin: 0; }
* {box-sizing: border-box;}
body {margin:0; font-family: Arial, sans-serif; color:#142c44; background:#edf2f6;}
.slide {width:13.333in; height:7.5in; padding:0.46in 0.64in; background:white; break-after:page; position:relative; border-top:0.1in solid #128276;}
.slide:last-child {break-after:auto;}
.eyebrow {font-size:12pt; letter-spacing:2px; color:#128276; margin:0 0 12px;}
h1 {font-size:31pt; line-height:1.1; margin:0 0 10px;}
.subtitle {font-size:18pt; color:#547087; margin:0 0 18px;}
ul {margin:0; padding-left:26px;}
li {font-size:21pt; line-height:1.25; margin-bottom:14px;}
.compact li {font-size:18pt; margin-bottom:10px;}
table {border-collapse:collapse; width:100%; margin:0 0 17px; font-size:18pt; line-height:1.2;}
th {text-align:left; background:#e1f2ee; color:#125b53;}
th,td {padding:10px 14px; border-bottom:1px solid #d6e2e8; vertical-align:top;}
tr:nth-child(even) td {background:#f5f8fa;}
.flow {display:flex; gap:10px; align-items:center; margin:0 0 22px;}
.flow span {padding:13px; border:1px solid #b6d5cd; background:#eef8f5; border-radius:5px; font-size:17pt; flex:1; text-align:center;}
.flow b {color:#128276;}
footer {position:absolute; bottom:0.28in; left:0.64in; right:0.64in; border-top:1px solid #cfdae3; padding-top:9px; font-size:11pt; color:#547087; display:flex; justify-content:space-between; gap:20px;}
footer span:first-child {max-width:92%;}
@media screen {.slide {margin:20px auto; box-shadow:0 3px 15px #aab8c4;}}
'''
parts=[]
for i,s in enumerate(slides,1):
    bullets=''.join('<li>'+html.escape(p)+'</li>' for p in s.get('puntos', []))
    content=''
    if 'flujo' in s:
        content+='<div class="flow">'+'<b>→</b>'.join('<span>'+html.escape(p)+'</span>' for p in s['flujo'])+'</div>'
    if 'tabla' in s:
        t=s['tabla']
        content+='<table><thead><tr>'+''.join('<th>'+html.escape(c)+'</th>' for c in t['cabecera'])+'</tr></thead><tbody>'
        content+=''.join('<tr>'+''.join('<td>'+html.escape(c)+'</td>' for c in row)+'</tr>' for row in t['filas'])+'</tbody></table>'
    parts.append('<section class="slide'+(' compact' if ('tabla' in s or 'flujo' in s) else '')+'"><p class="eyebrow">STREAMRETAIN · PROBLEMA, AGENTE Y EVIDENCIA</p><h1>'+html.escape(s['titulo'])+'</h1><p class="subtitle">'+html.escape(s['subtitulo'])+'</p>'+content+'<ul>'+bullets+'</ul><footer><span>'+html.escape(s['nota'])+'</span><span>'+str(i)+' / '+str(len(slides))+'</span></footer></section>')
out=raiz/'Entregables'/'streamretain_presentacion.html'
out.write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>StreamRetain · Presentación</title><style>'+css+'</style><body>'+''.join(parts)+'</body></html>',encoding='utf-8')
print(out)

