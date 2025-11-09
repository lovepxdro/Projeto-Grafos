import pytest
import sys
from pathlib import Path

# --- Configuração de Path ---
# Adiciona a pasta 'src' ao sys.path para permitir importações
# de 'src.graphs.graph' e 'src.graphs.algorithms'
# Isso garante que o teste possa ser executado da raiz do projeto (ex: 'pytest')
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
# ---------------------------

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
    """
    Cria um grafo de teste pequeno e previsível para os cenários do Dijkstra.
    
    Caminhos:
    - A -> B (1)
    - A -> C (4)
    - B -> C (2)
    - B -> D (5)
    - C -> D (1)
    - E -> F (1) (Componente desconectado)
    - G -> H (-1) (Para teste de peso negativo)
    """
    g = Graph()
    
    # Nós principais
    nodes = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for node in nodes:
        g.add_node(node) # Adiciona nós com microrregião padrão

    # Arestas
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
    """Testa um caminho simples e direto."""
    result = dijkstra(test_graph, "A", "B")
    assert result["cost"] == 1
    assert result["path"] == ["A", "B"]

def test_indirect_path(test_graph):
    """
    Testa um caminho onde a rota indireta é mais barata.
    A -> C (custo 4)
    A -> B -> C (custo 1 + 2 = 3)
    """
    result = dijkstra(test_graph, "A", "C")
    assert result["cost"] == 3
    assert result["path"] == ["A", "B", "C"]

def test_multi_hop_path(test_graph):
    """
    Testa um caminho mais longo.
    A -> B -> C -> D (custo 1 + 2 + 1 = 4)
    """
    result = dijkstra(test_graph, "A", "D")
    assert result["cost"] == 4
    assert result["path"] == ["A", "B", "C", "D"]

def test_no_path(test_graph):
    """Testa nós em componentes desconectados."""
    result = dijkstra(test_graph, "A", "E")
    assert result["cost"] == float('inf')
    assert result["path"] == []

def test_same_node(test_graph):
    """Testa o caminho de um nó para ele mesmo."""
    result = dijkstra(test_graph, "A", "A")
    assert result["cost"] == 0
    assert result["path"] == ["A"]

def test_nonexistent_nodes(test_graph):
    """Testa se o algoritmo falha corretamente se os nós não existirem."""
    with pytest.raises(ValueError, match="Nó de origem não encontrado"):
        dijkstra(test_graph, "Z", "A")
        
    with pytest.raises(ValueError, match="Nó de destino não encontrado"):
        dijkstra(test_graph, "A", "Z")

def test_negative_weight_failure(test_graph):
    """
    Verifica se o Dijkstra levanta um erro ao encontrar uma aresta
    [cite_start]com peso negativo, conforme exigido pelo PDF[cite: 162].
    """
    with pytest.raises(ValueError, match="Peso negativo encontrado"):
        # O caminho G -> H tem peso -1
        dijkstra(test_graph, "G", "H")