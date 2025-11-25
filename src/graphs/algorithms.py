import heapq
from typing import Dict, List, Any, Tuple
from collections import deque


try:
    from .graph import Graph
except ImportError:
    from graph import Graph

def dijkstra(graph: Graph, start_node: str, end_node: str) -> Dict[str, Any]:

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

        if current_distance > distances[current_node]:
            continue

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
    
    path.reverse() # Inverter para ficar da origem -> destino

    if path[0] == start_node:
        return {"cost": final_cost, "path": path}
    else:
        print(f"Erro na reconstrução do caminho para '{end_node}'.")
        return {"cost": float('inf'), "path": []}
    
def bfs(graph: Graph, start_node: str) -> Dict[str, Any]:

    # busca em largura

    if start_node not in graph.nodes_data:
        raise ValueError(f"Nó de origem não encontrado no grafo: '{start_node}'")

    visited: Dict[str, bool] = {node: False for node in graph.nodes_data}
    distance: Dict[str, int] = {node: -1 for node in graph.nodes_data}
    parent: Dict[str, str | None] = {node: None for node in graph.nodes_data}

    fila = deque()
    fila.append(start_node)
    visited[start_node] = True
    distance[start_node] = 0

    order: List[str] = []

    while fila:
        u = fila.popleft()
        order.append(u)

        for info in graph.adj.get(u, []):
            v = info["node"]
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                distance[v] = distance[u] + 1
                fila.append(v)

    return {
        "order": order,
        "distance": distance,
        "parent": parent,
    }

def dfs(graph: Graph, start_node: str) -> Dict[str, Any]:
    
    # busca em profundidade

    if start_node not in graph.nodes_data:
        raise ValueError(f"Nó de origem não encontrado no grafo: '{start_node}'")

    visited: Dict[str, bool] = {node: False for node in graph.nodes_data}
    parent: Dict[str, str | None] = {node: None for node in graph.nodes_data}

    stack: List[str] = [start_node]
    order: List[str] = []

    while stack:
        u = stack.pop()

        if visited[u]:
            continue

        visited[u] = True
        order.append(u)

        vizinhos = graph.adj.get(u, [])
        for info in reversed(vizinhos):
            v = info["node"]
            if not visited[v]:
                if parent[v] is None:
                    parent[v] = u
                stack.append(v)

    return {
        "order": order,
        "parent": parent,
    }

def bellman_ford(graph: Graph, start_node: str) -> Dict[str, Any]:
    
    if start_node not in graph.nodes_data:
        raise ValueError(f"Nó de origem não encontrado no grafo: '{start_node}'")

    dist: Dict[str, float] = {node: float("inf") for node in graph.nodes_data}
    parent: Dict[str, str | None] = {node: None for node in graph.nodes_data}
    dist[start_node] = 0.0

    edges: List[Tuple[str, str, float]] = []
    for u, vizinhos in graph.adj.items():
        for info in vizinhos:
            v = info["node"]
            w = info["weight"]
            edges.append((u, v, w))

    n = len(graph.nodes_data)

    for _ in range(n - 1):
        trocou = False
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                trocou = True
        if not trocou:
            break

    # checa ciclos negativos
    has_negative_cycle = False
    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    return {
        "distance": dist,
        "parent": parent,
        "has_negative_cycle": has_negative_cycle,
    }