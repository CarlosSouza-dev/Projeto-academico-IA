#!/usr/bin/env bash
# Cria labels, milestones e issues do projeto. Requer: gh auth login
# Rode DENTRO do clone do repositório. Gerado a partir de ISSUES.md; pode rodar de novo
# para labels/milestones (idempotente), mas as issues seriam duplicadas: rode uma vez só.
set -euo pipefail

gh label create fase-1 --color 0E8A16 --force >/dev/null
gh label create fase-2 --color 1D76DB --force >/dev/null
gh label create fase-3 --color 5319E7 --force >/dev/null
gh label create bug --color D73A4A --force >/dev/null
gh label create dados --color FBCA04 --force >/dev/null
gh label create modelo --color C5DEF5 --force >/dev/null
gh label create busca --color BFD4F2 --force >/dev/null
gh label create docs --color 0075CA --force >/dev/null
gh label create infra --color 6B7280 --force >/dev/null
gh label create bonus --color F9D0C4 --force >/dev/null
gh label create prioridade-alta --color B60205 --force >/dev/null

gh api repos/{owner}/{repo}/milestones -f title='Fase 2 - Aprendizado (entrega 11/11)' -f due_on=2026-11-11T22:00:00Z >/dev/null 2>&1 || echo "milestone ja existe: Fase 2 - Aprendizado (entrega 11/11)"
gh api repos/{owner}/{repo}/milestones -f title='Fase 3 - Agente com LLM (entrega 11/11)' -f due_on=2026-11-11T22:00:00Z >/dev/null 2>&1 || echo "milestone ja existe: Fase 3 - Agente com LLM (entrega 11/11)"
gh api repos/{owner}/{repo}/milestones -f title='Entrega e documentação (11/11)' -f due_on=2026-11-11T22:00:00Z >/dev/null 2>&1 || echo "milestone ja existe: Entrega e documentação (11/11)"

echo 'Criando issue 1/20'
gh issue create --title '[Fase 2] Pré-processar o dataset de trechos (faltantes, codificação, normalização)' --label fase-2,dados,prioridade-alta --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
`trechos.gerar_dataset_sintetico()` já gera o CSV (`python src/trechos.py`), mas o PDF exige pré-processamento **documentado**: tratamento de faltantes, codificação de variáveis e normalização.

## Tarefas
- [ ] Injetar uma pequena fração de valores faltantes controlada (ex.: 2% em `lombadas`/`semaforos`) para ter o que tratar, e documentar a estratégia (mediana/moda ou remoção)
- [ ] Codificar `tipo_via` (one-hot) e `hora` (sugestão: `sin`/`cos` de `2π·hora/24`, pois 23h e 0h são vizinhas)
- [ ] Normalizar variáveis numéricas (necessário para k-NN) usando `Pipeline`/`ColumnTransformer` do scikit-learn, ajustado **só no treino**
- [ ] Registrar no relatório as premissas do gerador (regras de `gerar_trechos`, parâmetros de `tempo_trecho`, nível de ruído)

## Critério de aceite
- Função/pipeline reutilizável que transforma o CSV bruto em matriz de features
- Nenhum ajuste (fit) de normalização usa dados de teste

## Referência
Projeto_Academico_IA_20262.pdf, seção 3.2
CORPO_DA_ISSUE

echo 'Criando issue 2/20'
gh issue create --title '[Fase 2] Treinar e comparar pelo menos dois modelos de previsão de tempo' --label fase-2,modelo,prioridade-alta --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
O agente da Fase 2 não recebe o custo pronto: ele **aprende** o tempo de cada trecho. Hoje `tempo_trecho` é o simulador (a 'verdade'); falta o modelo aprendido.

## Tarefas
- [ ] Treinar ao menos 2 modelos vistos na disciplina (ex.: k-NN, regressão linear/Ridge, árvore de decisão, floresta aleatória)
- [ ] Comparar com um baseline trivial (ex.: prever `distancia/velocidade média`)
- [ ] Salvar o melhor modelo (joblib) para uso na busca
- [ ] Dica: use `GroupKFold` agrupando por trecho. Com `KFold` comum, linhas do mesmo trecho caem em treino e teste e o erro fica otimista demais

## Critério de aceite
- Tabela comparando os modelos com a mesma validação
- Justificativa da escolha do modelo final

