#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DATA QUEST 8-BIT - A Aventura da Análise de Dados
=================================================
Como rodar:  python data_quest_8bit.py
Precisa só do Python 3.8+ com tkinter (já vem no instalador do python.org
para Windows/Mac. No Linux: sudo apt install python3-tk).

COMANDOS
  SETAS ou WASD ..... mover o personagem
  E / ESPAÇO / ENTER  falar com personagens e confirmar
  R ................. rever a aula da fase
  H ................. pedir dica no desafio (custa 3 XP)
  M ................. liga/desliga o som (Windows)
  ESC ............... pausa
"""
import builtins
import copy
import json
import math
import os
import random
import statistics
import textwrap
import threading
import traceback
import tkinter as tk

try:
    import winsound  # só existe no Windows
except ImportError:
    winsound = None

# ───────────────────────────── CONSTANTES ─────────────────────────────
PX = 4                      # cada "pixel" do sprite vira 4x4 na tela
TILE = 8 * PX               # 32 px
COLS, ROWS = 20, 12
HUD_TOP, HUD_BOT = 40, 56
W = COLS * TILE             # 640
H = HUD_TOP + ROWS * TILE + HUD_BOT  # 480
OY = HUD_TOP                # deslocamento vertical do mapa
FPS_MS = 33

FONT = ("Courier", 11, "bold")
FONT_S = ("Courier", 9, "bold")
FONT_B = ("Courier", 13, "bold")
FONT_T = ("Courier", 36, "bold")

SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progresso_dataquest8bit.json")
ESTADO = {"nome": "", "xp": 0, "concluidas": [], "som": True, "intro": False}

# ───────────────────────────── DADOS DO JOGO ─────────────────────────────
VENDAS = [
    {"produto": "Camiseta", "categoria": "Roupas",     "regiao": "Sudeste",  "preco": 50.0,  "qtd": 10},
    {"produto": "Tênis",    "categoria": "Calçados",   "regiao": "Sul",      "preco": 200.0, "qtd": 4},
    {"produto": "Boné",     "categoria": "Acessórios", "regiao": "Sudeste",  "preco": 30.0,  "qtd": 8},
    {"produto": "Calça",    "categoria": "Roupas",     "regiao": "Nordeste", "preco": 120.0, "qtd": 5},
    {"produto": "Mochila",  "categoria": "Acessórios", "regiao": "Sul",      "preco": 90.0,  "qtd": 6},
    {"produto": "Camiseta", "categoria": "Roupas",     "regiao": "Nordeste", "preco": 50.0,  "qtd": 12},
    {"produto": "Tênis",    "categoria": "Calçados",   "regiao": "Sudeste",  "preco": 200.0, "qtd": 7},
    {"produto": "Boné",     "categoria": "Acessórios", "regiao": "Nordeste", "preco": 30.0,  "qtd": 3},
]
SERIE = [10, 12, 12, 13, 14, 15, 16, 48]

SEGUROS = ["sum", "len", "min", "max", "sorted", "range", "round", "abs", "list", "dict", "set", "tuple",
           "str", "int", "float", "enumerate", "zip", "any", "all", "map", "filter", "reversed", "bool"]


def executar(src, dados):
    """Roda um trecho de Python de forma limitada e devolve a variável 'resultado'."""
    env = {"__builtins__": {n: getattr(builtins, n) for n in SEGUROS}}
    env.update(copy.deepcopy(dados))
    exec(src, env)
    return env.get("resultado")


def fmt(x):
    if isinstance(x, float):
        return f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    return str(x)


# ───────────────────────────── PIXEL ART (8x8) ─────────────────────────────
PAL = {"r": "#e53935", "s": "#ffcc99", "k": "#1b1b1b", "b": "#2962ff", "p": "#1a237e", "w": "#fafafa",
       "y": "#ffd600", "Y": "#fff59d", "o": "#e65100", "c": "#26c6da", "g": "#4caf50", "h": "#388e3c",
       "L": "#2e7d32", "l": "#66bb6a", "t": "#6d4c41", "B": "#a1887f", "m": "#3e2723", "n": "#29b6f6",
       "N": "#81d4fa", "G": "#76ff03", "a": "#9e9e9e", "A": "#616161", "f": "#f06292", "d": "#a1662f",
       "P": "#7b1fa2"}

HERO = [
    ["..rrrr..", ".rrrrrr.", ".ssssks.", ".ssssss.", "..bbbb..", ".sbbbbs.", "..bppb..", "..p..p.."],
    ["..rrrr..", ".rrrrrr.", ".ssssks.", ".ssssss.", "..bbbb..", ".sbbbbs.", "..bppb..", "...pp..."],
]
MENTOR = ["...PP...", "..PPPP..", ".PPPPPP.", "..ssss..", "..skks..", ".wwwwww.", ".wwwwww.", "..b..b.."]
GUARD = [".aaaaaa.", ".acccca.", ".aycyca.", "..aaaa..", ".aAaaAa.", ".aaaaaa.", ".aa..aa.", ".AA..AA."]
BUG = ["G......G", ".G.GG.G.", "..GGGG..", ".GGrrGG.", "GGGGGGGG", ".GGGGGG.", ".G.GG.G.", "G......G"]
COIN = ["..oooo..", ".oyyyyo.", "oyyYyyyo", "oyyYyyyo", "oyyyyyyo", "oyyyyyyo", ".oyyyyo.", "..oooo.."]
HEART = [".rr..rr.", "rrrrrrrr", "rrrrrrrr", "rrrrrrrr", ".rrrrrr.", "..rrrr..", "...rr...", "........"]
STAR = ["...yy...", "...yy...", "yyyyyyyy", ".yyyyyy.", "..yyyy..", "..yyyy..", ".yy..yy.", ".y....y."]
LOCK = ["..aaaa..", ".a....a.", ".a....a.", "yyyyyyyy", "yyykkyyy", "yyykkyyy", "yyyyyyyy", "........"]
FLOOR = ["gggggggg", "ggghgggg", "gggggggg", "gggggghg", "gggggggg", "ghgggggg", "gggggggg", "gggghggg"]
WALL = ["BBBBmBBB", "BBBBmBBB", "mmmmmmmm", "BmBBBBBB", "BmBBBBBB", "mmmmmmmm", "BBBBmBBB", "BBBBmBBB"]
TREE = ["ggLLLLgg", "gLllLLLg", "LLlLLLLL", "LLLLLlLL", "gLLLLLLg", "gggttggg", "gggttggg", "gggggggg"]
WATER = ["nnnnnnnn", "nNnnnnNn", "nnnnnnnn", "nnNnnnnn", "nnnnnNnn", "nnnnnnnn", "nNnnnnnn", "nnnnNnnn"]
FLOWER = ["gggggggg", "gggfgggg", "ggfyfggg", "gggfgggg", "ggghgggg", "ggghgggg", "gggggggg", "gggggggg"]
DOOR = ["mmmmmmmm", "mddddddm", "mddddddm", "mddddddm", "mdddyddm", "mddddddm", "mddddddm", "mddddddm"]


def make_image(rows, flip=False, zoom=PX, repl=None):
    img = tk.PhotoImage(width=len(rows[0]), height=len(rows))
    for y, row in enumerate(rows):
        if flip:
            row = row[::-1]
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if repl and ch in repl:
                ch = repl[ch]
            img.put(PAL[ch], to=(x, y, x + 1, y + 1))
    return img.zoom(zoom, zoom)


class Assets:
    def __init__(self):
        mk = make_image
        self.hero = {(f, d): mk(HERO[f], flip=(d == -1)) for f in (0, 1) for d in (1, -1)}
        self.hero_big = mk(HERO[0], zoom=10)
        self.mentor, self.guard = mk(MENTOR), mk(GUARD)
        self.bug, self.coin = mk(BUG), mk(COIN)
        self.heart, self.heart_off = mk(HEART, zoom=3), mk(HEART, zoom=3, repl={"r": "a"})
        self.star, self.lock = mk(STAR, zoom=2), mk(LOCK)
        self.tiles = {".": mk(FLOOR), "#": mk(WALL), "T": mk(TREE), "W": mk(WATER),
                      "F": mk(FLOWER), "D": mk(DOOR)}


# ───────────────────────────── CONTEÚDO DAS FASES ─────────────────────────────
def mc(q, op, certa, exp, dica=None, run=None):
    return {"tipo": "mc", "q": q, "op": op, "certa": certa, "exp": exp, "dica": dica, "run": run}


def num(q, valor, exp, tol=0.01, dica=None):
    return {"tipo": "num", "q": q, "valor": valor, "tol": tol, "exp": exp, "dica": dica, "run": None}


NIVEIS = [
    # ─────────── FASE 1 ───────────
    {"nome": "O Ciclo do Analista",
     "missao": "Colete as 6 etapas NA ORDEM correta",
     "mestre": [
         "Bem-vindo(a), jovem analista! Analisar dados é pegar números e informações soltas e transformá-los em RESPOSTAS que ajudam alguém a decidir.",
         "Exemplo: uma loja quer saber 'qual produto devo comprar mais?'. O analista olha as vendas e descobre a resposta.",
         "O trabalho tem 6 etapas, sempre nesta ordem:\n 1. PERGUNTAR\n 2. COLETAR\n 3. LIMPAR\n 4. ANALISAR\n 5. VISUALIZAR\n 6. COMUNICAR",
         "PERGUNTAR: qual problema resolver?\nCOLETAR: buscar os dados.\nLIMPAR: corrigir erros.\nANALISAR: calcular e comparar.\nVISUALIZAR: fazer gráficos.\nCOMUNICAR: contar a história.",
         "Existem 4 tipos de análise:\nDESCRITIVA: o que aconteceu?\nDIAGNÓSTICA: por que aconteceu?\nPREDITIVA: o que vai acontecer?\nPRESCRITIVA: o que devemos fazer?",
         "MISSÃO: colete as 6 etapas NA ORDEM certa! Errou a ordem? Perde um coração. Fuja dos bugs! Se esquecer, aperte R para rever a aula.",
     ],
     "coleta": {"ordenada": True, "bugs": 1, "vel": 2,
                "itens": [("PERGUNTAR", True, ""), ("COLETAR", True, ""), ("LIMPAR", True, ""),
                          ("ANALISAR", True, ""), ("VISUALIZAR", True, ""), ("COMUNICAR", True, "")]},
     "quiz": [
         mc("Antes de abrir qualquer planilha, qual é o primeiro passo?",
            ["Fazer um gráfico bonito", "Entender a pergunta que precisa ser respondida",
             "Apagar linhas com erro", "Comprar um computador novo"], 1,
            "Sem uma boa pergunta, você pode analisar muito e não resolver nada."),
         mc("Qual etapa vem logo DEPOIS de COLETAR os dados?",
            ["Comunicar", "Visualizar", "Limpar", "Perguntar"], 2,
            "Dados coletados quase sempre têm erros. Primeiro limpamos, depois analisamos."),
         mc("'Quanto vendemos no mês passado?' é uma análise...",
            ["Descritiva", "Prescritiva", "Diagnóstica", "Preditiva"], 0,
            "Ela só descreve o que já aconteceu."),
         mc("'Por que as vendas caíram em março?' é uma análise...",
            ["Descritiva", "Prescritiva", "Diagnóstica", "Preditiva"], 2,
            "A diagnóstica busca as CAUSAS de um resultado.", dica="Ela busca o 'por quê'."),
         mc("Por que limpar os dados antes de analisar?",
            ["Para a planilha ficar mais bonita", "Porque a lei exige",
             "Para o computador ficar mais rápido", "Porque dados com erro levam a conclusões erradas"], 3,
            "Lixo entra, lixo sai: dados ruins geram respostas ruins."),
     ],
     "cur": "O estatístico John Tukey, que popularizou a Análise Exploratória de Dados no livro de 1977, também foi quem criou o termo 'bit'."},

    # ─────────── FASE 2 ───────────
    {"nome": "Conhecendo os Dados",
     "missao": "Colete SÓ as colunas NUMÉRICAS",
     "mestre": [
         "Quase todo dado vem em TABELAS, como numa planilha do Excel.",
         "produto    regiao    preco   qtd\nBoné       Sul       30      8\nTênis      Sudeste   200     4\nCamiseta   Nordeste  50      12",
         "Cada LINHA é um registro (uma venda). Cada COLUNA é uma característica (produto, preço, quantidade...).",
         "Variáveis NUMÉRICAS são números com os quais dá para fazer contas: preço, quantidade, idade, peso.",
         "Variáveis CATEGÓRICAS são rótulos: região, produto, cor. Não faz sentido somar 'Sul + Sudeste'!",
         "As categóricas podem ter ordem (P, M, G: ORDINAL) ou não (cores: NOMINAL).",
         "MISSÃO: colete SÓ as colunas NUMÉRICAS. Pegar uma categórica faz você perder um coração!",
     ],
     "coleta": {"bugs": 2, "vel": 2,
                "itens": [("preco", True, ""), ("qtd", True, ""), ("idade", True, ""), ("peso", True, ""),
                          ("regiao", False, "'regiao' é um nome (categórica): não dá para fazer contas com ela."),
                          ("produto", False, "'produto' é um nome (categórica)."),
                          ("cor", False, "'cor' é categórica (azul, verde...)."),
                          ("cidade", False, "'cidade' é um nome (categórica).")]},
     "quiz": [
         mc("A tabela de vendas tem 8 linhas e 5 colunas. O que representa cada LINHA?",
            ["Uma característica, como o preço", "Um registro, como uma venda", "O nome da tabela",
             "Um tipo de gráfico"], 1, "Cada linha é um registro: uma venda."),
         mc("A coluna 'regiao' (Sul, Sudeste, Nordeste) é uma variável...",
            ["Numérica", "Categórica", "De data", "Impossível de classificar"], 1,
            "São rótulos (nomes), então é categórica."),
         mc("A coluna 'qtd' (unidades vendidas: 10, 4, 8...) é...",
            ["Categórica", "Numérica", "Texto livre", "Uma imagem"], 1,
            "É um número com o qual dá para somar e tirar média."),
         mc("Tamanho de camiseta (P, M, G, GG) é categórica ORDINAL porque...",
            ["Tem números", "Existe uma ordem natural entre as categorias", "Pode ser somada", "É sempre decimal"], 1,
            "P < M < G < GG: as categorias têm uma ordem."),
         num("Quantas COLUNAS tem a tabela: produto, categoria, regiao, preco, qtd?", 5,
             "Conte os nomes: são 5 colunas.", dica="Conte quantos nomes aparecem na lista."),
     ],
     "cur": "Em 2012, a Harvard Business Review chamou 'cientista de dados' de a profissão mais atraente do século XXI."},

    # ─────────── FASE 3 ───────────
    {"nome": "Estatística Descritiva",
     "missao": "Colete os 8 números das vendas diárias",
     "soma": True,
     "mestre": [
         "Imagine 8 dias de vendas de uma loja. Em vez de olhar um por um, usamos números-resumo.",
         "MÉDIA: some tudo e divida pela quantidade.\nEx.: 2, 4, 6 -> soma 12 ÷ 3 = 4.",
         "MEDIANA: coloque em ordem e pegue o do MEIO.\nEx.: 2, 4, 9 -> mediana 4.\nSe sobrarem dois no meio, tire a média deles.",
         "MODA: o valor que MAIS se repete.\nAMPLITUDE: maior valor menos menor valor.",
         "OUTLIER é um valor muito fora do normal (ex.: 48 no meio de números perto de 13). Ele puxa a média para cima!",
         "MISSÃO: colete os 8 números das vendas diárias. Eu somo tudo para você no painel de baixo. Depois, calcule a média com o Guardião!",
     ],
     "coleta": {"bugs": 2, "vel": 2, "itens": [(str(n), True, "") for n in SERIE]},
     "quiz": [
         num("Vendas diárias: 10, 12, 12, 13, 14, 15, 16, 48\nQual é a MÉDIA? (some tudo e divida por 8)", statistics.mean(SERIE),
             "A soma é 140 e 140 ÷ 8 = 17,5.", tol=0.05, dica="A soma dos 8 números é 140."),
         num("Qual é a MEDIANA? (os dois do meio são 13 e 14)", statistics.median(SERIE),
             "(13 + 14) ÷ 2 = 13,5.", tol=0.05, dica="Tire a média de 13 e 14."),
         num("Qual é a MODA (o valor que mais se repete)?", statistics.mode(SERIE),
             "O 12 aparece duas vezes: é o mais frequente."),
         num("Qual é a AMPLITUDE (maior valor menos menor valor)?", 38, "48 - 10 = 38."),
         mc("O dia com 48 vendas é muito diferente dos outros. Ele é um...",
            ["Outlier", "Moda", "Mediana", "Erro do Python"], 0,
            "Valor muito fora do padrão é chamado de outlier."),
     ],
     "cur": "Se Bill Gates entra em um bar, a renda MÉDIA dos clientes dispara, mas a MEDIANA quase não muda. É o exemplo clássico de por que olhar só a média pode enganar."},

    # ─────────── FASE 4 ───────────
    {"nome": "Limpeza de Dados",
     "missao": "Colete SÓ os dados SUJOS",
     "mestre": [
         "Dados do mundo real vêm SUJOS! Se analisar sem limpar, a resposta sai errada.",
         "Problemas comuns: valores VAZIOS (nulos), linhas REPETIDAS (duplicadas) e valores ABSURDOS (outliers).",
         "nome     idade\nAna      25\nBruno    (vazio)\nAna      25\nCarla    230\nDiego    31",
         "Aqui: a idade do Bruno está vazia, a Ana aparece 2 vezes e a Carla com 230 anos é provavelmente erro de digitação.",
         "MISSÃO: colete SÓ os dados sujos para levá-los à lavanderia! Pegar um dado limpo faz você perder um coração.",
     ],
     "coleta": {"bugs": 2, "vel": 2,
                "itens": [("(vazio)", True, ""), ("230 anos", True, ""), ("Ana (2a vez)", True, ""),
                          ("25 anos", False, "25 anos é um valor normal e correto!"),
                          ("31 anos", False, "31 anos é um valor normal e correto!"),
                          ("Diego", False, "Diego é um dado limpo."),
                          ("Bruno", False, "O nome Bruno está certo; o vazio é a idade.")]},
     "quiz": [
         num("Na tabela (Ana 25, Bruno vazio, Ana 25, Carla 230, Diego 31): quantos valores VAZIOS existem?", 1,
             "Só a idade do Bruno está vazia."),
         num("Quantas linhas DUPLICADAS (repetidas) existem?", 1,
             "A segunda linha da Ana repete exatamente a primeira.", dica="Procure uma linha igual a outra."),
         mc("Qual valor parece um OUTLIER (erro de digitação)?", ["25", "31", "230", "Ana"], 2,
            "Ninguém tem 230 anos: provavelmente era 23 ou 30."),
         mc("Qual o melhor jeito de tratar a idade vazia do Bruno?",
            ["Preencher com 0", "Apagar a tabela inteira",
             "Investigar a origem ou preencher com a mediana, anotando o que foi feito", "Fingir que não viu"], 2,
            "Preencher com 0 distorceria a média. E sempre documente o que você fez."),
     ],
     "cur": "Relatos do mercado costumam estimar que analistas gastam entre 50% e 80% do tempo coletando e limpando dados, e só o restante analisando."},

    # ─────────── FASE 5 ───────────
    {"nome": "Python: o Superpoder",
     "missao": "Colete as funções REAIS do Python",
     "mestre": [
         "Python é uma linguagem para conversar com o computador. Analistas usam para fazer contas com milhares de dados em segundos.",
         "Uma LISTA guarda vários valores:\n  numeros = [10, 20, 30]",
         "Funções mágicas:\n  len(numeros)  -> 3   (quantos)\n  sum(numeros)  -> 60  (soma)\n  max(numeros)  -> 30  (maior)\n  min(numeros)  -> 10  (menor)",
         "Média = soma ÷ quantidade:\n  sum(numeros) / len(numeros)  -> 20.0",
         "Um DICIONÁRIO guarda uma linha da tabela:\n  linha = {'produto': 'Boné', 'qtd': 8}\n  linha['qtd']  -> 8",
         "No jogo existe a lista 'vendas' (as 8 linhas da tabela). Para pegar uma coluna inteira:\n  [v['qtd'] for v in vendas]\nLeia: 'para cada v em vendas, pegue v['qtd']'.",
         "MISSÃO: colete as funções REAIS do Python: len, sum, max e min. Cuidado com as falsas! E fuja dos bugs!",
     ],
     "coleta": {"bugs": 3, "vel": 2,
                "itens": [("len()", True, ""), ("sum()", True, ""), ("max()", True, ""), ("min()", True, ""),
                          ("soma()", False, "No Python o nome certo é sum(), não soma()."),
                          ("maior()", False, "No Python o nome certo é max(), não maior()."),
                          ("tamanho()", False, "No Python o nome certo é len(), não tamanho().")]},
     "quiz": [
         mc("Qual código dá o TOTAL de unidades vendidas (soma da coluna qtd)?",
            ["resultado = len(vendas)", "resultado = sum([v['qtd'] for v in vendas])",
             "resultado = max(vendas)", "resultado = vendas['qtd']"], 1,
            "Montamos a lista de quantidades e somamos tudo.",
            run="resultado = sum([v['qtd'] for v in vendas])"),
         mc("Qual código dá QUANTAS vendas (linhas) existem?",
            ["resultado = sum(vendas)", "resultado = max(vendas)", "resultado = len(vendas)", "resultado = vendas.qtd"], 2,
            "len() conta quantos itens a lista tem.", dica="Qual função conta quantidade?",
            run="resultado = len(vendas)"),
         mc("Qual código dá o MAIOR preço?",
            ["resultado = min([v['preco'] for v in vendas])", "resultado = max([v['preco'] for v in vendas])",
             "resultado = len([v['preco'] for v in vendas])", "resultado = sum(vendas)"], 1,
            "max() devolve o maior valor da lista de preços.",
            run="resultado = max([v['preco'] for v in vendas])"),
         mc("Qual código dá o PREÇO MÉDIO (soma ÷ quantidade)?",
            ["resultado = sum([v['preco'] for v in vendas]) * len(vendas)",
             "resultado = len(vendas) / sum([v['preco'] for v in vendas])",
             "resultado = max([v['preco'] for v in vendas]) / 2",
             "resultado = sum([v['preco'] for v in vendas]) / len(vendas)"], 3,
            "Média = soma ÷ quantidade.",
            run="resultado = sum([v['preco'] for v in vendas]) / len(vendas)"),
     ],
     "cur": "O nome Python NÃO vem da cobra: vem do grupo de humor britânico Monty Python. A linguagem foi criada por Guido van Rossum e lançada em 1991."},

    # ─────────── FASE 6 ───────────
    {"nome": "Filtrar e Agrupar",
     "missao": "Colete SÓ os produtos vendidos no SUL",
     "mestre": [
         "Duas habilidades essenciais do analista: FILTRAR (ficar só com o que interessa) e AGRUPAR (somar por grupo).",
         "FILTRAR: pegar só as vendas do Sul:\n  [v for v in vendas if v['regiao'] == 'Sul']\nLeia: 'para cada v em vendas, SE a região é Sul, guarde v'.",
         "AGRUPAR: somar por grupo. Ex.: faturamento por região.\nFaturamento = preço × quantidade.",
         "Código do agrupamento:\n  total = {}\n  for v in vendas:\n    total[v['regiao']] = total.get(v['regiao'], 0) + v['preco'] * v['qtd']",
         "Dica de profissional: na biblioteca pandas, isso vira uma linha só:\n  df.groupby('regiao')['faturamento'].sum()",
         "MISSÃO: colete SÓ os produtos vendidos no SUL. Os de outras regiões custam um coração!",
     ],
     "coleta": {"bugs": 3, "vel": 2,
                "itens": [("Tênis (Sul)", True, ""), ("Mochila (Sul)", True, ""),
                          ("Boné (Sudeste)", False, "Esse foi vendido no Sudeste, não no Sul."),
                          ("Camiseta (Nordeste)", False, "Esse foi vendido no Nordeste."),
                          ("Calça (Nordeste)", False, "Esse foi vendido no Nordeste."),
                          ("Tênis (Sudeste)", False, "Esse Tênis foi vendido no Sudeste.")]},
     "quiz": [
         mc("Qual código lista os produtos vendidos no NORDESTE?",
            ["resultado = [v['produto'] for v in vendas if v['regiao'] = 'Nordeste']",
             "resultado = [v['produto'] for v in vendas if v['regiao'] == 'Nordeste']",
             "resultado = [v['produto'] for v in vendas if 'Nordeste']",
             "resultado = sum([v['regiao'] for v in vendas])"], 1,
            "Para comparar usamos '==' (dois iguais). Um '=' só serve para guardar valores.",
            dica="Comparar usa dois sinais de igual.",
            run="resultado = [v['produto'] for v in vendas if v['regiao'] == 'Nordeste']"),
         num("Faturamento do SUL: Tênis (200 × 4) + Mochila (90 × 6). Quanto dá?", 1340,
             "800 + 540 = 1340.", tol=0.5, dica="200 × 4 = 800 e 90 × 6 = 540."),
         mc("A região Sudeste faturou 2140, o Sul 1340 e o Nordeste 1290. Qual região tem o MAIOR faturamento?",
            ["Sul", "Sudeste", "Nordeste", "Todas empatam"], 1, "2140 é o maior valor: Sudeste."),
         mc("Somar o faturamento SEPARADAMENTE para cada categoria é...",
            ["Filtrar", "Agrupar", "Limpar", "Visualizar"], 1,
            "Agrupar é dividir em grupos (categorias) e calcular um total para cada."),
     ],
     "cur": "O pandas foi criado por Wes McKinney em 2008, quando trabalhava em um fundo de investimentos. O nome vem de 'panel data' (dados em painel)."},

    # ─────────── FASE 7 ───────────
    {"nome": "Visualização de Dados",
     "missao": "Colete os 2 gráficos: COMPARAR e EVOLUÇÃO",
     "mestre": [
         "Gráficos transformam números em imagens que o cérebro entende rapidinho.",
         "BARRAS: comparar categorias (ex.: vendas por região).\nLINHA: ver a evolução ao longo do tempo (ex.: vendas mês a mês).",
         "DISPERSÃO: ver a relação entre duas variáveis numéricas (ex.: preço × quantidade vendida).\nPIZZA: partes de um todo (poucas fatias!).",
         "Faturamento por categoria:\nCalçados   |████████████████████ 2200\nRoupas     |███████████████ 1700\nAcessórios |███████ 870",
         "Gráfico HONESTO: título claro, eixos com nome e barras começando no ZERO. Cortar o eixo exagera as diferenças e engana quem lê.",
         "MISSÃO: colete os 2 gráficos certos para (1) COMPARAR categorias e (2) mostrar a EVOLUÇÃO no tempo.",
     ],
     "coleta": {"bugs": 3, "vel": 2,
                "itens": [("BARRAS", True, ""), ("LINHA", True, ""),
                          ("PIZZA", False, "Pizza mostra partes de um todo, não evolução no tempo."),
                          ("DISPERSAO", False, "Dispersão mostra relação entre 2 números."),
                          ("MAPA", False, "Mapas mostram lugares, não servem aqui.")]},
     "quiz": [
         mc("No gráfico de faturamento por categoria, qual vendeu mais?",
            ["Roupas", "Calçados", "Acessórios", "Todas empatam"], 1, "Calçados tem a maior barra: 2200."),
         mc("Melhor gráfico para mostrar a EVOLUÇÃO das vendas mês a mês:",
            ["Pizza", "Linha", "Dispersão", "Mapa"], 1, "Linhas mostram tendência ao longo do tempo."),
         mc("Para ver a RELAÇÃO entre preço e quantidade vendida:",
            ["Pizza", "Barras empilhadas", "Dispersão", "Tabela de cores"], 2,
            "Cada ponto é um produto: dá para ver se preço alto significa menos vendas."),
         mc("O que deixa um gráfico de barras mais HONESTO?",
            ["Cortar o eixo para exagerar diferenças", "Eixo começando em zero e título claro",
             "Usar efeito 3D", "Usar o máximo de cores"], 1, "Eixo truncado engana o olhar do leitor."),
     ],
     "cur": "O Quarteto de Anscombe (1973) são 4 conjuntos de dados com quase a mesma média, mas gráficos completamente diferentes. É a prova de que sempre vale VISUALIZAR os dados."},

    # ─────────── FASE 8 ───────────
    {"nome": "CHEFÃO: Projeto Final",
     "missao": "Colete as 4 pistas do projeto NA ORDEM",
     "mestre": [
         "Chegou o chefão! O dono da loja pergunta: 'Onde devo investir meu dinheiro?'",
         "Você vai usar o ciclo todo: PERGUNTAR, COLETAR, LIMPAR, ANALISAR, VISUALIZAR e COMUNICAR.",
         "Dados da loja (8 vendas):\n  Unidades vendidas: 55\n  Faturamento total: R$ 4.770\n  Calçados:   R$ 2.200 (11 unid.)\n  Roupas:     R$ 1.700 (27 unid.)\n  Acessórios: R$   870 (17 unid.)",
         "MISSÃO: colete as 4 pistas NA ORDEM do projeto: PERGUNTA, DADOS, ANALISE e RECOMENDACAO. Muitos bugs por aqui!",
     ],
     "coleta": {"ordenada": True, "bugs": 4, "vel": 3,
                "itens": [("PERGUNTA", True, ""), ("DADOS", True, ""), ("ANALISE", True, ""),
                          ("RECOMENDACAO", True, "")]},
     "quiz": [
         num("TICKET MÉDIO por unidade = faturamento total ÷ unidades.\nR$ 4.770 ÷ 55 unidades. Quanto dá?", round(4770 / 55, 2),
             "4770 ÷ 55 = 86,73 reais por unidade.", tol=0.06, dica="Use uma calculadora: 4770 dividido por 55."),
         num("Quantos % do faturamento vêm dos CALÇADOS? (2200 de 4770; pode arredondar)", round(2200 / 4770 * 100, 1),
             "2200 ÷ 4770 × 100 = 46,1%.", tol=0.6, dica="Divida 2200 por 4770 e multiplique por 100."),
         mc("Calçados geram 46% do faturamento com apenas 20% das unidades. Qual conclusão os dados SUSTENTAM?",
            ["Acessórios devem ser descontinuados já, pois vendem menos",
             "Calçados rendem muito por unidade: vale proteger o estoque e testar ampliar o mix",
             "Todas as categorias são iguais, não há o que fazer",
             "O Nordeste não vende nada"], 1,
            "Uma boa conclusão liga o número a uma ação plausível, sem exagerar nem inventar."),
         mc("Qual a melhor forma de apresentar isso ao dono da loja?",
            ["Enviar a planilha inteira e deixar ele procurar",
             "Um resumo: a pergunta, 2 ou 3 achados com gráfico simples e uma recomendação",
             "Um relatório de 40 páginas cheio de termos técnicos",
             "Dizer 'os dados mostram...' sem mostrar nada"], 1,
            "Comunicar bem é ter clareza, poucos pontos fortes e uma ação recomendada."),
     ],
     "cur": "Florence Nightingale, enfermeira e estatística, usou gráficos criativos para convencer o governo britânico de que mais soldados morriam por doenças evitáveis do que em batalha. Foi data storytelling em pleno século XIX!"},
]

HUB_DOORS = [2, 4, 6, 8, 11, 13, 15, 17]


def patente():
    n = len(ESTADO["concluidas"])
    nome = "Estagiario de Dados"
    for minimo, nm in [(2, "Analista Junior"), (4, "Analista Pleno"), (6, "Analista Senior"),
                       (8, "Analista Certificado")]:
        if n >= minimo:
            nome = nm
    return nome


def salvar():
    try:
        with open(SAVE, "w", encoding="utf-8") as f:
            json.dump(ESTADO, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def carregar():
    try:
        with open(SAVE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def embrulhar(txt, largura=60):
    linhas = []
    for par in txt.split("\n"):
        linhas.append(textwrap.fill(par, largura) if par.strip() else "")
    return "\n".join(linhas)


# ───────────────────────────── O JOGO ─────────────────────────────
class Jogo:
    def __init__(self, root):
        self.root = root
        root.title("DATA QUEST 8-BIT - A Aventura da Análise de Dados")
        root.resizable(False, False)
        self.c = tk.Canvas(root, width=W, height=H, bg="#000000", highlightthickness=0)
        self.c.pack()
        self.A = Assets()
        self.keys, self.ev = set(), []
        root.bind("<KeyPress>", self.on_down)
        root.bind("<KeyRelease>", self.on_up)
        root.bind("<FocusOut>", lambda e: self.keys.clear())
        root.protocol("WM_DELETE_WINDOW", self.sair)
        self.frame = 0
        self.scene, self.dirty, self.sel = "title", True, 0
        self.tem_save = bool((carregar() or {}).get("nome"))
        self.nome_txt = ""
        self.dialog = self.quiz = None
        self.pausa = False
        self.toast_msg, self.toast_t, self.toast_cd = "", 0, 0
        self.confete = []
        rnd = random.Random(7)
        self.stars = [(rnd.randrange(W), rnd.randrange(H - 140)) for _ in range(45)]
        self.room, self.lv, self.p = None, None, None
        self.tick()

    # ───── entrada ─────
    def on_down(self, e):
        k = e.keysym.lower()
        if k == "kp_enter":
            k = "return"
        if k not in self.keys:
            self.ev.append((k, e.char or ""))
        self.keys.add(k)

    def on_up(self, e):
        k = e.keysym.lower()
        if k == "kp_enter":
            k = "return"
        self.keys.discard(k)

    def sair(self):
        salvar()
        self.root.destroy()

    # ───── som ─────
    def tocar(self, nome):
        if not ESTADO["som"] or winsound is None:
            return
        seqs = {"item": [(880, 60)], "ok": [(660, 80), (880, 120)], "erro": [(220, 180)],
                "dano": [(160, 120), (110, 200)], "nivel": [(523, 100), (659, 100), (784, 100), (1047, 260)]}

        def run():
            for f, d in seqs.get(nome, []):
                try:
                    winsound.Beep(f, d)
                except Exception:
                    return
        threading.Thread(target=run, daemon=True).start()

    # ───── loop ─────
    def tick(self):
        try:
            self.frame += 1
            ev, self.ev = self.ev, []
            if self.scene == "title":
                self.up_title(ev)
            elif self.scene == "nome":
                self.up_nome(ev)
            elif self.scene == "room":
                self.up_room(ev)
            elif self.scene == "fim":
                for k, _ in ev:
                    if k in ("return", "escape"):
                        self.sair()
                        return
            self.draw()
        except Exception:
            traceback.print_exc()
        self.root.after(FPS_MS, self.tick)

    # ───── mensagens ─────
    def toast(self, msg, t=110):
        self.toast_msg, self.toast_t = msg, t

    def falar(self, quem, paginas, cb=None, estilo="normal"):
        self.dialog = {"quem": quem, "pages": paginas, "i": 0, "chars": 0, "cb": cb, "estilo": estilo}
        self.prep_pagina()

    def prep_pagina(self):
        d = self.dialog
        d["wrapped"] = embrulhar(d["pages"][d["i"]], 60)
        d["chars"] = 0

    def add_xp(self, v):
        if self.lv and self.lv.get("rejogo"):
            return
        ESTADO["xp"] = max(0, ESTADO["xp"] + v)

    # ───── cenas: título e nome ─────
    def up_title(self, ev):
        opcoes = 2 if self.tem_save else 1
        for k, _ in ev:
            if k in ("up", "w"):
                self.sel = (self.sel - 1) % opcoes
            elif k in ("down", "s"):
                self.sel = (self.sel + 1) % opcoes
            elif k in ("return", "space"):
                if self.tem_save and self.sel == 1:
                    salvo = carregar() or {}
                    ESTADO.update(salvo)
                    self.ir_hub(None)
                else:
                    ESTADO.update({"nome": "", "xp": 0, "concluidas": [], "intro": False})
                    self.nome_txt = ""
                    self.scene, self.dirty = "nome", True

    def up_nome(self, ev):
        for k, ch in ev:
            if k == "backspace":
                self.nome_txt = self.nome_txt[:-1]
            elif k == "return":
                ESTADO["nome"] = self.nome_txt.strip() or "Analista"
                salvar()
                self.ir_hub(None)
            elif ch and ch.isprintable() and len(self.nome_txt) < 14:
                self.nome_txt += ch

    # ───── mapas ─────
    def mapa_base(self):
        return ([["#"] * COLS] + [["#"] + ["."] * (COLS - 2) + ["#"] for _ in range(ROWS - 2)] + [["#"] * COLS])

    def ir_hub(self, voltando):
        g = self.mapa_base()
        for c in HUB_DOORS:
            g[0][c] = "D"
        for x, y in [(1, 3), (18, 3), (1, 8), (18, 8), (5, 5), (14, 5), (5, 9), (14, 9)]:
            g[y][x] = "T"
        for x, y in [(9, 5), (10, 5), (9, 6), (10, 6)]:
            g[y][x] = "W"
        for x, y in [(3, 3), (16, 3), (8, 8), (12, 8), (7, 2), (12, 2)]:
            g[y][x] = "F"
        self.room = {"kind": "hub", "tiles": g,
                     "npcs": [{"id": "hub", "tx": 9, "ty": 8, "img": self.A.mentor, "nome": "MESTRE BYTE"}],
                     "start": (10 * TILE, 10 * TILE - 8)}
        if voltando:
            self.p = {"x": HUB_DOORS[voltando - 1] * TILE, "y": TILE, "dir": 1, "anim": 0}
        else:
            self.p = {"x": self.room["start"][0], "y": self.room["start"][1], "dir": 1, "anim": 0}
        self.lv = None
        self.scene, self.dirty = "room", True
        self.dialog = self.quiz = None
        if not ESTADO.get("intro"):
            ESTADO["intro"] = True
            salvar()
            self.falar("Mestre Byte", [
                f"Olá, {ESTADO['nome']}! Bem-vindo(a) à VILA DOS DADOS! Eu sou o Mestre Byte e vou te ensinar a profissão de analista de dados do zero.",
                "COMANDOS:\n  SETAS ou WASD: andar\n  E, ESPAÇO ou ENTER: falar / confirmar\n  R: rever a aula\n  H: dica nos desafios\n  ESC: pausa",
                "Cada porta numerada no alto é uma FASE. Cada fase tem: uma aula com o Mestre, uma missão para coletar itens (cuidado com os BUGS!) e um desafio com o Guardião.",
                "Comece pela porta número 1. Boa sorte, jovem analista!",
            ])

    def ir_nivel(self, n):
        g = self.mapa_base()
        g[ROWS - 1][9] = "D"
        for x, y in [(6, 5), (13, 5), (2, 8), (17, 8)]:
            g[y][x] = "T"
        for x, y in [(9, 2), (10, 2), (4, 9), (15, 9)]:
            g[y][x] = "F"
        self.room = {"kind": "level", "tiles": g,
                     "npcs": [{"id": "mestre", "tx": 3, "ty": 2, "img": self.A.mentor, "nome": "MESTRE"},
                              {"id": "guardiao", "tx": 16, "ty": 2, "img": self.A.guard, "nome": "GUARDIAO"}],
                     "start": (9 * TILE, 10 * TILE - 8)}
        self.p = {"x": self.room["start"][0], "y": self.room["start"][1], "dir": 1, "anim": 0}
        self.lv = {"n": n, "lesson_done": False, "collect_done": False, "quiz_done": False, "vidas": 3,
                   "itens": [], "bugs": [], "prox": 1, "soma": 0, "qtd": 0, "bons": 0, "bons_total": 0,
                   "invul": 0, "rejogo": n in ESTADO["concluidas"]}
        self.scene, self.dirty = "room", True
        self.dialog = self.quiz = None
        self.toast(f"FASE {n}: {NIVEIS[n - 1]['nome']}. Fale com o MESTRE (tecla E)!", 150)

    # ───── colisão ─────
    def solido_tile(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= COLS or ty >= ROWS:
            return True
        ch = self.room["tiles"][ty][tx]
        if ch in "#TW":
            return True
        if ch == "D" and self.room["kind"] == "hub":
            return not self.porta_aberta(tx)
        return False

    def porta_aberta(self, col):
        n = HUB_DOORS.index(col) + 1
        return n == 1 or (n - 1) in ESTADO["concluidas"]

    def bate_rect(self, x1, y1, x2, y2):
        for tx in range(int(x1 // TILE), int((x2 - 1) // TILE) + 1):
            for ty in range(int(y1 // TILE), int((y2 - 1) // TILE) + 1):
                if self.solido_tile(tx, ty):
                    return True
        for n in self.room["npcs"]:
            nx, ny = n["tx"] * TILE + 4, n["ty"] * TILE + 8
            if x1 < nx + 24 and x2 > nx and y1 < ny + 22 and y2 > ny:
                return True
        return False

    @staticmethod
    def hit(x, y):
        return (x + 8, y + 16, x + 24, y + 30)

    # ───── atualização da sala ─────
    def up_room(self, ev):
        if self.pausa:
            for k, _ in ev:
                if k in ("return", "escape"):
                    self.pausa = False
                elif k == "m":
                    ESTADO["som"] = not ESTADO["som"]
                elif k == "q":
                    self.sair()
                    return
            return
        self.atualiza_confete()
        if self.dialog:
            self.up_dialog(ev)
            return
        if self.quiz:
            self.up_quiz(ev)
            return
        for k, _ in ev:
            if k == "escape":
                self.pausa = True
                return
            if k in ("e", "space", "return"):
                self.interagir()
                if self.dialog or self.quiz:
                    return
            elif k == "r":
                self.revisar()
                if self.dialog:
                    return
            elif k == "m":
                ESTADO["som"] = not ESTADO["som"]
                self.toast("Som " + ("LIGADO" if ESTADO["som"] else "DESLIGADO"), 60)
        if self.toast_t > 0:
            self.toast_t -= 1
        if self.toast_cd > 0:
            self.toast_cd -= 1
        self.mover_player()
        if self.room["kind"] == "hub":
            self.checa_portas_hub()
        else:
            self.checa_nivel()

    def mover_player(self):
        k = self.keys
        dx = (1 if ("right" in k or "d" in k) else 0) - (1 if ("left" in k or "a" in k) else 0)
        dy = (1 if ("down" in k or "s" in k) else 0) - (1 if ("up" in k or "w" in k) else 0)
        p, v = self.p, 3
        if dx:
            p["dir"] = dx
            nx = p["x"] + dx * v
            if not self.bate_rect(*self.hit(nx, p["y"])):
                p["x"] = nx
        if dy:
            ny = p["y"] + dy * v
            if not self.bate_rect(*self.hit(p["x"], ny)):
                p["y"] = ny
        p["anim"] = (p["anim"] + 1) if (dx or dy) else 0

    def checa_portas_hub(self):
        x1, y1, x2, y2 = self.hit(self.p["x"], self.p["y"])
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        for i, col in enumerate(HUB_DOORS):
            n = i + 1
            if self.porta_aberta(col):
                if int(cx // TILE) == col and int(cy // TILE) == 0:
                    self.ir_nivel(n)
                    return
            elif y1 <= TILE + 4 and x2 > col * TILE and x1 < (col + 1) * TILE and self.toast_cd == 0:
                self.toast(f"Porta {n} trancada! Conclua a fase {n - 1} primeiro.", 90)
                self.toast_cd = 60

    # ───── NPCs ─────
    def npc_perto(self):
        px, py = self.p["x"] + 16, self.p["y"] + 20
        for n in self.room["npcs"]:
            if math.hypot(px - (n["tx"] * TILE + 16), py - (n["ty"] * TILE + 16)) <= 58:
                return n
        return None

    def interagir(self):
        n = self.npc_perto()
        if not n:
            return
        if n["id"] == "hub":
            self.fala_hub()
        elif n["id"] == "mestre":
            self.fala_mestre()
        else:
            self.fala_guardiao()

    def fala_hub(self):
        feitas = len(ESTADO["concluidas"])
        if feitas >= len(NIVEIS):
            self.falar("Mestre Byte", ["Você completou TODAS as fases! Pode rejogar qualquer porta para reforçar o aprendizado."])
        elif feitas == 0:
            self.falar("Mestre Byte", ["Entre pela porta número 1 (no alto da tela). Ande até ela!"])
        else:
            self.falar("Mestre Byte", [f"Muito bem! Você já concluiu {feitas} de {len(NIVEIS)} fases e tem {ESTADO['xp']} XP. A próxima é a porta {feitas + 1}."])

    def fala_mestre(self):
        lv, N = self.lv, NIVEIS[self.lv["n"] - 1]
        if not lv["lesson_done"]:
            self.falar("Mestre Byte", N["mestre"], self.fim_aula)
        elif not lv["collect_done"]:
            self.falar("Mestre Byte", [f"Sua missão: {N['missao']}.\nAperte R se quiser rever a aula!"])
        elif not lv["quiz_done"]:
            self.falar("Mestre Byte", ["Missão cumprida! Agora fale com o Guardião Bit para o desafio final da fase. Aperte R para rever a aula."])
        else:
            self.falar("Mestre Byte", ["Fase concluída! Saia pela porta lá embaixo e siga para a próxima."])

    def revisar(self):
        lv = self.lv
        if not lv:
            return
        if not lv["lesson_done"]:
            self.toast("Fale com o Mestre primeiro (tecla E perto dele).", 80)
            return
        self.falar("Mestre Byte (revisão)", NIVEIS[lv["n"] - 1]["mestre"])

    def fim_aula(self):
        lv = self.lv
        lv["lesson_done"] = True
        C = NIVEIS[lv["n"] - 1].get("coleta")
        if C:
            self.iniciar_coleta()
            self.toast("MISSÃO INICIADA! " + NIVEIS[lv["n"] - 1]["missao"], 150)
        else:
            lv["collect_done"] = True

    def fala_guardiao(self):
        lv, N = self.lv, NIVEIS[self.lv["n"] - 1]
        if lv["quiz_done"]:
            self.falar("Guardião Bit", ["Você já me venceu! Pode seguir pela porta de baixo."])
        elif not (lv["lesson_done"] and lv["collect_done"]):
            self.falar("Guardião Bit", ["Alto lá! Você ainda não está pronto. Fale com o Mestre, ouça a aula e cumpra a missão. Depois volte aqui!"])
        else:
            self.falar("Guardião Bit", ["Eu guardo o portal desta fase! Responda às perguntas do desafio. Acertando 70% ou mais, você passa. Dica: use a tecla H se travar (custa 3 XP)."],
                       lambda: self.abrir_quiz(N["quiz"]))

    # ───── coleta ─────
    def sortear_posicoes(self, n, evitar=()):
        livres = [(x, y) for y in range(3, 10) for x in range(2, 18)
                  if not self.solido_tile(x, y) and abs(x - 9) + abs(y - 10) > 3 and (x, y) not in evitar]
        random.shuffle(livres)
        for dist in (3, 2, 1, 0):
            esc = []
            for x, y in livres:
                if all(max(abs(x - a), abs(y - b)) >= dist for a, b in esc):
                    esc.append((x, y))
                if len(esc) == n:
                    break
            if len(esc) == n:
                return esc
        return esc

    def iniciar_coleta(self):
        lv = self.lv
        C = NIVEIS[lv["n"] - 1]["coleta"]
        pos = self.sortear_posicoes(len(C["itens"]))
        lv["itens"] = []
        for i, ((label, bom, why), (tx, ty)) in enumerate(zip(C["itens"], pos)):
            lv["itens"].append({"label": label, "bom": bom, "why": why, "tx": tx, "ty": ty,
                                "ordem": i + 1, "got": False, "cd": 0})
        lv["bons_total"] = sum(1 for it in lv["itens"] if it["bom"])
        lv["bons"], lv["prox"], lv["soma"], lv["qtd"] = 0, 1, 0, 0
        lv["bugs"] = []
        ocupadas = {(it["tx"], it["ty"]) for it in lv["itens"]}
        ocupadas |= {(n["tx"], n["ty"]) for n in self.room["npcs"]}
        livres = [(x, y) for y in range(2, 10) for x in range(2, 18)
                  if not self.solido_tile(x, y) and abs(x - 9) + abs(y - 10) > 6 and (x, y) not in ocupadas]
        random.shuffle(livres)
        for tx, ty in livres[:C.get("bugs", 0)]:
            vel = C.get("vel", 2)
            if random.random() < 0.5:
                vx, vy = random.choice([-vel, vel]), 0
            else:
                vx, vy = 0, random.choice([-vel, vel])
            lv["bugs"].append({"x": tx * TILE, "y": ty * TILE, "vx": vx, "vy": vy})

    def checa_nivel(self):
        lv, p = self.lv, self.p
        if lv["invul"] > 0:
            lv["invul"] -= 1
        px1, py1, px2, py2 = self.hit(p["x"], p["y"])
        # saída
        cx, cy = (px1 + px2) / 2, (py1 + py2) / 2
        if int(cy // TILE) == ROWS - 1 and int(cx // TILE) == 9:
            self.ir_hub(lv["n"])
            return
        # itens
        for it in lv["itens"]:
            if it["got"]:
                continue
            if it["cd"] > 0:
                it["cd"] -= 1
                continue
            ix, iy = it["tx"] * TILE, it["ty"] * TILE
            if px1 < ix + 26 and px2 > ix + 6 and py1 < iy + 26 and py2 > iy + 6:
                if not it["bom"] and lv["invul"] > 0:
                    continue
                self.pegar_item(it)
                if self.lv is not lv or not lv["itens"]:
                    break
        # bugs
        for b in lv["bugs"]:
            nx = b["x"] + b["vx"]
            if self.bate_rect(nx + 4, b["y"] + 4, nx + 28, b["y"] + 28):
                b["vx"] = -b["vx"]
            else:
                b["x"] = nx
            ny = b["y"] + b["vy"]
            if self.bate_rect(b["x"] + 4, ny + 4, b["x"] + 28, ny + 28):
                b["vy"] = -b["vy"]
            else:
                b["y"] = ny
            if lv["invul"] == 0 and px1 < b["x"] + 26 and px2 > b["x"] + 6 and py1 < b["y"] + 26 and py2 > b["y"] + 6:
                self.dano("Um BUG te pegou! Cuidado!", True)
                break

    def pegar_item(self, it):
        lv = self.lv
        C = NIVEIS[lv["n"] - 1]["coleta"]
        if C.get("ordenada"):
            if it["ordem"] == lv["prox"]:
                it["got"] = True
                lv["prox"] += 1
                lv["bons"] += 1
                self.tocar("item")
                self.toast(f"OK! {it['label']} coletado.", 50)
            else:
                it["cd"] = 120
                self.dano("Ops! Essa não é a próxima etapa. (R = rever a aula)", False)
        elif it["bom"]:
            it["got"] = True
            lv["bons"] += 1
            lv["qtd"] += 1
            if NIVEIS[lv["n"] - 1].get("soma"):
                lv["soma"] += int(it["label"])
            self.tocar("item")
            self.toast(f"Certo! {it['label']}", 40)
        else:
            it["got"] = True
            self.dano(it["why"] or "Esse não! Perdeu um coração.", False)
        if lv["bons"] >= lv["bons_total"] and lv["vidas"] > 0:
            self.concluir_coleta()

    def dano(self, msg, respawn):
        lv = self.lv
        if lv["invul"] > 0:
            return
        lv["vidas"] -= 1
        lv["invul"] = 60
        self.tocar("dano")
        self.toast(msg, 110)
        if respawn:
            self.p["x"], self.p["y"] = self.room["start"]
        if lv["vidas"] <= 0:
            self.game_over()

    def game_over(self):
        lv = self.lv
        lv["vidas"] = 3
        lv["invul"] = 60
        self.p["x"], self.p["y"] = self.room["start"]
        self.iniciar_coleta()
        self.toast("Acabaram os corações! A missão recomeçou.", 140)

    def concluir_coleta(self):
        lv = self.lv
        lv["collect_done"] = True
        extra = f" Soma coletada: {lv['soma']}." if NIVEIS[lv["n"] - 1].get("soma") else ""
        lv["itens"], lv["bugs"] = [], []
        self.tocar("ok")
        self.toast("MISSÃO CUMPRIDA!" + extra + " Fale com o Guardião (E).", 170)

    # ───── diálogo ─────
    def up_dialog(self, ev):
        d = self.dialog
        for k, _ in ev:
            if k in ("space", "return", "e"):
                if d["chars"] < len(d["wrapped"]):
                    d["chars"] = len(d["wrapped"])
                else:
                    d["i"] += 1
                    if d["i"] >= len(d["pages"]):
                        cb = d["cb"]
                        self.dialog = None
                        if cb:
                            cb()
                        return
                    self.prep_pagina()
        if self.dialog and d["chars"] < len(d["wrapped"]):
            d["chars"] += 2

    # ───── quiz ─────
    def abrir_quiz(self, qs):
        self.quiz = {"qs": qs, "i": 0, "ac": 0, "fase": "ask", "sel": 0, "tent": 1, "txt": "",
                     "aviso": "", "dica": "", "ok": None, "fb": ""}

    def up_quiz(self, ev):
        q = self.quiz
        Q = q["qs"][q["i"]]
        for k, ch in ev:
            if q["fase"] == "ask":
                if k == "h":
                    if Q.get("dica") and not q["dica"]:
                        q["dica"] = Q["dica"]
                        self.add_xp(-3)
                    elif not Q.get("dica"):
                        q["aviso"] = "Esta pergunta não tem dica."
                    continue
                if Q["tipo"] == "mc":
                    if k in ("up", "w"):
                        q["sel"] = (q["sel"] - 1) % len(Q["op"])
                    elif k in ("down", "s"):
                        q["sel"] = (q["sel"] + 1) % len(Q["op"])
                    elif ch in ("1", "2", "3", "4") and int(ch) <= len(Q["op"]):
                        q["sel"] = int(ch) - 1
                        self.responder()
                    elif k in ("return", "space"):
                        self.responder()
                else:
                    if k == "backspace":
                        q["txt"] = q["txt"][:-1]
                    elif k == "return":
                        self.responder()
                    elif ch and ch in "0123456789,.-" and len(q["txt"]) < 10:
                        q["txt"] += ch
            elif k in ("return", "space"):
                self.proxima_pergunta()
                return

    def texto_run(self, Q):
        if not Q.get("run"):
            return ""
        try:
            res = executar(Q["run"], {"vendas": VENDAS})
        except Exception as e:
            res = f"erro: {e}"
        return f"\n\nPython executou:\n  {Q['run']}\n  resultado = {res!r}"

    def responder(self):
        q = self.quiz
        Q = q["qs"][q["i"]]
        if Q["tipo"] == "mc":
            ok = q["sel"] == Q["certa"]
        else:
            try:
                ok = abs(float(q["txt"].replace(",", ".")) - Q["valor"]) <= Q["tol"]
            except ValueError:
                q["aviso"] = "Digite um número!"
                return
        q["aviso"] = ""
        if ok:
            ganho = 10 if q["tent"] == 1 else 5
            self.add_xp(ganho)
            q["ac"] += 1
            q["fb"] = f"CORRETO! +{ganho} XP\n{Q['exp']}{self.texto_run(Q)}"
            q["ok"], q["fase"] = True, "fb"
            self.tocar("ok")
        elif q["tent"] == 1:
            q["tent"] = 2
            q["aviso"] = "Quase! Tente mais uma vez (H = dica)."
            self.tocar("erro")
        else:
            resp = Q["op"][Q["certa"]] if Q["tipo"] == "mc" else fmt(Q["valor"])
            q["fb"] = f"Resposta certa: {resp}\n{Q['exp']}{self.texto_run(Q)}"
            q["ok"], q["fase"] = False, "fb"
            self.tocar("erro")

    def proxima_pergunta(self):
        q = self.quiz
        q["i"] += 1
        if q["i"] >= len(q["qs"]):
            ac, tot = q["ac"], len(q["qs"])
            self.quiz = None
            if ac / tot >= 0.7:
                self.quiz_passou(ac, tot)
            else:
                self.falar("Guardião Bit", [f"Você acertou {ac} de {tot}. Precisa de pelo menos 70%. Não desanime! Aperte R para rever a aula e fale comigo de novo."])
            return
        q.update({"fase": "ask", "sel": 0, "tent": 1, "txt": "", "aviso": "", "dica": "", "ok": None, "fb": ""})

    def quiz_passou(self, ac, tot):
        lv = self.lv
        n = lv["n"]
        lv["quiz_done"] = True
        bonus = 0
        if n not in ESTADO["concluidas"]:
            bonus = 20 + 5 * n
            ESTADO["xp"] += bonus
            ESTADO["concluidas"].append(n)
        salvar()
        self.tocar("nivel")
        self.confete = [[random.randrange(W), random.randrange(-200, 0), random.uniform(2, 5),
                         random.choice(["#ffd600", "#e53935", "#29b6f6", "#76ff03", "#f06292"])] for _ in range(90)]
        txt1 = f"FASE CONCLUÍDA! Você acertou {ac} de {tot}." + (f"\nBônus: +{bonus} XP" if bonus else "\n(Fase já concluída antes: sem XP extra)")
        txt1 += f"\nXP total: {ESTADO['xp']}\nPatente: {patente()}"

        def fim():
            if n == len(NIVEIS):
                self.scene, self.dirty = "fim", True
            else:
                self.toast("Porta da próxima fase liberada! Saia pela porta de baixo.", 160)
        self.falar("BÔNUS DE APRENDIZADO", [txt1, "CURIOSIDADE:\n" + NIVEIS[n - 1]["cur"]], fim, "bonus")

    def atualiza_confete(self):
        for cf in self.confete:
            cf[1] += cf[2]
        self.confete = [cf for cf in self.confete if cf[1] < H]

    # ───────────────────────────── DESENHO ─────────────────────────────
    def draw(self):
        c = self.c
        if self.dirty:
            c.delete("all")
            self.dirty = False
            if self.scene == "room":
                for y, row in enumerate(self.room["tiles"]):
                    for x, ch in enumerate(row):
                        c.create_image(x * TILE, OY + y * TILE, image=self.A.tiles[ch], anchor="nw")
        c.delete("dyn")
        s = self.scene
        if s == "title":
            self.draw_title()
        elif s == "nome":
            self.draw_nome()
        elif s == "room":
            self.draw_room()
        elif s == "fim":
            self.draw_fim()

    def txt(self, x, y, t, cor="#ffffff", fonte=FONT, anchor="nw", sombra=False, **kw):
        if sombra:
            self.c.create_text(x + 2, y + 2, text=t, fill="#000000", font=fonte, anchor=anchor, tags="dyn", **kw)
        return self.c.create_text(x, y, text=t, fill=cor, font=fonte, anchor=anchor, tags="dyn", **kw)

    def draw_title(self):
        c, A, f = self.c, self.A, self.frame
        c.create_rectangle(0, 0, W, H, fill="#0b1040", outline="", tags="dyn")
        for i, (sx, sy) in enumerate(self.stars):
            if (f // 10 + i) % 5:
                c.create_rectangle(sx, sy, sx + 3, sy + 3, fill="#ffffff", outline="", tags="dyn")
        for x in range(0, W, TILE):
            c.create_image(x, H - 96, image=A.tiles["."], anchor="nw", tags="dyn")
            c.create_image(x, H - 64, image=A.tiles["#"], anchor="nw", tags="dyn")
            c.create_image(x, H - 32, image=A.tiles["#"], anchor="nw", tags="dyn")
        self.txt(W // 2 + 4, 74, "DATA QUEST", "#7b1fa2", FONT_T, "center")
        self.txt(W // 2, 70, "DATA QUEST", "#ffd600", FONT_T, "center")
        self.txt(W // 2, 118, "A Aventura da Análise de Dados", "#ffffff", FONT_B, "center")
        c.create_image(W // 2 - 40, 150, image=A.hero_big, anchor="nw", tags="dyn")
        # desfile de personagens
        off = (f * 2) % (W + 200)
        for i, img in enumerate([A.hero[((f // 6) % 2, 1)], A.coin, A.bug, A.mentor]):
            c.create_image(off - 60 * i - 40, H - 128, image=img, anchor="nw", tags="dyn")
        ops = ["NOVO JOGO"] + (["CONTINUAR"] if self.tem_save else [])
        for i, o in enumerate(ops):
            cor = "#ffd600" if i == self.sel else "#9e9e9e"
            self.txt(W // 2, 275 + i * 34, ("> " if i == self.sel else "  ") + o, cor, FONT_B, "center")
        if (f // 15) % 2:
            self.txt(W // 2, 360, "SETAS escolhem  -  ENTER confirma", "#ffffff", FONT_S, "center")

    def draw_nome(self):
        c = self.c
        c.create_rectangle(0, 0, W, H, fill="#0b1040", outline="", tags="dyn")
        self.txt(W // 2, 150, "Qual é o seu nome, futuro(a) analista?", "#ffffff", FONT_B, "center")
        cur = "_" if (self.frame // 12) % 2 else " "
        self.txt(W // 2, 220, self.nome_txt + cur, "#ffd600", FONT_T, "center")
        self.txt(W // 2, 300, "Digite e aperte ENTER", "#9e9e9e", FONT, "center")

    def draw_room(self):
        c, A, lv, f = self.c, self.A, self.lv, self.frame
        hub = self.room["kind"] == "hub"
        # decorações das portas
        if hub:
            for i, col in enumerate(HUB_DOORS):
                n = i + 1
                x = col * TILE
                self.txt(x + 16, OY + 14, str(n), "#ffffff", FONT_B, "center", sombra=True)
                if not self.porta_aberta(col):
                    c.create_image(x, OY, image=A.lock, anchor="nw", tags="dyn")
                elif n in ESTADO["concluidas"]:
                    c.create_image(x + 8, OY + 18, image=A.star, anchor="nw", tags="dyn")
        else:
            self.txt(9 * TILE + 16, OY + (ROWS - 1) * TILE + 14, "SAIDA", "#ffffff", FONT_S, "center", sombra=True)
        ents = []
        for n in self.room["npcs"]:
            ents.append((n["ty"] * TILE, "npc", n))
        if lv:
            for b in lv["bugs"]:
                ents.append((b["y"], "bug", b))
            for it in lv["itens"]:
                if not it["got"]:
                    ents.append((it["ty"] * TILE, "item", it))
        ents.append((self.p["y"], "player", self.p))
        for _, kind, e in sorted(ents, key=lambda t: t[0]):
            if kind == "npc":
                x, y = e["tx"] * TILE, OY + e["ty"] * TILE
                c.create_image(x, y, image=e["img"], anchor="nw", tags="dyn")
                self.txt(x + 16, y - 2, e["nome"], "#ffd600", FONT_S, "s", sombra=True)
                if self.npc_tem_aviso(e) and (f // 10) % 2:
                    self.txt(x + 16, y - 16, "!", "#ff5252", FONT_B, "s", sombra=True)
            elif kind == "bug":
                c.create_image(e["x"], OY + e["y"], image=A.bug, anchor="nw", tags="dyn")
            elif kind == "item":
                bob = int(3 * math.sin((f + e["tx"] * 7) / 5))
                x, y = e["tx"] * TILE, OY + e["ty"] * TILE + bob
                c.create_image(x, y, image=A.coin, anchor="nw", tags="dyn")
                tid = self.txt(x + 16, y - 3, e["label"], "#ffffff", FONT_S, "s")
                bb = c.bbox(tid)
                if bb:
                    c.create_rectangle(bb[0] - 2, bb[1] - 1, bb[2] + 2, bb[3] + 1, fill="#000000", outline="#555555", tags="dyn")
                    c.tag_raise(tid)
            else:
                if lv and lv["invul"] > 0 and (f // 3) % 2:
                    continue
                img = A.hero[((e["anim"] // 6) % 2, e["dir"])]
                c.create_image(e["x"], OY + e["y"], image=img, anchor="nw", tags="dyn")
        for x, y, vy, cor in self.confete:
            c.create_rectangle(x, y, x + 6, y + 6, fill=cor, outline="", tags="dyn")
        self.draw_hud(hub)
        if self.toast_t > 0:
            tid = self.txt(W // 2, OY + 8, embrulhar(self.toast_msg, 56), "#ffffff", FONT, "n", justify="center")
            bb = c.bbox(tid)
            if bb:
                c.create_rectangle(bb[0] - 8, bb[1] - 5, bb[2] + 8, bb[3] + 5, fill="#1a1a4a", outline="#ffd600", width=2, tags="dyn")
                c.tag_raise(tid)
        if self.dialog:
            self.draw_dialog()
        if self.quiz:
            self.draw_quiz()
        if self.pausa:
            c.create_rectangle(120, 150, W - 120, 330, fill="#0b0b3a", outline="#ffffff", width=3, tags="dyn")
            self.txt(W // 2, 175, "PAUSA", "#ffd600", FONT_B, "n")
            self.txt(W // 2, 215, "ENTER ou ESC: continuar\nM: som " + ("LIGADO" if ESTADO["som"] else "DESLIGADO") + "\nQ: salvar e sair", "#ffffff", FONT, "n", justify="center")

    def npc_tem_aviso(self, n):
        lv = self.lv
        if n["id"] == "hub":
            return not ESTADO["concluidas"]
        if n["id"] == "mestre":
            return not lv["lesson_done"]
        return lv["lesson_done"] and lv["collect_done"] and not lv["quiz_done"]

    def draw_hud(self, hub):
        c, A = self.c, self.A
        c.create_rectangle(0, 0, W, HUD_TOP, fill="#111111", outline="", tags="dyn")
        c.create_rectangle(0, H - HUD_BOT, W, H, fill="#111111", outline="", tags="dyn")
        vidas = 3 if hub else self.lv["vidas"]
        for i in range(3):
            c.create_image(8 + i * 28, 8, image=A.heart if i < vidas else A.heart_off, anchor="nw", tags="dyn")
        self.txt(100, 20, f"XP {ESTADO['xp']}", "#ffd600", FONT, "w")
        titulo = "VILA DOS DADOS" if hub else f"FASE {self.lv['n']}: {NIVEIS[self.lv['n'] - 1]['nome']}"
        self.txt(W - 8, 12, titulo, "#ffffff", FONT_S, "ne")
        self.txt(W - 8, 28, f"{ESTADO['nome']} - {patente()}", "#9e9e9e", FONT_S, "ne")
        # status da missão
        if hub:
            st = "Entre numa porta numerada. Cadeado = fase bloqueada."
        else:
            lv = self.lv
            N = NIVEIS[lv["n"] - 1]
            if not lv["lesson_done"]:
                st = "Fale com o MESTRE (chegue perto e aperte E)"
            elif not lv["collect_done"]:
                st = f"MISSÃO: {N['missao']} ({lv['bons']}/{lv['bons_total']})"
                if N.get("soma"):
                    st += f"  Soma: {lv['soma']}"
            elif not lv["quiz_done"]:
                st = "Fale com o GUARDIÃO para o desafio!"
            else:
                st = "Fase concluída! Saia pela porta de baixo."
        self.txt(8, H - HUD_BOT + 8, st, "#ffd600", FONT_S, "nw")
        self.txt(8, H - HUD_BOT + 32, "SETAS/WASD mover | E falar | R rever aula | M som | ESC pausa", "#9e9e9e", FONT_S, "nw")

    def draw_dialog(self):
        c, d = self.c, self.dialog
        bonus = d["estilo"] == "bonus"
        c.create_rectangle(8, 276, W - 8, H - 8, fill="#2a0a4a" if bonus else "#0b0b3a", outline="#ffffff", width=3, tags="dyn")
        wq = max(120, len(d["quem"]) * 10 + 24)
        c.create_rectangle(20, 262, 20 + wq, 288, fill="#ffd600", outline="#ffffff", width=2, tags="dyn")
        self.txt(32, 275, d["quem"], "#000000", FONT, "w")
        self.txt(24, 298, d["wrapped"][:d["chars"]], "#ffffff", FONT)
        if d["chars"] >= len(d["wrapped"]) and (self.frame // 10) % 2:
            self.txt(W - 26, H - 20, "v", "#ffd600", FONT_B, "se")
        self.txt(W - 40, 275, f"{d['i'] + 1}/{len(d['pages'])}", "#9e9e9e", FONT_S, "e")

    def draw_quiz(self):
        c, q = self.c, self.quiz
        Q = q["qs"][q["i"]]
        c.create_rectangle(14, OY + 6, W - 14, H - 8, fill="#0b0b3a", outline="#ffffff", width=3, tags="dyn")
        self.txt(26, OY + 14, f"DESAFIO DO GUARDIÃO  -  pergunta {q['i'] + 1}/{len(q['qs'])}", "#ffd600", FONT_S)
        y = OY + 38
        corpo = embrulhar(Q["q"], 58)
        self.txt(26, y, corpo, "#ffffff", FONT)
        y += 20 * (corpo.count("\n") + 1) + 12
        if q["fase"] == "ask":
            if Q["tipo"] == "mc":
                for i, o in enumerate(Q["op"]):
                    sel = i == q["sel"]
                    t = embrulhar(f"{i + 1}) {o}", 54).replace("\n", "\n    ")
                    self.txt(26, y, ("> " if sel else "  ") + t, "#ffd600" if sel else "#cccccc", FONT)
                    y += 20 * (t.count("\n") + 1) + 6
                self.txt(26, H - 52, "SETAS escolhem, ENTER confirma (ou tecle 1-4). H = dica", "#9e9e9e", FONT_S)
            else:
                cur = "_" if (self.frame // 12) % 2 else " "
                c.create_rectangle(26, y, 260, y + 34, fill="#000000", outline="#ffd600", width=2, tags="dyn")
                self.txt(34, y + 17, q["txt"] + cur, "#ffffff", FONT_B, "w")
                self.txt(26, H - 52, "Digite o número e aperte ENTER. H = dica", "#9e9e9e", FONT_S)
                y += 44
            if q["dica"]:
                self.txt(26, H - 94, embrulhar("DICA: " + q["dica"], 64), "#4fc3f7", FONT_S)
            if q["aviso"]:
                self.txt(26, H - 72, q["aviso"], "#ff8a80", FONT_S)
        else:
            self.txt(26, y, embrulhar(q["fb"], 60), "#76ff03" if q["ok"] else "#ff8a80", FONT)
            self.txt(26, H - 30, "ENTER continua", "#ffd600", FONT_S)

    def draw_fim(self):
        c, A, f = self.c, self.A, self.frame
        c.create_rectangle(0, 0, W, H, fill="#0b1040", outline="", tags="dyn")
        for i, (sx, sy) in enumerate(self.stars):
            if (f // 10 + i) % 5:
                c.create_rectangle(sx, sy, sx + 3, sy + 3, fill="#ffffff", outline="", tags="dyn")
        self.txt(W // 2, 40, "DIPLOMA DATA QUEST", "#ffd600", FONT_B, "n", sombra=True)
        c.create_image(W // 2 - 40, 80, image=A.hero_big, anchor="nw", tags="dyn")
        self.txt(W // 2, 175, f"{ESTADO['nome']} concluiu todas as fases!", "#ffffff", FONT_B, "n")
        self.txt(W // 2, 200, f"XP total: {ESTADO['xp']}   Patente: {patente()}", "#76ff03", FONT, "n")
        self.txt(40, 245,
                 "O QUE VOCÊ APRENDEU\n"
                 "  - O ciclo do analista e os tipos de análise\n"
                 "  - Tipos de variáveis e leitura de tabelas\n"
                 "  - Média, mediana, moda e outliers\n"
                 "  - Limpeza de dados\n"
                 "  - Python: listas, dicionários, filtros e agrupamentos\n"
                 "  - Gráficos certos e como comunicar resultados\n\n"
                 "PRÓXIMOS PASSOS: pandas e matplotlib, SQL, Power BI/Tableau,\n"
                 "estatística e 2-3 projetos de portfólio (Kaggle, dados.gov.br).",
                 "#ffffff", FONT_S)
        if (f // 15) % 2:
            self.txt(W // 2, H - 24, "ENTER para sair", "#ffd600", FONT_S, "s")


def main():
    root = tk.Tk()
    Jogo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
