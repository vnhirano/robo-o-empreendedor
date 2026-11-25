"""
Rode UMA vez no seu computador (ou no GitHub) para descobrir o BUFFER_CHANNEL_ID da conta do X.

  Windows (PowerShell):
    $env:BUFFER_API_KEY="cole_sua_chave_aqui"
    python ferramentas/listar_canais_buffer.py
"""
import os
import requests

CHAVE = os.environ["BUFFER_API_KEY"]


def gql(consulta: str) -> dict:
    r = requests.post("https://api.buffer.com", json={"query": consulta}, timeout=30,
                      headers={"Authorization": f"Bearer {CHAVE}"})
    r.raise_for_status()
    return r.json()["data"]


orgs = gql("query { account { organizations { id name } } }")["account"]["organizations"]
for org in orgs:
    print(f"\nOrganização: {org['name']} (id {org['id']})")
    canais = gql(f'query {{ channels(input: {{ organizationId: "{org["id"]}" }}) '
                 "{ id name displayName service } }")["channels"]
    for c in canais:
        print(f"  - {c['service']:<10} {c.get('displayName') or c['name']:<30} BUFFER_CHANNEL_ID = {c['id']}")
