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
.
├── data/                # Arquivos de entrada (CSV)
│   ├── adjacencias_bairros.csv
│   ├── bairros_recife.csv
│   ├── bairros_unique.csv
│   ├── enderecos.csv
│   ├── routes.csv
│   └── routes_dijkstra_pairs.csv
│
├── out/                 # Resultados gerados pelo código
│   ├── *.png            # Figuras de análise (histograma, subgrafo, etc.)
│   ├── *.html           # Visualizações interativas (grafo, árvore de percurso)
│   ├── recife_global.json
│   ├── microrregioes.json
│   ├── graus.csv
│   ├── ego_bairro.csv
│   └── parte2_report_out.json   # Relatório consolidado da Parte 2
│
├── src/                 # Código-fonte principal
│   ├── algorithms.py    # BFS, DFS, Dijkstra, Bellman-Ford
│   ├── graph.py         # Estrutura de grafo e operações básicas
│   ├── io.py            # Leitura/escrita de dados (CSV

---
```

## ▶️ Como executar o projeto

Os dois cenários abordados no projeto compartilham os mesmos métodos de execução, centralizados em dois scripts principais:

- **`python src/solve.py`**  
  Este script atua como o **orquestrador principal** do projeto.  
  Ele é responsável por:
  - carregar os dados a partir da pasta `data/`;
  - construir as instâncias dos grafos (bairros do Recife e grafo da Parte 2);
  - calcular todas as métricas necessárias;
  - executar os algoritmos de caminhos mínimos;
  - gerar os artefatos e saídas obrigatórias na pasta `out/`.

  Ao ser executado, o script produz arquivos como:
  - métricas globais e por microrregião do grafo de Recife;
  - ego-networks;
  - figuras de análise (PNG);
  - visualizações interativas em HTML;
  - relatório consolidado da Parte 2 (`parte2_report_out.json`).

  Execução:

  ```bash
  python src/solve.py


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
