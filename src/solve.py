import json
import csv
from pathlib import Path
import unicodedata
import re

# Importações Locais
try:
    from graphs.graph import Graph
    from graphs.algorithms import dijkstra 
except ImportError:
    print("Erro: Dependências 'graphs' não encontradas.")
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

# --- Tasks de Processamento (Lógica de Grafos) ---

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
    # Tenta usar pyvis apenas para esta task simples (se instalado), senão pula
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

# --- GERADOR DE HTML CUSTOMIZADO (Task 9) ---

def gerar_html_customizado(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/grafo_interativo.html' construindo o HTML manualmente.
    Implementa lógica estrita: Clicou -> Isola. O resto vira cinza.
    """
    print("Gerando HTML Interativo Customizado (Manual)...")
    arquivo_saida = OUT_DIR / "grafo_interativo.html"

    # 1. Prepara os dados (Nodes e Edges) para JSON
    vis_nodes = []
    vis_edges = []
    
    path_nodes = list(resultado_percurso.get("percurso", [])) if resultado_percurso else []
    max_grau = max([g.get_grau(n) for n in g.nodes_data] or [1])

    # Dados dos Nós
    for node in g.nodes_data.keys():
        grau = g.get_grau(node)
        micro = g.get_microrregiao(node) or "N/A"
        
        # Tamanho visual
        size = 15 + (grau / max_grau) * 30
        
        vis_nodes.append({
            "id": node,
            "label": node,
            "title": f"<b>{node}</b><br>Microrregião: {micro}<br>Grau: {grau}",
            "group": micro,
            "value": size,
            "font": {"size": 16, "strokeWidth": 2, "strokeColor": "#ffffff"}
        })

    # Dados das Arestas
    added_edges = set()
    for u, neighbors in g.adj.items():
        for info in neighbors:
            v = info["node"]
            # Evita duplicatas (A-B e B-A)
            if (u, v) in added_edges or (v, u) in added_edges: continue
            
            w = info.get("weight", 1.0)
            log = info.get("data", {}).get("logradouro", "")
            
            vis_edges.append({
                "from": u,
                "to": v,
                "title": f"Via: {log}<br>Peso: {w}",
                "color": {"color": "#848484", "opacity": 0.4} # Cor padrão neutra
            })
            added_edges.add((u, v))

    # Serializa para JSON
    json_nodes = json.dumps(vis_nodes, ensure_ascii=False)
    json_edges = json.dumps(vis_edges, ensure_ascii=False)
    json_path = json.dumps(path_nodes, ensure_ascii=False)

    # 2. Template HTML Completo
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Grafo Interativo Recife</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; }}
        #mynetwork {{ width: 100%; height: 100%; }}
        
        /* Painel de Controles */
        #panel {{
            position: absolute; top: 20px; right: 20px; z-index: 10;
            background: rgba(255, 255, 255, 0.95);
            padding: 20px; border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            width: 280px;
        }}
        h3 {{ margin-top: 0; color: #333; font-size: 18px; }}
        p {{ font-size: 13px; color: #666; line-height: 1.5; }}
        
        button {{
            width: 100%; padding: 10px; margin-top: 8px;
            border: none; border-radius: 6px; cursor: pointer;
            font-weight: 600; transition: 0.2s;
        }}
        #btn-rota {{ background-color: #FF5733; color: white; }}
        #btn-rota:hover {{ background-color: #E64A19; }}
        
        #btn-reset {{ background-color: #2196F3; color: white; margin-top: 15px; }}
        #btn-reset:hover {{ background-color: #1976D2; }}

        select {{ width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 10px; }}
    </style>
</head>
<body>

<div id="panel">
    <h3>Controles do Grafo</h3>
    
    <select id="searchNode" onchange="selectFromDropdown(this.value)">
        <option value="">🔍 Buscar Bairro...</option>
    </select>

    <p>
        <b>Modo de Seleção:</b><br>
        • Clique em um bairro para destacá-lo.<br>
        • O restante ficará cinza.<br>
        • Use Ctrl+Clique (ou clique sequencial) para selecionar múltiplos.
    </p>

    <button id="btn-rota" onclick="showRoute()">🚀 Rota: N. Descoberta ➔ Setúbal</button>
    <button id="btn-reset" onclick="resetAll()">👁️ Mostrar Todos (Reset)</button>
</div>

<div id="mynetwork"></div>

<script type="text/javascript">
    // --- DADOS VINDOS DO PYTHON ---
    const nodesArray = {json_nodes};
    const edgesArray = {json_edges};
    const routeNodes = {json_path};

    // Inicializa DataSets
    const nodes = new vis.DataSet(nodesArray);
    const edges = new vis.DataSet(edgesArray);

    // Configuração do Grafo
    const container = document.getElementById('mynetwork');
    const data = {{ nodes: nodes, edges: edges }};
    const options = {{
        nodes: {{
            shape: 'dot',
            borderWidth: 2,
            shadow: true
        }},
        edges: {{
            width: 2,
            smooth: {{ type: 'continuous' }}
        }},
        physics: {{
            forceAtlas2Based: {{
                gravitationalConstant: -60,
                centralGravity: 0.005,
                springLength: 120,
                springConstant: 0.08
            }},
            maxVelocity: 50,
            solver: 'forceAtlas2Based',
            stabilization: {{ enabled: true, iterations: 600 }}
        }},
        interaction: {{
            hover: true,
            tooltipDelay: 200,
            multiselect: true,     // Permite selecionar vários
            selectConnectedEdges: false // CRUCIAL: Não seleciona vizinhos automaticamente
        }}
    }};

    const network = new vis.Network(container, data, options);

    // Popula o Dropdown de busca
    const select = document.getElementById('searchNode');
    const sortedNodes = [...nodesArray].sort((a, b) => a.label.localeCompare(b.label));
    sortedNodes.forEach(n => {{
        const opt = document.createElement('option');
        opt.value = n.id;
        opt.innerText = n.label;
        select.appendChild(opt);
    }});

    // --- ESTADO DA SELEÇÃO ---
    // Usamos um Set para rastrear o que deve estar colorido
    let activeNodes = new Set();

    // --- EVENTOS ---

    // 1. Clique no Grafo
    network.on("click", function (params) {{
        const clickedNode = params.nodes[0];

        if (clickedNode) {{
            // Se clicou num nó, alterna (adiciona/remove) do conjunto ativo
            if (activeNodes.has(clickedNode)) {{
                activeNodes.delete(clickedNode);
            }} else {{
                activeNodes.add(clickedNode);
            }}
        }} else {{
            // Se clicou no fundo vazio, limpa tudo (Reset)
            activeNodes.clear();
        }}

        updateVisuals();
    }});

    // 2. Seleção pelo Dropdown
    function selectFromDropdown(nodeId) {{
        if (!nodeId) return;
        activeNodes.add(nodeId); // Adiciona o buscado à seleção
        updateVisuals();
        
        // Foca a câmera
        network.fit({{ nodes: [nodeId], animation: true }});
        
        // Reseta o select para permitir buscar o mesmo novamente se quiser
        document.getElementById('searchNode').value = "";
    }}

    // 3. Botão Rota Especial
    function showRoute() {{
        if (routeNodes.length === 0) return alert("Rota não disponível.");
        
        activeNodes.clear();
        routeNodes.forEach(id => activeNodes.add(id));
        updateVisuals();
        network.fit({{ nodes: routeNodes, animation: true }});
    }}

    // 4. Botão Reset
    function resetAll() {{
        activeNodes.clear();
        updateVisuals();
        network.fit({{ animation: true }});
    }}

    // --- LÓGICA DE ATUALIZAÇÃO VISUAL (O CÉREBRO) ---
    function updateVisuals() {{
        const allN = nodes.get();
        const allE = edges.get();

        // Arrays para atualização em lote (performance)
        const updatesN = [];
        const updatesE = [];

        // MODO 1: Nada selecionado -> Mostra tudo colorido padrão
        if (activeNodes.size === 0) {{
            allN.forEach(n => {{
                updatesN.push({{ 
                    id: n.id, 
                    color: null,  // null volta para a cor definida no grupo (microrregião)
                    opacity: 1.0,
                    font: {{ color: '#343434' }} 
                }});
            }});
            allE.forEach(e => {{
                updatesE.push({{ 
                    id: e.id, 
                    color: {{ color: '#848484', opacity: 0.4 }}, 
                    width: 2 
                }});
            }});
        }} 
        // MODO 2: Algo selecionado -> Isola os ativos, acinzenta o resto
        else {{
            allN.forEach(n => {{
                if (activeNodes.has(n.id)) {{
                    // NÓ ATIVO: Cor original, opacidade total
                    updatesN.push({{ 
                        id: n.id, 
                        color: null, 
                        opacity: 1.0,
                        font: {{ color: '#000000', background: 'rgba(255,255,255,0.7)' }}
                    }});
                }} else {{
                    // NÓ INATIVO: Cinza, transparente
                    updatesN.push({{ 
                        id: n.id, 
                        color: 'rgba(200, 200, 200, 0.2)', 
                        opacity: 0.2,
                        font: {{ color: 'rgba(0,0,0,0)' }} // Esconde texto
                    }});
                }}
            }});

            allE.forEach(e => {{
                // Aresta só aparece colorida se AMBOS os lados estiverem ativos
                if (activeNodes.has(e.from) && activeNodes.has(e.to)) {{
                    updatesE.push({{ 
                        id: e.id, 
                        color: {{ color: '#FF5733', opacity: 1.0 }}, 
                        width: 4 
                    }});
                }} else {{
                    // Aresta inativa: quase invisível
                    updatesE.push({{ 
                        id: e.id, 
                        color: 'rgba(200, 200, 200, 0.05)', 
                        width: 1 
                    }});
                }}
            }});
        }}

        nodes.update(updatesN);
        edges.update(updatesE);
    }}

</script>
</body>
</html>
    """

    try:
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  -> {arquivo_saida} gerado com sucesso.")
    except Exception as e:
        print(f"  [ERRO] Falha ao salvar HTML: {e}")

# --- Main ---

def main():
    print("Iniciando tasks...")
    nodes_path = DATA_DIR / "bairros_unique.csv"
    edges_path = DATA_DIR / "adjacencias_bairros.csv" 

    if not nodes_path.exists() or not edges_path.exists():
        print("ERRO FATAL: Arquivos CSV não encontrados.")
        return

    g = Graph()
    g.load_from_csvs(nodes_file=nodes_path, edges_file=edges_path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        metricas = {"ordem": g.get_ordem(), "tamanho": g.get_tamanho()}
        with open(OUT_DIR / "recife_global.json", 'w', encoding='utf-8') as f:
            json.dump(metricas, f, indent=4)
        g.export_microrregioes_json()
        g.export_ego_csv()
        g.export_graus_csv()
    except: pass

    executar_task_6_distancias(g)
    res_esp = executar_task_6_percurso_especial(g)
    executar_task_7_arvore_percurso(g, res_esp)
    
    # Executa a geração customizada
    gerar_html_customizado(g, res_esp)
    
    print("Concluído.")

if __name__ == "__main__":
    main()