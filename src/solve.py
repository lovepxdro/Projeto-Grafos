import json
import csv
import unicodedata
import re
from pathlib import Path

# <--- NOVO: Importações adicionadas --->
try:
    from graphs.graph import Graph
    # Precisamos do dijkstra da nossa caixa de ferramentas
    from graphs.algorithms import dijkstra 
except ImportError:
    print("Erro: Não foi possível encontrar a classe Graph ou dijkstra.")
    print("Certifique-se de que 'src/graphs/graph.py' e 'src/graphs/algorithms.py' existem.")
    exit(1)
# <--- FIM NOVO --->

# Resolve os caminhos a partir da raiz do repositório
# Este arquivo está em src/, então subimos 1 nível
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "out"

def _get_nome_canonico(nome_bairro_raw: str, graph: Graph) -> str | None:
    """
    Tenta mapear um nome de bairro (do CSV ou input) 
    para o nome canônico existente no grafo, lidando com acentuação e
    regras especiais (Setúbal).
    """
    
    # 1. Função de normalização (remove acentos, lowercase)
    def _normalize_key(name: str) -> str:
        name = (name or "").strip()
        name = re.sub(r"\s+", " ", name)
        name = ''.join(c for c in unicodedata.normalize('NFD', name)
                       if unicodedata.category(c) != 'Mn')
        return name.lower()

    # 2. Regra especial para Setúbal (PDF) ou "Boa viagem" (do CSV de endereços)
    nome_lower = nome_bairro_raw.lower()
    if "setúbal" in nome_lower or "boa viagem" in nome_lower:
         if "Boa Viagem" in graph.nodes_data:
             return "Boa Viagem"
    
    # 3. Cria um mapa de normalizado -> canônico
    #    Ex: {'caxanga': 'Caxangá', 'recife': 'Recife', ...}
    try:
        # Tenta usar um mapa cacheado se já o construímos
        if not hasattr(graph, '_canon_map'):
            graph._canon_map = { _normalize_key(n): n for n in graph.nodes_data.keys() }
    except Exception as e:
        # Fallback simples se der erro
        print(f"Erro ao criar canon_map: {e}")
        graph._canon_map = {}

    # 4. Tenta encontrar pelo nome normalizado
    nome_normalizado = _normalize_key(nome_bairro_raw)
    nome_encontrado = graph._canon_map.get(nome_normalizado)
    
    if nome_encontrado:
        return nome_encontrado
    
    # 5. Se falhou tudo, retorna o nome original para o Dijkstra (que vai falhar e logar o erro)
    print(f"  [Aviso] Nome de bairro '{nome_bairro_raw}' não mapeado. Usando como está.")
    return nome_bairro_raw.strip()

# <--- NOVO: Função da Task 6.1 --->
def executar_task_6_distancias(g: Graph):
    """
    Task 6.1: Lê data/enderecos.csv, calcula distâncias com Dijkstra
    e salva em out/distancias_enderecos.csv.
    """
    print("Executando Task 6.1: Cálculo de Distâncias (enderecos.csv)...")
    
    arquivo_entrada = DATA_DIR / "enderecos.csv"
    arquivo_saida = OUT_DIR / "distancias_enderecos.csv"
    
    # Colunas de saída conforme PDF
    # Usamos os bairros como X e Y, pois o CSV de entrada não tem endereços
    headers = ["X", "Y", "bairro X", "bairro Y", "custo", "caminho"]
    
    resultados_csv = []
    
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_in:
            # Usamos DictReader para lidar com os headers
            reader = csv.DictReader(f_in)
            
            for row in reader:
                bairro_x_raw = ""
                bairro_y_raw = ""
                try:
                    # Os headers no CSV de endereços têm espaços!
                    bairro_x_raw = row['bairro_origem '] 
                    bairro_y_raw = row['bairro_destino']
                    
                    # Mapeia nomes do CSV para nomes canônicos do grafo
                    bairro_x = _get_nome_canonico(bairro_x_raw, g)
                    bairro_y = _get_nome_canonico(bairro_y_raw, g)

                    # Roda o Dijkstra
                    resultado = dijkstra(g, bairro_x, bairro_y)
                    
                    # Formata o caminho (lista) como "A -> B -> C"
                    caminho_str = " -> ".join(resultado["path"])
                    
                    resultados_csv.append({
                        "X": bairro_x, # Usando bairro como X
                        "Y": bairro_y, # Usando bairro como Y
                        "bairro X": bairro_x,
                        "bairro Y": bairro_y,
                        "custo": resultado["cost"],
                        "caminho": caminho_str
                    })
                
                except (ValueError, KeyError) as e:
                    print(f"  [ERRO] Falha ao processar par '{bairro_x_raw}'-'{bairro_y_raw}': {e}")
                    resultados_csv.append({
                        "X": bairro_x_raw, "Y": bairro_y_raw,
                        "bairro X": bairro_x_raw, "bairro Y": bairro_y_raw,
                        "custo": "ERRO", "caminho": str(e)
                    })

    except FileNotFoundError:
        print(f"  [ERRO FATAL] Arquivo de entrada não encontrado: {arquivo_entrada}")
        return
    except Exception as e:
        print(f"  [ERRO FATAL] Erro ao ler {arquivo_entrada}: {e}")
        return

    # Salvar os resultados no CSV de saída
    try:
        with open(arquivo_saida, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=headers)
            writer.writeheader()
            writer.writerows(resultados_csv)
        print(f"  -> {arquivo_saida} gerado com sucesso.")
    except Exception as e:
        print(f"  [ERRO FATAL] Falha ao salvar {arquivo_saida}: {e}")
# <--- FIM NOVO --->


# <--- NOVO: Função da Task 6.2 --->
def executar_task_6_percurso_especial(g: Graph):
    """
    Task 6.2: Calcula o percurso "Nova Descoberta -> Setúbal"
    e salva em out/percurso_nova_descoberta_setubal.json.
    """
    print("Executando Task 6.2: Percurso Nova Descoberta -> Setúbal...")
    
    arquivo_saida = OUT_DIR / "percurso_nova_descoberta_setubal.json"
    
    origem_raw = "Nova Descoberta"
    # PDF pede Setúbal, que mapeamos para "Boa Viagem"
    destino_raw = "Setúbal"
    
    origem_canon = _get_nome_canonico(origem_raw, g)
    destino_canon = _get_nome_canonico(destino_raw, g) # Deve retornar "Boa Viagem"

    try:
        resultado = dijkstra(g, origem_canon, destino_canon)
        
        # Prepara o JSON de saída
        output_data = {
            "origem_solicitada": origem_raw,
            "destino_solicitado": destino_raw,
            "origem_mapeada": origem_canon,
            "destino_mapeado": destino_canon,
            "custo": resultado["cost"],
            "percurso": resultado["path"]
        }
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"  -> {arquivo_saida} gerado com sucesso.")

    except Exception as e:
        print(f"  [ERRO FATAL] Falha ao calcular percurso especial: {e}")
# <--- FIM NOVO --->


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
        
        if ordem_v < 2:
            densidade = 0.0
        else:
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

    # <--- NOVO: Chamada para as funções da Task 6 --->
    print("-" * 30)
    
    # Task 6: Distâncias e Percursos
    executar_task_6_distancias(g)
    executar_task_6_percurso_especial(g)
    # <--- FIM NOVO --->

    print("-" * 30)
    print("Execução das tasks concluída.")


if __name__ == "__main__":
    main()