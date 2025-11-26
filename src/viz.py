import json
import math
import csv
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
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
#  TASK 7: ÁRVORE DE PERCURSO (Hierarchical Layout)
# ==============================================================================

def gerar_arvore_percurso(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/arvore_percurso.html' usando PyVis com Layout Hierárquico.
    """
    if Network is None:
        print("  [viz.py] PyVis não instalado. Pulando Task 7.")
        return

    if not resultado_percurso or not resultado_percurso.get("percurso"):
        # print("  [viz.py] Sem percurso para gerar árvore.") # Silenciado para não poluir Parte 2
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
        
        color = "#97C2FC" # Azul padrão
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

    # Adiciona Arestas
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        
        edge_weight = 1.0
        logradouro = "?"
        
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
            label=label_edge, 
            title=f"Via: {logradouro}<br>Custo: {edge_weight}",
            color="#555555",
            width=3,
            arrowStrikethrough=False
        )

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
#  TASK 9 + BÔNUS: GERAÇÃO DO HTML INTERATIVO (MULTI-DATASET)
# ==============================================================================

def _carregar_dados_routes(limit: int = 1000) -> tuple[list, list]:
    """
    Lê o CSV de rotas e retorna nós e arestas formatados para o Vis.js.
    """
    vis_nodes = {}
    vis_edges = []
    routes_file = DATA_DIR / "routes.csv"

    if not routes_file.exists():
        # print(f"  [viz.py] Aviso: {routes_file} não encontrado. Modo Rotas ficará vazio.")
        return [], []

    print(f"  [viz.py] Carregando dataset de rotas para HTML (limite: {limit} arestas)...")
    
    try:
        with open(routes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if count >= limit: break
                
                u = (row.get('source airport') or "").strip()
                v = (row.get('destination apirport') or row.get('destination airport') or "").strip()
                
                if not u or not v: continue

                if u not in vis_nodes:
                    vis_nodes[u] = {"id": u, "label": u, "group": "Aeroporto", "value": 10, "title": f"Aeroporto: {u}"}
                if v not in vis_nodes:
                    vis_nodes[v] = {"id": v, "label": v, "group": "Aeroporto", "value": 10, "title": f"Aeroporto: {v}"}

                airline = row.get('airline', '?')
                weight = row.get('weight', '?')
                
                vis_edges.append({
                    "from": u, "to": v,
                    "title": f"Airline: {airline}\nPeso: {weight}",
                    "color": {"color": "#848484", "opacity": 0.3},
                    "arrows": "to"
                })
                count += 1
                
        return list(vis_nodes.values()), vis_edges
    except Exception as e:
        print(f"  [viz.py] Erro ao ler rotas: {e}")
        return [], []


def gerar_html_customizado(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/grafo_interativo.html' manual com features avançadas de UX.
    """
    print("  [viz.py] Gerando HTML Interativo Customizado (Task 9)...")
    arquivo_saida = OUT_DIR / "grafo_interativo.html"

    # --- 1. Preparar Dados Recife ---
    recife_nodes = []
    recife_edges = []
    path_nodes = list(resultado_percurso.get("percurso", [])) if resultado_percurso else []
    graus = [g.get_grau(n) for n in g.nodes_data.keys()]
    max_grau = max(graus) if graus else 1
    microrregioes = set()

    for node in g.nodes_data.keys():
        grau = g.get_grau(node)
        micro = g.get_microrregiao(node) or "Desconhecida"
        microrregioes.add(micro)
        size = 15 + (grau / max_grau) * 30
        
        recife_nodes.append({
            "id": node,
            "label": node,
            "title": f"Bairro: {node}\nMicrorregião: {micro}\nGrau: {grau}",
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
            recife_edges.append({
                "from": u, "to": v,
                "title": f"Logradouro: {log}\nPeso: {w}",
                "color": {"color": "#848484", "opacity": 0.4}
            })
            added_edges.add((u, v))

    # --- 2. Preparar Dados Rotas ---
    routes_nodes, routes_edges = _carregar_dados_routes(limit=1000)

    # --- 3. Serializar para JS ---
    data_recife = json.dumps({"nodes": recife_nodes, "edges": recife_edges}, ensure_ascii=False)
    data_routes = json.dumps({"nodes": routes_nodes, "edges": routes_edges}, ensure_ascii=False)
    
    json_path = json.dumps(path_nodes, ensure_ascii=False)
    json_micros = json.dumps(sorted(list(microrregioes)), ensure_ascii=False)

    # --- 4. Gerar HTML ---
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Grafo Interativo - Projeto Grafos</title>
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
            max-height: 90vh; overflow-y: auto;
        }}
        h3 {{ margin-top: 0; color: var(--text); font-size: 18px; font-weight: 800; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
        label {{ display: block; font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 5px; text-transform: uppercase; margin-top: 10px; }}
        select {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 10px; background: white; }}
        .btn-row {{ display: flex; gap: 10px; margin-top: 15px; }}
        button {{ flex: 1; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.2s; }}
        #btn-rota {{ background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; }}
        #btn-physics {{ background: #e2e8f0; color: #1e293b; border: 1px solid #cbd5e1; }}
        #btn-neighbors {{ background: white; color: #1e293b; border: 1px solid #cbd5e1; }}
        #btn-reset {{ background: white; color: var(--text); border: 1px solid #cbd5e1; }}
        #btn-rota:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        #stats {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; font-size: 12px; color: #64748b; }}
        .stat-item b {{ display: block; font-size: 16px; color: var(--text); }}
    </style>
</head>
<body>
<div id="panel">
    <h3>Painel de Controle</h3>
    
    <label>Escolher Dataset</label>
    <select id="datasetSelect" onchange="switchDataset(this.value)">
        <option value="recife">Bairros do Recife (Parte 1)</option>
        <option value="routes">Malha Aérea (Parte 2)</option>
    </select>

    <label>Buscar Nó</label>
    <select id="searchNode" onchange="selectNode(this.value)"><option value="">Selecione...</option></select>
    
    <div id="microFilterDiv">
        <label>Filtrar Microrregião</label>
        <select id="filterMicro" onchange="filterByMicro(this.value)"><option value="">Todas</option></select>
    </div>

    <div class="btn-row">
        <button id="btn-rota" onclick="showRoute()">Rota Task 6</button>
        <button id="btn-physics" onclick="togglePhysics()">⏸ Pausar</button>
    </div>
    
    <div class="btn-row" style="margin-top:10px;">
        <button id="btn-neighbors" onclick="toggleNeighbors()">🕸 Vizinhança: OFF</button>
        <button id="btn-reset" onclick="resetAll()">Resetar Visual</button>
    </div>

    <div id="stats">
        <div class="stat-item"><b><span id="countNodes">0</span></b>Nós Visíveis</div>
        <div class="stat-item"><b><span id="countEdges">0</span></b>Arestas Visíveis</div>
    </div>
</div>

<div id="mynetwork"></div>

<script type="text/javascript">
    const DB = {{
        recife: {data_recife},
        routes: {data_routes}
    }};
    const routeNodesRecife = {json_path}; 
    const microListRecife = {json_micros};

    // Estados
    let currentKey = 'recife';
    let network = null;
    let nodesDataSet = new vis.DataSet([]);
    let edgesDataSet = new vis.DataSet([]);
    let activeNodes = new Set();
    let showNeighbors = false; // Novo estado para controlar vizinhança

    // Init
    const container = document.getElementById('mynetwork');
    const searchSelect = document.getElementById('searchNode');
    const filterSelect = document.getElementById('filterMicro');
    const microFilterDiv = document.getElementById('microFilterDiv');
    const btnRota = document.getElementById('btn-rota');

    const options = {{
        nodes: {{ shape: 'dot', borderWidth: 2, shadow: true }},
        edges: {{ width: 2, smooth: {{ type: 'continuous' }}, color: {{ inherit: 'from' }} }},
        physics: {{
            forceAtlas2Based: {{
                gravitationalConstant: -100,
                springLength: 150,
                springConstant: 0.08,
                damping: 0.8,
                avoidOverlap: 1
            }},
            solver: 'forceAtlas2Based',
            stabilization: {{ enabled: true, iterations: 1000 }}
        }},
        interaction: {{ hover: true, multiselect: true, selectConnectedEdges: false }}
    }};

    function initNetwork() {{
        const data = {{ nodes: nodesDataSet, edges: edgesDataSet }};
        network = new vis.Network(container, data, options);

        network.on("click", function (params) {{
            const clicked = params.nodes[0];
            if (clicked) {{
                if (activeNodes.has(clicked)) activeNodes.delete(clicked);
                else activeNodes.add(clicked);
            }} else {{
                activeNodes.clear();
            }}
            updateVisuals();
        }});
    }}
    
    // --- Lógica: Botões ---

    function togglePhysics() {{
        const btn = document.getElementById('btn-physics');
        const isEnabled = network.physics.physicsEnabled;
        if (isEnabled) {{
            network.setOptions({{ physics: {{ enabled: false }} }});
            btn.innerText = "▶ Ativar";
            btn.style.backgroundColor = "#94a3b8"; 
        }} else {{
            network.setOptions({{ physics: {{ enabled: true }} }});
            btn.innerText = "⏸ Pausar";
            btn.style.backgroundColor = "#e2e8f0";
        }}
    }}

    function toggleNeighbors() {{
        const btn = document.getElementById('btn-neighbors');
        showNeighbors = !showNeighbors;
        if (showNeighbors) {{
            btn.innerText = "🕸 Vizinhança: ON";
            btn.style.backgroundColor = "#e2e8f0"; // Estilo 'Ativo'
        }} else {{
            btn.innerText = "🕸 Vizinhança: OFF";
            btn.style.backgroundColor = "white";
        }}
        updateVisuals(); // Recalcula visualização com a nova regra
    }}

    // --- Lógica: Dados ---

    function loadDataset(key) {{
        currentKey = key;
        activeNodes.clear();
        
        const data = DB[key];
        nodesDataSet.clear();
        edgesDataSet.clear();
        nodesDataSet.add(data.nodes);
        edgesDataSet.add(data.edges);

        searchSelect.innerHTML = '<option value="">Selecione...</option>';
        [...data.nodes].sort((a, b) => a.label.localeCompare(b.label)).forEach(n => {{
            const opt = document.createElement('option');
            opt.value = n.id; opt.innerText = n.label; searchSelect.appendChild(opt);
        }});

        if (key === 'recife') {{
            microFilterDiv.style.display = 'block';
            filterSelect.innerHTML = '<option value="">Todas</option>';
            microListRecife.forEach(m => {{
                const opt = document.createElement('option'); opt.value = m; opt.innerText = m; filterSelect.appendChild(opt);
            }});
            btnRota.disabled = false;
            btnRota.innerText = "Rota Task 6";
        }} else {{
            microFilterDiv.style.display = 'none';
            btnRota.disabled = true; 
            btnRota.innerText = "N/A (Só Recife)";
        }}
        
        // Resetar configurações ao trocar dataset
        network.setOptions({{ physics: {{ enabled: true }} }});
        const btnPhys = document.getElementById('btn-physics');
        if(btnPhys) {{ btnPhys.innerText = "⏸ Pausar"; btnPhys.style.backgroundColor = "#e2e8f0"; }}
        
        // Reset vizinhança
        showNeighbors = false;
        const btnNeigh = document.getElementById('btn-neighbors');
        if(btnNeigh) {{ btnNeigh.innerText = "🕸 Vizinhança: OFF"; btnNeigh.style.backgroundColor = "white"; }}

        updateStats(data.nodes.length, data.edges.length);
        network.fit();
    }}

    function switchDataset(key) {{ loadDataset(key); }}
    
    function updateStats(n, e) {{ 
        document.getElementById('countNodes').innerText = n; 
        document.getElementById('countEdges').innerText = e; 
    }}

    // --- Lógica: Visual e Filtros ---

    function selectNode(id) {{
        if(!id) return;
        activeNodes.add(id);
        updateVisuals();
        network.fit({{ nodes: [id], animation: true }});
        searchSelect.value = "";
    }}

    function filterByMicro(micro) {{
        if (currentKey !== 'recife') return;
        if (!micro) return resetAll();
        activeNodes.clear();
        nodesDataSet.forEach(n => {{ if(n.microrregiao === micro) activeNodes.add(n.id); }});
        updateVisuals();
        const arr = Array.from(activeNodes);
        if(arr.length) network.fit({{ nodes: arr, animation: true }});
    }}

    function showRoute() {{
        if (currentKey !== 'recife') return;
        if (!routeNodesRecife.length) return alert("Rota vazia");
        activeNodes.clear();
        routeNodesRecife.forEach(id => activeNodes.add(id));
        updateVisuals();
        network.fit({{ nodes: routeNodesRecife, animation: true }});
    }}

    function resetAll() {{
        activeNodes.clear();
        if(currentKey === 'recife') filterSelect.value = "";
        updateVisuals();
        network.fit({{ animation: true }});
    }}

    function updateVisuals() {{
        const allN = nodesDataSet.get();
        const allE = edgesDataSet.get();
        const updatesN = [];
        const updatesE = [];
        const isActive = activeNodes.size > 0;
        
        // Sets para determinar o que fica "Brilhante" (highlighted)
        let highlightedNodes = new Set();
        let highlightedEdges = new Set();

        if (!isActive) {{
            // Se nada selecionado, tudo brilha
            allN.forEach(n => highlightedNodes.add(n.id));
            allE.forEach(e => highlightedEdges.add(e.id));
        }} else {{
            // Lógica principal de Vizinhança
            if (!showNeighbors) {{
                // MODO CLÁSSICO: Apenas nós selecionados + arestas entre eles
                activeNodes.forEach(id => highlightedNodes.add(id));
                allE.forEach(e => {{
                    if (activeNodes.has(e.from) && activeNodes.has(e.to)) highlightedEdges.add(e.id);
                }});
            }} else {{
                // MODO VIZINHANÇA: Nós selecionados + Arestas conectadas + Vizinhos
                activeNodes.forEach(id => highlightedNodes.add(id));
                allE.forEach(e => {{
                    // Se a aresta toca em um nó ativo (entrada ou saída)
                    if (activeNodes.has(e.from) || activeNodes.has(e.to)) {{
                        highlightedEdges.add(e.id);
                        highlightedNodes.add(e.from); // Ilumina origem
                        highlightedNodes.add(e.to);   // Ilumina destino
                    }}
                }});
            }}
        }}

        // Aplica estilos baseados nos Sets calculados acima
        allN.forEach(n => {{
            if (highlightedNodes.has(n.id)) {{
                updatesN.push({{ id: n.id, color: null, opacity: 1, font: {{ color: '#000', background: 'rgba(255,255,255,0.8)' }} }});
            }} else {{
                updatesN.push({{ id: n.id, color: 'rgba(200,200,200,0.2)', opacity: 0.2, font: {{ color: 'rgba(0,0,0,0)' }} }});
            }}
        }});
        
        allE.forEach(e => {{
            if (highlightedEdges.has(e.id)) {{
                updatesE.push({{ id: e.id, color: {{ color: '#f97316', opacity: 1 }}, width: 4 }});
            }} else {{
                updatesE.push({{ id: e.id, color: 'rgba(200,200,200,0.05)', width: 1 }});
            }}
        }});
        
        nodesDataSet.update(updatesN);
        edgesDataSet.update(updatesE);
        
        // Atualiza Stats com o que está REALMENTE visível (highlighted)
        updateStats(highlightedNodes.size, highlightedEdges.size);
    }}

    initNetwork();
    loadDataset('recife');

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

def gerar_visualizacoes_analiticas(g: Graph, file_prefix: str = ""):
    """
    Gera gráficos estáticos (.png) adaptáveis (Recife ou Rotas).
    - file_prefix: prefixo para o arquivo (ex: 'rota_') para não sobrescrever.
    """
    if plt is None: return
    print(f"  [viz.py] Gerando visualizações analíticas (prefixo='{file_prefix}')...")
    try: plt.style.use('ggplot')
    except: pass
    bairros = list(g.nodes_data.keys())
    graus = [g.get_grau(n) for n in bairros]
    if not graus:
        print("  [viz.py] Grafo vazio, pulando gráficos.")
        return

    # 1. Histograma
    try:
        plt.figure(figsize=(8, 5))
        plt.hist(graus, bins=range(min(graus), max(graus) + 2), color='#4A90E2', edgecolor='black', alpha=0.8, align='left')
        plt.title('Distribuição de Graus')
        plt.ylabel('Qtd. Nós')
        plt.xlabel('Grau')
        plt.tight_layout()
        nome_arq = OUT_DIR / f"{file_prefix}analise_1_histograma_graus.png"
        plt.savefig(nome_arq)
        plt.close()
        print(f"  -> {nome_arq}")
    except Exception as e: print(f"  [ERRO] G1: {e}")

    # 2. Top 10 Circular
    try:
        # Identificar Top 10 bairros
        ranking = sorted([(n, g.get_grau(n)) for n in g.nodes_data], key=lambda x: x[1], reverse=True)[:10]
        top_nodes = [r[0] for r in ranking]
        
        if top_nodes:
            plt.figure(figsize=(8, 8))
            
            # Layout Circular Manual (sem networkx)
            pos = {}
            n_top = len(top_nodes)
            radius = 1.0
            
            for i, node in enumerate(top_nodes):
                angle = 2 * math.pi * i / n_top
                angle += math.pi / 2 
                pos[node] = (radius * math.cos(angle), radius * math.sin(angle))
                
            # Desenhar Arestas (apenas entre os Top 10)
            
            # CORREÇÃO ROBUSTA: Usa getattr para evitar AttributeError se 'directed' falhar
            is_directed = getattr(g, "directed", False)
            
            for i, u in enumerate(top_nodes):
                for j, v in enumerate(top_nodes):
                    if i >= j: continue 
                    
                    # Verifica adjacência no grafo 'g'
                    conectados = False
                    # Checa u->v
                    for info in g.adj.get(u, []):
                        if info["node"] == v:
                            conectados = True; break
                    
                    # Se não achou e for dirigido, checa v->u? 
                    # Se for dirigido (Rotas), queremos ver conexão em qualquer sentido para o desenho estático
                    if not conectados and is_directed:
                         for info in g.adj.get(v, []):
                            if info["node"] == u:
                                conectados = True; break

                    if conectados:
                        x_vals = [pos[u][0], pos[v][0]]
                        y_vals = [pos[u][1], pos[v][1]]
                        plt.plot(x_vals, y_vals, color='gray', alpha=0.5, linewidth=1.5, zorder=1)

            # Desenhar Nós
            x_nodes = [pos[n][0] for n in top_nodes]
            y_nodes = [pos[n][1] for n in top_nodes]
            sizes = [g.get_grau(n) * 50 for n in top_nodes] # Escala o tamanho pelo grau
            
            plt.scatter(x_nodes, y_nodes, s=sizes, c='dodgerblue', edgecolors='white', linewidths=1.5, zorder=2)
            
            # Rótulos
            for node, (x, y) in pos.items():
                # Afasta o texto do centro
                dist = 1.15
                plt.text(x * dist, y * dist, node, fontsize=10, ha='center', va='center', fontweight='bold', color='#333')

            plt.title(f'Top {n_top} Nós Mais Conectados')
            plt.axis('off') 
            plt.xlim(-1.5, 1.5)
            plt.ylim(-1.5, 1.5)
            
            nome_arq = OUT_DIR / f"{file_prefix}analise_2_subgrafo_top10.png"
            plt.tight_layout()
            plt.savefig(nome_arq)
            plt.close()
            print(f"  -> {nome_arq}")
    except Exception as e:
        print(f"  [ERRO] Gráfico 2: {e}")

    # 3. Densidade Micro (Só gera se houver microrregiões reais)
    try:
        micro_dens = {}
        # Verifica se há dados válidos de microrregião
        valid_micros = set()
        
        for n in bairros:
            m = g.get_microrregiao(n)
            if m and m not in ["DESCONHECIDA", "N/A", None]:
                valid_micros.add(m)
                try: d = g.ego_metrics_for(n).get("densidade_ego", 0)
                except: d = 0
                micro_dens.setdefault(m, []).append(d)
        
        # Só plota se tiver pelo menos 2 grupos para comparar
        if len(valid_micros) < 2:
            pass # Silenciosamente pula para rotas
        else:
            ms = sorted(micro_dens.keys())
            avgs = [sum(micro_dens[m])/len(micro_dens[m]) for m in ms]
            plt.figure(figsize=(10, 6))
            plt.bar(ms, avgs, color='#48C9B0', edgecolor='#145A32')
            plt.title('Densidade Média por Microrregião'); plt.xticks(rotation=45, ha='right')
            nome_arq = OUT_DIR / f"{file_prefix}analise_3_densidade_micro.png"
            plt.tight_layout(); plt.savefig(nome_arq); plt.close()
            print(f"  -> {nome_arq}")
            
    except Exception as e: print(f"  [ERRO] G3: {e}")