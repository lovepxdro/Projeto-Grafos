import pytest
import sys
from pathlib import Path

# --- Configuração de Path ---
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# ---------------------------

from graphs.graph import Graph
from graphs.algorithms import bellman_ford


@pytest.fixture
def grafo_bf_sem_ciclo_negativo():
    """
    Grafo com pesos negativos, mas SEM ciclo negativo.

        A → B (1)
        B → C (-2)
        A → C (4)

    Menor caminho A → C tem custo -1 (A-B-C).
    """
    g = Graph(directed=True, weighted=True)

    for node in ["A", "B", "C"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", -2.0)
    g.add_edge("A", "C", 4.0)

    return g


@pytest.fixture
def grafo_bf_com_ciclo_negativo():
    """
    Grafo com ciclo negativo.

        A → B (1)
        B → C (-2)
        C → A (0)

    Ciclo A-B-C-A tem peso total -1.
    """
    g = Graph(directed=True, weighted=True)

    for node in ["A", "B", "C"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", -2.0)
    g.add_edge("C", "A", 0.0)

    return g


def test_bellman_ford_negative_weights_no_negative_cycle(grafo_bf_sem_ciclo_negativo):
    """
    Bellman–Ford: pesos negativos, mas sem ciclo negativo → distâncias corretas.
    """
    result = bellman_ford(grafo_bf_sem_ciclo_negativo, "A")

    dist = result["distance"]
    has_negative_cycle = result["has_negative_cycle"]

    # A → C via B: 1 + (-2) = -1
    assert pytest.approx(dist["C"]) == -1.0
    assert has_negative_cycle is False


def test_bellman_ford_detects_negative_cycle(grafo_bf_com_ciclo_negativo):
    """
    Bellman–Ford: deve sinalizar a presença de ciclo negativo.
    """
    result = bellman_ford(grafo_bf_com_ciclo_negativo, "A")

    assert result["has_negative_cycle"] is True


def test_bellman_ford_invalid_start():
    """Deve falhar com ValueError se o nó de origem não existir."""
    g = Graph(directed=True, weighted=True)
    g.add_node("A")

    with pytest.raises(ValueError, match="Nó de origem não encontrado"):
        bellman_ford(g, "X")