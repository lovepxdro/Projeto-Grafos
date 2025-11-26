# Projeto Final - Teoria dos Grafos 📊

Este repositório contém o desenvolvimento do **Grafo dos bairros de Recife**, cujo objetivo é trabalhar conceitos de grafos aplicados ao **mapa de bairros do Recife** e posteriormente realizar a **comparação de algoritmos clássicos de grafos** em dataset maior sobre a malha aérea global.

---

## 🎯 Objetivos do Projeto
1. **Parte 1 - Grafo dos Bairros do Recife**
   - Construção de um grafo rotulado com os bairros como nós e adjacências reais como arestas.
   - Cálculo de métricas globais, por microrregião e ego-networks.
   - Implementação dos algoritmos:
     - BFS
     - DFS
     - Dijkstra
     - Bellman-Ford
   - Geração de visualizações analíticas e grafo interativo.

2. **Parte 2 - Dataset Malha Aérea**
   - Escolhemos um grafo com ~59k arestas sobre o fluxo de viagens aéreas pelo mundo.
   - Comparação entre BFS, DFS, Dijkstra e Bellman-Ford em termos de corretude e desempenho.
   - Discussão crítica sobre resultados e limitações.


   ## 🗂️ Estrutura do Repositório

```
## 🗂️ Estrutura do Repositório
```text
.
├── data/                      # Arquivos de entrada (CSV)
├── out/                       # Resultados gerados pelo código
├── src/                       # Código-fonte principal
│   └── graphs/                # Implementação dos algoritmos de grafos
│       ├── algorithms.py      # BFS, DFS, Dijkstra, Bellman-Ford
│       ├── graph.py           # Estrutura de grafo e operações básicas
│       ├── io.py              # Leitura/escrita de dados (CSV)
│       ├── cli.py             # Interface de linha de comando (CLI)
│       ├── solve.py           # Rotinas auxiliares de resolução
│       └── viz.py             # Visualização de grafos
├── tests/                     # Testes automatizados

---
```

## ▶️ Como executar o projeto

Os dois cenários do projeto (bairros do Recife e rotas aéreas da Parte 2) são executados a partir de dois pontos principais:

- um **script orquestrador** (`solve.py`), que roda todo o pipeline de uma vez;
- uma **ferramenta de linha de comando (CLI)** (`src.cli`), para testar algoritmos e cenários específicos.

Use `python` para Windows ou `python3` para Linux/MacOs.

---

### 1) Execução completa – `solve.py`

`solve.py` funciona como o **orquestrador** do projeto: ele carrega os dados da pasta `data/`, constrói os grafos, calcula as métricas e gera todos os arquivos de saída na pasta `out/` (JSON, CSV, figuras e HTML).

```bash
python3 src/solve.py
```

## 🛠️ Tecnologias 
- **Linguagem**: Python 3.11+
- **Bibliotecas**: `pandas`, `argparse`, `heapq`, `dataclasses`, `typing`, `matplotlib`, `plotly`, `pyvis`
- **Framework**: `streamlit`

---

# MEMBROS

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
