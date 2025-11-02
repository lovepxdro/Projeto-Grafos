import csv
from pathlib import Path
from typing import Dict, List, Any
from pathlib import Path
import json
OUT_DIR = Path("out")

class Graph:
    """
    Representa o grafo dos bairros do Recife usando uma lista de adjacência.
    
    Atributos:
        nodes_data (dict): Armazena dados dos nós (ex: microrregião).
                           Formato: { "nome_bairro": {"microrregiao": "X.Y"} }
        adj (dict): A lista de adjacência do grafo.
                    Formato: { "bairro_A": [{"node": "bairro_B", "weight": 1.0, "data": {...}}, ...] }
    """

    def __init__(self):
        """Inicializa um grafo vazio."""
        self.nodes_data: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, List[Dict[str, Any]]] = {}
        print("Instância do Grafo criada.")

    def add_node(self, node_name: str, **kwargs):
        """
        Adiciona um nó (bairro) ao grafo.
        'kwargs' pode conter dados como 'microrregiao'.
        """
        if node_name not in self.nodes_data:
            self.nodes_data[node_name] = kwargs
            self.adj[node_name] = []

    def add_edge(self, u: str, v: str, weight: float, **kwargs):
        """
        Adiciona uma aresta NÃO-DIRECIONADA  entre os nós 'u' e 'v'.
        'kwargs' pode conter dados da aresta como 'logradouro', 'observacao'.
        """
        if u not in self.adj:
            self.add_node(u, microrregiao="DESCONHECIDA")
        if v not in self.adj:
            self.add_node(v, microrregiao="DESCONHECIDA")
            
        edge_data = kwargs
        
        self.adj[u].append({"node": v, "weight": weight, "data": edge_data})
        
        self.adj[v].append({"node": u, "weight": weight, "data": edge_data})

    def load_from_csvs(self, nodes_file: Path, edges_file: Path):
        """
        Carrega os nós e as arestas a partir dos arquivos CSV especificados.
        """
        print(f"Carregando nós de: {nodes_file}")
        try:
            with open(nodes_file, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha_limpa = linha.strip()
                    if not linha_limpa:
                        continue
                    
                    partes = linha_limpa.rsplit(' ', 1)
                    if len(partes) == 2:
                        bairro, microrregiao = partes[0].strip(), partes[1].strip()
                        self.add_node(bairro, microrregiao=microrregiao)
            print(f"Nós carregados: {len(self.nodes_data)}")
        except FileNotFoundError:
            print(f"ERRO FATAL: Arquivo de nós não encontrado em {nodes_file}")
            return
        except Exception as e:
            print(f"ERRO ao ler arquivo de nós: {e}")
            return

        print(f"Carregando arestas de: {edges_file}")
        try:
            with open(edges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    try:
                        weight_float = float(row['peso'])
                    except ValueError:
                        print(f"Aviso: Peso inválido '{row['peso']}' para {row['bairro_origem']}-{row['bairro_destino']}. Usando 1.0.")
                        weight_float = 1.0
                    
                    self.add_edge(
                        u=row['bairro_origem'],
                        v=row['bairro_destino'],
                        weight=weight_float,
                        logradouro=row['logradouro'],
                        observacao=row['observacao']
                    )
                    count += 1
            print(f"Arestas carregadas: {count} (Total de conexões na lista: {count * 2})")
        except FileNotFoundError:
            print(f"ERRO FATAL: Arquivo de arestas não encontrado em {edges_file}")
        except KeyError as e:
            print(f"ERRO FATAL: Coluna {e} faltando no CSV de arestas. Verifique o cabeçalho.")
        except Exception as e:
            print(f"ERRO ao ler arquivo de arestas: {e}")

    # --- Métodos de Acesso (Úteis para as próximas etapas) ---

    def get_ordem(self) -> int:
        """Retorna a Ordem |V| (número de nós) do grafo."""
        return len(self.nodes_data)

    def get_tamanho(self) -> int:
        """Retorna o Tamanho |E| (número de arestas) do grafo."""
        # Em um grafo não-direcionado, |E| = (soma de todos os graus) / 2
        total_grau = sum(len(vizinhos) for vizinhos in self.adj.values())
        return total_grau // 2 # Divisão inteira

    def get_grau(self, node_name: str) -> int:
        """Retorna o grau de um nó específico."""
        if node_name in self.adj:
            return len(self.adj[node_name])
        return 0

    def get_microrregiao(self, node_name: str) -> str | None:
        """Retorna a microrregião de um bairro."""
        if node_name in self.nodes_data:
            return self.nodes_data[node_name].get('microrregiao')
        return None
     
        # === Funções do item 2 ===
    @staticmethod
    def _densidade(n: int, e: int) -> float:
        if n < 2:
            return 0.0
        return (2.0 * e) / (n * (n - 1))

    def _contar_arestas_internas(self, conjunto: set[str]) -> int:
        """Conta arestas cujo par (u,v) está totalmente dentro de 'conjunto' (não-direcionado)."""
        contador = 0
        for u in conjunto:
            for info in self.adj.get(u, []):
                v = info["node"]
                if v in conjunto:
                    contador += 1
        return contador // 2  # corrige dupla contagem

    def export_microrregioes_json(self, saida: Path = OUT_DIR / "microrregioes.json"):
        """
        Para cada microrregião, calcula ordem, tamanho e densidade no subgrafo
        induzido pelos seus bairros. Salva em JSON (lista de objetos).
        """
        # agrupa bairros por microrregião (ignorando DESCONHECIDA)
        grupos: Dict[str, set[str]] = {}
        for bairro, dados in self.nodes_data.items():
            micro = (dados.get("microrregiao") or "").strip()
            if not micro or micro.upper() == "DESCONHECIDA":
                continue
            grupos.setdefault(micro, set()).add(bairro)

        resultados = []
        for micro, bairros in grupos.items():
            ordem = len(bairros)
            tamanho = self._contar_arestas_internas(bairros)
            densidade = self._densidade(ordem, tamanho)
            resultados.append({
                "microrregiao": micro,
                "ordem": ordem,
                "tamanho": tamanho,
                "densidade": densidade
            })

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=4, ensure_ascii=False)

        print(f"Métricas por microrregião salvas em: {saida}")


# --- Bloco de Teste ---
if __name__ == "__main__":
    # Este código só executa se você rodar 'python src/graphs/graph.py'
    # Ele serve para testar se a classe está funcionando.

    print("Testando a classe Graph...")

    # Caminhos relativos à raiz do projeto
    nodes_path = Path("data") / "bairros_unique.csv"
    edges_path = Path("data") / "adjacencias_bairros.csv"

    g = Graph()
    g.load_from_csvs(nodes_file=nodes_path, edges_file=edges_path)

    print("\n--- Teste de Carregamento ---")
    print(f"Ordem |V| (calculado): {g.get_ordem()}")
    print(f"Tamanho |E| (calculado): {g.get_tamanho()}")

    # Testar um bairro específico
    bairro_teste = "Recife"
    print(f"\nGrau do '{bairro_teste}': {g.get_grau(bairro_teste)}")
    print(f"Microrregiao do '{bairro_teste}': {g.get_microrregiao(bairro_teste)}")
    print(f"Vizinhos do '{bairro_teste}':")
    if bairro_teste in g.adj:
        for vizinho in g.adj[bairro_teste]:
            print(f"  -> {vizinho['node']} (Peso: {vizinho['weight']})")

    # === Item 2: exporta métricas por microrregião ===
    try:
        g.export_microrregioes_json()   # gera out/microrregioes.json
    except Exception as e:
        print(f"[microrregioes] erro: {e}")
