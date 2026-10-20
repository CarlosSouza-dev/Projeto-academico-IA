"""
FASE 2 - Características dos trechos e custo de caminho em TEMPO de viagem.

Na Fase 1 o custo de cada estrada era só a distância. Aqui cada trecho (aresta)
ganha as características exigidas no documento PEAS:

    * quantidade de lombadas
    * número de semáforos
    * ocorrência de acidente
    * horário (do dia) da viagem
    * tipo de via

e o custo passa a ser o tempo de travessia, em minutos.

Dois caminhos para obter o custo de um trecho (mesma interface para a busca):

    1. `tempo_trecho`  -> simulador determinístico ("verdade do mundo"), usado
       para gerar o dataset sintético e como baseline.
    2. um modelo aprendido (k-NN, árvore, regressão...) passado como `prever`
       em `montar_grafo_tempo`. É isso que o PDF da disciplina pede na Fase 2.

A busca (buscas.py) NÃO muda: ela recebe um grafo {origem: {destino: custo}}.
O que muda é como esse grafo é montado.
"""
import math
import random
from dataclasses import dataclass

from mapas import MAPA_GRANDE, PONTOS_VERDES

SEED = 2026  # semente única: os atributos sintéticos são reprodutíveis

# =====================================================================
# 1. PARÂMETROS DO MODELO DE TEMPO (documentados para o relatório)
# A distância das arestas é tratada como km; o tempo sai em minutos.
# =====================================================================
TIPOS_VIA = ("asfalto", "paralelepipedo", "terra", "obras")

# Velocidade média em fluxo livre (km/h) por tipo de via
VELOCIDADE_KMH = {"asfalto": 80.0, "paralelepipedo": 45.0, "terra": 35.0, "obras": 25.0}

# Quanto cada tipo de via sofre com o trânsito do horário (0 = indiferente,
# 1 = sofre o congestionamento por inteiro). Trilha de terra quase não tem fila.
SENSIBILIDADE_TRANSITO = {"asfalto": 1.0, "paralelepipedo": 0.8, "obras": 0.6, "terra": 0.2}

MIN_POR_LOMBADA = 0.25          # ~15 s para reduzir e voltar à velocidade
ESPERA_SEMAFORO_MIN = 0.7       # espera média por semáforo em fluxo livre
PENALIDADE_ACIDENTE_MIN = 20.0  # atraso fixo de um trecho com acidente


@dataclass(frozen=True)
class Trecho:
    """Características estáticas de uma estrada (não dependem da hora)."""
    distancia: float
    lombadas: int
    semaforos: int
    tipo_via: str


def chave_trecho(a, b):
    """Chave não direcionada: o trecho A-B é o mesmo que B-A."""
    return tuple(sorted((a, b)))


# =====================================================================
# 2. HORÁRIO -> FATOR DE TRÂNSITO
# =====================================================================
def _pico(hora, centro, largura):
    """Curva em sino (gaussiana) circular em torno de `centro`, valor em [0, 1]."""
    d = abs(hora - centro) % 24
    d = min(d, 24 - d)
    return math.exp(-0.5 * (d / largura) ** 2)


def fator_transito(hora):
    """Multiplicador de congestionamento: ~1.0 de madrugada, ~1.8-2.0 nos picos
    (8h e 18h). `hora` é decimal em [0, 24), ex.: 17.5 = 17h30."""
    return 1.0 + 0.8 * _pico(hora, 8.0, 1.3) + 1.0 * _pico(hora, 18.0, 1.6)


# =====================================================================
# 3. CUSTO DO TRECHO: SIMULADOR DE TEMPO
# =====================================================================
def tempo_trecho(trecho, hora, acidente=False):
    """Tempo de travessia (minutos) de um trecho em determinada hora.

        tempo = deslocamento x (1 + sensibilidade x (fator - 1))
              + lombadas x min_por_lombada
              + semáforos x espera x fator
              + acidente x penalidade
    """
    f = fator_transito(hora)
    deslocamento = trecho.distancia / VELOCIDADE_KMH[trecho.tipo_via] * 60.0
    deslocamento *= 1.0 + SENSIBILIDADE_TRANSITO[trecho.tipo_via] * (f - 1.0)
    return (
        deslocamento
        + trecho.lombadas * MIN_POR_LOMBADA
        + trecho.semaforos * ESPERA_SEMAFORO_MIN * f
        + (PENALIDADE_ACIDENTE_MIN if acidente else 0.0)
    )


# =====================================================================
# 4. DADOS SINTÉTICOS DOS TRECHOS (cidade fictícia, regras registradas)
# =====================================================================
def _eh_cidade(local):
    return local not in PONTOS_VERDES


