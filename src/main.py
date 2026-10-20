import re
import statistics
import time
import unicodedata
from pathlib import Path

from mapas import MAPA_GRANDE, MAPA_MEDIO, MAPA_PEQUENO
from buscas import (
    a_estrela, busca_custo_uniforme, calibrar_escala_heuristica, custo_do_caminho,
)
from trechos import montar_grafo_tempo
from desenhar_mapas import desenhar_mapa
from tabela import processar_e_exibir_tabela
from graficos import gerar_graficos

# CORREÇÃO: antes os caminhos eram "../outputs/..." relativos ao diretório onde
# o usuário rodava o comando. Rodando da raiz do repositório, os arquivos
# saíam FORA do projeto. Agora são relativos à localização deste arquivo.
SAIDA = Path(__file__).resolve().parent.parent / "outputs"

# O tempo de uma busca em um grafo de 36 nós é de microssegundos: uma única
# medição é só ruído. Reporta-se a MEDIANA de várias execuções.
REPETICOES = 30


def medir(funcao, repeticoes=REPETICOES):
    """Executa `funcao` várias vezes; retorna (resultado, mediana em ms)."""
    tempos, resultado = [], None
    for _ in range(repeticoes):
        t0 = time.perf_counter()
        resultado = funcao()
        tempos.append((time.perf_counter() - t0) * 1000)
    return resultado, round(statistics.median(tempos), 4)


def slug(texto):
    """'Grande (Johto-Kanto)' -> 'grande_johto_kanto' (nome de arquivo seguro)."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


# =====================================================================
# FASE 1 - custo = distância. UCS x A*
# Os três primeiros cenários são os do Marco 1 (mesmos pares, números
# comparáveis). O quarto cruza Johto -> Kanto: com origem e destino iguais nos
# mapas Médio e Grande, o Grande não expandia nenhuma cidade de Kanto e os dois
# mapas davam resultados idênticos, então não mostravam efeito de escala.
# =====================================================================
CENARIOS_FASE1 = [
    ("Pequeno", MAPA_PEQUENO, "Cianwood City", "Blackthorn City"),
    ("Médio", MAPA_MEDIO, "Cianwood City", "Blackthorn City"),
    ("Grande", MAPA_GRANDE, "Cianwood City", "Blackthorn City"),
    ("Grande (Johto-Kanto)", MAPA_GRANDE, "Cianwood City", "Lavender Town"),
]


def executar_fase1():
    resultados = []

    for nome_mapa, mapa, origem, destino in CENARIOS_FASE1:
        # O pré-cálculo da escala da heurística fica fora do tempo medido
        escala = calibrar_escala_heuristica(mapa)

        buscas = [
            ("Custo Uniforme", "ucs", lambda: busca_custo_uniforme(origem, destino, mapa)),
            ("A*", "astar", lambda: a_estrela(origem, destino, mapa, escala)),
        ]
        for algoritmo, prefixo, executar in buscas:
            (caminho, custo, nos, ordem), tempo = medir(executar)

            resultados.append({
                "Mapa": nome_mapa,
                "Algoritmo": algoritmo,
                "Custo Total": custo,
                "Nós Expandidos": nos,
                "Tempo (ms)": tempo,
                "Caminho": caminho,
            })

            desenhar_mapa(
                mapa=mapa,
                caminho=caminho,
                expandidos=ordem,
                titulo=f"{algoritmo} - Mapa {nome_mapa} ({origem} -> {destino})",
                salvar_em=SAIDA / "mapas",
                nome_arquivo=f"mapa_{prefixo}_{slug(nome_mapa)}.png",
            )

    print("Benchmark da Fase 1 concluído! Coletados", len(resultados), "registros.")

    df = processar_e_exibir_tabela(resultados, pasta_saida=SAIDA / "csv")
    gerar_graficos(df, pasta_saida=SAIDA / "graficos")
    return df


# =====================================================================
# FASE 2 - custo = tempo de viagem (lombadas, semáforos, acidentes, horário,
# tipo de via). A busca é a mesma da Fase 1; só o grafo de custos muda.
# Pergunta do experimento: a rota mais CURTA é a mais RÁPIDA?
# =====================================================================
# (nome, origem, destino, hora de saída, trechos com acidente)
CENARIOS_FASE2 = [
    ("Pewter-Fuchsia 03h", "Pewter City", "Fuchsia City", 3, []),
    ("Pewter-Fuchsia 08h", "Pewter City", "Fuchsia City", 8, []),
    ("Pewter-Fuchsia 18h", "Pewter City", "Fuchsia City", 18, []),
    ("Pewter-Fuchsia 18h + acidente", "Pewter City", "Fuchsia City", 18,
     [("Saffron City", "Vermillion City")]),
    ("Cianwood-Lavender 18h", "Cianwood City", "Lavender Town", 18, []),
]


def executar_fase2():
    resultados = []

    for nome, origem, destino, hora, acidentes in CENARIOS_FASE2:
        grafo_tempo = montar_grafo_tempo(MAPA_GRANDE, hora, acidentes)
        escala = calibrar_escala_heuristica(grafo_tempo)

        # Critério da Fase 1: menor distância
        rota_curta, dist_curta, _, _ = a_estrela(origem, destino, MAPA_GRANDE)
        # A mesma rota, avaliada com o critério da Fase 2 (tempo naquela hora)
        tempo_curta = custo_do_caminho(rota_curta, grafo_tempo)

        # Critério da Fase 2: menor tempo previsto
        rota_rapida, tempo_rapida, nos_astar, ordem = a_estrela(origem, destino, grafo_tempo, escala)
        _, tempo_ucs, nos_ucs, _ = busca_custo_uniforme(origem, destino, grafo_tempo)

        if abs(tempo_ucs - tempo_rapida) > 1e-6:
            raise RuntimeError(f"A* não ótimo em '{nome}': {tempo_rapida} vs UCS {tempo_ucs}")

        resultados.append({
            "Cenário": nome,
            "Hora": f"{hora:02d}h",
            "Rota curta (km)": dist_curta,
            "Tempo rota curta (min)": round(tempo_curta, 1),
            "Tempo rota rápida (min)": round(tempo_rapida, 1),
            "Economia (min)": round(max(0.0, tempo_curta - tempo_rapida), 1),
            "Mesma rota?": "sim" if rota_curta == rota_rapida else "não",
            "Nós A*": nos_astar,
            "Nós UCS": nos_ucs,
            "Rota curta": rota_curta,
            "Rota rápida": rota_rapida,
        })

        desenhar_mapa(
            mapa=grafo_tempo,
            caminho=rota_rapida,
            expandidos=ordem,
            titulo=f"A* por tempo (min) - {nome}",
            salvar_em=SAIDA / "mapas",
            nome_arquivo=f"mapa_tempo_{slug(nome)}.png",
        )

    colunas = [
        "Cenário", "Hora", "Rota curta (km)", "Tempo rota curta (min)",
        "Tempo rota rápida (min)", "Economia (min)", "Mesma rota?", "Nós A*", "Nós UCS",
    ]
    return processar_e_exibir_tabela(
        resultados,
        pasta_saida=SAIDA / "csv",
        titulo="RELATÓRIO DA FASE 2: ROTA MAIS CURTA x ROTA MAIS RÁPIDA",
        nome_csv="fase2_rota_curta_vs_rapida.csv",
        colunas_exibicao=colunas,
    )


def main():
    executar_fase1()
    executar_fase2()


if __name__ == "__main__":
    main()