## Referência
Projeto_Academico_IA_20262.pdf, seção 3.2
CORPO_DA_ISSUE

echo 'Criando issue 3/20'
gh issue create --title '[Fase 2] Avaliar com MAE/RMSE, validação cruzada e análise honesta dos erros' --label fase-2,modelo,docs --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
O PDF pede métricas para valor contínuo, validação cruzada e uma análise de **onde o modelo erra mais**.

## Tarefas
- [ ] Calcular MAE, RMSE e R² por validação cruzada (média ± desvio)
- [ ] Quebrar o erro por: tipo de via, presença de acidente, faixa de horário (pico x madrugada), trechos longos x curtos
- [ ] Gráfico de previsto x real e de resíduos
- [ ] Texto de 1 parágrafo no relatório com os piores casos e a hipótese do porquê

## Critério de aceite
- Tabela e gráficos prontos para o relatório
- Análise cita números reais, não impressões

## Referência
Projeto_Academico_IA_20262.pdf, seção 3.2
CORPO_DA_ISSUE

echo 'Criando issue 4/20'
gh issue create --title '[Fase 2] Integrar o modelo aprendido à busca A* (custo = tempo previsto)' --label fase-2,busca,modelo,prioridade-alta --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
`trechos.montar_grafo_tempo(mapa, hora, acidentes, prever=...)` já aceita um preditor. Falta ligar o modelo treinado e garantir que a heurística continue válida.

## Tarefas
- [ ] Criar `prever(trecho, hora, acidente) -> minutos` que carrega o modelo e monta as features
- [ ] Prever em lote (45 trechos) em vez de uma chamada por aresta, para não pesar no benchmark
- [ ] Garantir previsão > 0 (`max(ε, y)`), senão a calibração da HDD e o A* quebram
- [ ] A escala da HDD é calibrada no grafo previsto (`calibrar_escala_heuristica`): confirmar com teste que A* == UCS em todos os pares usando o grafo do modelo
- [ ] Rodar o experimento 'rota curta x rota rápida' (`main.executar_fase2`) com o modelo aprendido e comparar com o simulador

## Critério de aceite
- Mesmo `a_estrela` da Fase 1, sem alterar o laço de busca
- Teste automatizado de otimalidade com o grafo previsto

## Referência
Projeto_Academico_IA_20262.pdf, seção 3.2: 'o elo entre as duas primeiras fases'
CORPO_DA_ISSUE

echo 'Criando issue 5/20'
gh issue create --title '[Fase 2] Custo dependente do horário de chegada em cada trecho (time-dependent)' --label fase-2,busca --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
Hoje a hora é uma **foto**: o grafo todo usa a hora de saída. Em rotas de 1000+ minutos isso é irreal (sai às 8h, mas o trecho final é percorrido às 20h).

## Tarefas
- [ ] Fazer o custo da aresta depender de `hora_saida + g(n)` (g em minutos)
- [ ] Verificar a propriedade FIFO (sair depois nunca chega antes) e que a heurística calibrada com o **menor** tempo possível de cada trecho segue admissível
- [ ] Atualizar testes de otimalidade (comparar com UCS time-dependent)

## Critério de aceite
- Rota muda conforme a hora de saída ao longo da viagem
- Decisão documentada: manter a foto (simples) ou time-dependent (realista)
CORPO_DA_ISSUE

echo 'Criando issue 6/20'
gh issue create --title '[Fase 2] Acidentes dinâmicos: aparecem, desaparecem e podem bloquear a via' --label fase-2,busca --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
O PDF diz que acidentes 'aparecem e desaparecem'. Hoje o acidente é um parâmetro fixo da chamada, com atraso constante de 20 min.

## Tarefas
- [ ] Sortear acidentes por cenário com semente (probabilidade por trecho)
- [ ] Opção de bloqueio total (aresta removida) além do atraso
- [ ] Tratar destino inalcançável após bloqueios (o A* já devolve `None`; falta o agente reagir)
- [ ] Replanejar a rota quando um acidente surge no meio da viagem

## Critério de aceite
- Cenários reproduzíveis com semente
- Teste com bloqueio que isola o destino
CORPO_DA_ISSUE

