import pytest
import sys
from pathlib import Path

# --- Configuração de Path ---
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# ---------------------------

from graphs.graph import Graph
from graphs.algorithms import dfs


@pytest.fixture
def grafo_dfs_arvore():
    """
    Grafo em forma de árvore (sem ciclo).

        A
       / \
      B   C
         /
        D
    """
    g = Graph()
    for node in ["A", "B", "C", "D"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)
    g.add_edge("A", "C", 1.0)
    g.add_edge("C", "D", 1.0)

    return g


@pytest.fixture
def grafo_dfs_ciclico():
    """
    Grafo com ciclo simples.

        A
       / \
      B---C

    Arestas não direcionadas: A-B, B-C, C-A
    """
    g = Graph()
    for node in ["A", "B", "C"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "A", 1.0)

    return g


def test_dfs_order_tree(grafo_dfs_arvore):
    """DFS: verifica se visita todos os nós partindo da raiz."""
    result = dfs(grafo_dfs_arvore, "A")
    order = result["order"]

    # Deve visitar exatamente esses nós
    assert set(order) == {"A", "B", "C", "D"}
    # A precisa ser o primeiro
    assert order[0] == "A"


def _has_cycle_undirected(graph: Graph, parent: dict[str, str | None]) -> bool:
    """
    Detecta ciclo em grafo não-direcionado usando a árvore de DFS (parent)
    e a lista de adjacência.

    Ideia:
      - Em uma árvore, o número de arestas únicas = número de nós - 1.
      - Se existir alguma aresta {u, v} que não seja aresta de árvore (parent),
        temos um ciclo.
    """
    # Conjunto de arestas de árvore (u, v) como pares ordenados canônicos
    tree_edges = set()
    for v, p in parent.items():
        if p is not None:
            edge = tuple(sorted((v, p)))
            tree_edges.add(edge)

    # Conjunto de todas as arestas únicas do grafo (não-direcionado)
    graph_edges = set()
    for u, vizinhos in graph.adj.items():
        for info in vizinhos:
            v = info["node"]
            edge = tuple(sorted((u, v)))
            graph_edges.add(edge)

    # Se há alguma aresta no grafo que não é de árvore, há ciclo
    extra_edges = graph_edges - tree_edges
    return len(extra_edges) > 0


def test_dfs_detects_cycle(grafo_dfs_ciclico):
    """
    DFS: detecção de ciclo em grafo pequeno.

    O algoritmo dfs em si não retorna 'has_cycle',
    mas usando a árvore (parent) conseguimos identificar
    se existem arestas extras que formam ciclo.
    """
    result = dfs(grafo_dfs_ciclico, "A")
    parent = result["parent"]

    assert _has_cycle_undirected(grafo_dfs_ciclico, parent) is True


def test_dfs_invalid_start():
    """Deve falhar com ValueError se o nó de origem não existir."""
    g = Graph()
    g.add_node("A")

    with pytest.raises(ValueError, match="Nó de origem não encontrado"):
        dfs(g, "X")