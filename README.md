# 🎮 Data Quest 8-bit

> Aprenda os fundamentos da **Análise de Dados** jogando! Um jogo educativo em estilo 8 bits, feito em Python, para quem está começando do zero.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)
![Dependências](https://img.shields.io/badge/depend%C3%AAncias-nenhuma-brightgreen)

<!--
👉 ADICIONE UM PRINT OU GIF DO JOGO AQUI (recomendado!):
1. Crie a pasta "docs" e salve a imagem como docs/screenshot.png
2. Troque esta linha de comentário por:  ![Captura de tela](docs/screenshot.png)
-->

## 📖 Sobre o projeto

O **Data Quest 8-bit** transforma o estudo de análise de dados em uma aventura. Você controla um personagem pixelado pela **Vila dos Dados**, conversa com mestres, coleta itens, foge de bugs 🐛 e enfrenta desafios para liberar as próximas fases.

**Intenção:** tornar o aprendizado de dados mais leve, interativo e motivador, usando elementos de gamificação (XP, vidas, patentes, fases e bônus de curiosidade) e, ao mesmo tempo, praticar lógica de programação e design de conteúdo educativo.

Foi pensado para **iniciantes**: a linguagem é simples e o código Python aparece de forma gradual, sem exigir que a pessoa digite código

## 🚀 Como rodar

**Requisitos:** Python 3.8+ com `tkinter`. Não há nenhuma biblioteca para instalar.

```bash
git clone https://github.com/SEU-USUARIO/data-quest-8bit.git
cd data-quest-8bit
python data_quest_8bit.py
```

- **Windows / macOS:** o `tkinter` já vem no instalador do [python.org](https://www.python.org/downloads/).
- **Linux (Debian/Ubuntu):** `sudo apt install python3-tk`

## 🕹️ Comandos

| Tecla | Ação |
|---|---|
| Setas ou `W` `A` `S` `D` | Mover o personagem |
| `E`, `Espaço` ou `Enter` | Falar com personagens / confirmar |
| `R` | Rever a aula da fase |
| `H` | Pedir dica no desafio (custa 3 XP) |
| `M` | Liga/desliga o som (Windows) |
| `Esc` | Pausa |

## 🗺️ As 8 fases

| # | Fase | O que você aprende | Missão de coleta |
|---|---|---|---|
| 1 | O Ciclo do Analista | Etapas do trabalho e tipos de análise | Coletar as 6 etapas na ordem certa |
| 2 | Conhecendo os Dados | Linhas, colunas e tipos de variáveis | Coletar só colunas numéricas |
| 3 | Estatística Descritiva | Média, mediana, moda, amplitude e outliers | Coletar os números de uma série (o painel soma) |
| 4 | Limpeza de Dados | Nulos, duplicados e valores absurdos | Coletar só os dados "sujos" |
| 5 | Python: o Superpoder | `len`, `sum`, `max`, `min`, listas e dicionários | Coletar as funções reais do Python |
| 6 | Filtrar e Agrupar | Filtros e agrupamentos (ideia de `WHERE` e `GROUP BY`) | Coletar só produtos do Sul |
| 7 | Visualização de Dados | Escolha do gráfico certo e gráficos honestos | Coletar os gráficos adequados |
| 8 | **Chefão: Projeto Final** | Ticket médio, participação %, conclusões e comunicação | Coletar as 4 pistas do projeto na ordem |

Ao concluir cada fase você ganha **XP extra** e uma **curiosidade** sobre a área. No final, recebe um diploma. 🎓

### Regras do jogo

- **Aprovação:** 70% de acertos no desafio do Guardião.
- **XP:** 10 por acerto na 1ª tentativa, 5 na 2ª, bônus de `20 + 5 × nº da fase` ao concluir. Dica custa 3 XP.
- **Vidas:** 3 corações por fase. Bugs e itens errados tiram um coração. Se zerar, a missão recomeça.
- **Progresso:** salvo automaticamente em `progresso_dataquest8bit.json` (ignorado pelo Git).
- Nas fases de Python, o jogo **executa de verdade** o código da resposta correta e mostra o resultado.

## 🛠️ Tecnologias e conceitos

- **Python 3** (somente biblioteca padrão)
- **Tkinter / Canvas** para a interface gráfica
- **Pixel art desenhada em código:** sprites de 8×8 definidos como texto e ampliados com `PhotoImage.zoom`
- **Game loop** a ~30 FPS, movimentação com detecção de colisão por tiles
- **Máquina de estados simples** para cenas (título, vila, fase, diploma) e overlays (diálogo, quiz, pausa)
- **Persistência** de progresso em JSON
- **Execução controlada de código** (`exec` com `builtins` restritos) para mostrar o resultado das respostas de Python

## 📂 Estrutura

```
data-quest-8bit/
├── data_quest_8bit.py        # o jogo (versão gráfica 8 bits)
├── versao_terminal/
│   └── data_quest.py         # versão alternativa, só no terminal
├── tests/
│   └── test_simulacao.py     # joga as 8 fases por código, sem abrir janela
├── .github/workflows/ci.yml  # roda os testes no GitHub Actions
├── LICENSE
└── README.md
```

No arquivo principal: `NIVEIS` (conteúdo das fases), `Assets` (sprites) e `Jogo` (lógica, atualização e desenho).

## ➕ Como adicionar ou editar uma fase

Todo o conteúdo fica na lista `NIVEIS` em `data_quest_8bit.py`. Cada fase é um dicionário:

```python
{"nome": "Título da fase",
 "missao": "Texto curto da missão (aparece no painel)",
 "mestre": ["página 1 da aula", "página 2 da aula"],
 "coleta": {"ordenada": False, "bugs": 2, "vel": 2,
            "itens": [("rótulo", True, ""),                    # item certo
                      ("outro", False, "por que está errado")]},  # item errado
 "quiz": [
     mc("Pergunta?", ["A", "B", "C", "D"], 1, "explicação", dica="opcional"),
     num("Quanto é 2 + 2?", 4, "explicação", tol=0.01),
 ],
 "cur": "Curiosidade exibida como bônus ao concluir a fase."}
```

- `mc(...)` cria uma pergunta de múltipla escolha. Passe `run="resultado = ..."` para mostrar o código Python sendo executado (a lista `vendas` está disponível).
- Para ter mais de 8 fases, adicione também uma coluna livre em `HUB_DOORS`.

## ✅ Testes

O projeto inclui uma simulação que joga todas as fases sem precisar de tela:

```bash
python tests/test_simulacao.py
```

Ela substitui o `tkinter` por uma versão falsa e verifica: entrada nas portas, portas trancadas, aulas, coleta, dano, game over, quiz aprovado e reprovado, salvamento e diploma.

## 🗺️ Ideias para o futuro

- [ ] Fases com `pandas` e `matplotlib`
- [ ] Fase de SQL
- [ ] Desafios em que o jogador digita o próprio código
- [ ] Mais datasets e mais perguntas por fase
- [ ] Efeitos sonoros e música multiplataforma
- [ ] Empacotar como executável (`.exe`)

## 🤝 Contribuindo

Sugestões, correções de conteúdo e novas fases são bem-vindas! Abra uma *issue* ou um *pull request*.

## 🤖 Créditos

Projeto de aprendizado criado por **[NATHAN ASAFE]**, com apoio do assistente de IA **Claude (Anthropic)** no desenvolvimento do código e do conteúdo.

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
