# Projeto Acadêmico de IA — Agente de Logística no Mundo Pokémon

IESB · Ciência da Computação · Inteligência Artificial (2026/2) · Prof. Rodrigo Gonçalves

Um agente que evolui em três fases: **busca** (A*) → **custo aprendido** (tempo de viagem) → **agente com LLM**.
Cenário: entregas entre cidades de Kanto e Johto, modeladas como um grafo.

| Fase | Custo da aresta | Status |
|------|-----------------|--------|
| 1 — Busca | distância | feito (UCS x A*, 3+ mapas) |
| 2 — Aprendizado | tempo = f(lombadas, semáforos, acidente, horário, tipo de via) | simulador de custos pronto; falta o modelo aprendido ([issues](ISSUES.md)) |
| 3 — Agente com LLM | tempo previsto | a fazer |

## Como rodar
```bash
pip install -r requirements.txt
python src/main.py                        # benchmark da Fase 1 + experimento da Fase 2 -> outputs/
python src/mapas.py                       # valida os três mapas
python src/trechos.py                     # gera outputs/csv/dataset_trechos.csv (treino da Fase 2)
python -m unittest discover -s src -v     # testes
```

## Estrutura (`src/`)
- `mapas.py` — coordenadas, grafos (pequeno/médio/grande) e validação (`validar_mapa`).
- `buscas.py` — custo uniforme e A* sobre um núcleo comum; heurística de distância direta (HDD) com escala calibrada.
- `trechos.py` — características de cada trecho, horário → trânsito, `tempo_trecho`, `montar_grafo_tempo(..., prever=modelo)`, dataset sintético.
- `desenhar_mapas.py`, `tabela.py`, `graficos.py` — saídas visuais e CSV.
- `test_buscas.py` — otimalidade do A* em todos os pares, consistência da HDD, custos.

## Decisões de modelagem
- **Estado** = cidade; **ação** = ir a uma cidade vizinha; **custo** = distância (Fase 1) ou tempo em minutos (Fase 2).
- **Heurística (HDD)**: `h(n) = escala × distância em linha reta até o destino`, com
  `escala = min(custo / distância reta)` sobre todas as arestas. Pela desigualdade triangular isso garante
  `h(a) ≤ c(a,b) + h(b)` (consistente, logo admissível), para distância ou para tempo.
- **Tempo do trecho** (min): `deslocamento × (1 + sens_via × (fator_horário − 1)) + lombadas×0,25 + semáforos×0,7×fator_horário + acidente×20`.
- O horário é uma "foto" (hora de saída para todo o trajeto); ver issue sobre custo dependente do horário de chegada.

Tarefas e prazos: [ISSUES.md](ISSUES.md).
