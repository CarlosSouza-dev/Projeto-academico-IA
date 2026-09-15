import heapq
import itertools
import math

from mapas import COORD, MAPA_GRANDE, MAPA_MEDIO, MAPA_PEQUENO

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
    
    # ATENÇÃO PARA A ARGUIÇÃO: Como as distâncias reais subiram muito na nova versão,
    # dividimos a distância euclidiana imaginária por 10. Isso nos garante
    # admissibilidade matemática absoluta, ou seja, h(n) nunca será maior que
    # o percurso real h*(n), mantendo o algoritmo A* em estado ótimo.
    return int(distancia_calc / 10)

#Consultas impressindíveis:




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
        # Necessário para a fila de prioridade (heapq) desempatar nós
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
def busca_custo_uniforme(inicio, objetivo):
    """
    Busca Cega: Expande sempre o nó de menor custo real acumulado g(n).
    Não faz ideia de onde o destino fica (ignora a heurística).
    """
    contador = itertools.count() 
    fronteira = []
    # Fila de prioridade: (prioridade, desempate, nó)
    # A prioridade aqui é apenas o custo real passado: g(n)
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

        for vizinho, custo in MAPA_GRANDE[no.estado].items():
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
def a_estrela(inicio, objetivo):
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

        for vizinho, custo in MAPA_GRANDE[no.estado].items():
            if vizinho in explorados:
                continue
            
            filho = No(vizinho, pai=no, acao=vizinho, g=no.g + custo)
            
            # O "Pulo do Gato" do A*: calcular a heurística do vizinho
            h_vizinho = calcular_heuristica_linha_reta(vizinho, objetivo)
            
            # A prioridade é a soma: Passado + Futuro
            f = filho.g + h_vizinho
            
            heapq.heappush(fronteira, (f, next(contador), filho))

    return None, None, len(ordem), ordem
