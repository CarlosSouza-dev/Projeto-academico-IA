import os

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from mapas import COORD

# Removidos: `from adjustText import adjust_text`, `import math` e a lista
# `textos`. Nada disso era usado, e o adjustText é uma dependência externa que
# derrubava o programa inteiro (ModuleNotFoundError) em quem não o tinha.

VERMELHO_IESB = "#C8102E"
GRAFITE = "#1F2933"

# correções manuais para evitar sobreposição de rótulos em cidades específicas
CORRECOES = {
    "Safari Zone": (-15, 0, "right"),
    "Cianwood City": (0, -15, "center"),
    "National Park": (15, 0, "left"),
    "Ecruteak City": (0, -15, "center"),
    "Mt. Mortar": (0, 15, "center"),
    "Ilex Forest": (0, -15, "center"),
    "Union Cave": (0, -15, "center"),
    "Mahogany Town": (0, -15, "center"),
    "Tohjo Falls": (0, -15, "center"),
    "Blackthorn City": (0, -15, "left"),
    "Cinnabar Island": (-15, 0, "right"),
    "Seafoam Islands": (0, -15, "center"),
    "Mt. Silver": (-15, 0, "right"),
    "Victory Road": (15, 0, "left"),
}


def desenhar_mapa(
    mapa,
    caminho=None,
    expandidos=None,
    titulo=None,
    salvar_em=None,
    nome_arquivo="mapa_solucao.png",
):
    """Desenha o mapa e salva o resultado visual na pasta especificada.

    `mapa` é o grafo cujos custos aparecem nas arestas da rota: distância na
    Fase 1, minutos na Fase 2 (passe o grafo de tempo para ver os minutos).
    Cidades expandidas levam a ordem de expansão; o destino é marcado com "D".
    """
    if titulo is None:
        titulo = "Visualização do Mapa"

    caminho = caminho or []
    expandidos = expandidos or []
    destino = caminho[-1] if caminho else None
    ordem_de = {cidade: i for i, cidade in enumerate(expandidos, start=1)}

    fig, ax = plt.subplots(figsize=(13, 8))

    # 1) Estradas do mapa atual em cinza claro
    ja_desenhadas = set()
    for cidade, vizinhos in mapa.items():
        for vizinho in vizinhos:
            par = tuple(sorted([cidade, vizinho]))
            if par in ja_desenhadas:
                continue
            ja_desenhadas.add(par)
            if cidade in COORD and vizinho in COORD:
                x1, y1 = COORD[cidade]
                x2, y2 = COORD[vizinho]
                ax.plot([x1, x2], [y1, y2], color="#DDE2E7", lw=1.6, zorder=1)

    # 2) Estradas do caminho-solução, com o custo de cada trecho
    for a, b in zip(caminho, caminho[1:]):
        if a in COORD and b in COORD:
            x1, y1 = COORD[a]
            x2, y2 = COORD[b]
            ax.plot([x1, x2], [y1, y2], color=VERMELHO_IESB, lw=5, alpha=0.45, zorder=2)
            custo = mapa.get(a, {}).get(b)
            ax.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                "" if custo is None else f"{custo:.0f}",
                fontsize=10,
                color=VERMELHO_IESB,
                ha="center",
                va="center",
                zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=VERMELHO_IESB),
            )

    # 3) Cidades pertencentes apenas ao mapa atual
    for cidade in mapa.keys():
        if cidade not in COORD:
            continue
        x, y = COORD[cidade]
        if cidade in ordem_de:
            ax.scatter(x, y, s=330, color=VERMELHO_IESB, zorder=3)
            ax.text(x, y, str(ordem_de[cidade]), fontsize=10, color="white",
                    ha="center", va="center", fontweight="bold", zorder=4)
        elif cidade == destino:
            # O destino é desempilhado mas não expandido: antes ele aparecia
            # como um ponto branco comum, igual a uma cidade nunca visitada.
            ax.scatter(x, y, s=330, color=GRAFITE, zorder=3)
            ax.text(x, y, "D", fontsize=10, color="white",
                    ha="center", va="center", fontweight="bold", zorder=4)
        else:
            ax.scatter(x, y, s=90, color="white", edgecolors=GRAFITE, linewidths=1.4, zorder=3)

        destaque = cidade in caminho or cidade in ordem_de
        dx, dy, ha = CORRECOES.get(cidade, (0, 15, "center"))

        ax.text(
            x + dx,
            y - dy,  # eixo Y invertido (abaixo): dy positivo continua "para cima"
            cidade,
            fontsize=9.5 if destaque else 8.5,
            color=GRAFITE if destaque else "#8A94A0",
            ha=ha,
            fontweight="bold" if destaque else "normal",
            zorder=6,
        )

    ax.legend(
        handles=[
            Line2D([], [], marker="o", ls="", color=VERMELHO_IESB, markersize=11,
                   label="Expandida (nº = ordem)"),
            Line2D([], [], marker="o", ls="", color=GRAFITE, markersize=11, label="Destino (D)"),
            Line2D([], [], color=VERMELHO_IESB, lw=5, alpha=0.45, label="Rota encontrada"),
        ],
        loc="lower left", frameon=False, fontsize=9,
    )

    # CORREÇÃO: COORD usa Y crescendo para baixo (como diz mapas.py), mas o
    # matplotlib cresce para cima, então o mapa saía espelhado na vertical
    # (Pewter embaixo, Cinnabar em cima). Inverte o eixo para ficar como o mapa real.
    ax.invert_yaxis()
    ax.set_title(titulo, fontsize=15, fontweight="bold", loc="left")
    ax.axis("off")
    plt.tight_layout()

    # Salva na pasta especificada em vez de travar a execução na tela
    if salvar_em:
        os.makedirs(salvar_em, exist_ok=True)
        caminho_final = os.path.join(salvar_em, nome_arquivo)
        plt.savefig(caminho_final, dpi=300)
        plt.close()
        print(f"Mapa visual '{caminho_final}' gerado com sucesso!")
    else:
        plt.show()
        plt.close()
