import json
import math
from pathlib import Path
import typing

# Tenta importar matplotlib para gráficos estáticos (Task 8)
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    print("Aviso: 'matplotlib' não encontrado. Gráficos estáticos (Task 8) serão pulados.")

# Tenta importar PyVis para a Task 7 (Opcional/Bônus)
try:
    from pyvis.network import Network
except ImportError:
    Network = None

# Tenta importar Graph para Type Hinting
try:
    from graphs.graph import Graph
except ImportError:
    try:
        from src.graphs.graph import Graph
    except ImportError:
        Graph = typing.Any 

# Caminhos
REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
#  TASK 7: ÁRVORE DE PERCURSO (Hierarchical Layout)
# ==============================================================================

def gerar_arvore_percurso(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/arvore_percurso.html' usando PyVis com Layout Hierárquico.
    Atende ao requisito: "Transforme o percurso em árvore... destacar caminho".
    Visual: Origem (Verde) -> Destino (Vermelho) em layout Top-Down.
    """
    if Network is None:
        print("  [viz.py] PyVis não instalado. Pulando Task 7.")
        return

    if not resultado_percurso or not resultado_percurso.get("percurso"):
        print("  [viz.py] Sem percurso para gerar árvore.")
        return

    print("  [viz.py] Gerando Árvore de Percurso (Hierárquica)...")
    path_nodes = resultado_percurso.get("percurso", [])
    
    if len(path_nodes) < 2:
        return

    arquivo_saida = OUT_DIR / "arvore_percurso.html"
    
    # Directed=True para mostrar as setas do fluxo
    net = Network(height="700px", width="100%", notebook=False, cdn_resources='remote', directed=True)

    # Adiciona Nós com cores semânticas
    for i, node in enumerate(path_nodes):
        micro = g.get_microrregiao(node) or "N/A"
        
        # Definição de Cores e Formas
        color = "#97C2FC" # Azul padrão (Intermediário)
        shape = "dot"
        size = 20
        label_extra = ""

        if i == 0: # Origem
            color = "#00CC66" # Verde
            label_extra = "\n(Origem)"
            size = 30
        elif i == len(path_nodes) - 1: # Destino
            color = "#FF5733" # Vermelho
            label_extra = "\n(Destino)"
            size = 30
        
        tooltip = f"<b>{node}</b><br>Microrregião: {micro}<br>Passo: {i+1}/{len(path_nodes)}"
        
        net.add_node(
            node, 
            label=f"{i+1}. {node}{label_extra}", 
            title=tooltip, 
            color=color, 
            size=size,
            shape=shape,
            font={"size": 16, "face": "arial", "strokeWidth": 2, "strokeColor": "#ffffff"}
        )

    # Adiciona Arestas com nomes de ruas
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        
        # Recupera dados da aresta (peso e logradouro)
        edge_weight = 1.0
        logradouro = "?"
        
        # Busca na lista de adjacência
        found = False
        for info in g.adj.get(u, []):
            if info["node"] == v:
                edge_weight = info.get("weight", 1.0)
                logradouro = info.get("data", {}).get("logradouro", "")
                found = True
                break
        
        label_edge = f"{logradouro}" if logradouro else f"{edge_weight}"
        
        net.add_edge(
            u, v, 
            label=label_edge, # Mostra nome da rua na aresta
            title=f"Via: {logradouro}<br>Custo: {edge_weight}",
            color="#555555",
            width=3,
            arrowStrikethrough=False
        )

    # Opções para forçar Layout de Árvore (Hierarchical)
    net.set_options("""
    var options = {
        "layout": {
            "hierarchical": {
                "enabled": true,
                "direction": "UD",
                "sortMethod": "directed",
                "nodeSpacing": 150,
                "levelSeparation": 150
            }
        },
        "physics": {
            "hierarchicalRepulsion": {
                "centralGravity": 0,
                "springLength": 200,
                "nodeDistance": 150
            },
            "minVelocity": 0.75,
            "solver": "hierarchicalRepulsion"
        },
        "edges": {
            "smooth": {
                "type": "cubicBezier",
                "forceDirection": "vertical",
                "roundness": 0.4
            }
        }
    }
    """)

    try:
        net.save_graph(str(arquivo_saida))
        print(f"  -> {arquivo_saida} gerado com sucesso!")
    except Exception as e:
        print(f"  [ERRO] Falha ao salvar Task 7: {e}")


# ==============================================================================
#  TASK 9 + BÔNUS: GERAÇÃO DO HTML INTERATIVO
# ==============================================================================

def gerar_html_customizado(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/grafo_interativo.html' manual.
    Inclui Bônus de UX: Filtro por Microrregião, Isolamento visual, Stats.
    """
    print("  [viz.py] Gerando HTML Interativo Customizado (Task 9)...")
    arquivo_saida = OUT_DIR / "grafo_interativo.html"

    vis_nodes = []
    vis_edges = []
    
    path_nodes = list(resultado_percurso.get("percurso", [])) if resultado_percurso else []
    graus = [g.get_grau(n) for n in g.nodes_data.keys()]
    max_grau = max(graus) if graus else 1
    microrregioes = set()

    for node in g.nodes_data.keys():
        grau = g.get_grau(node)
        micro = g.get_microrregiao(node) or "Desconhecida"
        microrregioes.add(micro)
        size = 15 + (grau / max_grau) * 30
        
        vis_nodes.append({
            "id": node,
            "label": node,
            "title": f"<div style='font-family:sans-serif;'><b>{node}</b><br>📍 {micro}<br>🔗 Grau: {grau}</div>",
            "group": micro,
            "value": size,
            "microrregiao": micro,
            "font": {"size": 16, "strokeWidth": 3, "strokeColor": "#ffffff"}
        })

    added_edges = set()
    for u, neighbors in g.adj.items():
        for info in neighbors:
            v = info["node"]
            if (u, v) in added_edges or (v, u) in added_edges: continue
            w = info.get("weight", 1.0)
            log = info.get("data", {}).get("logradouro", "")
            vis_edges.append({
                "from": u, "to": v,
                "title": f"🛣️ {log}<br>⚖️ {w}",
                "color": {"color": "#848484", "opacity": 0.4}
            })
            added_edges.add((u, v))

    json_nodes = json.dumps(vis_nodes, ensure_ascii=False)
    json_edges = json.dumps(vis_edges, ensure_ascii=False)
    json_path = json.dumps(path_nodes, ensure_ascii=False)
    json_micros = json.dumps(sorted(list(microrregioes)), ensure_ascii=False)

    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Grafo Interativo do Recife</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #2563eb; --panel-bg: rgba(255, 255, 255, 0.95); --text: #1e293b; }}
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: 'Inter', sans-serif; background: #f8fafc; }}
        #mynetwork {{ width: 100%; height: 100%; }}
        #panel {{
            position: absolute; top: 20px; right: 20px; z-index: 100;
            background: var(--panel-bg); padding: 20px; border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); width: 300px;
            border: 1px solid rgba(255,255,255,0.5);
        }}
        h3 {{ margin-top: 0; color: var(--text); font-size: 18px; font-weight: 800; margin-bottom: 15px; }}
        label {{ display: block; font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 5px; text-transform: uppercase; }}
        select {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 15px; }}
        .btn-row {{ display: flex; gap: 10px; }}
        button {{ flex: 1; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.2s; }}
        #btn-rota {{ background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; }}
        #btn-reset {{ background: white; color: var(--text); border: 1px solid #cbd5e1; }}
        #stats {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; font-size: 12px; color: #64748b; }}
        .stat-item b {{ display: block; font-size: 16px; color: var(--text); }}
    </style>
