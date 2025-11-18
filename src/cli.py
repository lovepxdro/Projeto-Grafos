"""
CLI para executar algoritmos de grafos via linha de comando.

Comandos disponíveis:
  - dijkstra: caminho mínimo entre dois bairros
  - bfs: busca em largura a partir de um bairro
  - dfs: busca em profundidade a partir de um bairro
  - bellman-ford: distâncias e detecção de ciclo negativo a partir de um bairro

Exemplos de uso:
  python -m src.cli dijkstra "Boa Vista" "Graças"
  python -m src.cli bfs "Boa Vista"
  python -m src.cli dfs "Boa Vista"
  python -m src.cli bellman-ford "Boa Vista"

Opções globais:
  --nodes: caminho para o CSV de nós (default: data/bairros_unique.csv)
  --edges: caminho para o CSV de arestas (default: data/adjacencias_bairros.csv)
	--json:  caminho de saída para salvar o resultado em JSON (opcional)
	--verbose: imprime saídas completas (por padrão mostra um resumo)
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


def cmd_dijkstra(args: argparse.Namespace) -> int:
	g = carregar_grafo(args.nodes, args.edges)

	origem = _get_nome_canonico(args.start, g)
	destino = _get_nome_canonico(args.end, g)

	try:
		res = dijkstra(g, origem, destino)
	except Exception as e:
		print(f"[ERRO] {e}")
		return 2

	# Saída console
	caminho = " -> ".join(res.get("path", []))
	print(f"Custo: {res.get('cost')}")
	print(f"Caminho: {caminho}")

	# Salvar JSON (padrão: out/dijkstra_<origem>_<destino>.json)
	out_path = Path(args.json) if args.json else _default_json_path("dijkstra", origem, destino)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "dijkstra", "from": origem, "to": destino, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")

	return 0


def cmd_bfs(args: argparse.Namespace) -> int:
	g = carregar_grafo(args.nodes, args.edges, weighted=False)  # BFS ignora pesos
	origem = _get_nome_canonico(args.start, g)

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

	# Salvar JSON (padrão: out/bfs_<origem>.json)
	out_path = Path(args.json) if args.json else _default_json_path("bfs", origem)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "bfs", "from": origem, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")

	return 0


def cmd_dfs(args: argparse.Namespace) -> int:
	g = carregar_grafo(args.nodes, args.edges, weighted=False)  # DFS ignora pesos
	origem = _get_nome_canonico(args.start, g)

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

	# Salvar JSON (padrão: out/dfs_<origem>.json)
	out_path = Path(args.json) if args.json else _default_json_path("dfs", origem)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "dfs", "from": origem, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")

	return 0


def cmd_bellman_ford(args: argparse.Namespace) -> int:
	g = carregar_grafo(args.nodes, args.edges)
	origem = _get_nome_canonico(args.start, g)

	try:
		res = bellman_ford(g, origem)
	except Exception as e:
		print(f"[ERRO] {e}")
		return 2

	has_neg = res.get("has_negative_cycle", False)
	print(f"Ciclo negativo: {'SIM' if has_neg else 'NÃO'}")
	# Exibe um resumo das distâncias (primeiros 10)
	dist: Dict[str, Any] = res.get("distance", {})  # type: ignore[assignment]
	preview = list(dist.items())[:10]
	print("Algumas distâncias:")
	for k, v in preview:
		print(f"  - {k}: {v}")

	# Salvar JSON (padrão: out/bellman_ford_<origem>.json)
	out_path = Path(args.json) if args.json else _default_json_path("bellman_ford", origem)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"algorithm": "bellman-ford", "from": origem, **res}, f, ensure_ascii=False, indent=2)
	print(f"Resultado salvo em: {out_path}")

	return 0


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="recife-graph",
		description="CLI para executar algoritmos no grafo de bairros do Recife"
	)

	parser.add_argument(
		"--nodes", type=Path, default=None,
		help="Caminho para CSV de nós (default: data/bairros_unique.csv)"
	)
	parser.add_argument(
		"--edges", type=Path, default=None,
		help="Caminho para CSV de arestas (default: data/adjacencias_bairros.csv)"
	)
	parser.add_argument(
		"--json", type=str, default=None,
		help="Se fornecido, salva a saída em JSON no caminho especificado"
	)
	parser.add_argument(
		"--verbose", action="store_true",
		help="Mostra saídas completas no console (por padrão, mostra um resumo)"
	)

	sub = parser.add_subparsers(dest="command", required=True)

	# dijkstra
	p_dij = sub.add_parser("dijkstra", help="Caminho mínimo entre dois bairros")
	p_dij.add_argument("start", type=str, help="Bairro de origem")
	p_dij.add_argument("end", type=str, help="Bairro de destino")
	p_dij.set_defaults(func=cmd_dijkstra)

	# bfs
	p_bfs = sub.add_parser("bfs", help="Busca em largura a partir de um bairro")
	p_bfs.add_argument("start", type=str, help="Bairro de origem")
	p_bfs.set_defaults(func=cmd_bfs)

	# dfs
	p_dfs = sub.add_parser("dfs", help="Busca em profundidade a partir de um bairro")
	p_dfs.add_argument("start", type=str, help="Bairro de origem")
	p_dfs.set_defaults(func=cmd_dfs)

	# bellman-ford
	p_bf = sub.add_parser("bellman-ford", help="Distâncias e detecção de ciclo negativo")
	p_bf.add_argument("start", type=str, help="Bairro de origem")
	p_bf.set_defaults(func=cmd_bellman_ford)

	return parser


def main(argv: list[str] | None = None) -> int:
	parser = build_parser()
	args = parser.parse_args(argv)
	func = getattr(args, "func", None)
	if func is None:
		parser.print_help()
		return 1
	return int(func(args))


if __name__ == "__main__":
	raise SystemExit(main())

