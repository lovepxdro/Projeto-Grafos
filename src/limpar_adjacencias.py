import pandas as pd
from pathlib import Path

# --- 1. Configurar Caminhos ---
# Assume que o script está rodando da raiz do projeto, ou ajustamos os paths
# Baseado na sua estrutura, vamos usar caminhos relativos
DATA_DIR = Path("data")
ADJACENCIAS_FILE = DATA_DIR / "adjacencias_bairros.csv"
BAIRROS_UNIQUE_FILE = DATA_DIR / "bairros_unique.csv"
OUTPUT_FILE = DATA_DIR / "adjacencias_bairros_limpo.csv" # Salvar como um novo arquivo por segurança

print(f"Arquivo de entrada: {ADJACENCIAS_FILE}")
print(f"Arquivo de mapeamento: {BAIRROS_UNIQUE_FILE}")
print(f"Arquivo de saída: {OUTPUT_FILE}")

# --- 2. Criar Mapeamento Bairro -> Microrregião ---
# O formato em bairros_unique.csv é "Nome do Bairro X.Y"
mapeamento_bairro_micro = {}
try:
    with open(BAIRROS_UNIQUE_FILE, 'r', encoding='utf-8') as f:
        for linha in f:
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue
            
            # Divide a linha no último espaço
            # Ex: "Alto José Bonifácio 3.2" -> ["Alto José Bonifácio", "3.2"]
            partes = linha_limpa.rsplit(' ', 1)
            if len(partes) == 2:
                bairro, microrregiao = partes
                mapeamento_bairro_micro[bairro.strip()] = microrregiao.strip()
            else:
                print(f"Aviso: Linha mal formatada em bairros_unique.csv: {linha_limpa}")

    print(f"Mapeamento criado com {len(mapeamento_bairro_micro)} bairros.")

except FileNotFoundError:
    print(f"Erro: Arquivo de mapeamento não encontrado em {BAIRROS_UNIQUE_FILE}")
    exit()
except Exception as e:
    print(f"Erro ao ler o arquivo de mapeamento: {e}")
    exit()

# --- 3. Carregar e Processar Adjacências ---
try:
    df_adj = pd.read_csv(ADJACENCIAS_FILE)

    # 4. Mapear microrregiões para origem e destino
    df_adj['micro_origem'] = df_adj['bairro_origem'].map(mapeamento_bairro_micro)
    df_adj['micro_destino'] = df_adj['bairro_destino'].map(mapeamento_bairro_micro)

    # 5. Filtrar conexões INTER-regionais (ignorar intra-regionais)
    # Remove linhas onde a microrregião é a mesma, ou se algum bairro não foi mapeado (NaN)
    df_filtrado = df_adj.dropna(subset=['micro_origem', 'micro_destino'])
    df_filtrado = df_filtrado[df_filtrado['micro_origem'] != df_filtrado['micro_destino']]

    print(f"Encontradas {len(df_filtrado)} conexões inter-microrregiões.")

    # 6. Garantir conexão ÚNICA entre microrregiões
    # Criamos uma "chave" canônica para o par (ex: ('1.1', '2.1') é o mesmo que ('2.1', '1.1'))
    # Usamos frozenset para poder usar drop_duplicates
    df_filtrado['par_micro'] = df_filtrado.apply(
        lambda row: frozenset([row['micro_origem'], row['micro_destino']]),
        axis=1
    )

    # Mantém apenas a *primeira* ocorrência de cada par de microrregião
    df_final = df_filtrado.drop_duplicates(subset=['par_micro'])
    
    # 7. Limpar colunas temporárias
    df_final = df_final.drop(columns=['micro_origem', 'micro_destino', 'par_micro'])

    # --- 8. Salvar o Resultado ---
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

    print("-" * 30)
    print(f"Sucesso! Arquivo limpo salvo em: {OUTPUT_FILE}")
    print(f"Número de conexões original (total): {len(df_adj)}")
    print(f"Número de conexões final (uma por par de microrregião): {len(df_final)}")
    print("-" * 30)
    print("Amostra do resultado:")
    print(df_final.head())


except FileNotFoundError:
    print(f"Erro: Arquivo de adjacências não encontrado em {ADJACENCIAS_FILE}")
except Exception as e:
    print(f"Ocorreu um erro durante o processamento: {e}")