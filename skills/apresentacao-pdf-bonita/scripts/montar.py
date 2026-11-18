#!/usr/bin/env python3
"""Monta uma apresentação em PDF (1920x1080), preto e branco, a partir de um conteudo.json.

Uso:
    python3 montar.py caminho/do/conteudo.json [--pptx] [--sem-abrir]

Sai na pasta do conteudo.json:
    <nome>.pdf          a apresentação
    _build/apresentacao.html  o HTML que gerou o PDF (abre no navegador)
    _build/folha.png    as miniaturas de todas as páginas, para conferir de uma vez
    <nome>.pptx         só com --pptx: uma imagem por slide

Precisa de Google Chrome (ou Chromium/Edge). Para a folha e o PPTX: poppler (pdftoppm), Pillow e python-pptx.
"""
import html
import json
import os
import shutil
import subprocess
import sys
import glob

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(AQUI)
ASSETS = os.path.join(SKILL, 'assets')

# ---------------------------------------------------------------- ícones (traço, viewBox 48)
ICONES = {
    'estrada': '<path d="M18 6L10 42M30 6l8 36"/><path d="M24 9v5M24 20v6M24 32v6"/>',
    'pasta': '<path d="M6 14a3 3 0 0 1 3-3h10l4 5h16a3 3 0 0 1 3 3v17a3 3 0 0 1-3 3H9a3 3 0 0 1-3-3z"/>',
    'balao': '<path d="M8 9h32a3 3 0 0 1 3 3v17a3 3 0 0 1-3 3H21l-9 7v-7H8a3 3 0 0 1-3-3V12a3 3 0 0 1 3-3z"/>',
    'ia': '<path d="M22 6l3.5 10.5L36 20l-10.5 3.5L22 34l-3.5-10.5L8 20l10.5-3.5z"/>'
          '<path d="M37 30l1.5 4.5L43 36l-4.5 1.5L37 42l-1.5-4.5L31 36l4.5-1.5z"/>',
    'microfone': '<rect x="18" y="5" width="12" height="22" rx="6"/><path d="M11 22a13 13 0 0 0 26 0M24 35v8M17 43h14"/>',
    'relogio': '<circle cx="24" cy="24" r="17"/><path d="M24 14v10l6 4"/>',
    'grafico': '<path d="M6 6v36h36"/><path d="M13 32l8-9 6 5 11-13"/><path d="M31 15h7v7"/>',
    'ferramenta': '<path d="M31 5a10 10 0 0 0-9.5 13.5L6.5 33.5a4.2 4.2 0 0 0 6 6l15-15A10 10 0 0 0 41 14.5'
                  'l-6 6-6-1.5-1.5-6 6-6A10 10 0 0 0 31 5z"/>',
    'equipe': '<circle cx="17" cy="16" r="6"/><circle cx="33" cy="18" r="5"/>'
              '<path d="M5 40c0-7 5-12 12-12s12 5 12 12M30 31c1.5-1 3-1.5 5-1.5 5 0 8 4 8 10"/>',
    'porcentagem': '<circle cx="14" cy="14" r="5"/><circle cx="34" cy="34" r="5"/><path d="M38 10L10 38"/>',
    'ampulheta': '<path d="M13 6h22M13 42h22M15 6c0 10 9 12 9 18s-9 8-9 18M33 6c0 10-9 12-9 18s9 8 9 18"/>',
    'musica': '<path d="M18 36V10l22-5v26"/><circle cx="13" cy="36" r="5"/><circle cx="35" cy="31" r="5"/>',
    'cadeado': '<rect x="11" y="21" width="26" height="20" rx="3"/><path d="M16 21v-6a8 8 0 0 1 16 0v6"/>'
               '<circle cx="24" cy="31" r="2.5"/>',
    'chave': '<circle cx="15" cy="24" r="8"/><path d="M23 24h20M37 24v6M42 24v4"/>',
    'casa': '<path d="M6 22L24 7l18 15"/><path d="M11 19v22h26V19"/><path d="M20 41V29h8v12"/>',
    'documento': '<path d="M12 5h17l9 9v29H12z"/><path d="M29 5v9h9M18 24h14M18 31h14M18 38h9"/>',
    'repete': '<path d="M38 18a15 15 0 0 0-27-3M10 30a15 15 0 0 0 27 3"/><path d="M38 8v10H28M10 40V30h10"/>',
    'celular': '<rect x="14" y="5" width="20" height="38" rx="3"/><path d="M21 37h6"/>',
    'calendario': '<rect x="7" y="10" width="34" height="31" rx="3"/><path d="M7 19h34M16 6v8M32 6v8"/>',
    'email': '<rect x="6" y="11" width="36" height="26" rx="3"/><path d="M6 14l18 13 18-13"/>',
    'olho': '<path d="M4 24s7-12 20-12 20 12 20 12-7 12-20 12S4 24 4 24z"/><circle cx="24" cy="24" r="5"/>',
    'onda': '<path d="M6 24h3M14 16v16M20 10v28M26 18v12M32 13v22M38 20v8M42 24h1"/>',
    'ingresso': '<path d="M6 14h36v7a3 3 0 0 0 0 6v7H6v-7a3 3 0 0 0 0-6z"/><path d="M30 14v20" stroke-dasharray="3 3"/>',
    'predio': '<path d="M6 42h36M10 42V18l14-10 14 10v24"/><path d="M18 42V28h12v14"/>',
    'moeda': '<circle cx="24" cy="24" r="17"/><path d="M24 13v22M29 18h-7a3.5 3.5 0 0 0 0 7h4a3.5 3.5 0 0 1 0 7h-7"/>',
    'contrato': '<path d="M12 5h24v38H12z"/><path d="M18 14h12M18 21h12M18 28h6"/><path d="M19 37c3-4 5 1 9-2"/>',
    'balanca': '<path d="M24 6v36M14 42h20M10 12h28"/><path d="M10 12l-6 13a6 6 0 0 0 12 0zM38 12l-6 13a6 6 0 0 0 12 0z"/>',
    'redes': '<circle cx="12" cy="24" r="5"/><circle cx="36" cy="12" r="5"/><circle cx="36" cy="36" r="5"/>'
             '<path d="M16.5 21.5l15-7M16.5 26.5l15 7"/>',
    'anuncio': '<path d="M8 20v8h6l16 9V11L14 20z"/><path d="M36 18a8 8 0 0 1 0 12"/>',
    'caminhao': '<path d="M4 12h24v20H4zM28 19h9l6 7v6H28z"/><circle cx="12" cy="35" r="4"/><circle cx="35" cy="35" r="4"/>',
    'alvo': '<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="10"/><circle cx="24" cy="24" r="3"/>',
    'check': '<circle cx="24" cy="24" r="17"/><path d="M16 24.5l5.5 5.5L33 18.5"/>',
    'carrinho': '<path d="M5 8h6l5 23h22l4-16H13"/><circle cx="19" cy="38" r="3"/><circle cx="34" cy="38" r="3"/>',
    'coracao': '<path d="M24 41S6 30 6 18a9 9 0 0 1 18-3 9 9 0 0 1 18 3c0 12-18 23-18 23z"/>',
    'escudo': '<path d="M24 5l16 6v12c0 10-7 17-16 20-9-3-16-10-16-20V11z"/>',
    'foguete': '<path d="M24 4c8 6 11 15 9 26H15C13 19 16 10 24 4z"/><circle cx="24" cy="18" r="4"/>'
               '<path d="M15 30l-5 8 7-2M33 30l5 8-7-2M20 38h8"/>',
    'pessoa': '<circle cx="24" cy="15" r="8"/><path d="M8 42c0-9 7-15 16-15s16 6 16 15"/>',
    'lupa': '<circle cx="21" cy="21" r="13"/><path d="M31 31l11 11"/>',
    'engrenagem': '<circle cx="24" cy="24" r="6"/><path d="M24 5v6M24 37v6M5 24h6M37 24h6M10.6 10.6l4.2 4.2'
                  'M33.2 33.2l4.2 4.2M10.6 37.4l4.2-4.2M33.2 14.8l4.2-4.2"/>',
}


