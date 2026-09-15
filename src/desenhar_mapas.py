import os
import math
import matplotlib.pyplot as plt
from adjustText import adjust_text
from mapas import COORD

VERMELHO_IESB = "#C8102E"

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
    """Desenha o mapa e salva o resultado visual na pasta especificada."""
    if titulo is None:
        titulo = "Visualização do Mapa"

    caminho = caminho or []
    expandidos = expandidos or []

    fig, ax = plt.subplots(figsize=(13, 8))
    textos = []  # Lista para armazenar os objetos de texto para ajuste posterior

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

    # 2) Estradas do caminho-solução
    for a, b in zip(caminho, caminho[1:]):
        if a in COORD and b in COORD:
            x1, y1 = COORD[a]
            x2, y2 = COORD[b]
            ax.plot(
                [x1, x2],
                [y1, y2],
                color=VERMELHO_IESB,
                lw=5,
                alpha=0.45,
                zorder=2,
            )
            custo = mapa.get(a, {}).get(b, "")
            ax.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                str(custo),
                fontsize=10,
                color=VERMELHO_IESB,
                ha="center",
                va="center",
                zorder=5,
                bbox=dict(
                    boxstyle="round,pad=0.2", fc="white", ec=VERMELHO_IESB
                ),
            )

    # 3) Cidades pertencentes apenas ao mapa atual
    for cidade in mapa.keys():
        if cidade not in COORD:
            continue
        x, y = COORD[cidade]
        if cidade in expandidos:
            ordem = expandidos.index(cidade) + 1
            ax.scatter(x, y, s=330, color=VERMELHO_IESB, zorder=3)
            ax.text(
                x,
                y,
                str(ordem),
                fontsize=10,
                color="white",
                ha="center",
                va="center",
                fontweight="bold",
                zorder=4,
            )
        else:
            ax.scatter(
                x,
                y,
                s=90,
                color="white",
                edgecolors="#1F2933",
                linewidths=1.4,
                zorder=3,
            )

        destaque = cidade in caminho or cidade in expandidos
        dx, dy, ha = CORRECOES.get(cidade, (0, 15, "center"))

        ax.text(
            x + dx,
            y + dy,
            cidade,
            fontsize=9.5 if destaque else 8.5,
            color="#1F2933" if destaque else "#8A94A0",
            ha=ha,
            fontweight="bold" if destaque else "normal",
            zorder=6,
        )

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