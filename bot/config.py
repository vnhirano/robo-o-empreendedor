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

def _google_news_en(busca: str) -> str:
    """Google Notícias em inglês (EUA), para notícias internacionais."""
    from urllib.parse import quote
    return (f"https://news.google.com/rss/search?q={quote(busca)}+when:6h"
            "&hl=en-US&gl=US&ceid=US:en")


NICHOS = {
    "MERCADO": [
        _google_news("Ibovespa OR bolsa OR dólar OR ações"),
        "https://www.infomoney.com.br/mercados/feed/",
        "https://www.moneytimes.com.br/feed/",
        _google_news_en("stock market OR Wall Street OR Fed OR S&P 500 OR Nasdaq"),
        "https://www.cnbc.com/id/15839069/device/rss/rss.html",
        "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    ],
    "ECONOMIA": [
        _google_news("economia brasileira OR inflação OR juros OR Selic OR PIB"),
        "https://g1.globo.com/rss/g1/economia/",
        "https://www.infomoney.com.br/economia/feed/",
    ],
    "EMPREENDEDORISMO": [
        _google_news("abertura de empresas OR Sebrae OR MEI OR recuperação judicial OR falências OR ABF franquias OR pequenos negócios dados"),
    ],
    "NEGÓCIOS": [
        _google_news("empresa lucro OR aquisição OR fusão OR varejo OR faturamento"),
        "https://www.infomoney.com.br/negocios/feed/",
        "https://exame.com/negocios/feed/",
        _google_news_en("earnings OR acquisition OR merger OR CEO OR layoffs big tech"),
    ],
    "AUTOMOTIVO": [
        _google_news("emplacamentos OR Fenabrave OR Anfavea OR vendas de veículos OR produção de veículos OR montadora fábrica Brasil"),
        "https://autopapo.uol.com.br/feed/",
        "https://motor1.uol.com.br/rss/news/all/",
        _google_news_en("car sales OR EV sales OR automaker sales OR Tesla deliveries OR BYD sales"),
        "https://electrek.co/feed/",
    ],
    "IMOBILIÁRIO": [
        _google_news("lançamentos imobiliários OR vendas de imóveis OR inadimplência imobiliária OR crédito imobiliário OR Abrainc OR Secovi OR FipeZap OR construção civil"),
        "https://www.infomoney.com.br/minhas-financas/imoveis/feed/",
    ],
    "IA": [
        _google_news("inteligência artificial OR OpenAI OR Anthropic OR Nvidia OR IA generativa"),
        "https://www.tecmundo.com.br/inteligencia-artificial/rss",
        "https://canaltech.com.br/rss/",
        _google_news_en("artificial intelligence OR OpenAI OR Anthropic OR Nvidia OR Google AI"),
        "https://techcrunch.com/category/artificial-intelligence/feed/",
    ],
    "POLÍTICA": [
        _google_news("Congresso economia OR reforma tributária OR ajuste fiscal OR orçamento federal OR Ministério da Fazenda OR imposto aprovado"),
        "https://www.poder360.com.br/feed/",
        "https://g1.globo.com/rss/g1/politica/",
    ],
    "CRIPTO": [
        _google_news("bitcoin OR criptomoedas OR ethereum OR stablecoin OR cripto"),
        "https://livecoins.com.br/feed/",
        "https://portaldobitcoin.uol.com.br/feed/",
        _google_news_en("bitcoin OR crypto OR ethereum OR stablecoin OR SEC crypto"),
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
    ],
    "GEOPOLÍTICA": [
        _google_news("geopolítica OR guerra comercial OR tarifas OR sanções OR China Estados Unidos"),
        _google_news_en("geopolitics OR tariffs OR sanctions OR trade war OR OPEC OR China US"),
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
    ],
}
# Notícias mais antigas que isso são ignoradas (horas)
IDADE_MAXIMA_HORAS = 12

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
