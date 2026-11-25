"""Etapa 1: coleta as notícias recentes e descarta as que já foram postadas."""
import json
import re
import time
import unicodedata
from pathlib import Path

import feedparser
import requests

from . import config

ARQUIVO_HISTORICO = Path(__file__).resolve().parent.parent / "data" / "postados.json"


def _normalizar(texto: str) -> set[str]:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    palavras = re.findall(r"[a-z0-9]{4,}", texto)
    return set(palavras)


def _parecido(a: set, b: set) -> bool:
    if not a or not b:
        return False
    return len(a & b) / len(a | b) >= 0.5


def carregar_historico() -> list[dict]:
    if ARQUIVO_HISTORICO.exists():
        return json.loads(ARQUIVO_HISTORICO.read_text(encoding="utf-8")).get("postados", [])
    return []


def salvar_no_historico(titulo: str, nicho: str, manchete: str) -> None:
    historico = carregar_historico()
    historico.append({"titulo": titulo, "nicho": nicho, "manchete": manchete,
                      "quando": time.strftime("%Y-%m-%d %H:%M")})
    historico = historico[-500:]  # guarda só os 500 mais recentes
    ARQUIVO_HISTORICO.write_text(json.dumps({"postados": historico}, ensure_ascii=False, indent=1),
                                 encoding="utf-8")


NAVEGADOR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def _baixar_feed(url: str):
    """Baixa um feed RSS. Se a fonte falhar, avisa no log e segue com as outras."""
    site = url.split("/")[2]
    try:
        r = requests.get(url, headers={"User-Agent": NAVEGADOR}, timeout=20)
        if r.status_code != 200:
            print(f"   fonte {site}: erro HTTP {r.status_code}")
            return None
        feed = feedparser.parse(r.content)
        print(f"   fonte {site}: {len(feed.entries)} itens")
        return feed
    except Exception as erro:
        print(f"   fonte {site}: falhou ({type(erro).__name__})")
        return None


# Fontes que não são veículos de imprensa: notícias delas são descartadas
FONTES_BLOQUEADAS = {"instagram", "facebook", "youtube", "tiktok", "x", "twitter",
                     "linkedin", "threads", "kwai", "reddit", "medium", "blogspot"}

# Nome bonito para os portais diretos (o nome do feed às vezes vem estranho)
NOMES_FONTES = {
    "techcrunch.com": "TechCrunch", "www.cnbc.com": "CNBC", "feeds.bbci.co.uk": "BBC",
    "feeds.content.dowjones.io": "MarketWatch", "electrek.co": "Electrek",
    "www.coindesk.com": "CoinDesk", "cointelegraph.com": "Cointelegraph",
    "www.aljazeera.com": "Al Jazeera", "www.moneytimes.com.br": "Money Times",
    "g1.globo.com": "g1", "www.infomoney.com.br": "InfoMoney", "startups.com.br": "Startups",
    "exame.com": "Exame", "autopapo.uol.com.br": "AutoPapo", "motor1.uol.com.br": "Motor1",
    "www.tecmundo.com.br": "TecMundo", "canaltech.com.br": "Canaltech",
    "www.poder360.com.br": "Poder360", "livecoins.com.br": "Livecoins",
    "portaldobitcoin.uol.com.br": "Portal do Bitcoin",
}

