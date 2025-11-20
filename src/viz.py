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
#  TASK 9 + BÔNUS UX: HTML INTERATIVO COM FILTROS AVANÇADOS
# ==============================================================================

def gerar_html_customizado(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/grafo_interativo.html' manual.
    Inclui Bônus de UX:
    - Filtro por Microrregião (Camadas).
    - Estatísticas em tempo real.
    - Isolamento visual estrito.
    """
    print("  [viz.py] Gerando HTML Interativo com UX Avançada...")
    arquivo_saida = OUT_DIR / "grafo_interativo.html"

    # 1. Prepara dados para JSON
    vis_nodes = []
    vis_edges = []
    
    path_nodes = list(resultado_percurso.get("percurso", [])) if resultado_percurso else []
    graus = [g.get_grau(n) for n in g.nodes_data.keys()]
    max_grau = max(graus) if graus else 1

    # Coleta todas as microrregiões para filtro
    microrregioes = set()

    # Dados dos Nós
    for node in g.nodes_data.keys():
        grau = g.get_grau(node)
        micro = g.get_microrregiao(node) or "Desconhecida"
        microrregioes.add(micro)
        
        # Tamanho proporcional
        size = 15 + (grau / max_grau) * 30
        
        vis_nodes.append({
            "id": node,
            "label": node,
            "title": (
                f"<div style='text-align:left; font-family:sans-serif;'>"
                f"<b>{node}</b><br>"
                f"📍 Micro: {micro}<br>"
                f"🔗 Grau: {grau} conexões"
                f"</div>"
            ),
            "group": micro,
            "value": size,
            "microrregiao": micro, # Metadado extra para o JS filtrar
            "font": {"size": 16, "strokeWidth": 3, "strokeColor": "#ffffff"}
        })

    # Dados das Arestas
    added_edges = set()
    for u, neighbors in g.adj.items():
        for info in neighbors:
            v = info["node"]
            if (u, v) in added_edges or (v, u) in added_edges: continue
            
            w = info.get("weight", 1.0)
            log = info.get("data", {}).get("logradouro", "")
            
            vis_edges.append({
                "from": u,
                "to": v,
                "title": f"🛣️ Via: {log}<br>⚖️ Peso: {w}",
                "color": {"color": "#848484", "opacity": 0.4}
            })
            added_edges.add((u, v))

    # JSONs injetados
    json_nodes = json.dumps(vis_nodes, ensure_ascii=False)
    json_edges = json.dumps(vis_edges, ensure_ascii=False)
    json_path = json.dumps(path_nodes, ensure_ascii=False)
    json_micros = json.dumps(sorted(list(microrregioes)), ensure_ascii=False)

    # 2. HTML Template Rico
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grafo Interativo do Recife</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #2563eb;
            --accent: #f97316;
            --bg: #f8fafc;
            --panel-bg: rgba(255, 255, 255, 0.95);
            --text: #1e293b;
        }}
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: 'Inter', sans-serif; background: var(--bg); }}
        #mynetwork {{ width: 100%; height: 100%; }}
        
        /* Painel Flutuante Moderno */
        #panel {{
            position: absolute; top: 20px; right: 20px; z-index: 100;
            background: var(--panel-bg);
            padding: 20px; border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
            width: 300px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.5);
            transition: transform 0.3s ease;
        }}
        
        h3 {{ margin-top: 0; color: var(--text); font-size: 18px; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }}
        
        .control-group {{ margin-bottom: 15px; }}
        label {{ display: block; font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; }}
        
        select {{
            width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1;
            background: white; font-family: inherit; color: var(--text); cursor: pointer;
            appearance: none; background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat; background-position: right 10px center; background-size: 16px;
        }}
        select:focus {{ outline: 2px solid var(--primary); border-color: transparent; }}
        
        /* Botões */
        .btn-row {{ display: flex; gap: 10px; }}
        button {{
            flex: 1; padding: 12px; border: none; border-radius: 8px; cursor: pointer;
            font-weight: 600; font-size: 13px; transition: all 0.2s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        button:active {{ transform: scale(0.96); }}
        
        #btn-rota {{ background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; }}
        #btn-rota:hover {{ box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3); }}
        
        #btn-reset {{ background: white; color: var(--text); border: 1px solid #cbd5e1; }}
        #btn-reset:hover {{ background: #f1f5f9; }}

        /* Estatísticas */
        #stats {{
            margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0;
            display: flex; justify-content: space-between; font-size: 12px; color: #64748b;
        }}
        .stat-item b {{ display: block; font-size: 16px; color: var(--text); }}

        /* Helper de Seleção */
        .selection-info {{ font-size: 12px; color: #64748b; margin-bottom: 15px; line-height: 1.4; background: #f1f5f9; padding: 10px; border-radius: 8px; }}
    </style>
</head>
<body>

<div id="panel">
    <h3>🗺️ Grafo Recife</h3>
    
    <div class="selection-info">
        <b>Modo de Camadas:</b> Selecione abaixo ou clique nos nós para isolar visualmente bairros e regiões.
    </div>

    <div class="control-group">
        <label for="searchNode">🔍 Buscar Bairro</label>
        <select id="searchNode" onchange="selectNode(this.value)">
            <option value="">Digite ou selecione...</option>
        </select>
    </div>

    <div class="control-group">
        <label for="filterMicro">🏙️ Filtrar por Microrregião</label>
        <select id="filterMicro" onchange="filterByMicro(this.value)">
            <option value="">Todas as Regiões</option>
        </select>
    </div>

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
    // --- DADOS ---
    const nodesData = {json_nodes};
    const edgesData = {json_edges};
    const routeNodes = {json_path};
    const microList = {json_micros};

    // DataSets Vis.js
    const nodes = new vis.DataSet(nodesData);
    const edges = new vis.DataSet(edgesData);

    // --- INICIALIZAÇÃO DA UI ---
    
    // 1. Popula Busca de Bairros
    const searchSelect = document.getElementById('searchNode');
    [...nodesData].sort((a, b) => a.label.localeCompare(b.label)).forEach(n => {{
        const opt = document.createElement('option');
        opt.value = n.id; opt.innerText = n.label;
        searchSelect.appendChild(opt);
    }});

    // 2. Popula Filtro de Microrregiões
    const filterSelect = document.getElementById('filterMicro');
    microList.forEach(m => {{
        const opt = document.createElement('option');
        opt.value = m; opt.innerText = m;
        filterSelect.appendChild(opt);
    }});

    // 3. Atualiza Estatísticas
    function updateStats(n, e) {{
        document.getElementById('countNodes').innerText = n;
        document.getElementById('countEdges').innerText = e;
    }}
    updateStats(nodes.length, edges.length);

    // --- CONFIGURAÇÃO DO GRAFO ---
    const container = document.getElementById('mynetwork');
    const data = {{ nodes: nodes, edges: edges }};
    const options = {{
        nodes: {{ shape: 'dot', borderWidth: 2, shadow: true, color: {{ highlight: {{ border: '#2563eb', background: '#ffffff' }} }} }},
        edges: {{ width: 2, smooth: {{ type: 'continuous' }}, color: {{ inherit: 'from' }} }},
        physics: {{
            forceAtlas2Based: {{ gravitationalConstant: -80, springLength: 120, springConstant: 0.08, damping: 0.4 }},
            maxVelocity: 50, solver: 'forceAtlas2Based', 
            stabilization: {{ enabled: true, iterations: 700 }}
        }},
        interaction: {{ 
            hover: true, tooltipDelay: 100, 
            multiselect: true, selectConnectedEdges: false 
        }}
    }};

    const network = new vis.Network(container, data, options);

    // --- LÓGICA DE FILTRO E CAMADAS ---
    let activeNodes = new Set(); // IDs dos nós visíveis/ativos

    // Evento: Clique no Grafo
    network.on("click", function (params) {{
        const clicked = params.nodes[0];
        if (clicked) {{
            // Toggle: Adiciona ou remove da camada ativa
            if (activeNodes.has(clicked)) activeNodes.delete(clicked);
            else activeNodes.add(clicked);
        }} else {{
            // Clique no vazio limpa tudo
            activeNodes.clear();
        }}
        updateVisuals();
    }});

    // Ação: Selecionar Bairro (Busca)
    function selectNode(id) {{
        if (!id) return;
        activeNodes.add(id);
        updateVisuals();
        network.fit({{ nodes: [id], animation: true }});
        searchSelect.value = ""; // Reseta dropdown
    }}

    // Ação: Filtrar Microrregião (Camada)
    function filterByMicro(micro) {{
        if (!micro) {{
            resetAll();
            return;
        }}
        
        activeNodes.clear();
        // Adiciona TODOS os nós daquela região à seleção
        nodesData.forEach(n => {{
            if (n.microrregiao === micro) activeNodes.add(n.id);
        }});
        
        updateVisuals();
        // Foca na camada inteira
        const nodesInLayer = Array.from(activeNodes);
        if (nodesInLayer.length > 0) network.fit({{ nodes: nodesInLayer, animation: true }});
    }}

    // Ação: Rota Fixa (Task 6)
    function showRoute() {{
        if (routeNodes.length === 0) return alert("Rota não calculada.");
        activeNodes.clear();
        routeNodes.forEach(id => activeNodes.add(id));
        updateVisuals();
        network.fit({{ nodes: routeNodes, animation: true }});
    }}

    // Ação: Resetar
    function resetAll() {{
        activeNodes.clear();
        filterSelect.value = "";
        updateVisuals();
        network.fit({{ animation: true }});
    }}

    // --- ENGINE VISUAL (O CÉREBRO) ---
    function updateVisuals() {{
        const allN = nodes.get();
        const allE = edges.get();
        
        const updatesN = [];
        const updatesE = [];
        
        let visibleNodesCount = 0;
        let visibleEdgesCount = 0;

        const isFilterActive = activeNodes.size > 0;

        if (!isFilterActive) {{
            // MODO PADRÃO: Tudo colorido
            allN.forEach(n => updatesN.push({{ id: n.id, color: null, opacity: 1, font: {{ color: '#343434' }} }}));
            allE.forEach(e => updatesE.push({{ id: e.id, color: null, width: 2, opacity: 0.6 }}));
            visibleNodesCount = allN.length;
            visibleEdgesCount = allE.length;
        }} else {{
            // MODO CAMADAS: Isola Ativos
            allN.forEach(n => {{
                if (activeNodes.has(n.id)) {{
                    updatesN.push({{ id: n.id, color: null, opacity: 1, font: {{ color: '#000', background: 'rgba(255,255,255,0.8)' }} }});
                    visibleNodesCount++;
                }} else {{
                    updatesN.push({{ id: n.id, color: 'rgba(200,200,200,0.2)', opacity: 0.2, font: {{ color: 'rgba(0,0,0,0)' }} }});
                }}
            }});

            allE.forEach(e => {{
                // Aresta só aparece se conectar dois nós ativos
                if (activeNodes.has(e.from) && activeNodes.has(e.to)) {{
                    updatesE.push({{ id: e.id, color: {{ color: '#f97316', opacity: 1 }}, width: 4 }});
                    visibleEdgesCount++;
                }} else {{
                    updatesE.push({{ id: e.id, color: 'rgba(200,200,200,0.05)', width: 1 }});
                }}
            }});
        }}

        nodes.update(updatesN);
        edges.update(updatesE);
        updateStats(visibleNodesCount, visibleEdgesCount);
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

# ==============================================================================
#  TASK 8: VISUALIZAÇÕES ANALÍTICAS (Matplotlib) - MANTIDA
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
        plt.title('Distribuição de Graus dos Bairros')
        plt.xlabel('Grau'); plt.ylabel('Qtd. Bairros')
        plt.grid(axis='y', alpha=0.5); plt.tight_layout()
        plt.savefig(OUT_DIR / "analise_1_histograma_graus.png"); plt.close()
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
                if conn:
                    plt.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color='#555', alpha=0.6, linewidth=2, zorder=1)
        
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
        plt.title('Densidade Média (Ego-Rede) por Microrregião')
        plt.xticks(rotation=45, ha='right'); plt.tight_layout()
        plt.savefig(OUT_DIR / "analise_3_densidade_micro.png"); plt.close()
    except Exception as e: print(f"  [ERRO] G3: {e}")