echo 'Criando issue 7/20'
gh issue create --title '[Fase 2] Calibrar a escala do mundo (km/min) e revisar parâmetros do simulador' --label fase-2,dados --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
As distâncias do mapa vêm do jogo e viraram 'km'; um trecho de 170 km a 80 km/h já é 2h. A rota Cianwood→Lavender dá ~32 h às 18h, o que é pouco crível para entregas.

## Tarefas
- [ ] Escolher e documentar uma escala (ex.: dividir distâncias por 5) ou aceitar a escala atual com justificativa
- [ ] Revisar `VELOCIDADE_KMH`, `MIN_POR_LOMBADA`, `ESPERA_SEMAFORO_MIN`, `PENALIDADE_ACIDENTE_MIN` e a curva `fator_transito`
- [ ] Mover os parâmetros para um bloco de configuração único e citá-lo no relatório

## Critério de aceite
- Parâmetros em um só lugar, cada um com justificativa de uma linha
CORPO_DA_ISSUE

echo 'Criando issue 8/20'
gh issue create --title '[Busca] Tornar a heurística mais informativa (coordenadas proporcionais às distâncias)' --label fase-1,busca --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
A HDD agora é correta (admissível/consistente, escala calibrada), porém **fraca**: as coordenadas de `COORD` são esquemáticas (razão custo/pixel de 0,09 a 3,3), então a escala segura é 0,09 e h vale em média ~11% do custo real. Por isso A* expande quase os mesmos nós que o UCS. Um experimento com MDS (embedding das distâncias de menor caminho) subiu isso para ~57% e reduziu 3-4 nós por busca.

## Tarefas
- [ ] Opção A: manter `COORD` só para desenhar e criar `COORD_HEURISTICA` (MDS sobre a matriz de menor caminho)
- [ ] Opção B: reposicionar à mão as cidades com razão custo/pixel destoante (ex.: Celadon–Saffron, Victory Road–Indigo Plateau)
- [ ] Medir nós expandidos antes/depois e registrar no relatório
- [ ] Lembrar: o grafo é quase um corredor (45 estradas para 36 cidades); mesmo uma heurística perfeita só poda ramos sem saída

## Critério de aceite
- `test_hdd_*` continuam passando
- Tabela antes x depois de nós expandidos
CORPO_DA_ISSUE

echo 'Criando issue 9/20'
gh issue create --title '[Mapas] Decidir o tamanho do Mapa Médio (comentário dizia 21 nós, o mapa tem 18)' --label bug,dados --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
O comentário de `MAPA_MEDIO` dizia 21 nós, mas o dicionário tem 18. Além disso, `New Bark Town` apontava para `Tohjo Falls`, que não existe nesse mapa (gerava `KeyError`). A aresta foi removida e o comentário corrigido, mas talvez a intenção fosse incluir mais cidades.

## Tarefas
- [ ] Confirmar com o grupo: ficar com 18 nós ou incluir Tohjo Falls/Mt. Silver/Victory Road
- [ ] Se mudar, atualizar o relatório do Marco 1 e os testes

## Critério de aceite
- `python src/mapas.py` reporta os três mapas como íntegros
CORPO_DA_ISSUE

echo 'Criando issue 10/20'
gh issue create --title '[Experimento] Revisar pares origem/destino e a medição de tempo do benchmark' --label fase-1,docs --milestone 'Fase 2 - Aprendizado (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
Com a mesma origem/destino nos três mapas, Médio e Grande davam resultado idêntico (o Grande nunca chegava em Kanto). Foi adicionado o cenário `Grande (Johto-Kanto)` e o tempo passou a ser a mediana de 30 execuções. Falta consolidar no relatório.

## Tarefas
- [ ] Decidir se o Marco 1 já entregue será refeito com o novo cenário ou só citado como correção
- [ ] Rodar o benchmark com vários pares aleatórios (semente fixa) e reportar média de nós expandidos de UCS x A*
- [ ] Explicar no relatório por que A* pode ser mais lento em ms em grafos tão pequenos (custo da heurística)

## Critério de aceite
- Seção de resultados do relatório coerente com `outputs/csv/benchmark_resultados.csv`
CORPO_DA_ISSUE

echo 'Criando issue 11/20'
gh issue create --title '[Fase 3] Núcleo do agente com LLM e saída estruturada (tool calling)' --label fase-3,prioridade-alta --milestone 'Fase 3 - Agente com LLM (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
O LLM **não calcula a rota**: interpreta o pedido, escolhe a ferramenta e os argumentos, e explica o resultado.