def esc(t):
    return html.escape(str(t or ''), quote=True)


def multi(t):
    """Texto com quebra de linha manual: '\\n' vira <br>."""
    return '<br>'.join(esc(p) for p in str(t or '').split('\n'))


def icone(nome, t=40, cor='currentColor', w=2.4):
    corpo = ICONES.get(nome) or ICONES['check']
    return (f'<svg viewBox="0 0 48 48" width="{t}" height="{t}" fill="none" stroke="{cor}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{corpo}</svg>')


# ---------------------------------------------------------------- CSS
CSS = r"""
@font-face{font-family:'SG';src:url(assets/fontes/SchibstedGrotesk.ttf) format('truetype');font-weight:400 900;font-style:normal}
@font-face{font-family:'SG';src:url(assets/fontes/SchibstedGrotesk-Italic.ttf) format('truetype');font-weight:400 900;font-style:italic}
@page{size:1920px 1080px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff;font-family:'SG',Helvetica,Arial,sans-serif;color:#0a0a0a;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.s{position:relative;width:1920px;height:1080px;overflow:hidden;background:#fff;break-after:page;page-break-after:always}
.s:last-child{break-after:auto;page-break-after:auto}
@media screen{html,body{background:#3a3a3a}.s{margin:0 auto 24px;zoom:.5}}
.esc{background:#0a0a0a;color:#fff}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.tex{position:absolute;inset:0;background:radial-gradient(1200px 700px at 75% 30%,#3a3a3a 0%,#161616 55%,#0a0a0a 100%)}
.tex::after{content:'';position:absolute;inset:0;background:repeating-linear-gradient(115deg,rgba(255,255,255,.035) 0 2px,transparent 2px 22px)}
.ov{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.86) 0%,rgba(0,0,0,.62) 45%,rgba(0,0,0,.35) 100%)}
.ov2{position:absolute;inset:0;background:rgba(0,0,0,.55)}
.logo{position:absolute;top:56px;right:72px;height:44px;display:flex;align-items:center;z-index:5}
.logo img{height:44px;max-width:320px;object-fit:contain}
.logo b{font-size:40px;font-weight:800;letter-spacing:-.04em;line-height:1}
.esc .logo img{filter:brightness(0) invert(1)}
.logo img.pb{filter:brightness(0)}
.esc .logo img.pb{filter:brightness(0) invert(1)}
.logo.esq{left:72px;right:auto}
.logo.br b{color:#fff}.logo.br img{filter:brightness(0) invert(1)}
.k{font-size:17px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;display:flex;align-items:center;gap:12px;color:#3a3a3a}
.esc .k,.k.cl{color:#bdbdbd}
.k i{font-style:normal;font-size:22px;color:#0a0a0a}
.esc .k i,.k.cl i{color:#fff}
h1,h2{font-weight:900;letter-spacing:-.045em;line-height:.98}
.cab{position:absolute;bottom:40px;font-size:18px;color:#9a9a9a;letter-spacing:.02em}
/* capa */
.cp h1{position:absolute;left:72px;top:560px;width:1000px;font-size:118px;color:#fff}
.cp .k{position:absolute;left:72px;top:500px}
.cp .sub{position:absolute;left:72px;top:820px;width:860px;font-size:32px;line-height:1.38;color:#e6e6e6}
.cp .letra{position:absolute;right:-40px;top:40px;height:1000px;width:900px}
.cp .pe{position:absolute;left:72px;right:72px;bottom:44px;display:flex;justify-content:space-between;font-size:18px;color:#bdbdbd;border-top:1px solid rgba(255,255,255,.25);padding-top:20px}
/* números */
.nm .marca{position:absolute;left:72px;top:150px;font-size:170px;font-weight:900;letter-spacing:-.05em;color:#fff;line-height:1}
.nm .marca img{height:170px;filter:brightness(0) invert(1)}
.nm .slogan{position:absolute;left:76px;top:350px;font-size:36px;color:#e6e6e6}
.nm .lin{position:absolute;left:72px;bottom:150px;display:flex}
.nm .lin div{padding:0 64px 0 36px;border-left:1px solid rgba(255,255,255,.35);color:#fff}
.nm .lin div:first-child{padding-left:0;border-left:0}
.nm .lin b{display:block;font-size:84px;font-weight:500;letter-spacing:-.04em;line-height:1}
.nm .lin span{display:block;font-size:20px;color:#bdbdbd;margin-top:14px}
/* destaque */
.dq .alto{position:absolute;left:0;right:0;top:0;height:780px;background:#0a0a0a;overflow:hidden}
.dq .num{position:absolute;left:0;right:0;top:-30px;text-align:center;font-size:680px;font-weight:900;letter-spacing:-.07em;line-height:1;
 background-size:cover;background-position:center;-webkit-background-clip:text;background-clip:text;color:transparent}
.dq .rot{position:absolute;left:72px;top:150px;color:#fff;font-size:44px;font-weight:800;line-height:1.05;width:420px}
.dq .logos{position:absolute;left:72px;right:72px;top:810px;bottom:30px;display:grid;grid-template-columns:repeat(6,1fr);align-items:center;justify-items:center;row-gap:16px}
.dq .logos img{max-height:62px;max-width:200px;object-fit:contain;filter:grayscale(1)}
.lg-g{font-size:34px;color:#2a2a2a;white-space:nowrap}
/* frase */
.fr{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.fr h2{font-size:92px;max-width:1500px}
.fr p{font-size:30px;color:#5a5a5a;margin-top:44px;max-width:1200px;line-height:1.4}
.fr.esc p{color:#bdbdbd}
/* lista com foto ao lado */
.ld .foto{position:absolute;top:0;bottom:0;width:860px;overflow:hidden}
.ld .foto img{width:100%;height:100%;object-fit:cover}
.ld.dir .foto{right:0;clip-path:polygon(22% 0,100% 0,100% 100%,0 100%)}
.ld.esq .foto{left:0;clip-path:polygon(0 0,100% 0,78% 100%,0 100%)}
.ld .tx{position:absolute;top:120px;width:1060px}
.ld.dir .tx{left:72px}.ld.esq .tx{left:800px;width:1050px}
.ld .tx h2{font-size:76px;margin-top:22px}
.ld .tx>p{font-size:29px;line-height:1.4;color:#3a3a3a;margin-top:22px}
.ld .l{margin-top:30px;border-top:1px solid #d6d6d6}
.ld .l>div{display:grid;grid-template-columns:62px 1fr;align-items:center;padding:13px 0;border-bottom:1px solid #d6d6d6}
.ld .l b{display:block;font-size:28px;font-weight:800;letter-spacing:-.01em}
.ld .l span{display:block;font-size:22px;color:#5a5a5a;margin-top:3px}
.ld .fim{font-size:29px;font-weight:800;margin-top:24px;line-height:1.3}
.ld.esc .tx>p{color:#cfcfcf}.ld.esc .l,.ld.esc .l>div{border-color:rgba(255,255,255,.2)}.ld.esc .l span{color:#bdbdbd}
/* temas */
.tm .foto{position:absolute;right:0;top:0;bottom:0;width:700px;clip-path:polygon(24% 0,100% 0,100% 100%,0 100%);overflow:hidden}
.tm .foto img{width:100%;height:100%;object-fit:cover}
.tm .tx{position:absolute;left:72px;top:110px;width:1180px}
.tm h2{font-size:84px}
.tm .tx>p{font-size:30px;line-height:1.4;margin-top:26px;color:#2a2a2a;width:1100px}
.tm .rt{margin-top:60px;font-size:20px;font-weight:700;border-bottom:1.5px solid #0a0a0a;padding-bottom:14px;width:1100px}
.tm .gr{display:grid;grid-template-columns:1fr 1fr;column-gap:60px;width:1100px;margin-top:10px}
.tm .gr div{display:flex;align-items:center;gap:20px;padding:13px 0;font-size:24px;border-bottom:1px solid #e2e2e2}
/* ordem */
.od .foto{position:absolute;left:0;top:0;bottom:0;width:860px;clip-path:polygon(0 0,100% 0,78% 100%,0 100%);overflow:hidden}
.od .foto img{width:100%;height:100%;object-fit:cover}
.od .tx{position:absolute;left:800px;top:110px;width:1050px}
.od h2{font-size:84px;margin-top:22px}
.od .tx>p{font-size:28px;line-height:1.4;color:#3a3a3a;margin-top:24px}
.od .gf{position:relative;margin-top:70px;height:230px;display:flex;align-items:flex-end;gap:12px;border-bottom:1.5px solid #0a0a0a}
.od .gf i{flex:1;background:#e3e3e3;display:block}
.od .gf i:first-of-type{background:#0a0a0a}
.od .gf small{position:absolute;left:0;top:-38px;background:#0a0a0a;color:#fff;font-size:15px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;padding:6px 12px}
.od .cap{font-size:16px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#7a7a7a;margin-top:14px}
.od .cr{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:40px}
.od .cr div{display:flex;flex-direction:column;gap:10px}
.od .cr b{display:block;font-size:22px}.od .cr span{display:block;font-size:17px;color:#5a5a5a}
/* mosaico e proposta (fundo escuro com faixa embaixo) */
.ms h2,.pp h2{position:absolute;left:72px;top:140px;width:760px;font-size:100px;color:#fff}
.ms .lead,.pp .lead{position:absolute;left:72px;width:720px;font-size:30px;line-height:1.4;color:#d6d6d6}
.ms .grade{position:absolute;left:840px;top:150px;width:1010px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.ms .grade div{height:200px;position:relative;color:#fff;background:linear-gradient(180deg,rgba(255,255,255,.14),rgba(255,255,255,.06)),rgba(8,8,8,.58);border:1px solid rgba(255,255,255,.22)}
.ms .grade svg{position:absolute;left:24px;top:24px}
.ms .grade b{position:absolute;left:24px;right:16px;bottom:22px;font-size:25px;line-height:1.2}
.faixa{position:absolute;left:72px;right:72px;bottom:56px;display:grid;gap:30px;align-items:center;border-top:1px solid rgba(255,255,255,.3);padding-top:30px;color:#fff}
.faixa>div{display:grid;grid-template-columns:58px 1fr;align-items:center;gap:16px}
.faixa>div.ps{grid-template-columns:76px 1fr}
.faixa img{width:72px;height:72px;border-radius:50%;object-fit:cover;filter:grayscale(1)}
.faixa b{display:block;font-size:24px;font-weight:800}.faixa span{display:block;font-size:19px;color:#bdbdbd;margin-top:4px}
.pp .cx{position:absolute;top:150px;height:640px;padding:30px;color:#fff;background:linear-gradient(180deg,rgba(255,255,255,.14),rgba(255,255,255,.06)),rgba(8,8,8,.58);border:1px solid rgba(255,255,255,.22)}
.pp .cx.cl{background:#fff;color:#0a0a0a}
.pp .cx small{position:absolute;left:30px;right:24px;top:30px;font-size:17px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#cfcfcf}
.pp .cx.cl small{color:#5a5a5a}
.pp .cx .nome{position:absolute;left:30px;right:28px;bottom:356px;font-size:30px;font-weight:800;line-height:1.15}
.pp .cx .val{position:absolute;left:30px;right:20px;bottom:256px;font-size:84px;font-weight:900;letter-spacing:-.05em;line-height:1;white-space:nowrap}
.pp .cx .val em{font-style:normal;font-size:40px;letter-spacing:-.02em}
.pp .cx .val.risca{text-decoration:line-through;text-decoration-thickness:6px}
.pp .cx .un{position:absolute;left:30px;right:28px;top:394px;font-size:22px;color:#cfcfcf}
.pp .cx.cl .un{color:#5a5a5a}
.pp .cx .det{position:absolute;left:30px;right:28px;top:446px;border-top:1px solid #8a8a8a;padding-top:18px;font-size:25px;font-weight:700;line-height:1.3}
/* numerada escura */
.nu .tx{position:absolute;left:72px;top:110px;width:900px;color:#fff}
.nu h2{font-size:92px;margin-top:22px}
.nu .tx>p{font-size:30px;color:#cfcfcf;margin-top:24px;line-height:1.4}
.nu ol{list-style:none;margin-top:60px;border-top:1px solid rgba(255,255,255,.25)}
.nu li{display:grid;grid-template-columns:110px 1fr;align-items:center;padding:24px 0;border-bottom:1px solid rgba(255,255,255,.25)}
.nu li i{font-style:normal;font-size:52px;font-weight:900}
.nu li b{display:block;font-size:30px}.nu li span{display:block;font-size:22px;color:#bdbdbd;margin-top:4px}
.nu .ov{background:linear-gradient(90deg,rgba(0,0,0,.95) 0%,rgba(0,0,0,.8) 45%,rgba(0,0,0,.2) 100%)}
/* grade (cronograma) */
.gd .tx{position:absolute;left:72px;top:100px}
.gd h2{font-size:84px;margin-top:22px}
.gd .ln{position:absolute;left:72px;right:72px;display:grid;grid-template-columns:330px 1fr;gap:24px}
.gd .fs small{display:block;font-size:15px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#7a7a7a}
.gd .fs b{display:block;font-size:30px;font-weight:800;margin-top:8px}
.gd .sem{display:grid;gap:14px}
.gd .d{position:relative;padding:22px}
.gd .d small{font-size:14px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;opacity:.75}
.gd .d div{position:absolute;left:22px;right:18px;bottom:20px}
.gd .d b{display:block;font-size:27px;line-height:1.15}
.gd .d i{display:block;font-style:normal;font-size:19px;opacity:.78;margin-top:6px;line-height:1.3}
.gd .forte{background:#0a0a0a;color:#fff}.gd .claro{background:#ededed;color:#1a1a1a}.gd .borda{background:#fff;border:1.5px solid #0a0a0a}
.gd .nota{position:absolute;left:72px;right:72px;bottom:130px;font-size:28px;font-weight:700;line-height:1.35}
.gd .leg{position:absolute;left:72px;bottom:60px;display:flex;gap:36px;font-size:19px}
.gd .leg span{display:flex;align-items:center;gap:10px}
.gd .leg i{display:inline-block;width:20px;height:20px}
/* obrigado */
.ob blockquote{position:absolute;left:72px;top:250px;width:1100px;font-size:46px;font-weight:600;line-height:1.3;color:#fff}
.ob cite{position:absolute;left:72px;top:440px;font-style:normal;font-size:18px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#8a8a8a}
.ob h2{position:absolute;left:66px;bottom:84px;font-size:220px;color:#fff;letter-spacing:-.06em}
.ob .px{position:absolute;left:1240px;right:72px;bottom:110px;color:#fff;border-top:1px solid rgba(255,255,255,.35);padding-top:24px}
.ob .px small{display:block;font-size:18px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#8a8a8a}
.ob .px p{font-size:31px;line-height:1.36;font-weight:600;margin-top:12px}
"""

