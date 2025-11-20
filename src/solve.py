import json
import csv
from pathlib import Path
import unicodedata
import re

# Importações Locais
try:
    from graphs.graph import Graph
    from graphs.algorithms import dijkstra 
    # Importa as funções de visualização do novo módulo
    from viz import gerar_html_customizado, gerar_visualizacoes_analiticas
except ImportError:
    # Fallback para execução direta
    try:
        from src.graphs.graph import Graph
        from src.graphs.algorithms import dijkstra
        from src.viz import gerar_html_customizado, gerar_visualizacoes_analiticas
    except ImportError:
        print("Erro: Dependências não encontradas. Verifique o PYTHONPATH.")
        exit(1)

# Caminhos
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "out"

# --- Funções Auxiliares ---

def _get_nome_canonico(nome_bairro_raw: str, graph: Graph) -> str | None:
    def _normalize_key(name: str) -> str:
        name = (name or "").strip()
        name = re.sub(r"\s+", " ", name)
        name = ''.join(c for c in unicodedata.normalize('NFD', name)
                       if unicodedata.category(c) != 'Mn')
        return name.lower()

    nome_lower = nome_bairro_raw.lower()
    if "setúbal" in nome_lower or "boa viagem" in nome_lower:
         if "Boa Viagem" in graph.nodes_data: return "Boa Viagem"
    
    try:
        if not hasattr(graph, '_canon_map'):
            graph._canon_map = { _normalize_key(n): n for n in graph.nodes_data.keys() }
    except: graph._canon_map = {}

    return graph._canon_map.get(_normalize_key(nome_bairro_raw), nome_bairro_raw.strip())

# --- Tasks de Processamento ---

def executar_task_6_distancias(g: Graph):
    print("Executando Task 6.1: Cálculo de Distâncias...")
    arquivo_entrada = DATA_DIR / "enderecos.csv"
    if not arquivo_entrada.exists(): return
    
    resultados_csv = []
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                bx = _get_nome_canonico(row.get('bairro_origem', row.get('bairro_origem ', '')), g)
                by = _get_nome_canonico(row.get('bairro_destino', ''), g)
                try:
                    res = dijkstra(g, bx, by)
                    resultados_csv.append({
                        "X": row.get('bairro_origem'), "Y": row.get('bairro_destino'),
                        "bairro X": bx, "bairro Y": by,
                        "custo": res["cost"], "caminho": " -> ".join(res["path"])
                    })
                except: pass
        
        with open(OUT_DIR / "distancias_enderecos.csv", 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["X", "Y", "bairro X", "bairro Y", "custo", "caminho"])
            writer.writeheader()
            writer.writerows(resultados_csv)
    except Exception as e: print(f"Erro Task 6.1: {e}")

def executar_task_6_percurso_especial(g: Graph) -> dict | None:
    print("Executando Task 6.2: Percurso Nova Descoberta -> Setúbal...")
    origem = _get_nome_canonico("Nova Descoberta", g)
    destino = _get_nome_canonico("Setúbal", g)
    try:
        res = dijkstra(g, origem, destino)
        data = {
            "origem_solicitada": "Nova Descoberta", "destino_solicitada": "Setúbal",
            "custo": res["cost"], "percurso": res["path"]
        }
        with open(OUT_DIR / "percurso_nova_descoberta_setubal.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return data
    except: return None

def executar_task_7_arvore_percurso(g: Graph, resultado_percurso: dict | None):
    try:
        from pyvis.network import Network
    except ImportError:
        return

    if not resultado_percurso: return
    path_nodes = resultado_percurso.get("percurso", [])
    if len(path_nodes) < 2: return
        
    arquivo_saida = OUT_DIR / "arvore_percurso.html"
    net = Network(height="700px", width="100%", notebook=False, cdn_resources='remote', directed=True)

    for node in path_nodes:
        net.add_node(node, label=node, color="#FF5733")
    for i in range(len(path_nodes) - 1):
        net.add_edge(path_nodes[i], path_nodes[i+1], color="#FF5733", width=4)
    try:
        net.save_graph(str(arquivo_saida))
    except: pass

# --- Main ---

def main():
    print("Iniciando tasks (Parte 1)...")
    nodes_path = DATA_DIR / "bairros_unique.csv"
    edges_path = DATA_DIR / "adjacencias_bairros.csv" 

    if not nodes_path.exists() or not edges_path.exists():
        print("ERRO FATAL: Arquivos CSV não encontrados em data/.")
        return

    g = Graph()
    g.load_from_csvs(nodes_file=nodes_path, edges_file=edges_path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Métricas Globais e JSONs
    try:
        metricas = {"ordem": g.get_ordem(), "tamanho": g.get_tamanho()}
        with open(OUT_DIR / "recife_global.json", 'w', encoding='utf-8') as f:
            json.dump(metricas, f, indent=4)
        g.export_microrregioes_json()
        g.export_ego_csv()
        g.export_graus_csv()
    except: pass

    # Cálculos de Rota
    executar_task_6_distancias(g)
    res_esp = executar_task_6_percurso_especial(g)
    executar_task_7_arvore_percurso(g, res_esp)
    
    # ---------------------------------------------
    # VISUALIZAÇÃO (Task 8, Task 9 e Bônus)
    # ---------------------------------------------
    print("-" * 30)
    
    # Task 9 e Bônus: HTML Interativo (viz.py)
    gerar_html_customizado(g, res_esp)
    
    # Task 8: Gráficos Estáticos para o PDF (viz.py)
    gerar_visualizacoes_analiticas(g)
    
    print("-" * 30)
    print("Concluído. Verifique a pasta 'out/'.")

if __name__ == "__main__":
    main()