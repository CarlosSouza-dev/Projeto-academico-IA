import heapq
import itertools
import math

from mapas import COORD

def calcular_heuristica_linha_reta(cidade_atual, cidade_destino):
    """
    Calcula a distância euclidiana (linha reta) entre o estado atual e o objetivo.
    Garante a admissibilidade da heurística dividindo o resultado final.
    """
    if cidade_atual not in COORD or cidade_destino not in COORD:
        return 0 
        
    x1, y1 = COORD[cidade_atual]
    x2, y2 = COORD[cidade_destino]
    
    distancia_calc = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Garante que a heurística seja admissível (não superestima o custo real)
    return distancia_calc / 10

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
        # Permite que o heapq compare nós com base no custo g(n) acumulado.
        return self.g < outro.g

def reconstruir_caminho(no):
    """Sobe de pai em pai até a origem para montar a lista da rota final."""
    caminho = []
    while no is not None:
        caminho.append(no.estado)
        no = no.pai
    return caminho[::-1] # Inverte a lista para ficar da Origem -> Destino

# =====================================================================
# TASK 1.2: BUSCA NÃO INFORMADA (Custo Uniforme)
# =====================================================================
def busca_custo_uniforme(inicio, objetivo, mapa):
    """
    Busca Cega: Expande sempre o nó de menor custo real acumulado g(n).
    Não faz ideia de onde o destino fica (ignora a heurística).
    """
    contador = itertools.count() 
    fronteira = []
    # Fila de prioridade: (prioridade, desempate, nó)
    # A prioridade é o custo acumulado g(n) do nó.
    heapq.heappush(fronteira, (0, next(contador), No(inicio)))
    explorados = set()
    ordem = []

    while fronteira:
        _, _, no = heapq.heappop(fronteira)

        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        if no.estado in explorados:
            continue

        explorados.add(no.estado)
        ordem.append(no.estado)

        for vizinho, custo in mapa[no.estado].items():
            if vizinho in explorados:
                continue
            
            # Custo acumulado = Custo do pai + distância da nova estrada
            filho = No(vizinho, pai=no, acao=vizinho, g=no.g + custo)
            
            # Insere na fila priorizando QUEM ANDOU MENOS ATÉ AGORA (filho.g)
            heapq.heappush(fronteira, (filho.g, next(contador), filho))

    return None, None, len(ordem), ordem

# =====================================================================
# TASK 1.3: BUSCA INFORMADA (Algoritmo A*)
# =====================================================================
def a_estrela(inicio, objetivo, mapa):
    """
    Busca Inteligente: Ordena a fronteira por f(n) = g(n) + h(n).
    Soma o custo real percorrido com a estimativa de distância até o alvo.
    """
    contador = itertools.count()
    fronteira = []
    
    # Heurística do ponto de partida
    h_inicial = calcular_heuristica_linha_reta(inicio, objetivo)
    heapq.heappush(fronteira, (h_inicial, next(contador), No(inicio)))
    explorados = set()
    ordem = []

    while fronteira:
        _, _, no = heapq.heappop(fronteira)

        if no.estado == objetivo:
            return reconstruir_caminho(no), no.g, len(ordem), ordem

        if no.estado in explorados:
            continue

        explorados.add(no.estado)
        ordem.append(no.estado)

        for vizinho, custo in mapa[no.estado].items():
            if vizinho in explorados:
                continue
            
            filho = No(vizinho, pai=no, acao=vizinho, g=no.g + custo)
            
            # Calcula a heurística do vizinho em relação ao objetivo
            h_vizinho = calcular_heuristica_linha_reta(vizinho, objetivo)
            
            # Calcula f(n) = g(n) + h(n) para o vizinho
            f = filho.g + h_vizinho
            
            heapq.heappush(fronteira, (f, next(contador), filho))

    return None, None, len(ordem), ordem
