"""Etapa 1: coleta as notícias recentes e descarta as que já foram postadas."""
import json
import re
import time
import unicodedata
from pathlib import Path

import feedparser

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


def coletar(nicho: str, limite: int = 10) -> list[dict]:
    """Retorna até `limite` notícias inéditas do nicho, da mais nova para a mais antiga."""
    vistos = [_normalizar(h["titulo"]) for h in carregar_historico()]
    itens = []
    for url in config.NICHOS[nicho]:
        feed = feedparser.parse(url)
        for e in feed.entries:
            titulo = e.get("title", "")
            fonte = ""
            if "source" in e and hasattr(e.source, "get"):
                fonte = e.source.get("title", "")
            # O Google Notícias coloca " - Nome do Site" no fim do título
            if " - " in titulo:
                titulo, sufixo = titulo.rsplit(" - ", 1)
                fonte = fonte or sufixo
            resumo = re.sub(r"<[^>]+>", " ", e.get("summary", ""))
            resumo = re.sub(r"\s+", " ", resumo).strip()
            data = e.get("published_parsed") or time.gmtime()
            chave = _normalizar(titulo)
            if any(_parecido(chave, v) for v in vistos):
                continue
            if any(_parecido(chave, _normalizar(i["titulo"])) for i in itens):
                continue
            itens.append({"titulo": titulo.strip(), "fonte": fonte.strip() or "Imprensa",
                          "resumo": resumo[:400], "link": e.get("link", ""),
                          "data": time.mktime(data), "nicho": nicho})
    itens.sort(key=lambda i: i["data"], reverse=True)
    return itens[:limite]