## Tarefas
- [ ] Escolher o provedor/modelo e definir o contrato JSON da chamada (`origem`, `destino`, `hora`, `acidentes`/restrições)
- [ ] Prompts versionados em arquivos (`prompts/v1.md`, ...)
- [ ] Validar a saída do LLM (cidade existe em `MAPA_GRANDE`? hora válida?) antes de chamar a busca
- [ ] Chave de API só por variável de ambiente / Colab Secrets (o `.gitignore` já ignora `.env`)

## Critério de aceite
- Pedido em português -> chamada de ferramenta válida
- Nenhuma chave no repositório

## Referência
Projeto_Academico_IA_20262.pdf, seção 3.3
CORPO_DA_ISSUE

echo 'Criando issue 12/20'
gh issue create --title '[Fase 3] Expor as ferramentas ao LLM: buscar_rota e estimar_tempo_trecho' --label fase-3,busca --milestone 'Fase 3 - Agente com LLM (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
As funções já existem; falta empacotá-las como ferramentas com descrição e schema.

## Tarefas
- [ ] `buscar_rota(origem, destino, hora, acidentes)` -> caminho, tempo previsto, nós expandidos, comparação com a rota mais curta
- [ ] `estimar_tempo_trecho(a, b, hora)` -> minutos previstos pelo modelo da Fase 2
- [ ] Retornos em JSON e erros claros (cidade inexistente, destino inalcançável) para o LLM explicar ao usuário

## Critério de aceite
- O LLM obtém a rota da ferramenta, nunca a inventa

## Referência
Projeto_Academico_IA_20262.pdf, seção 3.3
CORPO_DA_ISSUE

echo 'Criando issue 13/20'
gh issue create --title '[Fase 3] Montar 15+ pedidos de teste e medir acerto do agente' --label fase-3,docs --milestone 'Fase 3 - Agente com LLM (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
O PDF exige um conjunto de pelo menos 15 pedidos em linguagem natural com resultado esperado.

## Tarefas
- [ ] Escrever 15+ pedidos variados: horário explícito, 'agora', evitar trecho com acidente, cidade com apelido/erro de digitação, pedido ambíguo, pedido fora de escopo
- [ ] Definir o resultado esperado de cada um (ferramenta, argumentos, rota)
- [ ] Script que roda todos, registra acertos e falhas, e salva CSV
- [ ] Analisar os casos de falha

## Critério de aceite
- Taxa de acerto reportada (ferramenta correta + rota válida)
- Análise dos erros no relatório

## Referência
Projeto_Academico_IA_20262.pdf, seção 3.3
CORPO_DA_ISSUE

echo 'Criando issue 14/20'
gh issue create --title '[Fase 3] IA responsável: alucinação, custo, latência, LGPD e pedidos fora de escopo' --label fase-3,docs --milestone 'Fase 3 - Agente com LLM (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
Seção obrigatória do relatório (4–8 páginas).

## Tarefas
- [ ] Medir custo (tokens) e latência por chamada
- [ ] Mostrar um caso em que o LLM alucina (ex.: cidade inexistente) e como a validação barra
- [ ] Testar pedido fora de escopo e o comportamento do agente
- [ ] Discutir viés dos dados sintéticos e LGPD (dados são fictícios; o que mudaria com endereços reais)
- [ ] Declaração de uso de IA generativa no desenvolvimento

## Critério de aceite
- Seção pronta no relatório com números medidos

## Referência
Projeto_Academico_IA_20262.pdf, seções 3.3 e 5.2
CORPO_DA_ISSUE

echo 'Criando issue 15/20'
gh issue create --title '[Bônus] Interface de conversa ou comparação entre dois LLMs' --label fase-3,bonus --milestone 'Fase 3 - Agente com LLM (entrega 11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
Vale até +0,5 na A2: chat em texto com o agente **ou** comparar dois LLMs orquestrando as mesmas ferramentas no mesmo conjunto de pedidos.

## Tarefas
- [ ] Escolher uma das duas opções depois que o núcleo estiver estável
- [ ] Se for comparação: reutilizar o conjunto de 15+ pedidos e reportar acerto, custo e latência de cada modelo

## Critério de aceite
- Só começar após o núcleo da Fase 3 funcionar

