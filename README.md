# Robô "O EMPREENDEDOR": posts automáticos em vídeo no X

Notícias de **Mercado, Economia, Empreendedorismo, Negócios, Automotivo, Imobiliário, IA, Cripto e Política (com foco em economia)**
transformadas em vídeos verticais com a marca do perfil, postadas sozinhas de hora em hora.

```
GitHub (despertador, toda hora)
   └─> Google Notícias (coleta as manchetes, grátis)
        └─> Claude Haiku (escolhe a melhor e escreve manchete + comentário)
             └─> Pexels (foto gratuita, opcional) + Pillow/ffmpeg (monta o vídeo)
                  └─> Cloudflare R2 (hospeda o vídeo)
                       └─> Buffer (posta no X)
```

---

## O que tem nesta pasta

| Arquivo | Para que serve |
|---|---|
| `bot/config.py` | **O único arquivo que você precisa editar**: nome, @, cores, nichos, horários, modo |
| `bot/noticias.py` | Busca as notícias e descarta as repetidas |
| `bot/redator.py` | Instruções do Haiku e montagem do texto do post |
| `bot/arte.py` | Desenha a arte e gera o vídeo |
| `bot/publicar.py` | Envia para a R2 e para o Buffer |
| `bot/main.py` | Liga tudo em sequência |
| `.github/workflows/robo.yml` | Agenda o robô no GitHub |
| `data/postados.json` | Histórico, para nunca repetir notícia |
| `ferramentas/gerar_identidade.py` | Gera a foto de perfil e a capa do X |
| `ferramentas/listar_canais_buffer.py` | Descobre o ID do seu canal no Buffer |

---

## Passo a passo (uma vez só, ~1 hora)

Você vai criar 5 contas e copiar algumas chaves. **Guarde as chaves num bloco de notas**:
elas vão no GitHub no passo 6. Nunca as coloque dentro dos arquivos do projeto.

### Passo 1: Conta no X
1. Crie a conta e veja se o @ que você quer está livre (`@oempreendedor` provavelmente está
   ocupado; teste variações como `@oempreendedorbr`, `@oempreendedor_br`).
2. Troque o `ARROBA` em `bot/config.py` pelo @ real.
3. Para gerar a foto de perfil e a capa: `python ferramentas/gerar_identidade.py` (já vão prontas na pasta `saida/`).
4. Na bio, deixe claro que é um perfil de notícias com curadoria automatizada. Isso dá transparência e protege a conta.

### Passo 2: Chave do Claude (Anthropic)
1. Acesse **console.anthropic.com** e crie a conta.
2. Em **Billing**, coloque um crédito pequeno (US$ 5 dura meses neste uso).
3. Em **API Keys → Create Key**, copie a chave. → anote como `ANTHROPIC_API_KEY`.

### Passo 3: Fotos do Pexels (opcional e gratuito)
Sem esta chave o robô usa um fundo com a identidade da marca, o que também fica bom.
1. Crie a conta em **pexels.com/api** e peça a chave (é gratuita e as fotos são liberadas para uso).
2. → anote como `PEXELS_API_KEY`.

> O robô **não** usa fotos de jornais ou agências, porque usar essas fotos sem licença gera denúncia por direitos autorais.

### Passo 4: Cloudflare R2 (onde os vídeos ficam guardados)
1. Crie a conta em **dash.cloudflare.com**, entre em **R2 Object Storage** e ative o plano gratuito.
   A Cloudflare pede um cartão para ativar, mas só cobra se você passar da franquia gratuita.
2. **Create bucket** → nome `o-empreendedor` → anote como `R2_BUCKET`.
3. Dentro do bucket: **Settings → Public Development URL → Enable**. Copie o endereço
   `https://pub-xxxx.r2.dev` → anote como `R2_PUBLIC_URL`.
4. Ainda em Settings: **Object lifecycle rules → Add rule** → apagar objetos com mais de 30 dias.
   Assim você nunca sai da cota gratuita.
5. Volte à página do R2 → **Manage API Tokens → Create API Token** → permissão
   **Object Read & Write**, limitado ao bucket `o-empreendedor`. Copie:
   - Access Key ID → `R2_ACCESS_KEY_ID`
   - Secret Access Key → `R2_SECRET_ACCESS_KEY`
   - O Account ID aparece no endpoint `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` → `R2_ACCOUNT_ID`

