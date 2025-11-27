# Projeto Final - Teoria dos Grafos

Este repositório contém o desenvolvimento do **Grafo dos bairros de Recife**, cujo objetivo é trabalhar conceitos de grafos aplicados ao **mapa de bairros do Recife** e posteriormente realizar a **comparação de algoritmos clássicos de grafos** em dataset maior sobre a malha aérea global.

---

## Objetivos do Projeto
1. **Parte 1 - Grafo dos Bairros do Recife**
   - Construção de um grafo rotulado com os bairros como nós e adjacências reais como arestas.
   - Cálculo de métricas globais, por microrregião e ego-networks.
   - Implementação dos algoritmos: BFS, DFS, Dijkstra e Bellman-Ford.
   - Geração de visualizações analíticas e grafo interativo.

2. **Parte 2 - Dataset Malha Aérea**
   - Escolhemos um grafo com ~67k arestas sobre o fluxo de viagens aéreas pelo mundo.
   - Comparação entre BFS, DFS, Dijkstra e Bellman-Ford em termos de corretude e desempenho.
   - Discussão crítica sobre resultados e limitações.

---

## Estrutura do Repositório

```
Projeto-Grafos/
├── data/                      # Arquivos de entrada (CSV)
│
├── out/                       # Resultados gerados pelo código
│
├── src/                       # Código-fonte principal
│   │
│   ├── graphs/                # Implementação dos algoritmos de grafos
│   │  ├── algorithms.py       # BFS, DFS, Dijkstra, Bellman-Ford
│   │  ├── graph.py            # Estrutura de grafo e operações básicas
│   │  └── io.py               # Leitura/escrita de dados (CSV)
│   │
│   ├── cli.py                 # Interface de linha de comando (CLI)
│   ├── solve.py               # Rotinas auxiliares de resolução
│   └── viz.py                 # Visualização de grafos
│
├── tests/                     # Testes automatizados
├── README.md
└── requirements.txt           # Bibliotecas necessárias
```

### Tecnologias
- Python 3.11+
- `pandas`, `matplotlib`, `pyvis`, `pytest`
- `argparse`, `heapq`, `typing`

---

## Como executar o projeto

### 1. Clonar o repositório.
```
git clone https://github.com/lovepxdro/Projeto-Grafos.git
```

Após clonar, entre na pasta do projeto. Todos os comandos abaixo devem ser executados na raiz do repositório.

### 2. Instale as dependências.
```
pip install -r requirements.txt
```

### 3. Executar o projeto.

O projeto pode ser executado de duas formas: Execução Completa ou Execução Dinâmica.
- Observação: Use `python` para Windows ou `python3` para Linux/MacOs.

#### 3.1. Execução completa: Um **script orquestrador** (`solve.py`), que roda todo o pipeline de uma vez.
```bash
python src/solve.py
```

#### 3.2. Execução dinâmica: Uma **ferramenta de linha de comando (CLI)** (`src.cli`), para testar algoritmos e cenários específicos.

**Sintaxe Básica:**
`python -m src.cli [DATASET] [COMANDO] [ARGUMENTOS]`

> **Nota:** Nos exemplos abaixo, utilizamos o bairro **'Boa Vista'** e o aeroporto **'MEX'**, mas eles podem ser trocados por qualquer nó existente nos arquivos CSV.

#### BFS (Busca em Largura)
* **Parte 1 (Recife):**
    ```bash
    python -m src.cli --adjacencias_bairros data/adjacencias_bairros.csv bfs "Boa Vista"
    ```
* **Parte 2 (Malha Aérea):**
    ```bash
    python -m src.cli --routes data/routes.csv bfs MEX
    ```

#### DFS (Busca em Profundidade)
* **Parte 1 (Recife):**
    ```bash
    python -m src.cli --adjacencias_bairros data/adjacencias_bairros.csv dfs "Boa Vista"
    ```
* **Parte 2 (Malha Aérea):**
    ```bash
    python -m src.cli --routes data/routes.csv dfs MEX
    ```

#### Dijkstra (Caminho Mínimo)
* **Parte 1 (Recife) - Boa Vista → Graças:**
    ```bash
    python -m src.cli --adjacencias_bairros data/adjacencias_bairros.csv dijkstra "Boa Vista" "Graças"
    ```
* **Parte 2 (Malha Aérea) - MEX → JFK:**
    ```bash
    python -m src.cli --routes data/routes.csv dijkstra MEX JFK
    ```
* **Execução em Lote (5 pares):**
    Para atender ao requisito de 5 pares de partida na Parte 2, utilizamos um arquivo CSV auxiliar:
    ```bash
    python -m src.cli --routes data/routes.csv dijkstra-pairs data/routes_dijkstra_pairs.csv
    ```

#### Bellman-Ford (Ciclos Negativos - Parte 2)
Para validação deste algoritmo, criamos micro-datasets específicos para teste de controle:
* **Sem ciclo negativo** (Esperado: `has_negative_cycle = false`):
    ```bash
    python -m src.cli --routes data/routes_negative_no_cycle.csv --directed bellman-ford AER
    ```
* **Com ciclo negativo** (Esperado: `has_negative_cycle = true`):
    ```bash
    python -m src.cli --routes data/routes_negative_cycle.csv --directed bellman-ford AER
    ```

#### Relatórios e Visualização (Parte 2)
* **Relatório de Performance:**
    Gera estatísticas de tempo de execução para nós específicos (ex: MEX, LAX, JFK) salvando em JSON customizado:
    ```bash
    python -m src.cli --routes data/routes.csv --json out/parte2_report_out.json report MEX LAX JFK
    ```
* **Visualizações Estáticas:**
    Gera gráficos analíticos (Top 10 Hubs) na pasta `out/`:
    ```bash
    python -m src.cli --routes data/routes.csv --directed viz
    ```

---

## Membros

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/lovepxdro">
        <img src="https://avatars.githubusercontent.com/lovepxdro" width="100px;" alt="Foto de Pedro Antônio"/>
        <br />
        <sub><b>Pedro Antônio</b></sub>
      </a>
      <br />
      <sub><b>✉️ pafm@cesar.school</b></sub>
    </td>
    <td align="center">
      <a href="https://github.com/emanusousa">
        <img src="https://avatars.githubusercontent.com/emanusousa" width="100px;" alt="Foto de Emanuel"/>
        <br />
        <sub><b>Emanuel Sousa</b></sub>
      </a>
      <br />
      <sub><b>✉️ @cesar.school</b></sub>
    </td>
    <td align="center">
      <a href="https://github.com/BrunoBMayer">
        <img src="https://avatars.githubusercontent.com/BrunoBMayer" width="100px;" alt="Foto de Bruno"/>
        <br />
        <sub><b>Bruno Mayer</b></sub>
      </a>
      <br />
      <sub><b>✉️ bbm@cesar.school</b></sub>
    </td>
     <td align="center">
        <a href="https://github.com/CaioAugustoMachadoDeMelo">
           <img src="https://avatars.githubusercontent.com/CaioAugustoMachadoDeMelo" width="100px;" alt="Foto de Caio"/>
           <br />
           <sub><b>Caio Melo</b></sub>
        </a>
        <br />
        <sub><b>✉️ @cesar.school</b></sub>
     </td>
  </tr>
</table>

ᓚᘏᗢ
