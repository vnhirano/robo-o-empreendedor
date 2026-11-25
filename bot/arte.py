"""Etapa 3: monta a arte (Pillow) e o vídeo vertical (ffmpeg).

Camadas do vídeo:
  - FUNDO: foto do Pexels (gratuita e liberada para uso) ou um fundo gerado com a marca.
           Recebe um zoom lento, que dá movimento ao vídeo.
  - FRENTE: logo, selo do nicho, manchete, linha de apoio, fonte e rodapé. Fica parada.
"""
import io
import os
import subprocess
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config

W, H = config.LARGURA, config.ALTURA
PASTA_FONTES = Path(__file__).resolve().parent.parent / "assets" / "fonts"
MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def _fonte(peso: str, tamanho: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(PASTA_FONTES / f"Inter-{peso}.otf"), tamanho)


def _hex(c: str, alfa: int = 255) -> tuple:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (alfa,)


def _quebrar(texto: str, fonte, largura_max: int) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if fonte.getlength(teste) <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


# ------------------------------------------------------------------ FUNDO
def buscar_foto(busca: str) -> Image.Image | None:
    """Busca uma foto vertical no Pexels (precisa da PEXELS_API_KEY, que é gratuita)."""
    chave = os.getenv("PEXELS_API_KEY")
    if not chave or not busca:
        return None
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": busca, "orientation": "portrait", "per_page": 15},
                         headers={"Authorization": chave}, timeout=20)
        fotos = r.json().get("photos", [])
        if not fotos:
            return None
        foto = fotos[int(time.time()) % len(fotos)]  # varia a foto entre posts
        img = requests.get(foto["src"]["large2x"], timeout=30).content
        return Image.open(io.BytesIO(img)).convert("RGB")
    except Exception as erro:  # sem foto, o robô segue com o fundo gerado
        print("Aviso: não consegui buscar foto:", erro)
        return None


def _cobrir(img: Image.Image) -> Image.Image:
    escala = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * escala) + 1, int(img.height * escala) + 1), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def fundo_gerado(nicho: str) -> Image.Image:
    """Fundo com a identidade da marca, para quando não houver foto."""
    base = Image.new("RGBA", (W, H), _hex(config.COR_FUNDO))
    # brilho dourado no alto
    brilho = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(brilho)
    d.ellipse((W * 0.25, -H * 0.15, W * 1.35, H * 0.45), fill=_hex(config.COR_DESTAQUE, 70))
    brilho = brilho.filter(ImageFilter.GaussianBlur(220))
    base = Image.alpha_composite(base, brilho)
    # grade sutil
    grade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(grade)
    for x in range(0, W, 90):
        g.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
    for y in range(0, H, 90):
        g.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)
    base = Image.alpha_composite(base, grade)
    # nome do nicho gigante, bem apagado
    marca = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = ImageDraw.Draw(marca)
    tamanho = 420
    f = _fonte("Black", tamanho)
    while f.getlength(nicho) > W - 120 and tamanho > 80:
        tamanho -= 10
        f = _fonte("Black", tamanho)
    m.text((60, 330), nicho, font=f, fill=(255, 255, 255, 18))
    base = Image.alpha_composite(base, marca)
    return base.convert("RGB")


