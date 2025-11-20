import json
import math  # Necessário para o layout circular
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
#  TASK 9 + BÔNUS: GERAÇÃO DO HTML INTERATIVO
# ==============================================================================

def gerar_html_customizado(g: Graph, resultado_percurso: dict | None):
    """
    Gera 'out/grafo_interativo.html' construindo o HTML manualmente.
    Responsável pela Task 9 e Bônus de UX (Isolamento visual).
    """
    print("  [viz.py] Gerando HTML Interativo Customizado...")
    arquivo_saida = OUT_DIR / "grafo_interativo.html"

    # 1. Prepara os dados (Nodes e Edges) para JSON
    vis_nodes = []
    vis_edges = []
    
    path_nodes = list(resultado_percurso.get("percurso", [])) if resultado_percurso else []
    
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
            if (u, v) in added_edges or (v, u) in added_edges: continue
            
            w = info.get("weight", 1.0)
            log = info.get("data", {}).get("logradouro", "")
            
            vis_edges.append({
                "from": u,
                "to": v,
                "title": f"Via: {log}<br>Peso: {w}",
                "color": {"color": "#848484", "opacity": 0.4}
            })
            added_edges.add((u, v))

    json_nodes = json.dumps(vis_nodes, ensure_ascii=False)
    json_edges = json.dumps(vis_edges, ensure_ascii=False)
    json_path = json.dumps(path_nodes, ensure_ascii=False)

    # 2. Template HTML
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
        #panel {{
            position: absolute; top: 20px; right: 20px; z-index: 10;
            background: rgba(255, 255, 255, 0.95);
            padding: 20px; border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15); width: 280px;
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
    const nodesArray = {json_nodes};
    const edgesArray = {json_edges};
    const routeNodes = {json_path};
    const nodes = new vis.DataSet(nodesArray);
    const edges = new vis.DataSet(edgesArray);
    const container = document.getElementById('mynetwork');
    const data = {{ nodes: nodes, edges: edges }};
    const options = {{
        nodes: {{ shape: 'dot', borderWidth: 2, shadow: true }},
        edges: {{ width: 2, smooth: {{ type: 'continuous' }} }},
        physics: {{
            forceAtlas2Based: {{ gravitationalConstant: -60, springLength: 120, springConstant: 0.08 }},
            solver: 'forceAtlas2Based', stabilization: {{ enabled: true, iterations: 600 }}
        }},
        interaction: {{ hover: true, tooltipDelay: 200, multiselect: true, selectConnectedEdges: false }}
    }};
    const network = new vis.Network(container, data, options);
    const select = document.getElementById('searchNode');
    [...nodesArray].sort((a, b) => a.label.localeCompare(b.label)).forEach(n => {{
        const opt = document.createElement('option'); opt.value = n.id; opt.innerText = n.label; select.appendChild(opt);
    }});
    let activeNodes = new Set();
    network.on("click", function (params) {{
        const clickedNode = params.nodes[0];
        if (clickedNode) {{
            if (activeNodes.has(clickedNode)) activeNodes.delete(clickedNode);
            else activeNodes.add(clickedNode);
        }} else {{ activeNodes.clear(); }}
        updateVisuals();
    }});
    function selectFromDropdown(nodeId) {{
        if (!nodeId) return;
        activeNodes.add(nodeId); updateVisuals();
        network.fit({{ nodes: [nodeId], animation: true }});
        document.getElementById('searchNode').value = "";
    }}
    function showRoute() {{
        if (routeNodes.length === 0) return alert("Rota não disponível.");
        activeNodes.clear(); routeNodes.forEach(id => activeNodes.add(id));
        updateVisuals(); network.fit({{ nodes: routeNodes, animation: true }});
    }}
    function resetAll() {{ activeNodes.clear(); updateVisuals(); network.fit({{ animation: true }}); }}
    function updateVisuals() {{
        const allN = nodes.get(); const allE = edges.get();
        const updatesN = []; const updatesE = [];
        if (activeNodes.size === 0) {{
            allN.forEach(n => updatesN.push({{ id: n.id, color: null, opacity: 1.0, font: {{ color: '#343434' }} }}));
            allE.forEach(e => updatesE.push({{ id: e.id, color: {{ color: '#848484', opacity: 0.4 }}, width: 2 }}));
        }} else {{
            allN.forEach(n => {{
                if (activeNodes.has(n.id)) updatesN.push({{ id: n.id, color: null, opacity: 1.0, font: {{ color: '#000000', background: 'rgba(255,255,255,0.7)' }} }});
                else updatesN.push({{ id: n.id, color: 'rgba(200, 200, 200, 0.2)', opacity: 0.2, font: {{ color: 'rgba(0,0,0,0)' }} }});
            }});
            allE.forEach(e => {{
                if (activeNodes.has(e.from) && activeNodes.has(e.to)) updatesE.push({{ id: e.id, color: {{ color: '#FF5733', opacity: 1.0 }}, width: 4 }});
                else updatesE.push({{ id: e.id, color: 'rgba(200, 200, 200, 0.05)', width: 1 }});
            }});
        }}
        nodes.update(updatesN); edges.update(updatesE);
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
#  TASK 8: VISUALIZAÇÕES ANALÍTICAS (Matplotlib)
# ==============================================================================

def gerar_visualizacoes_analiticas(g: Graph):
    """
    Gera gráficos estáticos (.png).
    1. Histograma de Distribuição de Graus.
    2. Subgrafo Top 10 (Layout Circular Manual).
    3. Densidade Média de Ego-Rede por Microrregião.
    """
    if plt is None:
        return

    print("  [viz.py] Gerando visualizações analíticas (Task 8)...")
    
    # Estilo básico
    try:
        plt.style.use('ggplot')
    except: pass

    bairros = list(g.nodes_data.keys())
    graus = [g.get_grau(n) for n in bairros]

    # --- GRÁFICO 1: Histograma de Graus ---
    try:
        plt.figure(figsize=(8, 5))
        plt.hist(graus, bins=range(min(graus), max(graus) + 2), color='skyblue', edgecolor='black', align='left')
        plt.title('Distribuição de Graus')
        plt.xlabel('Grau')
        plt.ylabel('Frequência')
        plt.grid(axis='y', alpha=0.75)
        plt.tight_layout()
        plt.savefig(OUT_DIR / "analise_1_histograma_graus.png")
        plt.close()
        print(f"  -> {OUT_DIR / 'analise_1_histograma_graus.png'}")
    except Exception as e:
        print(f"  [ERRO] Gráfico 1: {e}")

    # --- GRÁFICO 2: Subgrafo Top 10 (Layout Circular) ---
    try:
        # Identificar Top 10 bairros
        ranking = sorted([(n, g.get_grau(n)) for n in g.nodes_data], key=lambda x: x[1], reverse=True)[:10]
        top_nodes = [r[0] for r in ranking]
        
        plt.figure(figsize=(8, 8))
        
        # Layout Circular Manual (sem networkx)
        pos = {}
        n_top = len(top_nodes)
        radius = 1.0
        
        for i, node in enumerate(top_nodes):
            angle = 2 * math.pi * i / n_top
            # Gira 90 graus para o primeiro ficar no topo
            angle += math.pi / 2 
            pos[node] = (radius * math.cos(angle), radius * math.sin(angle))
            
        # Desenhar Arestas (apenas entre os Top 10)
        for i, u in enumerate(top_nodes):
            for j, v in enumerate(top_nodes):
                if i >= j: continue 
                
                # Verifica adjacência no grafo 'g'
                conectados = False
                for info in g.adj.get(u, []):
                    if info["node"] == v:
                        conectados = True
                        break
                
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

        plt.title(f'Subgrafo dos {n_top} Bairros Mais Conectados')
        plt.axis('off') 
        plt.xlim(-1.5, 1.5)
        plt.ylim(-1.5, 1.5)
        
        plt.tight_layout()
        plt.savefig(OUT_DIR / "analise_2_subgrafo_top10.png")
        plt.close()
        print(f"  -> {OUT_DIR / 'analise_2_subgrafo_top10.png'}")
    except Exception as e:
        print(f"  [ERRO] Gráfico 2: {e}")

    # --- GRÁFICO 3: Densidade Média por Microrregião ---
    try:
        micro_densidades = {}
        for node in bairros:
            micro = g.get_microrregiao(node) or "Outros"
            try:
                ego = g.ego_metrics_for(node)
                dens = ego.get("densidade_ego", 0)
            except: dens = 0
            micro_densidades.setdefault(micro, []).append(dens)
        
        micros_sorted = sorted(micro_densidades.keys())
        medias = []
        for m in micros_sorted:
            vals = micro_densidades[m]
            medias.append(sum(vals)/len(vals) if vals else 0)

        plt.figure(figsize=(10, 6))
        plt.bar(micros_sorted, medias, color='mediumseagreen', edgecolor='darkgreen')
        plt.title('Densidade Média das Ego-Redes por Microrregião')
        plt.xlabel('Microrregião')
        plt.ylabel('Densidade Média')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(OUT_DIR / "analise_3_densidade_micro.png")
        plt.close()
        print(f"  -> {OUT_DIR / 'analise_3_densidade_micro.png'}")
    except Exception as e:
        print(f"  [ERRO] Gráfico 3: {e}")