# Logos genéricas: cada "Empresa N" num estilo diferente, para a faixa de clientes parecer de verdade.
ESTILOS_LOGO = [
    'font-weight:900;font-style:italic;letter-spacing:-.04em',
    'font-weight:800;text-transform:uppercase;letter-spacing:.14em;font-size:26px',
    'font-weight:500;letter-spacing:-.02em',
    'font-family:Georgia,serif;font-style:italic;font-weight:400',
    'font-weight:900;text-transform:uppercase;letter-spacing:-.03em',
    'font-weight:400;letter-spacing:.3em;text-transform:lowercase;font-size:28px',
    'font-weight:700;border:3px solid #2a2a2a;padding:4px 14px;font-size:28px',
    'font-family:"Courier New",monospace;font-weight:700',
    'font-weight:900;background:#2a2a2a;color:#fff;padding:4px 14px;font-size:28px',
    'font-weight:600;font-style:italic;letter-spacing:.02em',
    'font-family:Georgia,serif;font-weight:700;text-transform:uppercase;letter-spacing:.08em;font-size:26px',
    'font-weight:300;letter-spacing:-.03em;font-size:38px',
]


class Deck:
    def __init__(self, dados, base):
        self.d = dados
        self.base = base
        self.marca = dados.get('marca', {})
        self.pessoa = dados.get('pessoa', {})
        self.arquivos = {}  # origem -> nome em assets/

    # ---------- imagens
    def img(self, caminho):
        """Copia a imagem para o build e devolve o caminho relativo; '' se não houver."""
        if not caminho:
            return ''
        for tentativa in (caminho, os.path.join(self.base, caminho), os.path.join(ASSETS, 'fotos', caminho)):
            p = os.path.expanduser(tentativa)
            if os.path.isfile(p):
                p = os.path.abspath(p)
                if p not in self.arquivos:
                    raiz, ext = os.path.splitext(os.path.basename(p))
                    if ext.lower() in ('.jpg', '.jpeg', '.webp', '.heic'):
                        ext = '.jpg'
                    nome = f'{len(self.arquivos):02d}-{raiz}{ext}'
                    self.arquivos[p] = nome
                return 'assets/img/' + self.arquivos[p]
        print(f'  aviso: imagem não encontrada: {caminho} (uso a textura no lugar)')
        return ''

    def fundo(self, foto, pos='50% 50%'):
        src = self.img(foto)
        if src:
            return f'<img class="bg" src="{src}" style="object-position:{esc(pos)}" alt="">'
        return '<div class="tex"></div>'

    def foto_bloco(self, foto, pos='50% 50%'):
        src = self.img(foto)
        if src:
            return f'<img src="{src}" style="object-position:{esc(pos)}" alt="">'
        return '<div class="tex" style="position:absolute;inset:0"></div>'

    def logo(self, extra=''):
        lg = self.img(self.marca.get('logo'))
        pb = ' class="pb"' if self.marca.get('logo_monocromatica', True) else ''
        corpo = f'<img src="{lg}"{pb} alt="{esc(self.marca.get("nome"))}">' if lg else f'<b>{esc(self.marca.get("nome"))}</b>'
        return f'<div class="logo {extra}">{corpo}</div>'

    def kicker(self, t, claro=False):
        if not t:
            return ''
        return f'<div class="k{" cl" if claro else ""}"><i>✱</i>{esc(t)}</div>'

    def faixa(self, itens):
        p = self.pessoa
        cel = []
        if p.get('nome'):
            ft = self.img(p.get('foto'))
            av = (f'<img src="{ft}" alt="">' if ft else
                  f'<div style="width:72px;height:72px;border-radius:50%;border:1.5px solid #fff;display:grid;'
                  f'place-items:center">{icone("pessoa", 38, "#fff")}</div>')
            cel.append(f'<div class="ps">{av}<div><b>{esc(p.get("nome"))}</b><span>{esc(p.get("cargo"))}</span></div></div>')
        for it in itens or []:
            cel.append(f'<div>{icone(it.get("icone"), 46, "#fff")}<div><b>{esc(it.get("titulo"))}</b>'
                       f'<span>{esc(it.get("texto"))}</span></div></div>')
        if not cel:
            return ''
        cols = ('520px ' if p.get('nome') else '') + ' '.join(['1fr'] * len(itens or []))
        return f'<div class="faixa" style="grid-template-columns:{cols}">{"".join(cel)}</div>'

    # ---------- páginas
    def capa(self, s):
        letra = esc((s.get('letra') or self.marca.get('nome') or 'A')[:1].upper())
        svg = (f'<svg class="letra" viewBox="0 0 900 1000"><text x="450" y="850" text-anchor="middle" '
               f'font-family="SG" font-weight="900" font-size="1050" fill="none" stroke="#fff" stroke-width="5">'
               f'{letra}</text></svg>')
        return ('<div class="s esc cp">' + self.fundo(s.get('foto'), s.get('foto_posicao', '50% 50%'))
                + '<div class="ov"></div>' + svg + self.logo('esq')
                + self.kicker(s.get('kicker'), True)
                + f'<h1>{multi(s.get("titulo"))}</h1><p class="sub">{esc(s.get("subtitulo"))}</p>'
                + f'<div class="pe"><span>{esc(s.get("rodape_esquerda") or self.marca.get("site"))}</span>'
                  f'<span>{esc(s.get("rodape_direita"))}</span></div></div>')

    def numeros(self, s):
        lg = self.img(self.marca.get('logo'))
        marca = f'<img src="{lg}" alt="">' if lg else esc(self.marca.get('nome'))
        lin = ''.join(f'<div><b>{esc(n.get("valor"))}</b><span>{esc(n.get("rotulo"))}</span></div>'
                      for n in s.get('numeros', []))
        return ('<div class="s esc nm">' + self.fundo(s.get('foto'), s.get('foto_posicao', '50% 50%'))
                + '<div class="ov"></div>'
                + f'<div class="marca">{marca}</div><div class="slogan">{esc(s.get("slogan") or self.marca.get("slogan"))}</div>'
                + f'<div class="lin">{lin}</div></div>')

    def destaque(self, s):
        src = self.img(s.get('foto'))
        fundo_num = (f'background-image:url({src})' if src else
                     'background-image:linear-gradient(160deg,#f2f2f2 0%,#9a9a9a 45%,#2a2a2a 100%)')
        logos = s.get('logos')
        if isinstance(logos, int) or logos is None:
            logos = [f'Empresa {i + 1}' for i in range(logos if isinstance(logos, int) else 12)]
        cels = []
        for i, lg in enumerate(logos[:12]):
            caminho = self.img(lg) if isinstance(lg, str) and os.path.splitext(lg)[1].lower() in (
                '.png', '.jpg', '.jpeg', '.svg', '.webp') else ''
            if caminho:
                cels.append(f'<img src="{caminho}" alt="">')
            else:
                cels.append(f'<span class="lg-g" style="{ESTILOS_LOGO[i % len(ESTILOS_LOGO)]}">{esc(lg)}</span>')
        return ('<div class="s dq"><div class="alto">'
                + f'<div class="num" style="{fundo_num}">{esc(s.get("numero"))}</div>'
                + f'<div class="rot">{multi(s.get("rotulo"))}</div></div>'
                + f'<div class="logos">{"".join(cels)}</div></div>')

    def frase(self, s):
        escuro = s.get('escuro')
        return (f'<div class="s fr{" esc" if escuro else ""}">' + self.logo()
                + f'<h2>{multi(s.get("titulo"))}</h2>'
                + (f'<p>{esc(s.get("texto"))}</p>' if s.get('texto') else '') + '</div>')

    def lista(self, s):
        lado = 'esq' if s.get('lado') == 'esq' else 'dir'
        itens = ''.join(f'<div>{icone(i.get("icone"), 38, "#0a0a0a")}<div><b>{esc(i.get("titulo"))}</b>'
                        f'<span>{esc(i.get("texto"))}</span></div></div>' for i in s.get('itens', []))
        fim = f'<p class="fim">{esc(s.get("fim"))}</p>' if s.get('fim') else ''
        n = len(s.get('itens', []))
        h2 = 76 if n <= 5 else 66
        return (f'<div class="s ld {lado}"><div class="foto">{self.foto_bloco(s.get("foto"), s.get("foto_posicao", "50% 50%"))}</div>'
                + self.logo('br' if lado == 'dir' else '') + '<div class="tx">' + self.kicker(s.get('kicker'))
                + f'<h2 style="font-size:{h2}px">{multi(s.get("titulo"))}</h2>'
                + (f'<p>{esc(s.get("texto"))}</p>' if s.get('texto') else '')
                + f'<div class="l">{itens}</div>{fim}</div></div>')

    def temas(self, s):
        gr = ''.join(f'<div>{icone(t.get("icone"), 34, "#0a0a0a")}<span>{esc(t.get("nome"))}</span></div>'
                     for t in s.get('temas', []))
        return ('<div class="s tm">' + f'<div class="foto">{self.foto_bloco(s.get("foto"), s.get("foto_posicao", "50% 50%"))}</div>'
                + self.logo('br') + '<div class="tx">' + self.kicker(s.get('kicker'))
                + f'<h2>{multi(s.get("titulo"))}</h2><p>{esc(s.get("texto"))}</p>'
                + f'<div class="rt">{esc(s.get("rotulo_temas", ""))}</div><div class="gr">{gr}</div></div></div>')

    def ordem(self, s):
        barras = s.get('barras') or [100, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18]
        mx = max(barras) or 1
        gf = ''.join(f'<i style="height:{max(4, round(v / mx * 100))}%"></i>' for v in barras)
        cr = ''.join(f'<div>{icone(c.get("icone"), 40, "#0a0a0a")}<div><b>{esc(c.get("nome"))}</b>'
                     f'<span>{esc(c.get("texto"))}</span></div></div>' for c in s.get('criterios', []))
        return ('<div class="s od">' + f'<div class="foto">{self.foto_bloco(s.get("foto"), s.get("foto_posicao", "50% 50%"))}</div>'
                + self.logo() + '<div class="tx">' + self.kicker(s.get('kicker'))
                + f'<h2>{multi(s.get("titulo"))}</h2><p>{esc(s.get("texto"))}</p>'
                + f'<div class="gf"><small>{esc(s.get("rotulo_primeiro", "Começamos por aqui"))}</small>{gf}</div>'
                + f'<div class="cap">{esc(s.get("legenda", ""))}</div><div class="cr">{cr}</div></div></div>')

    def mosaico(self, s):
        gr = ''.join(f'<div>{icone(b.get("icone"), 56, "#fff")}<b>{esc(b.get("nome"))}</b></div>'
                     for b in s.get('blocos', [])[:12])
        topo = 140 + 100 * (multi(s.get('titulo')).count('<br>') + 1) + 40
        return ('<div class="s esc ms">' + self.fundo(s.get('foto'), s.get('foto_posicao', '50% 50%'))
                + '<div class="ov2"></div>' + self.logo()
                + f'<h2>{multi(s.get("titulo"))}</h2>'
                + (f'<p class="lead" style="top:{topo}px">{esc(s.get("texto"))}</p>' if s.get('texto') else '')
                + f'<div class="grade">{gr}</div>' + self.faixa(s.get('faixa')) + '</div>')

    def numerada(self, s):
        li = ''.join(f'<li><i>{i + 1:02d}</i><div><b>{esc(it.get("titulo"))}</b><span>{esc(it.get("texto"))}</span></div></li>'
                     for i, it in enumerate(s.get('itens', [])))
        return ('<div class="s esc nu">' + self.fundo(s.get('foto'), s.get('foto_posicao', '50% 50%'))
                + '<div class="ov"></div>' + self.logo() + '<div class="tx">' + self.kicker(s.get('kicker'), True)
                + f'<h2>{multi(s.get("titulo"))}</h2><p>{esc(s.get("texto"))}</p><ol>{li}</ol></div></div>')

    def grade(self, s):
        linhas = s.get('linhas', [])
        n = max((len(l.get('celulas', [])) for l in linhas), default=4)
        altura = s.get('altura') or (200 if len(linhas) <= 2 else 150)
        topo, corpo = 300, ''
        for l in linhas:
            cel = ''.join(f'<div class="d {c.get("tipo", "claro")}" style="height:{altura}px"><small>{esc(c.get("tag"))}</small>'
                          f'<div><b>{esc(c.get("titulo"))}</b><i>{esc(c.get("texto"))}</i></div></div>'
                          for c in l.get('celulas', []))
            corpo += (f'<div class="ln" style="top:{topo}px"><div class="fs"><small>{esc(l.get("sub"))}</small>'
                      f'<b>{esc(l.get("fase"))}</b></div><div class="sem" style="grid-template-columns:repeat({n},1fr)">'
                      f'{cel}</div></div>')
            topo += altura + 34
        cores = {'forte': 'background:#0a0a0a', 'claro': 'background:#ededed', 'borda': 'background:#fff;border:1.5px solid #0a0a0a'}
        leg = ''.join(f'<span><i style="{cores.get(k, cores["claro"])}"></i>{esc(t)}</span>'
                      for k, t in (s.get('legenda') or {}).items())
        return ('<div class="s gd">' + self.logo() + '<div class="tx">' + self.kicker(s.get('kicker'))
                + f'<h2>{multi(s.get("titulo"))}</h2></div>{corpo}'
                + (f'<p class="nota">{esc(s.get("nota"))}</p>' if s.get('nota') else '')
                + f'<div class="leg">{leg}</div></div>')

    def proposta(self, s):
        caixas = s.get('caixas', [])
        total, gap = 1010, 13
        pesos = [c.get('largura', 1.4 if c.get('destaque') else 1) for c in caixas]
        livre = total - gap * (len(caixas) - 1)
        x, cx = 840, ''
        for c, p in zip(caixas, pesos):
            w = round(livre * p / sum(pesos))
            val = esc(c.get('valor'))
            if c.get('unidade_valor'):
                val += f'<em> {esc(c.get("unidade_valor"))}</em>'
            tam = c.get('tamanho') or (84 if len(str(c.get('valor', ''))) <= 7 else 68)
            cx += (f'<div class="cx{" cl" if c.get("destaque") else ""}" style="left:{x}px;width:{w}px">'
                   f'<small>{esc(c.get("rotulo"))}</small>'
                   + (f'<div class="nome">{esc(c.get("nome"))}</div>' if c.get('nome') else '')
                   + f'<div class="val{" risca" if c.get("riscado") else ""}" style="font-size:{tam}px">{val}</div>'
                   f'<div class="un">{esc(c.get("unidade"))}</div><div class="det">{esc(c.get("detalhe"))}</div></div>')
            x += w + gap
        topo = 140 + 100 * (multi(s.get('titulo')).count('<br>') + 1) + 40
        return ('<div class="s esc pp">' + self.fundo(s.get('foto'), s.get('foto_posicao', '50% 50%'))
                + '<div class="ov2"></div>' + self.logo() + f'<h2>{multi(s.get("titulo"))}</h2>'
                + (f'<p class="lead" style="top:{topo}px">{esc(s.get("texto"))}</p>' if s.get('texto') else '')
                + cx + self.faixa(s.get('faixa')) + '</div>')

    def obrigado(self, s):
        return ('<div class="s esc ob">' + self.logo()
                + (f'<blockquote>“{esc(s.get("citacao"))}”</blockquote><cite>{esc(s.get("autor"))}</cite>'
                   if s.get('citacao') else '')
                + f'<h2>{esc(s.get("titulo") or "Obrigado.")}</h2>'
                + (f'<div class="px"><small>{esc(s.get("rotulo", "Próximo passo"))}</small>'
                   f'<p>{esc(s.get("proximo_passo"))}</p></div>' if s.get('proximo_passo') else '')
                + '</div>')

    def montar_html(self):
        corpo = []
        for i, s in enumerate(self.d.get('paginas', [])):
            tipo = s.get('tipo')
            f = getattr(self, tipo, None) if tipo and not tipo.startswith('_') else None
            if not callable(f) or tipo in ('img', 'fundo', 'foto_bloco', 'logo', 'kicker', 'faixa', 'montar_html'):
                raise SystemExit(f'página {i + 1}: tipo desconhecido "{tipo}"')
            corpo.append(f(s))
        titulo = esc(self.d.get('titulo_arquivo') or 'Apresentação')
        return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{titulo}</title>'
                f'<style>{CSS}</style></head><body>' + '\n'.join(corpo) + '</body></html>')


