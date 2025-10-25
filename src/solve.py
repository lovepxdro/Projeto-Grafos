import json
import csv
from pathlib import Path

# --- 1. Configurar Caminhos ---
# Como o script é executado da RAIZ do projeto,
# podemos usar caminhos relativos diretamente.
DATA_DIR = Path("data")
OUT_DIR = Path("out")

def calcular_metricas_globais():
    """
    Executa a Etapa 3.1 do projeto:
    Calcula Ordem, Tamanho e Densidade do grafo completo e
    salva em 'out/recife_global.json'.
    """
    
    print("Iniciando Etapa 3.1: Cálculo de Métricas Globais...")
    
    # Caminhos relativos baseados no CWD (raiz do projeto)
    arquivo_nos = DATA_DIR / "bairros_unique.csv"
    arquivo_arestas = DATA_DIR / "adjacencias_bairros.csv" 
    arquivo_saida = OUT_DIR / "recife_global.json"

    try:
        # --- 2. Calcular Ordem (|V|) ---
        with open(arquivo_nos, 'r', encoding='utf-8') as f:
            ordem_v = sum(1 for linha in f if linha.strip())
        
        # --- 3. Calcular Tamanho (|E|) ---
        # Usando o adjacencias_bairros.csv 
        with open(arquivo_arestas, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Pula a linha do cabeçalho
            tamanho_e = sum(1 for linha in reader if linha) 
            
        # --- 4. Calcular Densidade ---
        if ordem_v < 2:
            densidade = 0.0
        else:
            densidade = (2 * tamanho_e) / (ordem_v * (ordem_v - 1))
            
        # --- 5. Preparar Saída ---
        metricas = {
            "ordem": ordem_v,
            "tamanho": tamanho_e,
            "densidade": densidade
        }
        
        # --- 6. Salvar JSON ---
        OUT_DIR.mkdir(parents=True, exist_ok=True) # Garante que a pasta 'out/' existe
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(metricas, f, indent=4)
            
        print("-" * 30)
        print(f"Métricas globais salvas com sucesso em: {arquivo_saida}")
        print(f"  Ordem (|V|): {ordem_v} bairros")
        print(f"  Tamanho (|E|): {tamanho_e} conexões")
        print(f"  Densidade: {densidade:.6f}")
        print("-" * 30)

    except FileNotFoundError as e:
        print(f"\n--- ERRO ---")
        print(f"Arquivo não encontrado: '{e.filename}'")
        print(f"Verifique se o arquivo existe e se você está executando o script")
        print(f"a partir da pasta raiz do projeto (ex: .../Projeto-Grafos-...).")
        print(f"------------\n")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- Ponto de entrada ---
if __name__ == "__main__":
    calcular_metricas_globais()