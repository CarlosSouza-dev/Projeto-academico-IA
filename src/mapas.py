# =====================================================================
# 1. COORDENADAS PARA A HEURÍSTICA (Plano Cartesiano X, Y)
# O eixo X cresce para a direita (Kanto) e diminui para a esquerda (Johto).
# O eixo Y cresce para baixo.
# =====================================================================
COORD = {
    # --- CIDADES DE JOHTO ---
    "Cianwood City": (50, 200),
    "Olivine City": (100, 150),
    "Ecruteak City": (200, 100),
    "Mahogany Town": (350, 100),
    "Blackthorn City": (450, 100),
    "Goldenrod City": (200, 250),
    "Azalea Town": (250, 350),
    "Violet City": (350, 200),
    "Cherrygrove City": (400, 300),
    "New Bark Town": (500, 300),

    # --- PONTOS VERDES DE JOHTO ---
    "Safari Zone": (20, 200),
    "Whirl Islands": (100, 250),
    "National Park": (150, 150),
    "Mt. Mortar": (275, 100),
    "Lake of Rage": (350, 50),
    "Ice Path": (400, 100),
    "Ilex Forest": (200, 350),
    "Union Cave": (300, 350),

    # --- LIGAÇÃO JOHTO-KANTO (Cidades e Pontos Verdes) ---
    "Tohjo Falls": (550, 300),
    "Victory Road": (600, 200),
    "Mt. Silver": (550, 200),
    "Indigo Plateau": (600, 100),

    # --- CIDADES DE KANTO ---
    "Pallet Town": (700, 300),
    "Viridian City": (700, 250),
    "Pewter City": (700, 100),
    "Cerulean City": (900, 100),
    "Saffron City": (900, 250),
    "Celadon City": (800, 250),
    "Lavender Town": (1000, 250),
    "Vermillion City": (900, 350),
    "Fuchsia City": (850, 450),
    "Cinnabar Island": (700, 450),

    # --- PONTOS VERDES DE KANTO ---
    "Viridian Forest": (700, 200),
    "Mt. Moon": (800, 100),
    "Rock Tunnel": (1000, 100),
    "Seafoam Islands": (775, 450)
}

# Pontos "verdes" (rotas, cavernas, florestas, ilhas): não são cidades.
# Usados na Fase 2 para decidir se um trecho tem semáforos/lombadas (só há
# em trechos que tocam uma cidade) e qual o tipo de via mais provável.
PONTOS_VERDES = {
    "Safari Zone", "Whirl Islands", "National Park", "Mt. Mortar",
    "Lake of Rage", "Ice Path", "Ilex Forest", "Union Cave",
    "Tohjo Falls", "Victory Road", "Mt. Silver",
    "Viridian Forest", "Mt. Moon", "Rock Tunnel", "Seafoam Islands",
}

# =====================================================================
# 2. O ESPAÇO DE ESTADOS (O Grafo, Rotas e Custos)
# Cada chave é um estado (cidade/ponto) e o valor é um dicionário 
# com os estados vizinhos e o custo (distância) da viagem.
# =====================================================================

# 2.1 Mapa Pequeno - Região de Johto (9 nós)
MAPA_PEQUENO = {
    "Safari Zone": {"Cianwood City": 35},
    "Cianwood City": {"Safari Zone": 35, "Whirl Islands": 15},
    "Whirl Islands": {"Cianwood City": 15, "Olivine City": 85},
    "Olivine City": {"Whirl Islands": 85, "Ecruteak City": 75},
    "Ecruteak City": {"Olivine City": 75, "Mt. Mortar": 40},
    "Mt. Mortar": {"Ecruteak City": 40, "Mahogany Town": 30},
    "Mahogany Town": {"Mt. Mortar": 30, "Ice Path": 22},
    "Ice Path": {"Mahogany Town": 22, "Blackthorn City": 40},
    "Blackthorn City": {"Ice Path": 40},
}

