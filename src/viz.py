import json
from pathlib import Path
import typing

# Tenta importar a classe Graph para Type Hinting
try:
    from graphs.graph import Graph
except ImportError:
    try:
        from src.graphs.graph import Graph
    except ImportError:
        Graph = typing.Any # Fallback se não encontrar

# Caminhos
REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "out"

def gerar_html_customizado(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/grafo_interativo.html' construindo o HTML manualmente.
    Responsável pela Task 9 e Bônus de UX (Isolamento visual).
    """
    print("  [viz.py] Gerando HTML Interativo Customizado...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    arquivo_saida = OUT_DIR / "grafo_interativo.html"

    # 1. Prepara os dados (Nodes e Edges) para JSON
    vis_nodes = []
    vis_edges = []
    
    path_nodes = list(resultado_percurso.get("percurso", [])) if resultado_percurso else []
    
    # Evita erro se lista de nós estiver vazia
    graus = [g.get_grau(n) for n in g.nodes_data.keys()]
    max_grau = max(graus) if graus else 1

    # Dados dos Nós
    for node in g.nodes_data.keys():
        grau = g.get_grau(node)
        micro = g.get_microrregiao(node) or "N/A"
        
        # Tamanho visual proporcional ao grau
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
            # Evita duplicatas visuais (A-B e B-A)
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
        • Use Ctrl+Clique para selecionar múltiplos.
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
        activeNodes.add(nodeId);
        updateVisuals();
        network.fit({{ nodes: [nodeId], animation: true }});
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

    // --- LÓGICA DE ATUALIZAÇÃO VISUAL ---
    function updateVisuals() {{
        const allN = nodes.get();
        const allE = edges.get();
        const updatesN = [];
        const updatesE = [];

        // MODO 1: Nada selecionado -> Mostra tudo colorido padrão
        if (activeNodes.size === 0) {{
            allN.forEach(n => {{
                updatesN.push({{ 
                    id: n.id, 
                    color: null, 
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
                    // NÓ ATIVO
                    updatesN.push({{ 
                        id: n.id, 
                        color: null, 
                        opacity: 1.0,
                        font: {{ color: '#000000', background: 'rgba(255,255,255,0.7)' }}
                    }});
                }} else {{
                    // NÓ INATIVO
                    updatesN.push({{ 
                        id: n.id, 
                        color: 'rgba(200, 200, 200, 0.2)', 
                        opacity: 0.2,
                        font: {{ color: 'rgba(0,0,0,0)' }} 
                    }});
                }}
            }});

            allE.forEach(e => {{
                if (activeNodes.has(e.from) && activeNodes.has(e.to)) {{
                    updatesE.push({{ 
                        id: e.id, 
                        color: {{ color: '#FF5733', opacity: 1.0 }}, 
                        width: 4 
                    }});
                }} else {{
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
        print(f"  -> {arquivo_saida} gerado com sucesso!")
    except Exception as e:
        print(f"  [ERRO] Falha ao salvar HTML: {e}")