import pandas as pd
from pathlib import Path
import unicodedata
from pyvis.network import Network
import random

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "out"

OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQUIVO_NOS = DATA_DIR / "bairros_unique.csv"
ARQUIVO_ARESTAS_LIMPO = DATA_DIR / "adjacencias_bairros.csv"

ARQUIVO_SAIDA_HTML = OUT_DIR / "grafo_interativo.html" 

def normalize(text):
    """Remove acentos, normaliza o texto e coloca em minúsculas."""
    if not isinstance(text, str):
        return text
    nfkd_form = unicodedata.normalize('NFD', text)
    # Coloca em minúsculas para garantir consistência total
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

net = Network(height="900px", width="100%", directed=False, notebook=False, cdn_resources='remote')

mapeamento_micro_id = {} 
group_id = 0
bairros_adicionados = set() # Armazenará nomes normalizados

print(f"Carregando nós de {ARQUIVO_NOS}...")
try:
    with open(ARQUIVO_NOS, 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().rsplit(' ', 1)
            if len(partes) == 2:
                bairro_orig, microrregiao = partes[0].strip(), partes[1].strip()
                
                bairro_norm = normalize(bairro_orig) # Normaliza o nome
                
                if microrregiao not in mapeamento_micro_id:
                    mapeamento_micro_id[microrregiao] = group_id
                    group_id += 1
                
                if bairro_norm not in bairros_adicionados:
                    net.add_node(
                        bairro_norm, # ID do nó é normalizado
                        label=bairro_orig, # Label (o que aparece) é o original
                        group=mapeamento_micro_id[microrregiao], 
                        title=f"Bairro: {bairro_orig}<br>Microrregião: {microrregiao}"
                    )
                    bairros_adicionados.add(bairro_norm) 

except Exception as e:
    print(f"Erro ao ler {ARQUIVO_NOS}: {e}")
    exit()

print(f"Carregando arestas de {ARQUIVO_ARESTAS_LIMPO}...")
try:
    df_arestas = pd.read_csv(ARQUIVO_ARESTAS_LIMPO, encoding='utf-8')
    
    for index, row in df_arestas.iterrows():
        b1_orig = row['bairro_origem']
        b2_orig = row['bairro_destino']
        peso = row['peso']
        logradouro = row['logradouro']
        
        b1_norm = normalize(b1_orig) # Normaliza nomes da aresta
        b2_norm = normalize(b2_orig)
        
        if b1_norm in bairros_adicionados and b2_norm in bairros_adicionados:
            net.add_edge(
                b1_norm, 
                b2_norm, 
                value=peso, 
                title=f"{b1_orig} <-> {b2_orig}<br>Peso: {peso}<br>Logradouro: {logradouro}"
            )
        else:
            print(f"Aviso: Aresta ignorada (bairros não encontrados): {b1_orig} ou {b2_orig}")

except Exception as e:
    print(f"Erro ao ler {ARQUIVO_ARESTAS_LIMPO}: {e}")
    exit()

print("Configurando layout de física (ForceAtlas2Based)...")
options = """
var options = {
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -100,
      "centralGravity": 0.01,
      "springLength": 100,
      "springConstant": 0.08,
      "avoidOverlap": 1
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
  }
}
"""
net.set_options(options)

print(f"Salvando visualização em {ARQUIVO_SAIDA_HTML}...")
try:
    net.save_graph(str(ARQUIVO_SAIDA_HTML)) 
    print(f"Sucesso! O arquivo '{ARQUIVO_SAIDA_HTML}' foi gerado.")
except Exception as e:
    print(f"--- ERRO AO SALVAR O HTML ---")
    print(f"Ocorreu um erro: {e}")