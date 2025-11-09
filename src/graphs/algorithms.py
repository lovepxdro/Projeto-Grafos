import heapq
from typing import Dict, List, Any, Tuple


try:
    from .graph import Graph
except ImportError:
    from graph import Graph

def dijkstra(graph: Graph, start_node: str, end_node: str) -> Dict[str, Any]:
    """
    Calcula o caminho mais curto entre dois nós usando o algoritmo de Dijkstra.

    Esta é uma implementação própria, usando 'heapq' como fila de prioridade,
    conforme permitido pelos requisitos do projeto.

    Argumentos:
        graph (Graph): A instância do grafo (da classe 'graph.py').
        start_node (str): O nome do bairro de origem.
        end_node (str): O nome do bairro de destino.

    Levanta:
        ValueError: Se um peso de aresta negativo for encontrado.
        ValueError: Se o nó de origem ou destino não existir no grafo.

    Retorna:
        Dict[str, Any]: Um dicionário contendo:
            - "cost" (float): O custo total do caminho (inf se não houver caminho).
            - "path" (List[str]): A lista de nós (bairros) no caminho.
    """
    
    if start_node not in graph.nodes_data:
        raise ValueError(f"Nó de origem não encontrado no grafo: '{start_node}'")
    if end_node not in graph.nodes_data:
        raise ValueError(f"Nó de destino não encontrado no grafo: '{end_node}'")

    distances: Dict[str, float] = {node: float('inf') for node in graph.nodes_data}
    previous_nodes: Dict[str, str | None] = {node: None for node in graph.nodes_data}

    distances[start_node] = 0

    priority_queue: List[Tuple[float, str]] = [(0, start_node)]

    print(f"Iniciando Dijkstra de '{start_node}' para '{end_node}'...")

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Otimização: Se já processamos um caminho mais curto para este nó, ignore
        if current_distance > distances[current_node]:
            continue
            
        # Otimização: Se chegamos ao destino, podemos parar
        if current_node == end_node:
            print("Destino encontrado.")
            break


        for neighbor_info in graph.adj.get(current_node, []):
            neighbor = neighbor_info["node"]
            weight = neighbor_info["weight"]

            # Requisito do PDF: Dijkstra não deve aceitar pesos negativos [cite: 265]
            if weight < 0:
                raise ValueError(
                    f"Peso negativo encontrado na aresta {current_node}-{neighbor}. "
                    "Dijkstra não é aplicável."
                )

            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node

                heapq.heappush(priority_queue, (new_distance, neighbor))

    path: List[str] = []
    final_cost = distances[end_node]

    if final_cost == float('inf'):
        print(f"Não foi encontrado caminho de '{start_node}' para '{end_node}'.")
        return {"cost": float('inf'), "path": []}

    current = end_node
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    
    path.reverse() # Inverte para ficar da origem -> destino

    # Verificação final
    if path[0] == start_node:
        return {"cost": final_cost, "path": path}
    else:
        # Isso não deve acontecer se a lógica estiver correta e end_node foi alcançado
        print(f"Erro na reconstrução do caminho para '{end_node}'.")
        return {"cost": float('inf'), "path": []}