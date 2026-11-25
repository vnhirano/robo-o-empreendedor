"""Gera a foto de perfil (800x800) e a capa (1500x500) do X no estilo minimalista da marca.

  python ferramentas/gerar_identidade.py
Os arquivos ficam na pasta "saida/".
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageDraw  # noqa: E402

from bot import config  # noqa: E402
from bot.arte import _fonte, _hex  # noqa: E402

saida = Path(__file__).resolve().parent.parent / "saida"
saida.mkdir(exist_ok=True)
BRANCO, ESCURO, DOURADO, CINZA = (255, 255, 255), _hex(config.COR_FUNDO)[:3], _hex(config.COR_DESTAQUE)[:3], (98, 108, 122)

# FOTO DE PERFIL
a = Image.new("RGB", (800, 800), BRANCO)
d = ImageDraw.Draw(a)
d.text((400, 370), "OE", font=_fonte("Black", 330), fill=ESCURO, anchor="mm")
d.rectangle((230, 560, 570, 600), fill=DOURADO)
a.save(saida / "foto_perfil.png")

# CAPA (o conteúdo fica do centro para a direita, longe da foto de perfil)
W, H = 1500, 500
c = Image.new("RGB", (W, H), BRANCO)
d = ImageDraw.Draw(c)
# marca d'água "OE" bem clara à esquerda
d.text((-40, 230), "OE", font=_fonte("Black", 400), fill=(245, 246, 248), anchor="lm")  # termina antes do título

x = 560
d.text((x, 150), "O EMPREENDEDOR", font=_fonte("Black", 92), fill=ESCURO)
d.rectangle((x + 4, 268, x + 230, 280), fill=DOURADO)
temas = ["Mercado", "Economia", "Política", "Negócios"]
temas2 = ["Empreendedorismo", "Imobiliário", "Automotivo", "IA", "Cripto"]
for linha, (y, lista) in enumerate([(310, temas), (356, temas2)]):
    cx = x + 4
    f = _fonte("Medium", 32)
    for i, t in enumerate(lista):
        d.text((cx, y), t, font=f, fill=CINZA)
        cx += f.getlength(t)
        if i < len(lista) - 1:
            d.ellipse((cx + 13, y + 16, cx + 21, y + 24), fill=DOURADO)
            cx += 34
# faixa dourada fina na base
d.rectangle((0, H - 10, W, H), fill=DOURADO)
c.save(saida / "capa_perfil.png")
print("Gerados: saida/foto_perfil.png e saida/capa_perfil.png")