# ------------------------------------------------------------------ FRENTE
def camada_frente(manchete: str, linha_apoio: str, nicho: str, fonte_noticia: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # degradê escuro de baixo para cima, para o texto ficar legível em cima da foto
    degrade = Image.new("L", (1, H), 0)
    for y in range(H):
        p = max(0.0, (y - H * 0.38) / (H * 0.62))
        degrade.putpixel((0, y), int(245 * min(1.0, p ** 0.8)))
    sombra = Image.new("RGBA", (W, H), _hex(config.COR_FUNDO))
    sombra.putalpha(degrade.resize((W, H)))
    img = Image.alpha_composite(img, sombra)
    # faixa escura no topo
    topo = Image.new("L", (1, H), 0)
    for y in range(320):
        topo.putpixel((0, y), int(170 * (1 - y / 320)))
    faixa = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    faixa.putalpha(topo.resize((W, H)))
    img = Image.alpha_composite(img, faixa)

    d = ImageDraw.Draw(img)
    branco, dourado, cinza = _hex(config.COR_TEXTO), _hex(config.COR_DESTAQUE), _hex(config.COR_SECUNDARIA)

    # LOGO (canto superior esquerdo)
    d.rounded_rectangle((60, 70, 150, 160), radius=18, fill=branco)
    d.text((105, 108), "OE", font=_fonte("Black", 40), fill=_hex(config.COR_FUNDO), anchor="mm")
    d.rectangle((84, 134, 126, 140), fill=dourado)
    d.text((172, 82), config.NOME_PERFIL, font=_fonte("Black", 40), fill=branco)
    d.text((174, 132), config.ARROBA, font=_fonte("Medium", 26), fill=cinza)

    # FONTE (canto superior direito)
    txt_fonte = f"FONTE: {fonte_noticia.upper()}"[:34]
    f_fonte = _fonte("Bold", 22)
    larg = f_fonte.getlength(txt_fonte)
    d.rounded_rectangle((W - 60 - larg - 36, 92, W - 60, 140), radius=24,
                        fill=(0, 0, 0, 140), outline=(255, 255, 255, 60), width=2)
    d.text((W - 60 - larg - 18, 116), txt_fonte, font=f_fonte, fill=branco, anchor="lm")

    # MANCHETE (encaixa o tamanho da letra no espaço)
    margem, largura_txt = 96, W - 96 - 70
    for tamanho in range(92, 50, -4):
        f_manchete = _fonte("Black", tamanho)
        linhas = _quebrar(manchete, f_manchete, largura_txt)
        if len(linhas) <= 5:
            break
    altura_linha = int(tamanho * 1.12)
    f_apoio = _fonte("Medium", 36)
    linhas_apoio = _quebrar(linha_apoio, f_apoio, largura_txt)[:2] if linha_apoio else []

    y_fim = 1690
    y_apoio = y_fim - len(linhas_apoio) * 48
    y_manchete = y_apoio - 30 - len(linhas) * altura_linha
    y_selo = y_manchete - 90

    # selo do nicho
    f_selo = _fonte("ExtraBold", 28)
    larg_selo = f_selo.getlength(nicho) + 44
    d.rounded_rectangle((margem - 36, y_selo, margem - 36 + larg_selo, y_selo + 54), radius=10, fill=dourado)
    d.text((margem - 36 + 22, y_selo + 27), nicho, font=f_selo, fill=_hex(config.COR_FUNDO), anchor="lm")

    # barra dourada + manchete
    d.rectangle((margem - 36, y_manchete + 6, margem - 26, y_manchete + len(linhas) * altura_linha - 10), fill=dourado)
    for i, linha in enumerate(linhas):
        d.text((margem, y_manchete + i * altura_linha), linha, font=f_manchete, fill=branco)

    for i, linha in enumerate(linhas_apoio):
        d.text((margem, y_apoio + i * 48), linha, font=f_apoio, fill=_hex("#D6DCE4"))

    # RODAPÉ
    agora = time.gmtime(time.time() - 3 * 3600)  # horário de Brasília
    data_txt = f"{agora.tm_mday:02d} {MESES[agora.tm_mon - 1]} {agora.tm_year}"
    d.line((margem - 36, 1770, W - 60, 1770), fill=(255, 255, 255, 50), width=2)
    d.text((margem - 36, 1800), f"SIGA {config.ARROBA.upper()}", font=_fonte("ExtraBold", 28), fill=dourado)
    f_data = _fonte("Medium", 26)
    d.text((W - 60, 1800), data_txt, font=f_data, fill=cinza, anchor="ra")
    return img


# ------------------------------------------------------------------ VÍDEO
def gerar_video(textos: dict, noticia: dict, pasta_saida: Path) -> tuple[Path, Path]:
    """Gera o MP4 e uma capa PNG. Retorna (video, capa)."""
    pasta_saida.mkdir(parents=True, exist_ok=True)
    nome = time.strftime("%Y%m%d-%H%M%S")
    foto = buscar_foto(textos.get("busca_imagem", ""))
    fundo = _cobrir(foto) if foto else fundo_gerado(noticia["nicho"])
    frente = camada_frente(textos["manchete"], textos.get("linha_apoio", ""),
                           noticia["nicho"], noticia["fonte"])

    arq_fundo = pasta_saida / f"{nome}-fundo.png"
    arq_frente = pasta_saida / f"{nome}-frente.png"
    arq_capa = pasta_saida / f"{nome}-capa.png"
    arq_video = pasta_saida / f"{nome}.mp4"
    fundo.save(arq_fundo)
    frente.save(arq_frente)
    Image.alpha_composite(fundo.convert("RGBA"), frente).convert("RGB").save(arq_capa)

    dur = config.DURACAO_VIDEO
    filtro = (
        f"[0:v]scale=w='trunc({W}*(1+0.08*t/{dur})/2)*2':h=-2:eval=frame,"
        f"crop={W}:{H},setsar=1[bg];"
        f"[1:v]format=rgba,fade=in:st=0:d=0.6:alpha=1[fr];"
        f"[bg][fr]overlay=0:0:format=auto,format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-loop", "1", "-framerate", "30", "-t", str(dur), "-i", str(arq_fundo),
           "-loop", "1", "-framerate", "30", "-t", str(dur), "-i", str(arq_frente),
           "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", filtro, "-map", "[v]", "-map", "2:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-r", "30",
           "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart",
           str(arq_video)]
    subprocess.run(cmd, check=True)
    arq_fundo.unlink()
    arq_frente.unlink()
    return arq_video, arq_capa
