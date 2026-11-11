import os
from pathlib import Path

import pandas as pd


def processar_e_exibir_tabela(
    resultados,
    pasta_saida=Path(__file__).resolve().parent.parent / "outputs" / "csv",
    titulo="RELATÓRIO DO BENCHMARK (MARCO 1)",
    nome_csv="benchmark_resultados.csv",
    colunas_exibicao=None,
):
    """Monta o DataFrame, imprime as colunas de `colunas_exibicao` e salva o CSV.

    Antes o título e o nome do arquivo eram fixos em "MARCO 1"; agora a mesma
    função serve para as tabelas da Fase 1 e da Fase 2.
    """
    os.makedirs(pasta_saida, exist_ok=True)  # Cria a pasta de saída se não existir

    df = pd.DataFrame(resultados)  # Cria um DataFrame a partir da lista de resultados

    # Caminho é uma lista; no CSV fica legível como "A > B > C"
    if "Caminho" in df.columns:
        df["Caminho"] = df["Caminho"].apply(
            lambda c: " > ".join(c) if isinstance(c, (list, tuple)) else c
        )

    # Ajusta a exibição do Pandas no console
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

    if colunas_exibicao is None:
        colunas_exibicao = ["Mapa", "Algoritmo", "Custo Total", "Nós Expandidos", "Tempo (ms)"]

    print("\n" + "=" * 100)
    print(titulo.center(100))
    print("=" * 100)
    print(df[colunas_exibicao].to_string(index=False))
    print("=" * 100 + "\n")

    # Salva os resultados em um arquivo CSV
    caminho_csv = os.path.join(pasta_saida, nome_csv)
    df.to_csv(caminho_csv, index=False)
    print(f"Arquivo '{caminho_csv}' gerado com sucesso!")

    return df