def gerar_trechos(mapa, seed=SEED):
    """Sorteia as características de cada estrada do mapa, de forma
    determinística (mesma estrada -> mesmos atributos, em qualquer mapa).

    Regras (justificativa para o relatório):
      * verde-verde (caverna, floresta...): terra, sem semáforo nem lombada;
      * cidade-verde: maioria terra/paralelepípedo, 0-2 lombadas, 0-1 semáforo;
      * cidade-cidade: maioria asfalto, com lombadas e semáforos
        proporcionais à distância, e chance de obras.
    """
    trechos = {}
    for a, vizinhos in mapa.items():
        for b, dist in vizinhos.items():
            chave = chave_trecho(a, b)
            if chave in trechos:
                continue
            rng = random.Random(f"{seed}|{chave[0]}|{chave[1]}")
            cidades = _eh_cidade(a) + _eh_cidade(b)
            if cidades == 0:
                tipo, lombadas, semaforos = "terra", 0, 0
            elif cidades == 1:
                tipo = rng.choices(TIPOS_VIA, weights=[2, 3, 5, 0])[0]
                lombadas, semaforos = rng.randint(0, 2), rng.randint(0, 1)
            else:
                tipo = rng.choices(TIPOS_VIA, weights=[60, 25, 0, 15])[0]
                lombadas = rng.randint(0, max(1, int(dist // 25)))
                semaforos = rng.randint(0, max(1, int(dist // 30)))
            trechos[chave] = Trecho(dist, lombadas, semaforos, tipo)
    return trechos


# Trechos de TODAS as estradas do jogo. Pequeno e Médio são subconjuntos do
# Grande, então reaproveitam os mesmos atributos.
TRECHOS = gerar_trechos(MAPA_GRANDE)


# =====================================================================
# 5. GRAFO DE TEMPO (entrada da busca na Fase 2)
# =====================================================================
def montar_grafo_tempo(mapa, hora, acidentes=(), prever=None):
    """Converte o mapa de distâncias em um grafo cujo custo é o TEMPO (min).

    mapa      : {cidade: {vizinho: distancia}} (MAPA_PEQUENO/MEDIO/GRANDE)
    hora      : horário da viagem (decimal, 0-24)
    acidentes : pares (a, b) com acidente; a ordem não importa
    prever    : opcional, `prever(trecho, hora, acidente) -> minutos`. Aqui
                entra o modelo aprendido; se None, usa o simulador.
    """
    ocorrencias = {chave_trecho(a, b) for a, b in acidentes}
    estimar = prever or tempo_trecho
    grafo = {}
    for a, vizinhos in mapa.items():
        grafo[a] = {}
        for b in vizinhos:
            chave = chave_trecho(a, b)
            if chave not in TRECHOS:
                raise KeyError(f"Trecho {a}-{b} sem características em TRECHOS")
            grafo[a][b] = round(estimar(TRECHOS[chave], hora, chave in ocorrencias), 4)
    return grafo


# =====================================================================
# 6. DATASET SINTÉTICO PARA TREINAR O MODELO (Fase 2)
# =====================================================================
def gerar_dataset_sintetico(n_por_trecho=60, ruido=0.08, p_acidente=0.10, seed=SEED):
    """Gera amostras (trecho, hora, acidente) -> tempo observado.

    O tempo observado é o do simulador com ruído multiplicativo gaussiano
    (`ruido` = desvio relativo), imitando a variação real de travessias.
    Retorna lista de dicts, uma linha por observação.
    """
    rng = random.Random(f"{seed}|dataset")
    linhas = []
    for (a, b), t in sorted(TRECHOS.items()):
        for _ in range(n_por_trecho):
            hora = round(rng.uniform(0, 24), 2)
            acidente = rng.random() < p_acidente
            tempo = tempo_trecho(t, hora, acidente) * max(0.2, rng.gauss(1.0, ruido))
            linhas.append({
                "origem": a, "destino": b,
                "distancia": t.distancia, "lombadas": t.lombadas,
                "semaforos": t.semaforos, "tipo_via": t.tipo_via,
                "hora": hora, "acidente": int(acidente),
                "tempo_min": round(tempo, 3),
            })
    return linhas


if __name__ == "__main__":
    # Gera o CSV de treino em ../outputs/csv/dataset_trechos.csv
    from pathlib import Path
    import pandas as pd

    pasta = Path(__file__).resolve().parent.parent / "outputs" / "csv"
    pasta.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(gerar_dataset_sintetico())
    destino = pasta / "dataset_trechos.csv"
    df.to_csv(destino, index=False)
    print(f"Dataset com {len(df)} linhas salvo em '{destino}'")
