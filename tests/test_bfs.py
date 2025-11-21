import pytest
import sys
from pathlib import Path

# --- Configuração de Path ---
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# ---------------------------

from graphs.graph import Graph
from graphs.algorithms import bfs


@pytest.fixture
def grafo_bfs():
    """
    Grafo pequeno para testar níveis de BFS.

        A
       / \
      B   C
     /
    D

    Níveis a partir de A:
    - A: 0
    - B: 1
    - C: 1
    - D: 2
    """
    g = Graph()
    for node in ["A", "B", "C", "D"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)
    g.add_edge("A", "C", 1.0)
    g.add_edge("B", "D", 1.0)

    return g


def test_bfs_levels(grafo_bfs):
    """BFS: verifica se os níveis (distâncias) estão corretos em um grafo pequeno."""
    result = bfs(grafo_bfs, "A")

    dist = result["distance"]

    assert dist["A"] == 0
    assert dist["B"] == 1
    assert dist["C"] == 1
    assert dist["D"] == 2


def test_bfs_order(grafo_bfs):
    """
    Garante que a ordem de visita respeita as camadas:
    primeiro A, depois B/C (em alguma ordem), depois D.
    """
    result = bfs(grafo_bfs, "A")
    order = result["order"]

    # A deve ser o primeiro
    assert order[0] == "A"
    # B e C aparecem antes de D
    assert order.index("B") < order.index("D")
    assert order.index("C") < order.index("D")


def test_bfs_unreachable():
    """
    Testa nós inalcançáveis: distâncias devem permanecer -1.
    Grafo:
        A -- B

        C isolado
    """
    g = Graph()
    for node in ["A", "B", "C"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)

    result = bfs(g, "A")
    dist = result["distance"]

    assert dist["A"] == 0
    assert dist["B"] == 1
    # C não é alcançável a partir de A
    assert dist["C"] == -1


def test_bfs_invalid_start():
    """Deve falhar com ValueError se o nó de origem não existir."""
    g = Graph()
    g.add_node("A")

    with pytest.raises(ValueError, match="Nó de origem não encontrado"):
        bfs(g, "X")