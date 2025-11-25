import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from graphs.graph import Graph
from graphs.algorithms import bellman_ford

# criação dos grafos!!!!!!!!!

@pytest.fixture
def grafo_bf_sem_ciclo_negativo():

    # Menor caminho A → C tem custo -1 (A-B-C).

    g = Graph(directed=True, weighted=True)

    for node in ["A", "B", "C"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", -2.0)
    g.add_edge("A", "C", 4.0)

    return g


@pytest.fixture
def grafo_bf_com_ciclo_negativo():

    # Ciclo A-B-C-A tem peso total -1.

    g = Graph(directed=True, weighted=True)

    for node in ["A", "B", "C"]:
        g.add_node(node)

    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", -2.0)
    g.add_edge("C", "A", 0.0)

    return g

# parte de testes a partir daqui!!!!!!!!!!!!

def test_bellman_ford_negative_weights_no_negative_cycle(grafo_bf_sem_ciclo_negativo):

    # Bellman–Ford: pesos negativos, mas sem ciclo negativo → distâncias corretas.
   
    result = bellman_ford(grafo_bf_sem_ciclo_negativo, "A")

    dist = result["distance"]
    has_negative_cycle = result["has_negative_cycle"]

    # A → C via B: 1 + (-2) = -1
    assert pytest.approx(dist["C"]) == -1.0
    assert has_negative_cycle is False


def test_bellman_ford_detects_negative_cycle(grafo_bf_com_ciclo_negativo):

    # Bellman–Ford: deve sinalizar a presença de ciclo negativo.

    result = bellman_ford(grafo_bf_com_ciclo_negativo, "A")

    assert result["has_negative_cycle"] is True


def test_bellman_ford_invalid_start():

    # Deve falhar com ValueError se o nó de origem não existir.

    g = Graph(directed=True, weighted=True)
    g.add_node("A")

    with pytest.raises(ValueError, match="Nó de origem não encontrado"):
        bellman_ford(g, "X")

def test_bellman_ford_negative_cycle_unreachable_from_start():

    # Ciclo negativo existe, mas não é alcançável a partir de 'A'.
    # Bellman–Ford NÃO deve marcar has_negative_cycle=True.

    g = Graph(directed=True, weighted=True)

    for node in ["A", "B", "C", "D"]:
        g.add_node(node)

    # parte acessível
    g.add_edge("A", "B", 1.0)

    # parte separada (tipo pontos fora do grafo principal) separado com ciclo negativo
    g.add_edge("C", "D", -1.0)
    g.add_edge("D", "C", -1.0)

    result = bellman_ford(g, "A")

    assert result["distance"]["A"] == 0.0
    assert result["distance"]["B"] == 1.0
    assert result["distance"]["C"] == float("inf")
    assert result["distance"]["D"] == float("inf")

    # O ciclo negativo existe, mas não afeta caminhos partindo de A
    assert result["has_negative_cycle"] is False

def test_bellman_ford_positive_weights_parents_and_distances():

    # Checa distâncias e predecessores em um grafo 100% positivo
    # É um teste basico, para ver se o algoritimo está funcional no caso mais "vanilla" possivel

    g = Graph(directed=True, weighted=True)

    for node in ["A", "B", "C"]:
        g.add_node(node)

    g.add_edge("A", "B", 2.0)
    g.add_edge("A", "C", 5.0)
    g.add_edge("B", "C", 1.0)

    result = bellman_ford(g, "A")

    dist = result["distance"]
    parent = result["parent"]

    # Distâncias esperadas
    assert dist["A"] == 0.0
    assert dist["B"] == 2.0
    assert dist["C"] == 3.0

    # Pais esperados
    assert parent["B"] == "A"
    assert parent["C"] == "B"

# nota pessoal: valido remover as fixtures que existem. Somente são usadas por 1 função cada, 
# da pra remover elas e colocar nas funções que as usam como foi aplicado nos 3 ultimos testes
# motivo desse comentario é para checar se essa junção seria possivel, ja que o proposito de uma 
# fixture é que ela seja amplamente reutilizada pelo codigo mas aqui apenas um teste utiliza cada
# fixture 