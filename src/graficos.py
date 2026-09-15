import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def gerar_graficos(df_ou_csv=None, pasta_saida="../outputs/graficos"):
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    # Trata a entrada (caminho str, DataFrame ou None)
    if df_ou_csv is None:
        caminho_csv = os.path.join(pasta_saida, "benchmark_resultados.csv")
        df = pd.read_csv(caminho_csv)
    elif isinstance(df_ou_csv, str):
        df = pd.read_csv(df_ou_csv)
    else:
        df = df_ou_csv  

    sns.set_theme(style="whitegrid")

    # 1. Gráfico de Nós Expandidos 
    plt.figure(figsize=(8, 5))
    ax1 = sns.barplot(
        data=df, x="Mapa", y="Nós Expandidos", hue="Algoritmo", palette="Set2"
    )
    plt.title("Comparativo de Esforço: Nós Expandidos por Mapa", fontsize=12)
    plt.xlabel("Escala do Mapa")
    plt.ylabel("Nós Expandidos (Cidades Visitadas)")

    for container in ax1.containers:
        ax1.bar_label(container, fmt="%d", padding=3)

    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafico_nos_expandidos.png"), dpi=300)
    plt.close()

    # 2. Gráfico de Tempo de Execução 
    plt.figure(figsize=(8, 5))
    ax2 = sns.barplot(
        data=df, x="Mapa", y="Tempo (ms)", hue="Algoritmo", palette="Set2"
    )
    plt.title("Comparativo de Latência: Tempo de Execução (ms)", fontsize=12)
    plt.xlabel("Escala do Mapa")
    plt.ylabel("Tempo (ms)")

    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.3f", padding=3)

    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafico_tempo_execucao.png"), dpi=300)
    plt.close()

    print(f"Gráficos salvos com sucesso na pasta '{pasta_saida}/'!")

if __name__ == "__main__":
    gerar_graficos()