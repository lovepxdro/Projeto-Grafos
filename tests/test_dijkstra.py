import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from graphs.graph import Graph
    from graphs.algorithms import dijkstra
except ImportError as e:
    print(f"Erro de importação: {e}")
    print(f"Verifique se os arquivos 'src/graphs/graph.py' e ")
    print(f"'src/graphs/algorithms.py' existem.")
    sys.exit(1)


@pytest.fixture
def test_graph():

    # Cria um grafo de teste pequeno e previsível para os cenários do Dijkstra.
    
    g = Graph()

    nodes = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for node in nodes:
        g.add_node(node)

    g.add_edge("A", "B", 1)
    g.add_edge("A", "C", 4)
    g.add_edge("B", "C", 2)
    g.add_edge("B", "D", 5)
    g.add_edge("C", "D", 1)
    
    # Componente desconectado
    g.add_edge("E", "F", 1)
    
    # Aresta com peso negativo (para teste de falha)
    g.add_edge("G", "H", -1)
    
    return g


def test_simple_path(test_graph):
    # pra testar um caminho simples e direto.
    result = dijkstra(test_graph, "A", "B")
    assert result["cost"] == 1
    assert result["path"] == ["A", "B"]

def test_indirect_path(test_graph):

    # Testa um caminho onde a rota indireta é mais barata.

    result = dijkstra(test_graph, "A", "C")
    assert result["cost"] == 3
    assert result["path"] == ["A", "B", "C"]

def test_multi_hop_path(test_graph):

    # Teste de caminho mais longo.

    result = dijkstra(test_graph, "A", "D")
    assert result["cost"] == 4
    assert result["path"] == ["A", "B", "C", "D"]

def test_no_path(test_graph):
    #teste em nós desconexos
    result = dijkstra(test_graph, "A", "E")
    assert result["cost"] == float('inf')
    assert result["path"] == []

def test_same_node(test_graph):
    # teste nó indo para si mesmo
    result = dijkstra(test_graph, "A", "A")
    assert result["cost"] == 0
    assert result["path"] == ["A"]

def test_nonexistent_nodes(test_graph):
    # O algoritimo deve falhar caso os nós não existam
    with pytest.raises(ValueError, match="Nó de origem não encontrado"):
        dijkstra(test_graph, "Z", "A")
        
    with pytest.raises(ValueError, match="Nó de destino não encontrado"):
        dijkstra(test_graph, "A", "Z")

def test_negative_weight_failure(test_graph):
    # falha ao encontrar peso negativo
    with pytest.raises(ValueError, match="Peso negativo encontrado"):
        # O caminho G -> H tem peso -1
        dijkstra(test_graph, "G", "H")