# 2.2 Mapa Médio - Região de Johto (18 nós)
# CORREÇÃO: o comentário dizia 21 nós, mas o mapa tem 18. Além disso, "New Bark
# Town" apontava para "Tohjo Falls", que não é um nó deste mapa (KeyError ao
# expandir). Essa aresta pertence ao Mapa Grande e foi removida daqui.
MAPA_MEDIO = {
    "Safari Zone": {"Cianwood City": 35},
    "Cianwood City": {"Safari Zone": 35, "Whirl Islands": 15},
    "Whirl Islands": {"Cianwood City": 15, "Olivine City": 85},
    "Olivine City": {"Whirl Islands": 85, "Ecruteak City": 75},
    "Ecruteak City": {"Olivine City": 75, "Mt. Mortar": 40, "National Park": 40, "Violet City": 40},
    "Mt. Mortar": {"Ecruteak City": 40, "Mahogany Town": 30},
    "Mahogany Town": {"Mt. Mortar": 30, "Lake of Rage": 50, "Ice Path": 22},
    "Lake of Rage": {"Mahogany Town": 50},
    "Ice Path": {"Mahogany Town": 22, "Blackthorn City": 40},
    "Blackthorn City": {"Ice Path": 40, "Cherrygrove City": 95, "New Bark Town": 105},
        
    "National Park": {"Ecruteak City": 40, "Goldenrod City": 25, "Violet City": 45},
    "Goldenrod City": {"National Park": 25, "Ilex Forest": 30},
    "Ilex Forest": {"Goldenrod City": 30, "Azalea Town": 75},
    "Azalea Town": {"Ilex Forest": 75, "Union Cave": 20},
    "Union Cave": {"Azalea Town": 20, "Violet City": 140},
        
    "Violet City": {"Union Cave": 140, "Ecruteak City": 40, "National Park": 45, "Cherrygrove City": 110},
    "Cherrygrove City": {"Violet City": 110, "Blackthorn City": 95, "New Bark Town": 75},
    "New Bark Town": {"Cherrygrove City": 75, "Blackthorn City": 105}
}

