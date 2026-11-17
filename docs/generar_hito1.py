"""Genera la maqueta HTML del hito 1 a partir del Markdown, sin dependencias."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parent
source = (ROOT / "streamretain_hito1.md").read_text(encoding="utf-8-sig")

def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text.replace("  \n", "<br>")

header, body = [], []
started = False
for block in source.strip().split("\n\n"):
    if block.startswith("## "):
        started = True
        part = "<h2>" + inline(block[3:]) + "</h2>"
    elif block.startswith("# "):
        part = "<h1>" + inline(block[2:]) + "</h1>"
    else:
        part = "<p>" + inline(block) + "</p>"
    (body if started else header).append(part)

css = """
@page { size: Letter; margin: 14mm 19mm 15mm; }
* {box-sizing:border-box}
body {font-family:'Times New Roman',serif;font-size:10pt;line-height:1.13;color:#000;margin:0}
header {text-align:center;margin-bottom:9pt}
header p {margin:0 0 4pt;text-align:center;font-size:10pt}
header p:first-child {font-size:11pt}
h1 {font-size:15pt;margin:6pt 0 4pt;line-height:1.1}
h2 {font-size:11pt;color:#2e74b5;margin:6pt 0 3pt;break-after:avoid}
p {margin:0 0 4pt;text-align:justify;orphans:2;widows:2}
footer {position:fixed;bottom:0;right:0;font-size:9pt;color:#444}
main p:last-child {font-size:8pt;line-height:1.1;text-align:left;overflow-wrap:anywhere}
@media screen {
 html {background:#ddd}
 body {background:white;width:816px;min-height:1056px;margin:0;padding:53px 72px 57px}
 footer {position:absolute;top:1020px;right:72px;bottom:auto}
}
"""
document = ('<!doctype html><html lang="es"><meta charset="utf-8">'
            '<title>StreamRetain - Hito 1</title><style>' + css + '</style>'
            '<body><header>' + ''.join(header) + '</header><main>'
            + ''.join(body) + '</main><footer>Página 1</footer></body></html>')
(ROOT / "streamretain_hito1.html").write_text(document, encoding="utf-8")
print("Maqueta HTML generada.")
