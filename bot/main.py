"""
ROBÔ "O EMPREENDEDOR" - arquivo principal
=========================================
Roda uma rodada completa:
  1) escolhe o nicho da vez  2) coleta notícias  3) Haiku escreve
  4) gera o vídeo  5) sobe na R2  6) manda para o Buffer  7) anota no histórico

Uso:
  python -m bot.main            -> rodada normal (é o que o GitHub executa)
  python -m bot.main --teste    -> gera um vídeo de exemplo, sem internet e sem postar
"""
import os
import random
import sys
import time
from pathlib import Path

from . import arte, config, noticias, publicar, redator

PASTA_SAIDA = Path(__file__).resolve().parent.parent / "saida"

NOTICIA_TESTE = {
    "titulo": "Vendas de carros elétricos no Brasil batem recorde em novembro e já superam 10% do mercado",
    "fonte": "Exemplo",
    "resumo": "Notícia fictícia usada apenas para testar a montagem do vídeo.",
    "link": "", "data": time.time(), "nicho": "AUTOMOTIVO",
}


def hora_brasilia() -> int:
    return time.gmtime(time.time() - 3 * 3600).tm_hour


def nicho_da_vez() -> list[str]:
    """Gira entre os nichos a cada hora; devolve a ordem de tentativa."""
    nichos = list(config.NICHOS)
    inicio = (int(time.time() // 3600)) % len(nichos)
    return nichos[inicio:] + nichos[:inicio]


def sortear_formato() -> str:
    escolhido = os.getenv("FORMATO", "auto").lower()
    if escolhido in config.FORMATOS:
        return escolhido
    nomes, pesos = zip(*config.FORMATOS.items())
    return random.choices(nomes, weights=pesos, k=1)[0]


def rodada_teste() -> None:
    # Textos fixos de exemplo (no uso real quem escreve é o Haiku)
    textos = {
        "manchete": "CARROS ELÉTRICOS JÁ SÃO MAIS DE 10% DAS VENDAS NO BRASIL",
        "comentario": "Quem ainda acha que é moda vai descobrir que é mercado.",
        "linha_apoio": "Recorde em novembro acende alerta nas montadoras tradicionais",
        "busca_imagem": "electric car charging",
    }
    video, capa = arte.gerar_video(textos, NOTICIA_TESTE, PASTA_SAIDA)
    card = arte.gerar_imagem(textos, NOTICIA_TESTE, PASTA_SAIDA)
    print("Texto do post:\n" + redator.texto_do_post(textos, NOTICIA_TESTE))
    print(f"\nVídeo: {video}\nCard:  {card}")


def rodada() -> None:
    hora = hora_brasilia()
    forcar = os.getenv("FORCAR", "nao").lower() == "sim"
    if not forcar and not (config.HORA_INICIO <= hora <= config.HORA_FIM):
        print(f"Fora do horário de postagem ({hora}h). Nada a fazer.")
        return

    feitos = 0
    for nicho in nicho_da_vez():
        if feitos >= config.POSTS_POR_EXECUCAO:
            break
        lista = noticias.coletar(nicho)
        print(f"[{nicho}] {len(lista)} notícias inéditas")
        if not lista:
            continue
        textos = redator.escrever(lista, nicho)
        if textos.get("pular"):
            print(f"[{nicho}] IA preferiu pular.")
            continue
        noticia = lista[textos["escolha"]]
        texto = redator.texto_do_post(textos, noticia)
        print("Post:\n" + texto)

        formato = sortear_formato()
        print("Formato:", formato)
        url = None
        if formato == "video":
            arquivo, _capa = arte.gerar_video(textos, noticia, PASTA_SAIDA)
        elif formato == "imagem":
            arquivo = arte.gerar_imagem(textos, noticia, PASTA_SAIDA)
        else:
            arquivo = None
        if arquivo:
            url = publicar.enviar_para_r2(arquivo)
            print("Mídia na nuvem:", url)
        id_post = publicar.postar_no_buffer(texto, url, formato)
        print(f"Enviado ao Buffer ({config.MODO}, {formato}): {id_post}")

        noticias.salvar_no_historico(noticia["titulo"], nicho, textos["manchete"])
        feitos += 1

    print(f"Rodada concluída: {feitos} post(s).")


if __name__ == "__main__":
    if "--teste" in sys.argv:
        rodada_teste()
    else:
        rodada()
