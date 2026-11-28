from pathlib import Path
import zipfile, copy, re, xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Entregables'; AS=ROOT/'docs'/'figuras_informe'; AS.mkdir(exist_ok=True)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
bold=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
im=Image.new('RGB',(1000,1020),'white');d=ImageDraw.Draw(im)
boxes=[('PREPARACION HISTORICA','Transacciones comprimidas y muestra de usuarios'),('Separacion por fecha','Historia previa | Seguimiento para etiquetas'),('Cohortes y validacion temporal','Marzo, junio y septiembre'),('Modelo congelado y evaluacion','Diciembre: V1 inicial / V4 exploratoria'),('USO DEL AGENTE','Formulario ficticio con diez caracteristicas'),('Decision trazable','Puntaje, umbral, explicacion y registro')]
for i,(title,sub) in enumerate(boxes):
 y=15+i*167;d.rounded_rectangle((15,y,985,y+125),radius=12,fill='#f0f3f6',outline='#263d52',width=3)
 d.text((500,y+24),title,font=bold(30),fill='#152c40',anchor='mt');d.text((500,y+72),sub,font=font(28),fill='black',anchor='mt')
 if i<5:
  d.line((500,y+130,500,y+157),fill='#263d52',width=5);d.polygon([(489,y+148),(511,y+148),(500,y+161)],fill='#263d52')
im.save(AS/'arquitectura_informe.png')
im=Image.new('RGB',(1100,750),'white');d=ImageDraw.Draw(im)
labels=['Arbol V1: media validacion','Arbol ampliado: media validacion','Bosque: media validacion','V4: media validacion','Arbol V1: diciembre','V4: diciembre exploratorio'];vals=[.4490399112,.4572674497,.4482495765,.5397526713,.3461538462,.4205426357]
x0=560;scale=700
for i,(label,v) in enumerate(zip(labels,vals)):
 y=100+i*92;d.text((15,y+16),label,font=font(27),fill='black');d.rectangle((x0,y,x0+v*scale,y+57),fill='#385d7b' if i<4 else '#777777');d.text((x0+v*scale+10,y+16),format(v,'.4f'),font=font(25),fill='black')
xx=x0+.5*scale;d.line((xx,65,xx,650),fill='#a23030',width=4);d.text((xx,20),'Meta 0,50',font=bold(26),fill='#a23030',anchor='mt');d.text((20,700),'Azul: desarrollo | Gris: diciembre (distinto uso experimental)',font=font(27),fill='black')
im.save(AS/'resultados_informe.png')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PR='http://schemas.openxmlformats.org/package/2006/relationships'
E.register_namespace('w',W);E.register_namespace('r',R)
def el(tag,attrs={},parent=None):
 n=E.Element('{'+W+'}'+tag,{'{'+W+'}'+k:str(v) for k,v in attrs.items()})
 if parent is not None:parent.append(n)
 return n
with zipfile.ZipFile(ROOT/'context/docs/ieee_template.dotx') as z: files={n:z.read(n) for n in z.namelist()}
old=E.fromstring(files['word/document.xml']);base=copy.deepcopy(old.findall('.//{'+W+'}sectPr')[-1])
def sect(cols=2,typ='continuous'):
 s=copy.deepcopy(base)
 for n in list(s):
  if n.tag in ['{'+W+'}type','{'+W+'}cols','{'+W+'}docGrid']:s.remove(n)
 el('type',{'val':typ},s);el('cols',{'num':cols,'space':360},s)
 # retain page size and side/top margins from supplied template, use standard usable bottom margin
 s.find('{'+W+'}pgMar').set('{'+W+'}bottom','1077')
 return s
root=el('document');body=el('body',parent=root)
rels=E.Element('{'+PR+'}Relationships');rid=0
for typ,target,id_ in [('numbering','numbering.xml','rIdNumbering'),('styles','styles.xml','rIdStyles'),('settings','settings.xml','rIdSettings'),('fontTable','fontTable.xml','rIdFonts'),('theme','theme/theme1.xml','rIdTheme')]:
 E.SubElement(rels,'{'+PR+'}Relationship',{'Id':id_,'Type':R+'/'+typ,'Target':target})
def para(text='',style='IETParagraph',size=21,b=False,align='both',keep=False):
 p=el('p',parent=body);pp=el('pPr',parent=p);el('pStyle',{'val':style},pp);el('jc',{'val':align},pp);el('spacing',{'after':80,'line':240,'lineRule':'auto'},pp);el('ind',{'firstLine':0,'left':0,'right':0},pp);np=el('numPr',parent=pp);el('numId',{'val':0},np);el('pageBreakBefore',{'val':0},pp)
 el('widowControl',parent=pp)
 if keep:el('keepNext',parent=pp)
 r=el('r',parent=p);rp=el('rPr',parent=r);el('rFonts',{'ascii':'Times New Roman','hAnsi':'Times New Roman','cs':'Times New Roman'},rp);el('sz',{'val':size},rp);el('color',{'val':'000000'},rp)
 if b:el('b',parent=rp)
 t=el('t',parent=r);t.text=text
 return p
