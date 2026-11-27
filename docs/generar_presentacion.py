import html
import json
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
slides = json.loads((raiz / 'docs' / 'presentacion_contenido.json').read_text(encoding='utf-8-sig'))
css = '''
@page { size: 13.333in 7.5in; margin: 0; }
* {box-sizing: border-box;}
body {margin:0; font-family: Arial, sans-serif; color:#142c44; background:#edf2f6;}
.slide {width:13.333in; height:7.5in; padding:0.55in 0.7in; background:white; break-after:page; position:relative; border-top:0.12in solid #128276; overflow:hidden;}
.slide:last-child {break-after:auto;}
.eyebrow {font-size:13pt; letter-spacing:2px; color:#128276; margin:0 0 16px;}
h1 {font-size:34pt; line-height:1.1; margin:0 0 12px;}
.subtitle {font-size:20pt; color:#547087; margin:0 0 22px;}
ul {margin:0; padding-left:28px;}
li {font-size:21pt; line-height:1.25; margin-bottom:15px;}
footer {position:absolute; bottom:0.35in; left:0.7in; right:0.7in; border-top:1px solid #cfdae3; padding-top:10px; font-size:12pt; color:#547087; display:flex; justify-content:space-between; gap:20px;}
@media screen {.slide {margin:20px auto; box-shadow:0 3px 15px #aab8c4;}}
'''
parts=[]
for i,s in enumerate(slides,1):
    bullets=''.join('<li>'+html.escape(p)+'</li>' for p in s['puntos'])
    parts.append('<section class="slide"><p class="eyebrow">STREAMRETAIN · SUSTENTACIÓN</p><h1>'+html.escape(s['titulo'])+'</h1><p class="subtitle">'+html.escape(s['subtitulo'])+'</p><ul>'+bullets+'</ul><footer><span>'+html.escape(s['nota'])+'</span><span>'+str(i)+' / '+str(len(slides))+'</span></footer></section>')
out=raiz/'Entregables'/'streamretain_presentacion_borrador.html'
out.write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>StreamRetain · Presentación</title><style>'+css+'</style><body>'+''.join(parts)+'</body></html>',encoding='utf-8')
print(out)
