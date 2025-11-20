import csv
from pathlib import Path
from typing import Dict, List, Any
import json

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "out"


class Graph:
    """
    Representa o grafo usando uma lista de adjacência.

    Atributos:
        nodes_data (dict): Armazena dados dos nós (ex: microrregião).
                           Formato: { "nome_bairro": {"microrregiao": "X.Y"} }
        adj (dict): A lista de adjacência do grafo.
                    Formato: {
                        "bairro_A": [
                            {"node": "bairro_B", "weight": 1.0, "data": {...}},
                            ...
                        ],
                        ...
                    }
    """

    def __init__(self, directed: bool = False, weighted: bool = True):
        """
        directed: True  -> grafo dirigido
                  False -> não dirigido (padrão, caso dos bairros)
        weighted: True  -> usa pesos das arestas (padrão)
                  False -> grafo não ponderado (peso tratado como 1.0)
        """
        self.directed = directed
        self.weighted = weighted

        self.nodes_data: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, List[Dict[str, Any]]] = {}

        print("Instância do Grafo criada.")

    # === Métricas genéricas (úteis para a Parte 2) ===

    @property
    def num_vertices(self) -> int:
        """Número de vértices |V|."""
        # usa a adjacência, que sempre existe
        return len(self.adj)

    @property
    def num_edges(self) -> int:
        """
        Número de arestas |E|.
        - Se o grafo é dirigido, conta todas as entradas da lista de adjacência.
        - Se não é dirigido, divide por 2 (pois cada aresta aparece duas vezes).
        """
        total = sum(len(vizinhos) for vizinhos in self.adj.values())
        return total if self.directed else total // 2

    def degrees(self) -> Dict[str, int]:
        """Retorna um dicionário {nó: grau(nó)}."""
        return {v: len(vizinhos) for v, vizinhos in self.adj.items()}

    def degree_distribution(self) -> Dict[int, int]:
        """
        Distribuição de graus: {grau k: quantidade de vértices com esse grau}.
        Serve direto para montar o item 'distribuição de graus' da Parte 2.
        """
        dist: Dict[int, int] = {}
        for d in self.degrees().values():
            dist[d] = dist.get(d, 0) + 1
        return dist

    # === Operações básicas de construção ===

    def add_node(self, node_name: str, **kwargs):
        """
        Adiciona um nó ao grafo.
        'kwargs' pode conter dados como 'microrregiao'.
        """
        if node_name not in self.nodes_data:
            self.nodes_data[node_name] = kwargs
            self.adj[node_name] = []

    def add_edge(self, u: str, v: str, weight: float = 1.0, **kwargs):
        """
        Adiciona uma aresta entre 'u' e 'v'.
        - Se self.directed == False, adiciona nos dois sentidos (u->v e v->u).
        - Se self.weighted == False, o peso é tratado como 1.0.
        'kwargs' pode conter dados da aresta (logradouro, observacao, etc.).
        """
        if u not in self.adj:
            self.add_node(u, microrregiao="DESCONHECIDA")
        if v not in self.adj:
            self.add_node(v, microrregiao="DESCONHECIDA")

        edge_data = kwargs

        # Se o grafo não for ponderado, ignoramos o peso passado e usamos 1.0
        if not self.weighted:
            weight = 1.0

        # Aresta u -> v
        self.adj[u].append({"node": v, "weight": weight, "data": edge_data})

        # Se não for dirigido, duplicamos a aresta no sentido contrário
        if not self.directed:
            self.adj[v].append({"node": u, "weight": weight, "data": edge_data})

    # === Carregamento específico dos bairros do Recife (Parte 1) ===

    def load_from_csvs(self, nodes_file: Path, edges_file: Path):
        """
        Carrega os nós e as arestas a partir dos arquivos CSV especificados
        (formato da Parte 1: bairros + adjacencias_bairros.csv).
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

        # === Normalização e mapeamento canônico de nomes ===
        import unicodedata, re

        def _normalize_key(name: str) -> str:
            name = (name or "").strip()
            name = re.sub(r"\s+", " ", name)
            name = ''.join(
                c for c in unicodedata.normalize('NFD', name)
                if unicodedata.category(c) != 'Mn'
            )
            return name.lower()

        # Cria um dicionário que mapeia a forma normalizada para o nome original já carregado
        canon_map = {_normalize_key(n): n for n in self.nodes_data.keys()}

        def _canon_name(raw: str) -> str:
            """Tenta encontrar o nome canônico já existente; se não achar, devolve formatado."""
            key = _normalize_key(raw)
            return canon_map.get(key, raw.strip().title())

        print(f"Carregando arestas de: {edges_file}")
        try:
            with open(edges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    try:
                        weight_float = float(row['peso'])
                    except ValueError:
                        print(
                            f"Aviso: Peso inválido '{row['peso']}' "
                            f"para {row['bairro_origem']}-{row['bairro_destino']}. Usando 1.0."
                        )
                        weight_float = 1.0

                    # Normaliza e busca forma canônica
                    u = _canon_name(row['bairro_origem'])
                    v = _canon_name(row['bairro_destino'])

                    # Se ainda não existir, cria (com aviso)
                    if u not in self.nodes_data:
                        print(f"[AVISO] '{u}' não encontrado. Criando nó DESCONHECIDA.")
                        self.add_node(u, microrregiao="DESCONHECIDA")
                    if v not in self.nodes_data:
                        print(f"[AVISO] '{v}' não encontrado. Criando nó DESCONHECIDA.")
                        self.add_node(v, microrregiao="DESCONHECIDA")

                    # Adiciona a aresta
                    self.add_edge(
                        u=u,
                        v=v,
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

    # === Carregamento adicional de rotas (ex.: routes.csv / aeroportos) ===
    def load_routes_csv(self, routes_file: Path, source_col: str = "source airport", dest_col: str = "destination apirport"):
        """Carrega arestas adicionais a partir de um CSV de rotas (ex. dataset de voos).

        O arquivo esperado deve ter colunas como:
          airline, airline ID, source airport, source airport id, destination apirport, destination airport id, codeshare, stops, equipment

        Apenas as colunas de origem e destino são usadas para criar arestas. Dados extras
        (ex.: airline, stops, equipment) são armazenados em "data" da aresta para possível uso futuro.

        Parâmetros:
          routes_file: Path para o CSV.
          source_col: nome da coluna de origem (default: 'source airport').
          dest_col: nome da coluna de destino (default: 'destination apirport').
        """
        if not routes_file.exists():
            print(f"[rotas] Arquivo não encontrado: {routes_file}")
            return
        print(f"Carregando rotas adicionais de: {routes_file}")
        try:
            with open(routes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for raw_row in reader:
                    # normaliza chaves removendo espaços laterais
                    row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in raw_row.items()}
                    u = row.get(source_col, "").strip()
                    v = row.get(dest_col, "").strip()
                    if not u or not v:
                        continue
                    # Cria nós se não existirem (microrregião desconhecida para este dataset)
                    if u not in self.nodes_data:
                        self.add_node(u, microrregiao="DESCONHECIDA")
                    if v not in self.nodes_data:
                        self.add_node(v, microrregiao="DESCONHECIDA")
                    # Peso: se o grafo não for ponderado, será forçado a 1.0 em add_edge.
                    # Caso queira algum peso, poderia-se derivar de 'stops' (ex.: int(stops)+1). Mantemos 1.0 por simplicidade.
                    self.add_edge(
                        u=u,
                        v=v,
                        weight=1.0,
                        airline=row.get('airline'),
                        stops=row.get('stops'),
                        equipment=row.get('equipment')
                    )
                    count += 1
            print(f"Rotas adicionadas: {count} (Total de conexões inseridas: {count * (1 if self.directed else 2)})")
        except KeyError as e:
            print(f"[rotas] Coluna ausente no CSV: {e}. Verifique o cabeçalho.")
        except Exception as e:
            print(f"[rotas] Erro ao ler rotas: {e}")

    # --- Métodos de Acesso (Úteis para as próximas etapas) ---

    def get_ordem(self) -> int:
        """Retorna a Ordem |V| (número de nós) do grafo."""
        return self.num_vertices  # usa a propriedade genérica

    def get_tamanho(self) -> int:
        """Retorna o Tamanho |E| (número de arestas) do grafo."""
        return self.num_edges  # usa a propriedade genérica

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

    # === Funções do item 2 (microrregiões) ===

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

    # === Funções para calcular o ego-rede de um bairro (item 3) ===

    def _vizinhos(self, u: str) -> set[str]:
        """Retorna o conjunto de vizinhos imediatos de u."""
        return {info["node"] for info in self.adj.get(u, [])}

    def ego_metrics_for(self, v: str) -> dict:
        """
        Calcula métricas da ego-rede de v: S = {v} ∪ N(v).
        Retorna: bairro, grau, ordem_ego, tamanho_ego, densidade_ego.
        """
        grau = self.get_grau(v)
        S = {v} | self._vizinhos(v)          # {v} ∪ N(v)
        N = len(S)                           # ordem_ego
        E = self._contar_arestas_internas(S) # tamanho_ego
        dens = self._densidade(N, E)         # densidade_ego
        return {
            "bairro": v,
            "grau": grau,
            "ordem_ego": N,
            "tamanho_ego": E,
            "densidade_ego": dens
        }

    def export_ego_csv(self, saida: Path = OUT_DIR / "ego_bairro.csv"):
        """
        Gera out/ego_bairro.csv com colunas:
        bairro, grau, ordem_ego, tamanho_ego, densidade_ego.
        """
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        campos = ["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]
        with open(saida, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            # usa os bairros carregados em nodes_data (garante presença mesmo sem arestas)
            for bairro in sorted(self.nodes_data.keys()):
                w.writerow(self.ego_metrics_for(bairro))
        print(f"Ego-métricas salvas em: {saida}")

    # === Item 4: graus e rankings ===

    def export_graus_csv(self, saida: Path = OUT_DIR / "graus.csv"):
        """
        Gera out/graus.csv com colunas:
        bairro, grau (número de interconexões do bairro).
        """
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        campos = ["bairro", "grau"]
        with open(saida, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for bairro in sorted(self.nodes_data.keys()):
                w.writerow({
                    "bairro": bairro,
                    "grau": self.get_grau(bairro)
                })
        print(f"Lista de graus salva em: {saida}")

    def get_bairro_maior_grau(self) -> tuple[str, int]:
        """
        Retorna (bairro, grau) do bairro com maior grau no grafo.
        """
        melhor_bairro = None
        melhor_grau = -1

        for bairro in self.nodes_data.keys():
            g = self.get_grau(bairro)
            if g > melhor_grau:
                melhor_bairro = bairro
                melhor_grau = g

        return melhor_bairro, melhor_grau

    def get_bairro_mais_denso_ego(self) -> dict:
        """
        Retorna o dicionário de métricas da ego-rede do
        bairro com maior densidade_ego.
        """
        melhor_metrics = None
        melhor_dens = -1.0

        for bairro in self.nodes_data.keys():
            metrics = self.ego_metrics_for(bairro)
            dens = metrics["densidade_ego"]
            if dens > melhor_dens:
                melhor_dens = dens
                melhor_metrics = metrics

        return melhor_metrics