## Referência
Projeto_Academico_IA_20262.pdf, seção 5.2
CORPO_DA_ISSUE

echo 'Criando issue 16/20'
gh issue create --title '[Entrega] Notebook no Google Colab que roda do início ao fim em sessão nova' --label infra,prioridade-alta --milestone 'Entrega e documentação (11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
O ambiente oficial é o Colab. O código hoje está em `src/*.py`; precisa rodar integrado, sem chave no código.

## Tarefas
- [ ] Notebook que clona o repo (ou carrega os `.py`), instala dependências e executa Fase 1, 2 e 3
- [ ] Chaves via `userdata.get(...)` do Colab
- [ ] Testar em sessão nova (Runtime > Restart) antes da apresentação; link com permissão de leitura para o professor
- [ ] Mostrar ao vivo: busca achando a rota, modelo de custo mudando a decisão, LLM explicando

## Critério de aceite
- Executa do início ao fim sem erro
- Nenhuma chave escrita

## Referência
Projeto_Academico_IA_20262.pdf, seções 5.3 e 10
CORPO_DA_ISSUE

echo 'Criando issue 17/20'
gh issue create --title '[Entrega] Relatório de 4 a 8 páginas, arquivo AUTORES e declaração de uso de IA' --label docs --milestone 'Entrega e documentação (11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
Entrega no Google Sala de Aula até 19h de 11/11: link do notebook, relatório em PDF e `AUTORES` com a fase de cada integrante.

## Tarefas
- [ ] Estrutura: modelagem, dados, modelos e métricas, integração com a busca, agente LLM, IA responsável
- [ ] Incluir as tabelas e gráficos de `outputs/`
- [ ] Arquivo `AUTORES` declarando a fase de cada integrante
- [ ] Declaração de uso de ferramentas de IA generativa

## Critério de aceite
- PDF dentro de 4–8 páginas
- Prazo: 11/11/2026, 19h

## Referência
Projeto_Academico_IA_20262.pdf, seções 5.2 e 5.3
CORPO_DA_ISSUE

echo 'Criando issue 18/20'
gh issue create --title '[Infra] Rodar os testes automaticamente no GitHub Actions' --label infra --milestone 'Entrega e documentação (11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
`python -m unittest discover -s src` roda em ~1 s e cobre otimalidade do A*, consistência da HDD e o modelo de custos.

## Tarefas
- [ ] Workflow `.github/workflows/tests.yml` com Python 3.11+ rodando os testes a cada push/PR
- [ ] Instalar dependências a partir do `requirements.txt`
- [ ] Proteger a branch `main` exigindo o check verde

## Critério de aceite
- Badge de status no README
CORPO_DA_ISSUE

echo 'Criando issue 19/20'
gh issue create --title '[Equipe] Preparar a arguição cruzada (cada um defende a fase de outro)' --label docs,prioridade-alta --milestone 'Entrega e documentação (11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
Na arguição, cada integrante responde sobre a fase de **outro** colega, sem consulta a colegas ou IA. Seminário em 18/11 ou 25/11; mentoria dia 28/10.

## Tarefas
- [ ] Cada responsável escreve uma 'cola' de 1 página da própria fase para os outros dois
- [ ] Perguntas-treino: por que a HDD é admissível? Por que `GroupKFold`? Como o LLM decide qual ferramenta chamar? Por que a escala da heurística é calibrada e não fixa?
- [ ] Ensaiar a demonstração ao vivo (~9 min) com cronômetro
- [ ] Levar dúvidas à mentoria de 28/10

## Critério de aceite
- Os três conseguem explicar as três fases

## Referência
Projeto_Academico_IA_20262.pdf, seção 7
CORPO_DA_ISSUE

echo 'Criando issue 20/20'
gh issue create --title '[Infra] Atualizar README e estrutura do repositório' --label infra,docs --milestone 'Entrega e documentação (11/11)' --body-file - <<'CORPO_DA_ISSUE'
## Contexto
Organizar o repositório para quem for avaliar.

## Tarefas
- [ ] Conferir se o README reflete os comandos atuais
- [ ] Decidir se `outputs/` vai versionado ou no `.gitignore`
- [ ] Adicionar `LICENSE` e `AUTORES`

## Critério de aceite
- Alguém de fora consegue rodar o projeto só com o README
CORPO_DA_ISSUE