### Passo 5: Buffer (quem posta no X)
1. Crie a conta em **buffer.com** e conecte o canal do **X** com a conta nova.
2. Para criar a chave da API, entre em **publish.buffer.com → Settings → API** → copie → `BUFFER_API_KEY`.
3. Descubra o ID do canal. No computador, com Python instalado, rode no PowerShell:
   ```
   pip install requests
   $env:BUFFER_API_KEY="cole_a_chave"
   python ferramentas/listar_canais_buffer.py
   ```
   Copie o número da linha do X → `BUFFER_CHANNEL_ID`.

### Passo 6: GitHub (onde o robô mora e roda sozinho)
1. Crie a conta em **github.com** → **New repository** → nome `robo-o-empreendedor` → marque **Private**.
2. Clique em **uploading an existing file** e arraste **todo o conteúdo** desta pasta.
   Se a pasta `.github` não for junto (no Windows ela pode ficar oculta), crie o arquivo pelo site:
   **Add file → Create new file** → nome `.github/workflows/robo.yml` → cole o conteúdo.
3. Vá em **Settings → Secrets and variables → Actions → New repository secret** e cadastre,
   um por um, os 9 itens que você anotou (o nome tem que ser exatamente igual):
   `ANTHROPIC_API_KEY`, `PEXELS_API_KEY`, `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`,
   `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_PUBLIC_URL`, `BUFFER_API_KEY`, `BUFFER_CHANNEL_ID`.

### Passo 7: Primeiro teste (em modo rascunho)
1. No repositório: **Actions → Robo O Empreendedor → Run workflow → modo: rascunho → Run**.
2. Espere ~2 minutos. Clique na execução para ver o "diário" (o texto do post aparece ali).
3. Abra o app do Buffer → **Drafts**: o post com vídeo estará lá esperando sua aprovação.
4. A partir daí ele roda **sozinho toda hora** (das 7h às 23h), sempre como rascunho.

### Passo 8: Ligar o piloto automático
Depois de 1 ou 2 semanas aprovando e ajustando o tom:
**Settings → Secrets and variables → Actions → aba Variables → New variable**
→ nome `MODO`, valor `publicar`. Pronto: os posts vão ao ar sozinhos.
Para voltar a aprovar manualmente, troque para `rascunho`.

---

## Custos estimados (17 posts/dia ≈ 500/mês)

| Serviço | Custo |
|---|---|
| GitHub Actions | Grátis (~1 minuto por rodada, cabe nos 2.000 min/mês do plano gratuito) |
| Google Notícias + Pexels | Grátis |
| Claude Haiku | Centavos de dólar por mês |
| Cloudflare R2 | Grátis (com a regra de apagar após 30 dias) |
| Buffer | O plano gratuito permite 1 chave de API e tem limite de posts na fila. Se o robô começar a dar erro de limite, assine o plano Essentials |
| X Premium | Opcional, para selo e monetização |

---

## Ajustes comuns

- **Mudar o tom dos textos**: edite o bloco `INSTRUCOES` em `bot/redator.py`.
- **Adicionar/remover nichos ou termos de busca**: `NICHOS` em `bot/config.py`.
- **Postar mais ou menos**: `POSTS_POR_EXECUCAO`, `HORA_INICIO` e `HORA_FIM` em `bot/config.py`.
- **Mudar cores**: `COR_DESTAQUE` e `COR_FUNDO` em `bot/config.py`.
- **Ver um vídeo de exemplo no seu PC**: instale o ffmpeg e rode `python -m bot.main --teste`.

## Se der erro

Abra **Actions**, clique na execução com o ❌ e leia as últimas linhas.
- `KeyError: 'R2_...'` ou `'BUFFER_...'` → um Secret está faltando ou com nome errado.
- `Erro do Buffer` / `Buffer recusou` → chave errada, ID do canal errado ou limite do plano atingido.
- `0 notícias inéditas` em todos os nichos → normal de madrugada; o robô tenta de novo na hora seguinte.

## Boas práticas para não perder a conta
- Comece em modo **rascunho** e revise o tom.
- Mantenha 1 post por hora: volume exagerado é sinalizado como spam.
- Responda comentários de vez em quando. O engajamento real é o que faz o alcance crescer.
- A IA está instruída a não inventar dados, mas **notícia errada derruba credibilidade**: revise
  os rascunhos no começo e ajuste as instruções se precisar.