</head>
<body>
<div id="panel">
    <h3>🗺️ Grafo Recife</h3>
    <label>🔍 Buscar Bairro</label>
    <select id="searchNode" onchange="selectNode(this.value)"><option value="">Selecione...</option></select>
    <label>🏙️ Filtrar Microrregião</label>
    <select id="filterMicro" onchange="filterByMicro(this.value)"><option value="">Todas</option></select>
    <div class="btn-row">
        <button id="btn-rota" onclick="showRoute()">🚀 Rota Task 6</button>
        <button id="btn-reset" onclick="resetAll()">👁️ Resetar</button>
    </div>
    <div id="stats">
        <div class="stat-item"><b><span id="countNodes">0</span></b>Bairros</div>
        <div class="stat-item"><b><span id="countEdges">0</span></b>Conexões</div>
    </div>
</div>
<div id="mynetwork"></div>
<script type="text/javascript">
    const nodesData = {json_nodes}; const edgesData = {json_edges};
    const routeNodes = {json_path}; const microList = {json_micros};
    const nodes = new vis.DataSet(nodesData); const edges = new vis.DataSet(edgesData);
    
    // UI Init
    const searchSelect = document.getElementById('searchNode');
    [...nodesData].sort((a, b) => a.label.localeCompare(b.label)).forEach(n => {{
        const opt = document.createElement('option'); opt.value = n.id; opt.innerText = n.label; searchSelect.appendChild(opt);
    }});
    const filterSelect = document.getElementById('filterMicro');
    microList.forEach(m => {{
        const opt = document.createElement('option'); opt.value = m; opt.innerText = m; filterSelect.appendChild(opt);
    }});
    function updateStats(n, e) {{ document.getElementById('countNodes').innerText = n; document.getElementById('countEdges').innerText = e; }}
    updateStats(nodes.length, edges.length);

    // Grafo
    const container = document.getElementById('mynetwork');
    const data = {{ nodes: nodes, edges: edges }};
    const options = {{
        nodes: {{ shape: 'dot', borderWidth: 2, shadow: true }},
        edges: {{ width: 2, smooth: {{ type: 'continuous' }}, color: {{ inherit: 'from' }} }},
        physics: {{ forceAtlas2Based: {{ gravitationalConstant: -80, springLength: 120 }}, stabilization: {{ iterations: 700 }} }},
        interaction: {{ hover: true, multiselect: true, selectConnectedEdges: false }}
    }};
    const network = new vis.Network(container, data, options);

    let activeNodes = new Set();

    network.on("click", function (params) {{
        const clicked = params.nodes[0];
        if (clicked) {{ if (activeNodes.has(clicked)) activeNodes.delete(clicked); else activeNodes.add(clicked); }}
        else {{ activeNodes.clear(); }}
        updateVisuals();
    }});

    function selectNode(id) {{ if(!id) return; activeNodes.add(id); updateVisuals(); network.fit({{ nodes: [id], animation: true }}); searchSelect.value = ""; }}
    function filterByMicro(micro) {{
        if (!micro) return resetAll();
        activeNodes.clear(); nodesData.forEach(n => {{ if(n.microrregiao === micro) activeNodes.add(n.id); }});
        updateVisuals();
        const arr = Array.from(activeNodes); if(arr.length) network.fit({{ nodes: arr, animation: true }});
    }}
    function showRoute() {{
        if (!routeNodes.length) return alert("Rota vazia");
        activeNodes.clear(); routeNodes.forEach(id => activeNodes.add(id));
        updateVisuals(); network.fit({{ nodes: routeNodes, animation: true }});
    }}
    function resetAll() {{ activeNodes.clear(); filterSelect.value = ""; updateVisuals(); network.fit({{ animation: true }}); }}

    function updateVisuals() {{
        const allN = nodes.get(); const allE = edges.get();
        const updatesN = []; const updatesE = [];
        const isActive = activeNodes.size > 0;
        let vn = 0, ve = 0;

        if (!isActive) {{
            allN.forEach(n => updatesN.push({{ id: n.id, color: null, opacity: 1, font: {{ color: '#343434' }} }}));
            allE.forEach(e => updatesE.push({{ id: e.id, color: null, width: 2, opacity: 0.6 }}));
            vn = allN.length; ve = allE.length;
        }} else {{
            allN.forEach(n => {{
                if (activeNodes.has(n.id)) {{
                    updatesN.push({{ id: n.id, color: null, opacity: 1, font: {{ color: '#000', background: 'rgba(255,255,255,0.8)' }} }});
                    vn++;
                }} else {{
                    updatesN.push({{ id: n.id, color: 'rgba(200,200,200,0.2)', opacity: 0.2, font: {{ color: 'rgba(0,0,0,0)' }} }});
                }}
            }});
            allE.forEach(e => {{
                if (activeNodes.has(e.from) && activeNodes.has(e.to)) {{
                    updatesE.push({{ id: e.id, color: {{ color: '#f97316', opacity: 1 }}, width: 4 }});
                    ve++;
                }} else {{
                    updatesE.push({{ id: e.id, color: 'rgba(200,200,200,0.05)', width: 1 }});
                }}
            }});
        }}
        nodes.update(updatesN); edges.update(updatesE);
        updateStats(vn, ve);
    }}
