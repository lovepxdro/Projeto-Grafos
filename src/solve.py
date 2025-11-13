import json
import csv
from pathlib import Path

# Importa a classe Graph
try:
    from graphs.graph import Graph
except ImportError:
    print("Erro: Não foi possível encontrar a classe Graph.")
    print("Certifique-se de que 'src/graphs/graph.py' existe.")
    exit(1)

# Resolve os caminhos a partir da raiz do repositório
# Este arquivo está em src/, então subimos 1 nível
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "out"


def main():
    """
    Orquestrador principal para executar as tarefas da Parte 1.
    Carrega o grafo e gera todos os arquivos de saída de métricas.
    """
    print("Iniciando a execução das tarefas de métricas da Parte 1...")
    
    # Caminhos dos arquivos de dados
    nodes_path = DATA_DIR / "bairros_unique.csv"
    edges_path = DATA_DIR / "adjacencias_bairros.csv" 

    if not nodes_path.exists() or not edges_path.exists():
        print(f"ERRO FATAL: Arquivo de dados não encontrado.")
        print(f"Verifique se '{nodes_path}' e '{edges_path}' existem.")
        return

    # 1. Carregar o grafo
    print("-" * 30)
    g = Graph()
    g.load_from_csvs(nodes_file=nodes_path, edges_file=edges_path)
    print("-" * 30)

    # Garante que a pasta 'out/' exista
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Gerar arquivos de saída (Tasks 3 e 4)
    
    # Task 3.1: Métricas Globais (recife_global.json)
    try:
        print("Executando Task 3.1: Métricas Globais...")
        ordem_v = g.get_ordem()
        tamanho_e = g.get_tamanho()
        
        # Lógica de densidade (a mesma que você tinha)
        if ordem_v < 2:
            densidade = 0.0
        else:
            # Usando o método _densidade da própria classe
            densidade = g._densidade(ordem_v, tamanho_e) 
            
        metricas = {
            "ordem": ordem_v,
            "tamanho": tamanho_e,
            "densidade": densidade
        }
        
        arquivo_saida_global = OUT_DIR / "recife_global.json"
        with open(arquivo_saida_global, 'w', encoding='utf-8') as f:
            json.dump(metricas, f, indent=4)
            
        print(f"  -> {arquivo_saida_global} gerado com sucesso.")
        print(f"     Ordem: {ordem_v}, Tamanho: {tamanho_e}, Densidade: {densidade:.6f}")

    except Exception as e:
        print(f"[ERRO Task 3.1] {e}")

    # Task 3.2: Métricas por Microrregião (microrregioes.json)
    try:
        print("Executando Task 3.2: Métricas por Microrregião...")
        g.export_microrregioes_json() # O método já imprime o sucesso
    except Exception as e:
        print(f"[ERRO Task 3.2] {e}")

    # Task 3.3: Métricas Ego-Rede (ego_bairro.csv)
    try:
        print("Executando Task 3.3: Métricas Ego-Rede...")
        g.export_ego_csv() # O método já imprime o sucesso
    except Exception as e:
        print(f"[ERRO Task 3.3] {e}")
        
    # Task 4: Graus e Rankings (graus.csv)
    try:
        print("Executando Task 4: Lista de Graus...")
        g.export_graus_csv() # O método já imprime o sucesso
    except Exception as e:
        print(f"[ERRO Task 4] {e}")

    # Task 4: Rankings (impresso no console)
    try:
        print("Executando Task 4: Rankings (Console)...")
        bairro_max_grau, max_grau = g.get_bairro_maior_grau()
        print(f"\n  [Bairro com maior grau]")
        print(f"  - Bairro: {bairro_max_grau}")
        print(f"  - Grau: {max_grau}")

        ego_max = g.get_bairro_mais_denso_ego()
        if ego_max:
            print(f"\n  [Bairro mais denso na ego-rede]")
            print(f"  - Bairro: {ego_max['bairro']}")
            print(f"  - Densidade_ego: {ego_max['densidade_ego']:.4f}")
    except Exception as e:
        print(f"[ERRO Task 4 Rankings] {e}")

    print("-" * 30)
    print("Execução de métricas concluída.")


if __name__ == "__main__":
    main()