import time

from mapas import MAPA_GRANDE, MAPA_MEDIO, MAPA_PEQUENO 
from buscas import busca_custo_uniforme, a_estrela
from desenhar_mapas import desenhar_mapa
from tabela import processar_e_exibir_tabela
from graficos import gerar_graficos

# =====================================================================
# TESTANDO E COMPARANDO OS ALGORITMOS
# =====================================================================
def main():
    origem = "Cianwood City"
    destino = "Blackthorn City"
        
    mapas = [
        ("Pequeno", MAPA_PEQUENO),
        ("Médio", MAPA_MEDIO),
        ("Grande", MAPA_GRANDE)
    ]

    resultados = []

    for nome_mapa, mapa in mapas:
        # 1. Medição do Custo Uniforme (UCS)
        t_inicio = time.perf_counter()
        caminho_ucs, custo_ucs, nos_ucs, ordem_ucs = busca_custo_uniforme(origem, destino, mapa)
        t_fim = time.perf_counter()
        tempo_ucs = round((t_fim - t_inicio) * 1000, 4)  # Converte para milissegundos

        resultados.append({
            "Mapa": nome_mapa,
            "Algoritmo": "Custo Uniforme",
            "Custo Total": custo_ucs,
            "Nós Expandidos": nos_ucs,
            "Tempo (ms)": tempo_ucs,
            "Caminho": caminho_ucs
        })

        # Gera o mapa visual do UCS
        desenhar_mapa(
            mapa=mapa,
            caminho=caminho_ucs,
            expandidos=ordem_ucs,  # Lista de cidades (para o desenho)
            titulo=f"UCS - Mapa {nome_mapa}",
            salvar_em="../outputs/mapas",
            nome_arquivo=f"mapa_ucs_{nome_mapa.lower()}.png",
        )

        # 2. Medição do Algoritmo A*
        t_inicio = time.perf_counter()
        caminho_ast, custo_ast, nos_ast, ordem_ast = a_estrela(origem, destino, mapa)
        t_fim = time.perf_counter()
        tempo_ast = round((t_fim - t_inicio) * 1000, 4)  # Converte para milissegundos

        resultados.append({
            "Mapa": nome_mapa,
            "Algoritmo": "A*",
            "Custo Total": custo_ast,
            "Nós Expandidos": nos_ast,
            "Tempo (ms)": tempo_ast,
            "Caminho": caminho_ast
        })

        # Gera o mapa visual do A*
        desenhar_mapa(
            mapa=mapa,
            caminho=caminho_ast,
            expandidos=ordem_ast,  # Lista de cidades (para o desenho)
            titulo=f"A* - Mapa {nome_mapa}",
            salvar_em="../outputs/mapas",
            nome_arquivo=f"mapa_astar_{nome_mapa.lower()}.png",
        )

    print("Benchmark concluído! Coletados", len(resultados), "registros.")

    # Exibe a tabela de resultados
    df_resultados = processar_e_exibir_tabela(resultados, pasta_saida="../outputs/csv")

    # Gera os gráficos
    gerar_graficos(df_resultados, pasta_saida="../outputs/graficos")

if __name__ == "__main__":
    main()