def preparar_imagem(origem, destino):
    """Foto: preto e branco e no máximo 2400 px, já no arquivo (filtro no CSS deixa o PDF com 50 MB).
    Logo e PNG com transparência: cópia como está."""
    ext = os.path.splitext(origem)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.webp', '.heic'):
        shutil.copy2(origem, destino)
        return
    try:
        from PIL import Image, ImageOps
    except ImportError:
        shutil.copy2(origem, destino)
        return
    im = ImageOps.exif_transpose(Image.open(origem)).convert('L')
    im.thumbnail((2400, 2400))
    im.save(destino, 'JPEG', quality=82, optimize=True, progressive=True)


def achar_chrome():
    candidatos = [
        os.environ.get('CHROME', ''),
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ]
    for c in candidatos:
        if c and os.path.isfile(c):
            return c
    for nome in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'msedge'):
        p = shutil.which(nome)
        if p:
            return p
    raise SystemExit('Não achei o Google Chrome. Instale o Chrome ou diga o caminho em CHROME=...')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        raise SystemExit(__doc__)
    conteudo = os.path.abspath(args[0])
    base = os.path.dirname(conteudo)
    dados = json.load(open(conteudo, encoding='utf-8'))
    build = os.path.join(base, '_build')
    if os.path.isdir(build):
        shutil.rmtree(build)
    os.makedirs(os.path.join(build, 'assets', 'img'))
    shutil.copytree(os.path.join(ASSETS, 'fontes'), os.path.join(build, 'assets', 'fontes'))

    deck = Deck(dados, base)
    h = deck.montar_html()
    for origem, nome in deck.arquivos.items():
        preparar_imagem(origem, os.path.join(build, 'assets', 'img', nome))
    html_path = os.path.join(build, 'apresentacao.html')
    open(html_path, 'w', encoding='utf-8').write(h)

    nome = dados.get('titulo_arquivo') or 'Apresentacao'
    pdf = os.path.join(base, nome + '.pdf')
    chrome = achar_chrome()
    cmd = [chrome, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--hide-scrollbars',
           '--allow-file-access-from-files', '--run-all-compositor-stages-before-draw',
           '--virtual-time-budget=15000', f'--print-to-pdf={pdf}', 'file://' + html_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if not os.path.isfile(pdf):
        print(r.stdout, r.stderr)
        raise SystemExit('O Chrome não gerou o PDF.')
    print('PDF:', pdf)

    # Conferência: uma PNG por página e a folha de miniaturas.
    pngs = []
    if shutil.which('pdftoppm'):
        subprocess.run(['pdftoppm', '-r', '48', '-png', pdf, os.path.join(build, 'pagina')], check=True)
        pngs = sorted(glob.glob(os.path.join(build, 'pagina-*.png')))
        try:
            from PIL import Image
            ims = [Image.open(p) for p in pngs]
            w, hh = ims[0].size
            col = 4
            folha = Image.new('RGB', (col * w + (col + 1) * 12, ((len(ims) + col - 1) // col) * (hh + 12) + 12), '#777')
            for i, im in enumerate(ims):
                folha.paste(im, (12 + (i % col) * (w + 12), 12 + (i // col) * (hh + 12)))
            folha.save(os.path.join(build, 'folha.png'))
            print('Folha de conferência:', os.path.join(build, 'folha.png'))
        except ImportError:
            print('  (sem Pillow: pulei a folha de miniaturas)')
    else:
        print('  (sem pdftoppm/poppler: pulei a folha de miniaturas)')

    if '--pptx' in sys.argv:
        try:
            from pptx import Presentation
            from pptx.util import Emu
        except ImportError:
            raise SystemExit('Para o PPTX: pip install python-pptx')
        subprocess.run(['pdftoppm', '-r', '144', '-png', pdf, os.path.join(build, 'alta')], check=True)
        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
        for p in sorted(glob.glob(os.path.join(build, 'alta-*.png'))):
            sl = prs.slides.add_slide(prs.slide_layouts[6])
            sl.shapes.add_picture(p, 0, 0, prs.slide_width, prs.slide_height)
        pp = os.path.join(base, nome + '.pptx')
        prs.save(pp)
        print('PPTX:', pp)

    if '--sem-abrir' not in sys.argv and sys.platform == 'darwin':
        subprocess.run(['open', pdf])


if __name__ == '__main__':
    main()
