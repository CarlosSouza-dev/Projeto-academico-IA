import os
import pandas as pd

def processar_e_exibir_tabela(resultados, pasta_saida="../outputs/csv"):
    os.makedirs(pasta_saida, exist_ok=True)  # Cria a pasta de saída se não existir

    df = pd.DataFrame(resultados) # Cria um DataFrame a partir da lista de resultados

    # Ajusta a exibição do Pandas no console
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

    print("\n" + "=" * 65)
    print("             RELATÓRIO DO BENCHMARK (MARCO 1)")
    print("=" * 65)
    
    colunas_exibicao = ["Mapa", "Algoritmo", "Custo Total", "Nós Expandidos", "Tempo (ms)"]
    print(df[colunas_exibicao].to_string(index=False))
    
    print("=" * 65 + "\n")

    # Salva os resultados em um arquivo CSV
    caminho_csv = os.path.join(pasta_saida, "benchmark_resultados.csv")
    df.to_csv(caminho_csv, index=False)
    print(f"Arquivo '{caminho_csv}' gerado com sucesso!")

    return df

