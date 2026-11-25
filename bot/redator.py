"""Etapa 2: o Claude Haiku escolhe a melhor notícia e escreve os textos.

A IA faz SÓ isso: escolher e escrever. Todo o resto é código fixo (por isso fica barato).
"""
import json
import os
import re

from . import config

INSTRUCOES = f"""Você é o editor do perfil "{config.NOME_PERFIL}" no X, voltado a empreendedores,
investidores e pessoas de negócios no Brasil. Estilo: manchetes curtas e fortes, em CAIXA ALTA,
e um comentário de uma linha, direto e com personalidade, que provoque a conversa.

Regras obrigatórias:
1. Use SOMENTE fatos que estão no título e no resumo recebidos. Nunca invente números, nomes,
   datas ou declarações. Se faltar informação, escreva algo mais genérico, mas verdadeiro.
2. Nada de ataques pessoais, ofensas ou militância partidária. Pode opinar sobre impacto
   econômico, para o bolso e para os negócios.
   Em notícias de POLÍTICA: priorize decisões com efeito na economia (impostos, gastos públicos,
   juros, regras para empresas). Trate todos os partidos e governos com o mesmo critério,
   e o comentário deve focar na consequência prática para quem empreende ou investe.
3. Sem hashtags, sem emojis e sem links.
4. Português do Brasil, linguagem simples.

Responda APENAS com um JSON válido, neste formato:
{{
  "escolha": <número da notícia escolhida (a mais relevante e com maior potencial de engajamento)>,
  "manchete": "<CAIXA ALTA, até 100 caracteres>",
  "comentario": "<1 frase, até 140 caracteres, com opinião ou consequência prática>",
  "linha_apoio": "<frase curta para o vídeo, até 80 caracteres, que dê contexto>",
  "busca_imagem": "<2 a 4 palavras EM INGLÊS para buscar uma foto genérica de banco de imagens; nunca nomes de pessoas ou marcas>",
  "pular": <true se nenhuma notícia servir, senão false>
}}"""


def _lista(noticias: list[dict]) -> str:
    linhas = []
    for i, n in enumerate(noticias):
        linhas.append(f"[{i}] ({n['fonte']}) {n['titulo']}\n    Resumo: {n['resumo'][:300]}")
    return "\n".join(linhas)


def escrever(noticias: list[dict], nicho: str) -> dict:
    """Retorna os textos do post. Sem chave da Anthropic, usa um texto de teste."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        n = noticias[0]
        return {"escolha": 0, "manchete": n["titulo"].upper()[:100],
                "comentario": "Texto de teste: configure a ANTHROPIC_API_KEY para o comentário da IA.",
                "linha_apoio": n["fonte"], "busca_imagem": "business office", "pular": False}

    import anthropic
    cliente = anthropic.Anthropic()
    resposta = cliente.messages.create(
        model=config.MODELO_IA,
        max_tokens=600,
        system=INSTRUCOES,
        messages=[{"role": "user",
                   "content": f"Nicho: {nicho}\n\nNotícias disponíveis:\n{_lista(noticias)}"}],
    )
    texto = resposta.content[0].text
    bloco = re.search(r"\{.*\}", texto, re.S)
    dados = json.loads(bloco.group(0))
    dados["escolha"] = max(0, min(int(dados.get("escolha", 0)), len(noticias) - 1))
    dados["manchete"] = dados["manchete"].upper()[:110]
    return dados


def texto_do_post(textos: dict, noticia: dict) -> str:
    """Monta o texto final do post no X (limite de 280 caracteres)."""
    corpo = f"++ {textos['manchete']}\n\n{textos['comentario']}"
    rodape = f"\n\nFonte: {noticia['fonte']}"
    if len(corpo) + len(rodape) > 280:
        corpo = corpo[: 280 - len(rodape) - 1] + "…"
    return corpo + rodape
