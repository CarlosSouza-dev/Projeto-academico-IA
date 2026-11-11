import heapq
import itertools
import math

from mapas import COORD

# =====================================================================
# HEURÍSTICA DE DISTÂNCIA DIRETA (HDD)
#
# h(n) = escala x distância_em_linha_reta(n, objetivo)
#
# ERRO CORRIGIDO: antes a escala era "dividir por 10", um número mágico que
# não garante admissibilidade (na estrada Saffron-Celadon a heurística dava
# 10 para um custo real de 9). Agora a escala é CALIBRADA no próprio grafo:
#
#     escala = min sobre todas as arestas (custo / distância_em_linha_reta)
#
# Prova de que h é admissível e consistente: para qualquer aresta (a, b),
# custo(a, b) >= escala x dist(a, b). Pela desigualdade triangular,
#   h(a) = escala x dist(a, obj) <= escala x (dist(a, b) + dist(b, obj))
#                                <= custo(a, b) + h(b).
# Logo h(a) <= c(a, b) + h(b) (consistência), e consistência implica
# admissibilidade. Vale para qualquer função de custo: distância na Fase 1,
# tempo previsto na Fase 2.
# =====================================================================
def distancia_direta(cidade_a, cidade_b):
    """Distância euclidiana entre duas cidades, nas unidades de COORD."""
    for c in (cidade_a, cidade_b):
        if c not in COORD:
            # Antes devolvia h=0 em silêncio, escondendo erro de cadastro.
            raise KeyError(f"'{c}' não possui coordenada em COORD")
    return math.dist(COORD[cidade_a], COORD[cidade_b])


def calibrar_escala_heuristica(grafo):
    """Maior escala que ainda mantém a HDD admissível/consistente no grafo."""
    razoes = [
        custo / distancia_direta(a, b)
        for a, vizinhos in grafo.items()
        for b, custo in vizinhos.items()
        if distancia_direta(a, b) > 0
    ]
    return min(razoes)


def heuristica_hdd(cidade_atual, cidade_destino, escala):
    """h(n) da busca A*: distância em linha reta até o destino x escala."""
    return escala * distancia_direta(cidade_atual, cidade_destino)


# --------------------------------------------------
# ESTRUTURA BASE DA BUSCA (Classe Nó e Reconstrução)
# --------------------------------------------------

class No:
    """Um nó da árvore de busca: guarda a cidade e a memória do trajeto."""
    __slots__ = ("estado", "pai", "acao", "g")

    def __init__(self, estado, pai=None, acao=None, g=0):
        self.estado = estado    # A cidade atual
        self.pai = pai          # O nó anterior (None se for a origem)
        self.acao = acao        # A ação que levou a este nó
        self.g = g              # O custo acumulado g(n) desde o início

    def __lt__(self, outro):
        return self.g < outro.g


def reconstruir_caminho(no):
    """Sobe de pai em pai até a origem para montar a lista da rota final."""
    caminho = []
    while no is not None:
        caminho.append(no.estado)
        no = no.pai
    return caminho[::-1]  # Inverte a lista para ficar da Origem -> Destino


def custo_do_caminho(caminho, grafo):
    """Soma o custo das arestas de `caminho` em `grafo`.

    Serve para avaliar uma rota achada com um critério (ex.: distância) sob
    outro critério (ex.: tempo no horário de pico).
    """
    return sum(grafo[a][b] for a, b in zip(caminho, caminho[1:]))


# =====================================================================
# NÚCLEO COMUM: busca de melhor-primeiro com f(n) = g(n) + h(n)
# UCS é o caso h(n) = 0; A* usa a HDD. Antes eram duas cópias do mesmo laço.
#
# Detalhes da correção:
#   * `melhor_g` guarda o menor g já visto por cidade: evita empilhar rotas
#     piores e descarta entradas "velhas" da fronteira ao desempilhar.
#   * Se uma heurística passada pelo usuário for admissível mas inconsistente,
#     uma cidade já expandida é reaberta ao achar um g menor (o `set` de
#     explorados anterior bloquearia isso e perderia a otimalidade).
#   * O teste de objetivo é feito ao DESEMPILHAR (não ao gerar), que é o que
#     garante a rota ótima.
# =====================================================================
def _busca_melhor_primeiro(inicio, objetivo, grafo, h):
    for cidade in (inicio, objetivo):
        if cidade not in grafo:
            raise ValueError(f"'{cidade}' não existe neste mapa")

    contador = itertools.count()  # desempate estável no heap
    fronteira = [(h(inicio), next(contador), No(inicio))]
    melhor_g = {inicio: 0}
    ordem = []  # cidades expandidas, na ordem (o objetivo NÃO entra)

    while fronteira:
        _, _, no = heapq.heappop(fronteira)

        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        if no.g > melhor_g[no.estado]:
            continue  # entrada velha: já existe caminho melhor até aqui

        ordem.append(no.estado)

        for vizinho, custo in grafo[no.estado].items():
            g = no.g + custo
            if g >= melhor_g.get(vizinho, math.inf):
                continue
            melhor_g[vizinho] = g
            filho = No(vizinho, pai=no, acao=vizinho, g=g)
            heapq.heappush(fronteira, (g + h(vizinho), next(contador), filho))

    return None, None, len(ordem), ordem


# =====================================================================
# TASK 1.2: BUSCA NÃO INFORMADA (Custo Uniforme)
# =====================================================================
def busca_custo_uniforme(inicio, objetivo, mapa):
    """Busca cega: expande sempre o nó de menor custo acumulado g(n)."""
    return _busca_melhor_primeiro(inicio, objetivo, mapa, lambda _estado: 0)


# =====================================================================
# TASK 1.3: BUSCA INFORMADA (Algoritmo A*)
# =====================================================================
def a_estrela(inicio, objetivo, mapa, escala=None):
    """A*: ordena a fronteira por f(n) = g(n) + h(n), com h = HDD.

    `escala` é a escala da HDD. Se None, é calibrada no grafo (custo O(E));
    em benchmarks, calibre uma vez com `calibrar_escala_heuristica` e passe
    o valor para esse pré-cálculo não entrar no tempo medido.
    """
    if escala is None:
        escala = calibrar_escala_heuristica(mapa)
    return _busca_melhor_primeiro(
        inicio, objetivo, mapa, lambda estado: heuristica_hdd(estado, objetivo, escala)
    )
