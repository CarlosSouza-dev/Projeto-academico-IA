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

# 2.2 Mapa Médio - Região de Johto (21 nós)
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
    "New Bark Town": {"Cherrygrove City": 75, "Blackthorn City": 105, "Tohjo Falls": 165}
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

print("Cidades no mapa:", len(MAPA_GRANDE))
print("Estradas no mapa:", sum(len(v) for v in MAPA_GRANDE.values()) // 2)

# Verificação de SIMETRIA e FECHAMENTO
problemas = []

for cidade, vizinhos in  MAPA_GRANDE.items():
    for vizinho, distancia in vizinhos.items():

        #Verificação 1: FECHAMENTO

        if vizinho not in MAPA_GRANDE:
            problemas.append(f"{vizinho} aparece como vizinha mas não existe nas cidades principais.")

        # Verificação 2: SIMETRIA

        elif MAPA_GRANDE[vizinho].get(cidade) != distancia:
            problemas.append(f"{cidade}-{vizinho}: assimetria de distância")

if problemas:
    print("Problemas encontrados:")
    for p in problemas:
        print("-- ", p)
else:
    print("Mapa íntegro: 36 cidades, 45 estradas, todas simétricas.")