# 2.3 Mapa Grande - Região de Kanto + Johto (36 nós)
MAPA_GRANDE = {
    # ================= JOHTO =================
    "Safari Zone": {"Cianwood City": 35},
    "Cianwood City": {"Safari Zone": 35, "Whirl Islands": 15},
    "Whirl Islands": {"Cianwood City": 15, "Olivine City": 85},
    "Olivine City": {"Whirl Islands": 85, "Ecruteak City": 75},
    "Ecruteak City": {"Olivine City": 75, "Mt. Mortar": 40, "National Park": 40, "Violet City": 40},
    "Mt. Mortar": {"Ecruteak City": 40, "Mahogany Town": 30},
    "Mahogany Town": {"Mt. Mortar": 30, "Lake of Rage": 50, "Ice Path": 22},
    "Lake of Rage": {"Mahogany Town": 50},
    "Ice Path": {"Mahogany Town": 22, "Blackthorn City": 40},
    "Blackthorn City": {"Ice Path": 40, "Cherrygrove City": 95, "New Bark Town": 105},
    
    "National Park": {"Ecruteak City": 40, "Goldenrod City": 25, "Violet City": 45},
    "Goldenrod City": {"National Park": 25, "Ilex Forest": 30},
    "Ilex Forest": {"Goldenrod City": 30, "Azalea Town": 75},
    "Azalea Town": {"Ilex Forest": 75, "Union Cave": 20},
    "Union Cave": {"Azalea Town": 20, "Violet City": 140},
    
    "Violet City": {"Union Cave": 140, "Ecruteak City": 40, "National Park": 45, "Cherrygrove City": 110},
    "Cherrygrove City": {"Violet City": 110, "Blackthorn City": 95, "New Bark Town": 75},
    "New Bark Town": {"Cherrygrove City": 75, "Blackthorn City": 105, "Tohjo Falls": 165},

    # ================= LIGAÇÃO =================
    "Tohjo Falls": {"New Bark Town": 165, "Mt. Silver": 125, "Victory Road": 150, "Viridian City": 170},
    "Mt. Silver": {"Tohjo Falls": 125, "Victory Road": 35},
    "Victory Road": {"Mt. Silver": 35, "Tohjo Falls": 150, "Indigo Plateau": 15},
    "Indigo Plateau": {"Victory Road": 15},

    # ================= KANTO =================
    "Pallet Town": {"Viridian City": 65, "Cinnabar Island": 40},
    "Viridian City": {"Pallet Town": 65, "Tohjo Falls": 170, "Viridian Forest": 25},
    "Viridian Forest": {"Viridian City": 25, "Pewter City": 105},
    
    "Pewter City": {"Viridian Forest": 105, "Mt. Moon": 28},
    "Mt. Moon": {"Pewter City": 28, "Cerulean City": 60},
    "Cerulean City": {"Mt. Moon": 60, "Rock Tunnel": 40, "Saffron City": 105},
    "Rock Tunnel": {"Cerulean City": 40, "Lavender Town": 30},
    
    "Lavender Town": {"Rock Tunnel": 30, "Saffron City": 105, "Vermillion City": 135, "Fuchsia City": 170},
    "Saffron City": {"Cerulean City": 105, "Lavender Town": 105, "Celadon City": 9, "Vermillion City": 35},
    "Celadon City": {"Saffron City": 9, "Fuchsia City": 110},
    "Vermillion City": {"Saffron City": 35, "Lavender Town": 135, "Fuchsia City": 90},
    
    "Fuchsia City": {"Celadon City": 110, "Vermillion City": 90, "Lavender Town": 170, "Seafoam Islands": 50},
    "Seafoam Islands": {"Fuchsia City": 50, "Cinnabar Island": 30},
    "Cinnabar Island": {"Seafoam Islands": 30, "Pallet Town": 40}
}


# =====================================================================
# 3. VALIDAÇÃO DOS MAPAS
# Antes isto rodava (e imprimia) a cada "import mapas" e só checava o
# MAPA_GRANDE, com a mensagem de sucesso escrita à mão. Agora é uma função,
# vale para qualquer mapa e é chamada pelos testes e por `python mapas.py`.
# =====================================================================
def validar_mapa(mapa):
    """Retorna a lista de problemas do mapa (vazia se estiver íntegro).

    Verifica: (1) fechamento - todo vizinho é também um nó do mapa;
    (2) simetria - A->B e B->A têm o mesmo custo; (3) custos positivos;
    (4) todo nó possui coordenada em COORD (exigida pela heurística).
    """
    problemas = []
    for cidade, vizinhos in mapa.items():
        if cidade not in COORD:
            problemas.append(f"{cidade}: sem coordenada em COORD")
        for vizinho, distancia in vizinhos.items():
            if vizinho not in mapa:
                problemas.append(f"{cidade}->{vizinho}: vizinho não existe como nó do mapa")
            elif mapa[vizinho].get(cidade) != distancia:
                problemas.append(f"{cidade}<->{vizinho}: assimetria de distância")
            if distancia <= 0:
                problemas.append(f"{cidade}->{vizinho}: custo não positivo ({distancia})")
    return problemas


def resumo_mapa(mapa):
    """(nº de nós, nº de estradas não direcionadas)."""
    return len(mapa), sum(len(v) for v in mapa.values()) // 2


if __name__ == "__main__":
    for nome, m in [("Pequeno", MAPA_PEQUENO), ("Médio", MAPA_MEDIO), ("Grande", MAPA_GRANDE)]:
        nos, estradas = resumo_mapa(m)
        problemas = validar_mapa(m)
        status = "íntegro" if not problemas else f"{len(problemas)} problema(s)"
        print(f"Mapa {nome}: {nos} nós, {estradas} estradas -> {status}")
        for p in problemas:
            print("  --", p)