picid=0
for line in (ROOT/'docs/informe_ieee_contenido.txt').read_text(encoding='utf-8-sig').splitlines():
 if not line.strip():continue
 if line.startswith('@tabla '):
  table_rows=[line[7:].split(';')];continue
 if ';' in line and 'table_rows' in locals() and not line.startswith('@fintabla'):
  table_rows.append(line.split(';'));continue
 if line.startswith('@fintabla'):
  # transpose for legible single-column width
  rows=list(map(list,zip(*table_rows)));rows[0]=['Metrica','Base','Log. V1','Arbol V1','V4*']
  tbl=el('tbl',parent=body);props=el('tblPr',parent=tbl);el('tblW',{'w':4962,'type':'dxa'},props);el('tblLayout',{'type':'fixed'},props)
  borders=el('tblBorders',parent=props)
  for side in ['top','bottom','insideH']:el(side,{'val':'single','sz':4,'color':'AAAAAA'},borders)
  grid=el('tblGrid',parent=tbl)
  for width in [1250,928,928,928,928]:el('gridCol',{'w':width},grid)
  for i,row in enumerate(rows):
   tr=el('tr',parent=tbl);tp=el('trPr',parent=tr);el('cantSplit',parent=tp)
   for j,txt in enumerate(row):
    tc=el('tc',parent=tr);cp=el('tcPr',parent=tc);el('tcW',{'w':1250 if j==0 else 928,'type':'dxa'},cp)
    p=para(txt,size=17,b=i==0,align='left',keep=True);body.remove(p);tc.append(p)
  para(line.split(' ',1)[1],style='IETFigureCaption',size=18,align='left');del table_rows;continue
 if line in ['@referencias','@anexos']:
  p=para(size=2);p.find('{'+W+'}pPr').append(sect(2 if line=='@referencias' else 1,'continuous' if line=='@referencias' else 'nextPage'));continue
 if line.startswith('# '):para(line[2:],'IETPaperTitle',32,True,'center',True)
 elif line.startswith('@autor '):para(line[7:],size=23,align='center',keep=True)
 elif line.startswith('@afiliacion '):para(line[12:],size=20,align='center',keep=True)
 elif line.startswith('@curso '):para(line[7:],size=18,align='center',keep=True)
 elif line.startswith('@resumen '):para(line[9:],'IETAbstractText',20,False,'both')
 elif line.startswith('@palabras '):
  p=para(line[10:],size=20);p.find('{'+W+'}pPr').append(sect(1))
 elif line.startswith('## '):para(line[3:],'IETHeading1',22,True,'left',True)
 elif line.startswith('### '):para(line[4:],'IETHeading2',21,True,'left',True)
 elif line.startswith('@link '):
  url=line[6:];rid+=1;ident='rIdLink'+str(rid);E.SubElement(rels,'{'+PR+'}Relationship',{'Id':ident,'Type':R+'/hyperlink','Target':url,'TargetMode':'External'})
  p=para('',size=20,align='left');h=E.SubElement(p,'{'+W+'}hyperlink',{'{'+R+'}id':ident});r=el('r',parent=h);rp=el('rPr',parent=r);el('color',{'val':'154C79'},rp);el('sz',{'val':20},rp);el('u',{'val':'single'},rp);el('t',parent=r).text=url
 elif line.startswith('@fig '):
  filename,caption=line[5:].split('|',1);picid+=1;ident='rIdPic'+str(picid);E.SubElement(rels,'{'+PR+'}Relationship',{'Id':ident,'Type':R+'/image','Target':'media/'+filename});files['word/media/'+filename]=(AS/filename).read_bytes()
  im=Image.open(AS/filename);cx=3100000;cy=int(cx*im.height/im.width)
  p=para('',size=2,align='center',keep=True);r=el('r',parent=p)
  drawing=E.fromstring(f'''<w:drawing xmlns:w="{W}" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" xmlns:r="{R}"><wp:inline><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{picid}" name="{filename}" descr="{caption}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="{filename}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{ident}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>''');r.append(drawing);para(caption,'IETFigureCaption',18,False,'left')
 else:para(line,size=20 if line.startswith('[') else 21)
body.append(sect(1,'nextPage'))
files['word/document.xml']=E.tostring(root,encoding='utf-8',xml_declaration=True);files['word/_rels/document.xml.rels']=E.tostring(rels,encoding='utf-8',xml_declaration=True)
ct=E.fromstring(files['[Content_Types].xml']);nsct='http://schemas.openxmlformats.org/package/2006/content-types'
for x in ct:
 if x.get('PartName')=='/word/document.xml':x.set('ContentType','application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml')
if not any(x.get('Extension')=='png' for x in ct):E.SubElement(ct,'{'+nsct+'}Default',{'Extension':'png','ContentType':'image/png'})
files['[Content_Types].xml']=E.tostring(ct,encoding='utf-8',xml_declaration=True)
# Remove stale template personal metadata and links to the original template.
files['word/settings.xml']=re.sub(rb'<w:attachedTemplate[^>]*/>',b'',files['word/settings.xml'])
files['docProps/core.xml']=b'''<?xml version="1.0" encoding="UTF-8"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>StreamRetain-Agent - Informe final</dc:title><dc:creator>Levis Adrian Ortiz Cano</dc:creator><dc:description>Informe academico con asistencia de IA declarada.</dc:description></cp:coreProperties>'''
path=OUT/'streamretain_hito3.docx'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in files.items():z.writestr(n,v)
print('DOCX',path)
print('Words',len((ROOT/'docs/informe_ieee_contenido.txt').read_text(encoding='utf-8-sig').split()))
