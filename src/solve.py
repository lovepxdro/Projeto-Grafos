import json
import csv
from pathlib import Path
import unicodedata
import re

# Importações
try:
    from pyvis.network import Network
except ImportError:
    print("Aviso: 'pyvis' não instalado. Task 7 e Task 9 não funcionarão.")
    print("Execute: pip install pyvis")
    Network = None 

try:
    from graphs.graph import Graph
    from graphs.algorithms import dijkstra 
except ImportError:
    print("Erro: Não foi possível encontrar a classe Graph ou dijkstra.")
    print("Certifique-se de que 'src/graphs/graph.py' e 'src/graphs/algorithms.py' existem.")
    exit(1)

# Caminhos
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "out"

# ... (Função _get_nome_canonico(...) permanece a mesma) ...
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
    try:
        if not hasattr(graph, '_canon_map'):
            graph._canon_map = { _normalize_key(n): n for n in graph.nodes_data.keys() }
    except Exception as e:
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


# ... (Função executar_task_6_distancias(...) permanece a mesma) ...
def executar_task_6_distancias(g: Graph):
    """
    Task 6.1: Lê data/enderecos.csv, calcula distâncias com Dijkstra
    e salva em out/distancias_enderecos.csv.
    """
    print("Executando Task 6.1: Cálculo de Distâncias (enderecos.csv)...")
    
    arquivo_entrada = DATA_DIR / "enderecos.csv"
    arquivo_saida = OUT_DIR / "distancias_enderecos.csv"
    
    headers = ["X", "Y", "bairro X", "bairro Y", "custo", "caminho"]
    
    resultados_csv = []
    
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            
            for row in reader:
                bairro_x_raw = ""
                bairro_y_raw = ""
                try:
                    bairro_x_raw = row['bairro_origem '] 
                    bairro_y_raw = row['bairro_destino']
                    
                    bairro_x = _get_nome_canonico(bairro_x_raw, g)
                    bairro_y = _get_nome_canonico(bairro_y_raw, g)

                    resultado = dijkstra(g, bairro_x, bairro_y)
                    
                    caminho_str = " -> ".join(resultado["path"])
                    
                    resultados_csv.append({
                        "X": bairro_x, 
                        "Y": bairro_y, 
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

    try:
        with open(arquivo_saida, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=headers)
            writer.writeheader()
            writer.writerows(resultados_csv)
        print(f"  -> {arquivo_saida} gerado com sucesso.")
    except Exception as e:
        print(f"  [ERRO FATAL] Falha ao salvar {arquivo_saida}: {e}")

# ... (Função executar_task_6_percurso_especial(...) permanece a mesma) ...
def executar_task_6_percurso_especial(g: Graph) -> dict | None:
    """
    Task 6.2: Calcula o percurso "Nova Descoberta -> Setúbal"
    e salva em out/percurso_nova_descoberta_setubal.json.
    
    Retorna: O dicionário do resultado, ou None em caso de falha.
    """
    print("Executando Task 6.2: Percurso Nova Descoberta -> Setúbal...")
    
    arquivo_saida = OUT_DIR / "percurso_nova_descoberta_setubal.json"
    
    origem_raw = "Nova Descoberta"
    destino_raw = "Setúbal"
    
    origem_canon = _get_nome_canonico(origem_raw, g)
    destino_canon = _get_nome_canonico(destino_raw, g) 

    try:
        resultado = dijkstra(g, origem_canon, destino_canon)
        
        output_data = {
            "origem_solicitada": origem_raw,
            "destino_solicitado": destino_raw,
            "origem_mapeada": origem_canon,
            "destino_mapeado": destino_canon,
            "custo": resultado["cost"],
            "percurso": resultado["path"] # Esta é a lista de nós
        }
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"  -> {arquivo_saida} gerado com sucesso.")
        return output_data # Retorna o resultado

    except Exception as e:
        print(f"  [ERRO FATAL] Falha ao calcular percurso especial: {e}")
        return None # Retorna None em falha

# ... (Função executar_task_7_arvore_percurso(...) permanece a mesma) ...
def executar_task_7_arvore_percurso(g: Graph, resultado_percurso: dict | None):
    """
    Task 7: Cria uma visualização (pyvis) apenas com o
    caminho de Nova Descoberta -> Setúbal.
    """
    print("Executando Task 7: Visualização Árvore de Percurso...")
    
    if Network is None:
        print("  [AVISO] 'pyvis' não está instalado. Pulando Task 7.")
        return
        
    if not resultado_percurso or not resultado_percurso.get("percurso"):
        print("  [AVISO] Percurso não foi calculado (Task 6.2 falhou?). Pulando Task 7.")
        return

    path_nodes = resultado_percurso.get("percurso", [])
    if len(path_nodes) < 2:
        print("  [AVISO] Percurso encontrado tem menos de 2 nós. Pulando Task 7.")
        return
        
    arquivo_saida = OUT_DIR / "arvore_percurso.html"
    
    net = Network(height="700px", width="100%", notebook=False, cdn_resources='remote', directed=True)

    for node_name in path_nodes:
        micro = g.get_microrregiao(node_name) or "N/A"
        net.add_node(
            node_name, 
            label=node_name, 
            title=f"Bairro: {node_name}<br>Microrregião: {micro}"
        )

    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        
        edge_weight = 1.0 
        logradouro = "N/A"
        try:
            for neighbor_info in g.adj.get(u, []):
                if neighbor_info["node"] == v:
                    edge_weight = neighbor_info.get("weight", 1.0)
                    logradouro = neighbor_info.get("data", {}).get("logradouro", "N/A")
                    break
        except Exception:
            pass 
        
        net.add_edge(
            u, v, 
            value=edge_weight, 
            title=f"{u} -> {v}<br>Custo: {edge_weight}<br>Logradouro: {logradouro}",
            color="#FF5733", 
            width=4           
        )

    try:
        net.save_graph(str(arquivo_saida))
        print(f"  -> {arquivo_saida} gerado com sucesso.")
    except Exception as e:
        print(f"  [ERRO FATAL] Falha ao salvar {arquivo_saida}: {e}")


# <--- INÍCIO DA MUDANÇA (Task 9) --->
def executar_task_9_visualizacao_interativa(g: Graph, resultado_percurso: dict | None):
    """
    Task 9: Gera o HTML interativo completo com tooltips,
    busca e filtro de "camada" para o percurso.
    """
    print("Executando Task 9: Visualização Interativa do Grafo...")
    
    if Network is None:
        print("  [AVISO] 'pyvis' não está instalado. Pulando Task 9.")
        return
        
    arquivo_saida = OUT_DIR / "grafo_interativo.html"
    
    # Pega o caminho especial (lista de nós) para destacar
    path_nodes = []
    if resultado_percurso and resultado_percurso.get("percurso"):
        path_nodes = resultado_percurso.get("percurso", [])
        
    # Requisito 2: Adiciona menus de seleção (Busca e Filtro)
    net = Network(
        height="900px", 
        width="100%", 
        notebook=False, 
        cdn_resources='remote', 
        directed=False,
        select_menu=True, # Caixa de busca por nó (Requisito 9.2)
        filter_menu=True  # Filtro por grupo (para o Requisito 9.3)
    )

    # Adiciona todos os Nós
    print("  ... Adicionando nós (calculando métricas de ego)...")
    for node_name in g.nodes_data.keys():
        
        # Requisito 1: Tooltip com grau, microrregião, densidade_ego
        grau = g.get_grau(node_name)
        micro = g.get_microrregiao(node_name) or "N/A"
        
        try:
            ego_metrics = g.ego_metrics_for(node_name)
            densidade_ego = ego_metrics.get("densidade_ego", 0.0)
        except Exception:
            densidade_ego = 0.0 # Fallback
            
        tooltip = (
            f"Bairro: {node_name}<br>"
            f"Microrregião: {micro}<br>"
            f"Grau: {grau}<br>"
            f"Densidade_Ego: {densidade_ego:.4f}"
        )
        
        # Requisito 3: Agrupa o percurso especial
        # O grupo padrão será a Microrregião
        grupo = micro
        cor_node = None # Deixa o pyvis decidir a cor com base no grupo
        tamanho_node = 15
        
        if node_name in path_nodes:
            # Sobrepõe o grupo para ser o do percurso
            grupo = "Percurso (Nova Descoberta -> Setúbal)" 
            cor_node = "#FF5733" # Cor de destaque
            tamanho_node = 25
        
        net.add_node(
            node_name, 
            label=node_name, 
            title=tooltip,
            group=grupo, # Agrupa por microrregião OU pelo percurso
            color=cor_node,
            size=tamanho_node
        )

    # Adiciona todas as Arestas
    print("  ... Adicionando arestas...")
    arestas_adicionadas = set()
    for u, neighbors in g.adj.items():
        for info in neighbors:
            v = info["node"]
            
            if (v, u) in arestas_adicionadas:
                continue
                
            edge_weight = info.get("weight", 1.0)
            logradouro = info.get("data", {}).get("logradouro", "N/A")
            
            tooltip_aresta = f"{u} <-> {v}<br>Peso: {edge_weight}<br>Logradouro: {logradouro}"
            
            # Requisito 3: Realçar arestas do caminho
            cor_aresta = "#DDDDDD" # Cor padrão
            largura_aresta = 2
            
            # Verifica se a aresta (u,v) ou (v,u) faz parte do caminho
            is_path_edge = False
            if u in path_nodes and v in path_nodes:
                try:
                    idx_u = path_nodes.index(u)
                    idx_v = path_nodes.index(v)
                    if abs(idx_u - idx_v) == 1:
                        is_path_edge = True
                except ValueError:
                    pass 
            
            if is_path_edge:
                cor_aresta = "#FF5733" # Cor de destaque
                largura_aresta = 5
            
            net.add_edge(
                u, v, 
                value=edge_weight, 
                title=tooltip_aresta,
                color=cor_aresta,
                width=largura_aresta
            )
            arestas_adicionadas.add((u, v))

    # Configura a física
    print("  ... Configurando física e salvando HTML...")
    net.set_options("""
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
      },
      "interaction": {
        "tooltipDelay": 200,
        "hideEdgesOnDrag": true
      }
    }
    """)

    try:
        net.save_graph(str(arquivo_saida))
        print(f"  -> {arquivo_saida} gerado com sucesso.")
    except Exception as e:
        print(f"  [ERRO FATAL] Falha ao salvar {arquivo_saida}: {e}")
# <--- FIM DA MUDANÇA (Task 9) --->


def main():
    """
    Orquestrador principal para executar as tarefas da Parte 1.
    """
    print("Iniciando a execução das tarefas de métricas da Parte 1...")
    
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
    # (Task 3.1)
    try:
        print("Executando Task 3.1: Métricas Globais...")
        ordem_v = g.get_ordem()
        tamanho_e = g.get_tamanho()
        densidade = g._densidade(ordem_v, tamanho_e) if ordem_v >= 2 else 0.0
            
        metricas = {"ordem": ordem_v, "tamanho": tamanho_e, "densidade": densidade}
        
        arquivo_saida_global = OUT_DIR / "recife_global.json"
        with open(arquivo_saida_global, 'w', encoding='utf-8') as f:
            json.dump(metricas, f, indent=4)
            
        print(f"  -> {arquivo_saida_global} gerado com sucesso.")
        print(f"     Ordem: {ordem_v}, Tamanho: {tamanho_e}, Densidade: {densidade:.6f}")
    except Exception as e:
        print(f"[ERRO Task 3.1] {e}")

    # (Task 3.2)
    try:
        print("Executando Task 3.2: Métricas por Microrregião...")
        g.export_microrregioes_json() 
    except Exception as e:
        print(f"[ERRO Task 3.2] {e}")

    # (Task 3.3)
    try:
        print("Executando Task 3.3: Métricas Ego-Rede...")
        g.export_ego_csv() 
    except Exception as e:
        print(f"[ERRO Task 3.3] {e}")
        
    # (Task 4)
    try:
        print("Executando Task 4: Lista de Graus...")
        g.export_graus_csv() 
    except Exception as e:
        print(f"[ERRO Task 4] {e}")

    # (Task 4 Rankings)
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
    
    # Task 6: Distâncias e Percursos
    executar_task_6_distancias(g)
    resultado_percurso_especial = executar_task_6_percurso_especial(g)
    
    # Task 7: Árvore de Percurso
    executar_task_7_arvore_percurso(g, resultado_percurso_especial)
    
    # Task 9: Visualização Interativa
    executar_task_9_visualizacao_interativa(g, resultado_percurso_especial)
    
    print("-" * 30)
    print("Execução das tasks concluída.")


if __name__ == "__main__":
    main()