"""Etapa 4: guarda o vídeo na Cloudflare R2 e manda o post para o Buffer."""
import datetime as dt
import os
from pathlib import Path

import requests

from . import config

BUFFER_API = "https://api.buffer.com"


# ------------------------------------------------------------------ CLOUDFLARE R2
def enviar_para_r2(arquivo: Path) -> str:
    """Envia o arquivo para o bucket R2 e devolve o link público."""
    import boto3
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )
    chave = f"videos/{arquivo.name}"
    tipo = "video/mp4" if arquivo.suffix == ".mp4" else "image/png"
    s3.upload_file(str(arquivo), os.environ["R2_BUCKET"], chave, ExtraArgs={"ContentType": tipo})
    return f"{os.environ['R2_PUBLIC_URL'].rstrip('/')}/{chave}"


# ------------------------------------------------------------------ BUFFER
def _graphql(consulta: str) -> dict:
    r = requests.post(BUFFER_API, json={"query": consulta}, timeout=60,
                      headers={"Authorization": f"Bearer {os.environ['BUFFER_API_KEY']}",
                               "Content-Type": "application/json"})
    r.raise_for_status()
    dados = r.json()
    if dados.get("errors"):
        raise RuntimeError(f"Erro do Buffer: {dados['errors']}")
    return dados["data"]


def _texto_graphql(s: str) -> str:
    """Escapa o texto para caber dentro da consulta GraphQL."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def postar_no_buffer(texto: str, url_video: str) -> str:
    canal = os.environ["BUFFER_CHANNEL_ID"]
    if config.MODO == "publicar":
        # agenda para daqui a 2 minutos = publica quase na hora
        quando = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        modo = f'mode: customScheduled, dueAt: "{quando}"'
    else:
        modo = "mode: addToQueue, saveToDraft: true"

    consulta = f'''
    mutation {{
      createPost(input: {{
        text: "{_texto_graphql(texto)}",
        channelId: "{canal}",
        schedulingType: automatic,
        {modo},
        assets: [{{ video: {{ url: "{url_video}" }} }}]
      }}) {{
        ... on PostActionSuccess {{ post {{ id }} }}
        ... on MutationError {{ message }}
      }}
    }}'''
    resposta = _graphql(consulta)["createPost"]
    if "message" in resposta:
        raise RuntimeError(f"Buffer recusou o post: {resposta['message']}")
    return resposta["post"]["id"]