# LISTA DE VEÍCULOS CONFIÁVEIS (para notícias que vêm do Google Notícias).
# Só passam notícias cujo veículo comece com um destes nomes. Para incluir um veículo, adicione aqui.
FONTES_CONFIAVEIS = [
    # Brasil
    "valor", "infomoney", "exame", "folha de s.paulo", "folha de s. paulo", "estadao", "estadão",
    "e-investidor", "o globo", "g1", "cnn brasil", "bloomberg linea", "bloomberg línea", "poder360",
    "money times", "metropoles", "metrópoles", "uol", "veja", "epoca negocios", "época negócios",
    "pequenas empresas", "pegn", "forbes", "neofeed", "brazil journal", "seu dinheiro",
    "agencia brasil", "agência brasil", "bbc", "investing.com", "correio braziliense", "jovem pan",
    "band", "sbt news", "terra", "autoesporte", "quatro rodas", "motor1", "autopapo", "tecmundo",
    "canaltech", "olhar digital", "startups", "startse", "livecoins", "portal do bitcoin",
    "cointelegraph", "gazeta do povo", "valor investe", "istoe dinheiro", "istoé dinheiro",
    "o estado de s. paulo", "cbn", "globonews", "jota", "agencia senado", "agência senado",
    "agencia camara", "agência câmara", "infomoney", "suno", "the shift", "mobile time",
    # Exterior
    "reuters", "bloomberg", "cnbc", "the wall street journal", "wsj", "financial times",
    "the new york times", "new york times", "the washington post", "associated press", "ap news",
    "the guardian", "the economist", "fortune", "business insider", "axios", "politico",
    "techcrunch", "the verge", "wired", "ars technica", "coindesk", "the block", "decrypt",
    "electrek", "marketwatch", "barron's", "yahoo finance", "al jazeera", "nikkei", "south china morning post",
    "deutsche welle", "dw", "le monde", "el pais", "el país", "euronews", "sky news", "npr",
    "cbs news", "abc news", "nbc news", "fox business", "the information", "semafor", "cnn",
]


def _fonte_confiavel(fonte: str) -> bool:
    f = fonte.strip().lower()
    return any(f == a or f.startswith(a + " ") or f.startswith(a + ":") or f.startswith(a + ">")
               or f.startswith(a + ".") or f.startswith(a + "-") for a in FONTES_CONFIAVEIS)


POR_FONTE = 4   # no máximo 4 notícias de cada fonte, para misturar Brasil e exterior


def coletar(nicho: str, limite: int = 15) -> list[dict]:
    """Retorna até `limite` notícias inéditas do nicho, da mais nova para a mais antiga."""
    vistos = [_normalizar(h["titulo"]) for h in carregar_historico()]
    itens = []
    limite_idade = time.time() - config.IDADE_MAXIMA_HORAS * 3600
    for url in config.NICHOS[nicho]:
        feed = _baixar_feed(url)
        if feed is None:
            continue
        do_feed = 0
        entradas = sorted(feed.entries, key=lambda e: time.mktime(
            e.get("published_parsed") or e.get("updated_parsed") or time.gmtime()), reverse=True)
        for e in entradas:
            if do_feed >= POR_FONTE:
                break
            titulo = e.get("title", "")
            fonte = ""
            if "source" in e and hasattr(e.source, "get"):
                fonte = e.source.get("title", "")
            # O Google Notícias coloca " - Nome do Site" no fim do título
            if "news.google" in url and " - " in titulo:
                titulo, sufixo = titulo.rsplit(" - ", 1)
                fonte = fonte or sufixo
            resumo = re.sub(r"<[^>]+>", " ", e.get("summary", ""))
            resumo = re.sub(r"\s+", " ", resumo).strip()
            data = e.get("published_parsed") or e.get("updated_parsed") or time.gmtime()
            if time.mktime(data) < limite_idade:
                continue
            chave = _normalizar(titulo)
            if any(_parecido(chave, v) for v in vistos):
                continue
            if any(_parecido(chave, _normalizar(i["titulo"])) for i in itens):
                continue
            do_feed += 1
            if not fonte:  # portais diretos: usa um nome conhecido ou o do próprio feed
                fonte = NOMES_FONTES.get(url.split("/")[2]) or \
                    feed.feed.get("title", "").split(" - ")[0].split(" | ")[0]
            if fonte.strip().lower() in FONTES_BLOQUEADAS:
                continue
            # notícias do Google Notícias só entram se o veículo estiver na lista de confiáveis
            if "news.google" in url and not _fonte_confiavel(fonte):
                continue
            itens.append({"titulo": titulo.strip(), "fonte": fonte.strip() or "Imprensa",
                          "resumo": resumo[:400], "link": e.get("link", ""),
                          "data": time.mktime(data), "nicho": nicho})
    itens.sort(key=lambda i: i["data"], reverse=True)
    return itens[:limite]
