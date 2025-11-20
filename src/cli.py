"""
CLI para executar algoritmos de grafos em dois domínios distintos:
	1. Bairros do Recife (bairros_unique.csv + adjacencias_bairros.csv)
	2. Rotas (aeroportos) via routes.csv

Regra fundamental: NUNCA misturar os dois conjuntos. A seleção é feita por:
	--routes <arquivo>            -> grafo puro de rotas (aeroportos)
	--adjacencias_bairros <arquivo> -> grafo de bairros (usa nodes default)
Se nenhuma flag for fornecida, assume grafo de bairros padrão.

Algoritmos:
	bfs            Busca em largura a partir de um nó
	dfs            Busca em profundidade
	dijkstra       Caminho mínimo entre dois nós (não suporta pesos negativos)
	bellman-ford   Distâncias + detecção de ciclo negativo

Exemplos bairros:
	python -m src.cli --adjacencias_bairros data/adjacencias_bairros.csv bfs "Boa Vista"
	python -m src.cli --adjacencias_bairros data/adjacencias_bairros.csv dijkstra "Boa Vista" "Graças"

Exemplos rotas:
	python -m src.cli --routes data/routes.csv bfs MEX
	python -m src.cli --routes data/routes.csv dijkstra MEX JFK

Flags úteis:
	--routes <csv>                Usa grafo puro de rotas
	--adjacencias_bairros <csv>   Usa grafo de bairros (nós em data/bairros_unique.csv)
	--json <arquivo>              Salva saída em JSON
	--verbose                     Mostra saída completa (ordem de visita completa)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import unicodedata
from typing import Any, Dict

# Imports locais
try:
	from graphs.graph import Graph
	from graphs.algorithms import dijkstra, bfs, dfs, bellman_ford
except ImportError:
	# Permite rodar também como script direto de src/ (sem pacote)
	from src.graphs.graph import Graph  # type: ignore
	from src.graphs.algorithms import dijkstra, bfs, dfs, bellman_ford  # type: ignore


# Caminhos padrão (relativos ao repo)
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "out"


def _normalize_key(name: str) -> str:
	name = (name or "").strip()
	name = re.sub(r"\s+", " ", name)
	name = "".join(c for c in unicodedata.normalize("NFD", name) if unicodedata.category(c) != "Mn")
	return name.lower()


def _get_nome_canonico(nome_bairro_raw: str, graph: Graph) -> str:
	"""
	Mapeia um nome de bairro informado no CLI para o nome canônico no grafo,
	lidando com acentuação e a regra especial de Setúbal/Boa Viagem.
	"""
	# Regra especial (compatível com solve.py)
	nome_lower = (nome_bairro_raw or "").lower()
	if "setúbal" in nome_lower or "setubal" in nome_lower or "boa viagem" in nome_lower:
		if "Boa Viagem" in graph.nodes_data:
			return "Boa Viagem"

	# Cria (ou reusa) mapa canônico normalizado -> original
	if not hasattr(graph, "_canon_map_cli"):
		try:
			graph._canon_map_cli = {_normalize_key(n): n for n in graph.nodes_data.keys()}  # type: ignore[attr-defined]
		except Exception:
			graph._canon_map_cli = {}  # type: ignore[attr-defined]

	nome_normalizado = _normalize_key(nome_bairro_raw)
	return getattr(graph, "_canon_map_cli", {}).get(nome_normalizado, nome_bairro_raw.strip())


def carregar_grafo(nodes_path: Path | None, edges_path: Path | None, directed: bool = False, weighted: bool = True) -> Graph:
	"""
	Carrega o grafo a partir dos CSVs informados (ou padrões).
	"""
	nodes = nodes_path or (DATA_DIR / "bairros_unique.csv")
	edges = edges_path or (DATA_DIR / "adjacencias_bairros.csv")

	g = Graph(directed=directed, weighted=weighted)
	g.load_from_csvs(nodes_file=nodes, edges_file=edges)
	return g


def _slug(*parts: str) -> str:
	"""Gera um nome de arquivo simples a partir de partes de texto."""
	txt = "_".join(p or "" for p in parts)
	txt = txt.strip().lower()
	txt = re.sub(r"[^a-z0-9]+", "_", txt)
	txt = re.sub(r"_+", "_", txt).strip("_")
	return txt or "out"


def _default_json_path(command: str, *name_parts: str) -> Path:
	OUT_DIR.mkdir(parents=True, exist_ok=True)
	return OUT_DIR / f"{command}_{_slug(*name_parts)}.json"


def _build_graph(args: argparse.Namespace, weighted: bool, directed: bool = False) -> tuple[Graph, bool]:
	"""Cria o grafo conforme flags. Retorna (grafo, modo_rotas)."""
	routes_path: Path | None = getattr(args, "routes", None)
	bairros_edges: Path | None = getattr(args, "adjacencias_bairros", None)
	if routes_path and bairros_edges:
		raise SystemExit("[ERRO] Use apenas UMA das flags: --routes OU --adjacencias_bairros")
	if routes_path:
		g = Graph(directed=directed, weighted=weighted)
		if not routes_path.exists():
			raise SystemExit(f"[ERRO] Arquivo de rotas não encontrado: {routes_path}")
		print(f"[LOAD] Grafo de rotas: {routes_path}")
		g.load_routes_csv(routes_path)
		return g, True
	# Bairros
	edges_file = bairros_edges or (DATA_DIR / "adjacencias_bairros.csv")
	nodes_file = DATA_DIR / "bairros_unique.csv"
	if not edges_file.exists():
		raise SystemExit(f"[ERRO] Arquivo de arestas de bairros não encontrado: {edges_file}")
	if not nodes_file.exists():
		raise SystemExit(f"[ERRO] Arquivo de nós de bairros não encontrado: {nodes_file}")
	print(f"[LOAD] Grafo de bairros: {nodes_file} + {edges_file}")
	g = Graph(directed=directed, weighted=weighted)
	g.load_from_csvs(nodes_file=nodes_file, edges_file=edges_file)
	return g, False

def _resolve_nome(raw: str, g: Graph, is_routes: bool) -> str:
	"""Resolve nome canônico apenas para bairros; em rotas retorna cru."""
	return raw if is_routes else _get_nome_canonico(raw, g)

def cmd_dijkstra(args: argparse.Namespace) -> int:
	g, is_routes = _build_graph(args, weighted=True, directed=False)
	origem = _resolve_nome(args.start, g, is_routes)
	destino = _resolve_nome(args.end, g, is_routes)
	try:
		res = dijkstra(g, origem, destino)
	except Exception as e:
		print(f"[ERRO] {e}")
		return 2
	caminho = " -> ".join(res.get("path", []))
	print(f"Custo: {res.get('cost')}")
	print(f"Caminho: {caminho}")
	out_path = Path(args.json) if args.json else _default_json_path("dijkstra", origem, destino)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "dijkstra", "from": origem, "to": destino, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")
	return 0


def cmd_bfs(args: argparse.Namespace) -> int:
	g, is_routes = _build_graph(args, weighted=False, directed=False)
	origem = _resolve_nome(args.start, g, is_routes)
	try:
		res = bfs(g, origem)
	except Exception as e:
		print(f"[ERRO] {e}")
		return 2
	order = res.get("order", [])
	print(f"Visitados: {len(order)} nós")
	if args.verbose:
		print(f"Ordem: {order}")
	else:
		preview = order[:10]
		suffix = " …" if len(order) > 10 else ""
		print(f"Ordem (preview): {preview}{suffix}")
	out_path = Path(args.json) if args.json else _default_json_path("bfs", origem)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "bfs", "from": origem, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")
	return 0


def cmd_dfs(args: argparse.Namespace) -> int:
	g, is_routes = _build_graph(args, weighted=False, directed=False)
	origem = _resolve_nome(args.start, g, is_routes)
	try:
		res = dfs(g, origem)
	except Exception as e:
		print(f"[ERRO] {e}")
		return 2
	order = res.get("order", [])
	print(f"Visitados: {len(order)} nós")
	if args.verbose:
		print(f"Ordem: {order}")
	else:
		preview = order[:10]
		suffix = " …" if len(order) > 10 else ""
		print(f"Ordem (preview): {preview}{suffix}")
	out_path = Path(args.json) if args.json else _default_json_path("dfs", origem)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "dfs", "from": origem, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")
	return 0


def cmd_bellman_ford(args: argparse.Namespace) -> int:
	g, is_routes = _build_graph(args, weighted=True, directed=False)
	origem = _resolve_nome(args.start, g, is_routes)
	try:
		res = bellman_ford(g, origem)
	except Exception as e:
		print(f"[ERRO] {e}")
		return 2
	has_neg = res.get("has_negative_cycle", False)
	print(f"Ciclo negativo: {'SIM' if has_neg else 'NÃO'}")
	dist: Dict[str, Any] = res.get("distance", {})  # type: ignore[assignment]
	preview = list(dist.items())[:10]
	print("Algumas distâncias:")
	for k, v in preview:
		print(f"  - {k}: {v}")
	out_path = Path(args.json) if args.json else _default_json_path("bellman_ford", origem)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "bellman-ford", "from": origem, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")
	return 0


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="recife-graph",
		description="Algoritmos sobre grafo de bairros OU grafo de rotas (não misturados)"
	)
	parser.add_argument("--routes", type=Path, default=None, help="CSV de rotas (usa grafo puro de aeroportos)")
	parser.add_argument("--adjacencias_bairros", type=Path, default=None, help="CSV de adjacências de bairros (usa grafo de bairros)")
	parser.add_argument("--json", type=str, default=None, help="Salva saída em JSON")
	parser.add_argument("--verbose", action="store_true", help="Mostra saída completa")
	sub = parser.add_subparsers(dest="command", required=True)
	# dijkstra
	p_dij = sub.add_parser("dijkstra", help="Caminho mínimo entre dois nós")
	p_dij.add_argument("start", type=str, help="Nó de origem")
	p_dij.add_argument("end", type=str, help="Nó de destino")
	p_dij.set_defaults(func=cmd_dijkstra)
	# bfs
	p_bfs = sub.add_parser("bfs", help="Busca em largura")
	p_bfs.add_argument("start", type=str, help="Nó de origem")
	p_bfs.set_defaults(func=cmd_bfs)
	# dfs
	p_dfs = sub.add_parser("dfs", help="Busca em profundidade")
	p_dfs.add_argument("start", type=str, help="Nó de origem")
	p_dfs.set_defaults(func=cmd_dfs)
	# bellman-ford
	p_bf = sub.add_parser("bellman-ford", help="Distâncias + ciclo negativo")
	p_bf.add_argument("start", type=str, help="Nó de origem")
	p_bf.set_defaults(func=cmd_bellman_ford)
	return parser


def main(argv: list[str] | None = None) -> int:
	parser = build_parser()
	args = parser.parse_args(argv)
	func = getattr(args, "func", None)
	if func is None:
		parser.print_help(); return 1
	return int(func(args))


if __name__ == "__main__":
	raise SystemExit(main())