</script>
</body>
</html>
    """
    try:
        with open(arquivo_saida, "w", encoding="utf-8") as f: f.write(html_content)
        print(f"  -> {arquivo_saida} gerado com sucesso!")
    except Exception as e: print(f"  [ERRO] HTML: {e}")

# ==============================================================================
#  TASK 8: VISUALIZAÇÕES ANALÍTICAS (Matplotlib)
# ==============================================================================

def gerar_visualizacoes_analiticas(g: Graph):
    """
    Gera gráficos estáticos (.png).
    """
    if plt is None: return
    print("  [viz.py] Gerando visualizações analíticas (Task 8)...")
    try: plt.style.use('ggplot')
    except: pass
    bairros = list(g.nodes_data.keys())
    graus = [g.get_grau(n) for n in bairros]

    # 1. Histograma
    try:
        plt.figure(figsize=(8, 5))
        plt.hist(graus, bins=range(min(graus), max(graus) + 2), color='#4A90E2', edgecolor='black', alpha=0.8, align='left')
        plt.title('Distribuição de Graus'); plt.ylabel('Qtd. Bairros')
        plt.tight_layout(); plt.savefig(OUT_DIR / "analise_1_histograma_graus.png"); plt.close()
    except Exception as e: print(f"  [ERRO] G1: {e}")

    # 2. Top 10 Circular
    try:
        ranking = sorted([(n, g.get_grau(n)) for n in g.nodes_data], key=lambda x: x[1], reverse=True)[:10]
        top_nodes = [r[0] for r in ranking]
        plt.figure(figsize=(9, 9))
        pos = {}
        for i, node in enumerate(top_nodes):
            angle = 2 * math.pi * i / len(top_nodes) + (math.pi / 2)
            pos[node] = (3.0 * math.cos(angle), 3.0 * math.sin(angle))
        
        for i, u in enumerate(top_nodes):
            for j, v in enumerate(top_nodes):
                if i >= j: continue
                conn = any(info["node"] == v for info in g.adj.get(u, []))
                if conn: plt.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color='#555', alpha=0.6, linewidth=2, zorder=1)
        
        X = [pos[n][0] for n in top_nodes]; Y = [pos[n][1] for n in top_nodes]
        plt.scatter(X, Y, s=800, c='#FF6B6B', edgecolors='#333', linewidths=2, zorder=2)
        for n, (x,y) in pos.items(): plt.text(x, y, n, fontsize=9, ha='center', va='center', fontweight='bold', color='white')
        plt.title(f'Interconectividade Top {len(top_nodes)} Hubs'); plt.axis('off'); plt.tight_layout()
        plt.savefig(OUT_DIR / "analise_2_subgrafo_top10.png"); plt.close()
    except Exception as e: print(f"  [ERRO] G2: {e}")

    # 3. Densidade Micro
    try:
        micro_dens = {}
        for n in bairros:
            m = g.get_microrregiao(n) or "N/A"
            try: d = g.ego_metrics_for(n).get("densidade_ego", 0)
            except: d = 0
            micro_dens.setdefault(m, []).append(d)
        if "N/A" in micro_dens: del micro_dens["N/A"]
        ms = sorted(micro_dens.keys())
        avgs = [sum(micro_dens[m])/len(micro_dens[m]) for m in ms]
        plt.figure(figsize=(10, 6))
        plt.bar(ms, avgs, color='#48C9B0', edgecolor='#145A32')
        plt.title('Densidade Média por Microrregião'); plt.xticks(rotation=45, ha='right')
        plt.tight_layout(); plt.savefig(OUT_DIR / "analise_3_densidade_micro.png"); plt.close()
    except Exception as e: print(f"  [ERRO] G3: {e}")