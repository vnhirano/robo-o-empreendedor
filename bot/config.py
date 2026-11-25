"""
CONFIGURAÇÕES DO ROBÔ "O EMPREENDEDOR"
=======================================
Este é o único arquivo que você precisa editar para mudar o comportamento do robô:
nome do perfil, cores, nichos, fontes de notícia e horários.
As chaves secretas (API keys) NÃO ficam aqui: elas ficam nos "Secrets" do GitHub.
"""
import os

# ---------------------------------------------------------------
# 1. IDENTIDADE DO PERFIL
# ---------------------------------------------------------------
NOME_PERFIL = "O EMPREENDEDOR"
ARROBA = "@_O_Empreendedor"

# Cores da marca (formato hexadecimal)
COR_FUNDO = "#0B0F14"      # quase preto
COR_DESTAQUE = "#F5B700"   # dourado
COR_TEXTO = "#FFFFFF"
COR_SECUNDARIA = "#9AA4B2" # cinza

# ---------------------------------------------------------------
# 2. NICHOS E FONTES DE NOTÍCIA
# ---------------------------------------------------------------
# Usamos o Google Notícias (RSS gratuito, sem chave). Cada nicho tem buscas.
# Para adicionar um nicho, copie uma linha e mude o nome e os termos.
def _google_news(busca: str) -> str:
    from urllib.parse import quote
    return (f"https://news.google.com/rss/search?q={quote(busca)}+when:6h"
            "&hl=pt-BR&gl=BR&ceid=BR:pt-419")

NICHOS = {
    "MERCADO":          [_google_news("Ibovespa OR bolsa OR dólar OR ações")],
    "ECONOMIA":         [_google_news("economia brasileira OR inflação OR juros OR Selic OR PIB")],
    "EMPREENDEDORISMO": [_google_news("empreendedorismo OR startup OR pequenas empresas OR franquia")],
    "NEGÓCIOS":         [_google_news("empresa lucro OR aquisição OR fusão OR varejo OR faturamento")],
    "AUTOMOTIVO":       [_google_news("montadora OR carro elétrico OR lançamento carro OR mercado automotivo")],
    "IMOBILIÁRIO":      [_google_news("mercado imobiliário OR financiamento imobiliário OR construtora OR aluguel")],
    "IA":               [_google_news("inteligência artificial OR OpenAI OR Anthropic OR Nvidia OR IA generativa")],
    "POLÍTICA":         [_google_news("Congresso economia OR reforma tributária OR ajuste fiscal OR orçamento federal OR Ministério da Fazenda OR imposto aprovado")],
    "CRIPTO":           [_google_news("bitcoin OR criptomoedas OR ethereum OR stablecoin OR cripto")],
}

# ---------------------------------------------------------------
# 3. RITMO DE POSTAGEM
# ---------------------------------------------------------------
# O GitHub roda o robô de hora em hora. Aqui você limita o horário (horário de Brasília).
HORA_INICIO = 7    # primeiro post às 7h
HORA_FIM = 23      # último post às 23h
POSTS_POR_EXECUCAO = 1   # quantos posts a cada rodada (1 por hora = ~17 por dia)

# Mistura de formatos (pesos em %). O robô sorteia um formato a cada post.
# Mude os números para ter mais ou menos de cada tipo.
FORMATOS = {
    "texto": 60,    # só texto (manchete + comentário)
    "imagem": 25,   # texto + card com a manchete
    "video": 15,    # texto + vídeo vertical
}

# ---------------------------------------------------------------
# 4. MODO DE OPERAÇÃO
# ---------------------------------------------------------------
# "rascunho" -> o post vai para os RASCUNHOS do Buffer e você aprova pelo app (recomendado no início)
# "publicar" -> o post vai ao ar sozinho em ~2 minutos
MODO = os.getenv("MODO", "rascunho")

# ---------------------------------------------------------------
# 5. IA (Claude Haiku)
# ---------------------------------------------------------------
MODELO_IA = os.getenv("MODELO_IA", "claude-haiku-5-5")

# ---------------------------------------------------------------
# 6. VÍDEO
# ---------------------------------------------------------------
DURACAO_VIDEO = 9    # segundos
LARGURA, ALTURA = 1080, 1920   # formato vertical 9:16 (X, Reels, TikTok, Shorts)
