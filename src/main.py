from mapas import MAPA_GRANDE, MAPA_MEDIO, MAPA_PEQUENO 
from buscas import busca_custo_uniforme, a_estrela

# =====================================================================
# TESTANDO E COMPARANDO OS ALGORITMOS
# =====================================================================
def main():
    origem = "Ecruteak City"
    destino = "Lavender Town"
        
    print(f"--- ROTA DE {origem.upper()} PARA {destino.upper()} ---")
        
    # Testando a Busca de Custo Uniforme (Cega)
    caminho_ucs, custo_ucs, nos_ucs, _ = busca_custo_uniforme(origem, destino)
    print("\n[BUSCA DE CUSTO UNIFORME]")
    print(f"Custo total: {custo_ucs} km")
    print(f"Nós expandidos (Esforço): {nos_ucs}")
    print(f"Caminho: {' -> '.join(caminho_ucs)}")
        
        # Testando o Algoritmo A* (Inteligente)
    caminho_ast, custo_ast, nos_ast, _ = a_estrela(origem, destino)
    print("\n[ALGORITMO A*]")
    print(f"Custo total: {custo_ast} km")
    print(f"Nós expandidos (Esforço): {nos_ast}")
    print(f"Caminho: {' -> '.join(caminho_ast)}")
        
    print("\n[CONCLUSÃO]")
    if custo_ucs == custo_ast:
        economia = ((nos_ucs - nos_ast) / nos_ucs) * 100
        print(f"Ambos acharam a rota perfeita! Mas o A* explorou {nos_ucs - nos_ast} cidades a menos.")
        print(f"Isso é uma economia de {economia:.1f}% de processamento na memória da IA!")

if __name__ == "__main__":
    main()