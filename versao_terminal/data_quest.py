#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║  DATA QUEST - Aprenda Análise de Dados jogando           ║
╚══════════════════════════════════════════════════════════╝
Como rodar:   python data_quest.py      (Python 3.8+, não precisa instalar nada)
O progresso é salvo automaticamente em "progresso_dataquest.json".
"""
import builtins
import copy
import json
import os
import statistics
import textwrap

ARQUIVO_SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progresso_dataquest.json")
ESTADO = {"nome": "", "xp": 0, "concluidas": []}

# ──────────────────────────── DADOS DO JOGO ────────────────────────────
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
SERIE = [10, 12, 12, 13, 14, 15, 16, 48]  # vendas diárias de uma loja


def faturamento(v):
    return v["preco"] * v["qtd"]


def por_chave(chave):
    d = {}
    for v in VENDAS:
        d[v[chave]] = d.get(v[chave], 0) + faturamento(v)
    return d


# ──────────────────────────── INTERFACE ────────────────────────────
def limpar():
    os.system("cls" if os.name == "nt" else "clear")


def linha(c="═"):
    print(c * 60)


def titulo(t):
    linha()
    print(t.center(60))
    linha()


def esperar(msg="\n(Enter para continuar) "):
    input(msg)


def texto(s):
    print(textwrap.dedent(s).strip("\n"))


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",") if isinstance(x, float) else str(x)


def mostrar_vendas():
    cols = ["produto", "categoria", "regiao", "preco", "qtd"]
    print("    " + "".join(c.ljust(13) for c in cols))
    for i, v in enumerate(VENDAS):
        print(f"{i:<4}" + "".join(str(v[c]).ljust(13) for c in cols))


def patente():
    n = len(ESTADO["concluidas"])
    nomes = [(0, "Estagiário de Dados 🐣"), (2, "Analista Júnior 📊"), (4, "Analista Pleno 📈"),
             (6, "Analista Sênior 🧠"), (8, "Analista de Dados Certificado 🎓")]
    atual = nomes[0][1]
    for minimo, nome in nomes:
        if n >= minimo:
            atual = nome
    return atual


def status():
    print(f"👤 {ESTADO['nome']}  |  ⭐ {ESTADO['xp']} XP  |  🏅 {patente()}  |  "
          f"Fases: {len(ESTADO['concluidas'])}/{len(FASES)}")


# ──────────────────────────── SAVE ────────────────────────────
def salvar():
    try:
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
            json.dump(ESTADO, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def carregar():
    try:
        with open(ARQUIVO_SAVE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ──────────────────────────── MOTOR DE PERGUNTAS ────────────────────────────
def _avaliar(checker, certa_txt, explicacao, dica=None, prompt="➜ Sua resposta"):
    tentativa, dica_usada = 1, False
    while tentativa <= 2:
        extra = " (ou digite dica)" if dica and not dica_usada else ""
        r = input(f"{prompt}{extra}: ").strip()
        if r.lower() == "dica" and dica and not dica_usada:
            dica_usada = True
            ESTADO["xp"] = max(0, ESTADO["xp"] - 3)
            print(f"💡 Dica (-3 XP): {dica}")
            continue
        if checker(r):
            ganho = 10 if tentativa == 1 else 5
            ESTADO["xp"] += ganho
            print(f"✅ Correto! +{ganho} XP")
            print(f"   {explicacao}")
            return True
        if tentativa == 1:
            print("❌ Não foi dessa vez. Você tem mais uma chance!")
        tentativa += 1
    print(f"❌ A resposta era: {certa_txt}")
    print(f"   {explicacao}")
    return False


def multipla(enun, opcoes, certa, explicacao, dica=None):
    print("\n" + enun)
    for i, o in enumerate(opcoes):
        print(f"   {'ABCD'[i]}) {o}")
    letra = "ABCD"[certa]
    return _avaliar(lambda r: r.upper() == letra, f"{letra}) {opcoes[certa]}", explicacao, dica,
                    "➜ Escolha A, B, C ou D")


def numerica(enun, valor, explicacao, dica=None, tol=0.01):
    print("\n" + enun)

    def chk(r):
        try:
            return abs(float(r.replace(",", ".")) - valor) <= tol
        except ValueError:
            return False

    return _avaliar(chk, fmt(float(valor)) if isinstance(valor, float) else str(valor), explicacao, dica,
                    "➜ Digite o número")


SEGUROS = ["sum", "len", "min", "max", "sorted", "range", "round", "abs", "list", "dict", "set", "tuple",
           "str", "int", "float", "enumerate", "zip", "print", "any", "all", "map", "filter", "reversed",
           "bool", "isinstance"]


def executar(src, dados):
    env = {"__builtins__": {n: getattr(builtins, n) for n in SEGUROS}}
    env.update(copy.deepcopy(dados))
    exec(src, env)
    return env.get("resultado", None)


def iguais(a, b):
    if a is None or isinstance(a, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 0.05
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(iguais(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return sorted(map(str, a)) == sorted(map(str, b))
    return a == b


def codigo(enun, esperado, explicacao, solucao, dica=None):
    dados = {"vendas": VENDAS}
    print("\n" + enun)
    print("   ✍️  Escreva seu código e termine com uma LINHA VAZIA. Guarde a resposta em 'resultado'.")
    print("   (digite 'dica' para uma dica por -3 XP, ou 'pular' para ver a solução)")
    tentativa, dica_usada = 1, False
    while tentativa <= 3:
        linhas = []
        while True:
            l = input(">>> " if not linhas else "... ")
            if l.strip() == "":
                if linhas:
                    break
                continue
            linhas.append(l)
            if len(linhas) == 1 and l.strip().lower() in ("dica", "pular"):
                break
        src = "\n".join(linhas)
        if src.strip().lower() == "dica":
            if dica and not dica_usada:
                dica_usada = True
                ESTADO["xp"] = max(0, ESTADO["xp"] - 3)
                print(f"💡 Dica (-3 XP): {dica}")
            else:
                print("💡 Sem mais dicas disponíveis.")
            continue
        if src.strip().lower() == "pular":
            break
        try:
            res = executar(src, dados)
        except Exception as e:  # erro do usuário: mostramos de forma amigável
            print(f"⚠️  Seu código deu erro: {type(e).__name__}: {e}")
            tentativa += 1
            continue
        print(f"📦 resultado = {res!r}")
        if iguais(res, esperado):
            ganho = {1: 15, 2: 10, 3: 5}[tentativa]
            ESTADO["xp"] += ganho
            print(f"✅ Código correto! +{ganho} XP")
            print(f"   {explicacao}")
            return True
        print("❌ O resultado não bate com o esperado." + (" Tente de novo!" if tentativa < 3 else ""))
        tentativa += 1
    print("📖 Solução de exemplo:")
    for l in solucao.split("\n"):
        print("     " + l)
    print(f"   {explicacao}")
    return False


# ──────────────────────────── FASES ────────────────────────────
def fase1():
    texto("""
    Análise de dados é transformar dados brutos em respostas que
    ajudam alguém a TOMAR UMA DECISÃO melhor.

    O CICLO DO ANALISTA
      1. PERGUNTAR   - qual problema queremos resolver?
      2. COLETAR     - de onde vêm os dados? (planilhas, bancos, APIs)
      3. LIMPAR      - corrigir erros, duplicados e valores faltantes
      4. ANALISAR    - calcular, comparar, buscar padrões
      5. VISUALIZAR  - gráficos e tabelas que facilitam entender
      6. COMUNICAR   - contar a história e recomendar ações

    OS 4 TIPOS DE ANÁLISE
      Descritiva    -> O que aconteceu?
      Diagnóstica   -> Por que aconteceu?
      Preditiva     -> O que vai acontecer?
      Prescritiva   -> O que devemos fazer?
    """)
    esperar("\n(Enter para começar o desafio) ")
    q = []
    q.append(multipla("1) Antes de abrir qualquer planilha, qual é o primeiro passo?",
                      ["Fazer um gráfico bonito", "Entender a pergunta que precisa ser respondida",
                       "Rodar um modelo de IA", "Apagar linhas com erro"], 1,
                      "Sem uma boa pergunta, você pode analisar muito e não resolver nada."))
    q.append(multipla("2) 'Quanto vendemos no mês passado?' é uma análise...",
                      ["Descritiva", "Prescritiva", "Diagnóstica", "Preditiva"], 0,
                      "Ela só descreve o que já aconteceu."))
    q.append(multipla("3) 'Por que as vendas caíram em março?' é uma análise...",
                      ["Descritiva", "Prescritiva", "Diagnóstica", "Preditiva"], 2,
                      "Diagnóstica busca as CAUSAS de um resultado.", dica="Busca o 'porquê'."))
    q.append(multipla("4) Por que limpar os dados antes de analisar?",
                      ["Para deixar a planilha mais bonita", "Porque é exigência legal",
                       "Para o computador rodar mais rápido",
                       "Porque dados com erro levam a conclusões erradas"], 3,
                      "Lixo entra, lixo sai (garbage in, garbage out)."))
    return q


def fase2():
    print("Dados costumam vir em TABELAS. Veja a tabela de vendas que usaremos no jogo:\n")
    mostrar_vendas()
    texto("""

    LINHAS   = registros (cada venda)       COLUNAS = variáveis (atributos)

    TIPOS DE VARIÁVEIS
      Numérica discreta   -> contagens (qtd de itens: 1, 2, 3...)
      Numérica contínua   -> medidas com decimais (preço, peso)
      Categórica nominal  -> categorias sem ordem (região, cor)
      Categórica ordinal  -> categorias COM ordem (P < M < G)
    """)
    esperar("\n(Enter para começar o desafio) ")
    q = []
    q.append(numerica("1) Quantas LINHAS (registros) tem a tabela de vendas?", len(VENDAS),
                      "Cada linha é uma venda registrada."))
    q.append(numerica("2) Quantas COLUNAS (variáveis) ela tem?", 5,
                      "produto, categoria, regiao, preco e qtd."))
    q.append(multipla("3) A coluna 'regiao' é de que tipo?",
                      ["Numérica contínua", "Categórica nominal", "Numérica discreta", "Data"], 1,
                      "São categorias sem ordem natural."))
    q.append(multipla("4) A coluna 'qtd' (unidades vendidas) é:",
                      ["Categórica", "Numérica discreta (contagem)", "Numérica contínua", "Texto livre"], 1,
                      "Você não vende 2,5 camisetas: é uma contagem."))
    q.append(multipla("5) Tamanho de camiseta (P, M, G, GG) é uma variável:",
                      ["Categórica ordinal", "Numérica contínua", "Categórica nominal", "Numérica discreta"], 0,
                      "São categorias, mas existe uma ordem entre elas."))
    return q


def fase3():
    print(f"Vendas diárias de uma loja: {SERIE}\n")
    texto("""
    ESTATÍSTICA DESCRITIVA - resumir muitos números em poucos:
      MÉDIA    = soma dos valores / quantidade de valores
      MEDIANA  = valor do MEIO quando ordenados (se par: média dos 2 do meio)
      MODA     = valor que MAIS se repete
      AMPLITUDE= maior valor - menor valor

    Atenção: a média é sensível a valores extremos (outliers);
    a mediana é mais resistente.
    """)
    esperar("\n(Enter para começar o desafio) ")
    media, mediana, moda = statistics.mean(SERIE), statistics.median(SERIE), statistics.mode(SERIE)
    q = []
    q.append(numerica("1) Qual é a MÉDIA das vendas diárias?", media,
                      f"Soma {sum(SERIE)} / {len(SERIE)} dias = {fmt(media)}.", tol=0.05))
    q.append(numerica("2) Qual é a MEDIANA?", mediana,
                      "Ordenados, os dois do meio são 13 e 14: (13+14)/2 = 13,5.", tol=0.05,
                      dica="A lista já está ordenada. Pegue os 2 valores centrais."))
    q.append(numerica("3) Qual é a MODA?", moda, "O 12 aparece duas vezes: é o mais frequente."))
    q.append(numerica("4) Qual é a AMPLITUDE (maior - menor)?", max(SERIE) - min(SERIE),
                      "48 - 10 = 38."))
    q.append(multipla("5) O dia com 48 vendas é atípico. Qual medida representa melhor o 'dia normal'?",
                      ["A média", "A mediana", "A amplitude", "A soma"], 1,
                      "A média (17,5) foi puxada pelo outlier; a mediana (13,5) é mais fiel ao dia típico."))
    return q


def fase4():
    texto("""
    Dados do mundo real vêm SUJOS. Os problemas mais comuns:
      • Valores nulos (faltantes)      • Linhas duplicadas
      • Outliers (valores absurdos)    • Formatos inconsistentes ('SP' x 'São Paulo')
      • Tipos errados (número guardado como texto)

    Veja esta tabela de clientes:
    """)
    print("""
        nome      idade
      0 Ana       25
      1 Bruno     (vazio)
      2 Ana       25
      3 Carla     230
      4 Diego     31
    """)
    esperar("(Enter para começar o desafio) ")
    q = []
    q.append(numerica("1) Quantos valores FALTANTES existem?", 1, "A idade do Bruno está vazia."))
    q.append(numerica("2) Quantas linhas DUPLICADAS existem?", 1,
                      "A linha 2 repete exatamente a linha 0 (Ana, 25)."))
    q.append(multipla("3) Qual valor parece um OUTLIER (erro de digitação)?",
                      ["25", "31", "230", "Ana"], 2, "Ninguém tem 230 anos: provavelmente era 23 ou 30."))
    q.append(multipla("4) Qual o melhor tratamento para a idade faltante do Bruno?",
                      ["Preencher com 0", "Apagar a tabela inteira",
                       "Investigar a fonte ou preencher pela mediana, documentando a decisão",
                       "Ignorar e seguir"], 2,
                      "Preencher com 0 distorceria a média. Sempre documente o que você fez."))
    return q


def fase5():
    texto("""
    Python é a linguagem favorita dos analistas. Vocabulário mínimo:

      numeros = [10, 20, 30]                 # lista
      len(numeros)                           # 3   (quantidade)
      sum(numeros)                           # 60  (soma)
      sum(numeros) / len(numeros)            # 20.0 (média)
      linha = {"produto": "Boné", "qtd": 8}  # dicionário (uma linha da tabela)
      linha["qtd"]                           # 8
      [v["qtd"] for v in vendas]             # lista só com as quantidades

    Neste jogo existe a variável  vendas  = lista de dicionários, uma
    para cada linha da tabela da Fase 2. Guarde sempre a resposta em  resultado.
    Exemplo:   resultado = len(vendas)       # -> 8

    🐼 No mundo real você usaria o pandas:  df["qtd"].sum()
    """)
    esperar("\n(Enter para começar o desafio) ")
    q = []
    q.append(codigo("1) Calcule o TOTAL de unidades vendidas (soma da coluna qtd).",
                    sum(v["qtd"] for v in VENDAS), "Total: 55 unidades.",
                    'resultado = sum(v["qtd"] for v in vendas)',
                    dica='Use sum() em cima de uma lista com v["qtd"] para cada v em vendas.'))
    q.append(codigo("2) Calcule o FATURAMENTO total (preco x qtd de cada linha, somados).",
                    sum(faturamento(v) for v in VENDAS), "Faturamento total: R$ 4.770.",
                    'resultado = sum(v["preco"] * v["qtd"] for v in vendas)',
                    dica='Dentro do sum(), multiplique v["preco"] * v["qtd"].'))
    q.append(codigo("3) Calcule o PREÇO MÉDIO (média simples da coluna preco), com round(x, 2).",
                    round(sum(v["preco"] for v in VENDAS) / len(VENDAS), 2), "Preço médio: R$ 96,25.",
                    'resultado = round(sum(v["preco"] for v in vendas) / len(vendas), 2)',
                    dica="Média = soma / quantidade. Use sum() e len()."))
    return q


def fase6():
    texto("""
    Duas operações essenciais do analista:

    FILTRAR (ficar só com o que interessa)
      sul = [v for v in vendas if v["regiao"] == "Sul"]

    AGRUPAR (somar por categoria)
      total = {}
      for v in vendas:
          total[v["regiao"]] = total.get(v["regiao"], 0) + v["qtd"]

    Achar a chave com maior valor de um dicionário:
      max(total, key=total.get)

    🐼 pandas:  df[df.regiao == "Sul"]   e   df.groupby("regiao")["qtd"].sum()
    """)
    esperar("\n(Enter para começar o desafio) ")
    cat, reg = por_chave("categoria"), por_chave("regiao")
    q = []
    q.append(codigo('1) Gere uma LISTA com os nomes dos produtos vendidos na região "Sul".',
                    [v["produto"] for v in VENDAS if v["regiao"] == "Sul"], "Sul: Tênis e Mochila.",
                    'resultado = [v["produto"] for v in vendas if v["regiao"] == "Sul"]',
                    dica='List comprehension com um "if" no final.'))
    q.append(codigo("2) Gere um DICIONÁRIO com o faturamento (preco x qtd) por categoria.",
                    cat, "Calçados 2200, Roupas 1700, Acessórios 870.",
                    'resultado = {}\nfor v in vendas:\n    resultado[v["categoria"]] = resultado.get(v["categoria"], 0) + v["preco"] * v["qtd"]',
                    dica="Use o padrão acumulador: d[chave] = d.get(chave, 0) + valor. "
                         "Dica: no terminal, mantenha a indentação do 'for'."))
    q.append(codigo("3) Qual REGIÃO tem o maior faturamento? (guarde o nome em resultado)",
                    max(reg, key=reg.get), "Sudeste lidera com R$ 2.140.",
                    'fat = {}\nfor v in vendas:\n    fat[v["regiao"]] = fat.get(v["regiao"], 0) + v["preco"] * v["qtd"]\nresultado = max(fat, key=fat.get)',
                    dica="Agrupe por região (como no desafio 2) e use max(d, key=d.get)."))
    return q


def fase7():
    cat = por_chave("categoria")
    print("Faturamento por categoria (gráfico de barras em texto):\n")
    mx = max(cat.values())
    for k, val in sorted(cat.items(), key=lambda x: -x[1]):
        print(f"  {k.ljust(11)}|{'█' * int(val / mx * 30)} {val:.0f}")
    texto("""

    ESCOLHENDO O GRÁFICO CERTO
      Barras     -> comparar categorias
      Linha      -> evolução ao longo do tempo
      Dispersão  -> relação entre duas variáveis numéricas
      Histograma -> distribuição de uma variável
      Pizza      -> partes de um todo (poucas fatias!)

    BOAS PRÁTICAS: título claro, eixos nomeados, barras começando no zero.
    🐼 matplotlib:  plt.bar(categorias, valores); plt.show()
    """)
    esperar("(Enter para começar o desafio) ")
    nomes = ["Roupas", "Calçados", "Acessórios", "Todas empatam"]
    lider = max(cat, key=cat.get)
    q = []
    q.append(multipla("1) Qual categoria tem a maior barra no gráfico acima?", nomes, nomes.index(lider),
                      f"{lider} lidera com R$ {cat[lider]:.0f}."))
    q.append(multipla("2) Melhor gráfico para mostrar a EVOLUÇÃO das vendas mês a mês:",
                      ["Pizza", "Linha", "Dispersão", "Mapa"], 1, "Linhas mostram tendência no tempo."))
    q.append(multipla("3) Melhor gráfico para COMPARAR o faturamento entre 3 categorias:",
                      ["Barras", "Linha", "Dispersão", "Radar de 12 eixos"], 0,
                      "Barras permitem comparar tamanhos lado a lado."))
    q.append(multipla("4) Para ver a RELAÇÃO entre preço e quantidade vendida:",
                      ["Pizza", "Barras empilhadas", "Dispersão (scatter)", "Tabela de cores"], 2,
                      "Cada ponto é um produto: dá para ver se preço alto = menos vendas."))
    q.append(multipla("5) O que torna um gráfico de barras mais HONESTO?",
                      ["Cortar o eixo Y para exagerar diferenças", "Eixo começando em zero e título claro",
                       "Usar efeito 3D", "Usar o máximo de cores possível"], 1,
                      "Eixo truncado engana o olhar do leitor."))
    return q


def fase8():
    cat = por_chave("categoria")
    total = sum(faturamento(v) for v in VENDAS)
    unid = sum(v["qtd"] for v in VENDAS)
    u_cal = sum(v["qtd"] for v in VENDAS if v["categoria"] == "Calçados")
    pct_fat = cat["Calçados"] / total * 100
    pct_un = u_cal / unid * 100
    texto("""
    🔥 CHEFÃO FINAL 🔥
    O dono da loja pergunta: "Onde devo investir meu dinheiro?"
    Use TUDO o que aprendeu: perguntar, analisar, interpretar e comunicar.
    """)
    esperar("\n(Enter para enfrentar o chefão) ")
    q = []
    q.append(codigo("1) Calcule o TICKET MÉDIO POR UNIDADE (faturamento total / unidades totais), round(x, 2).",
                    round(total / unid, 2), "R$ 4.770 / 55 unidades = R$ 86,73 por unidade.",
                    'fat = sum(v["preco"] * v["qtd"] for v in vendas)\nun = sum(v["qtd"] for v in vendas)\nresultado = round(fat / un, 2)',
                    dica="Faturamento total (fase 5) dividido pelo total de unidades."))
    q.append(codigo('2) Qual o % do faturamento vem da categoria "Calçados"? Use round(x, 1) (ex.: 12.3).',
                    round(pct_fat, 1), "Calçados = 2200 de 4770, ou seja ~46%.",
                    'tot = sum(v["preco"] * v["qtd"] for v in vendas)\ncal = sum(v["preco"] * v["qtd"] for v in vendas if v["categoria"] == "Calçados")\nresultado = round(cal / tot * 100, 1)',
                    dica="Filtre só Calçados, some o faturamento e divida pelo total x 100."))
    q.append(multipla(f"3) Calçados geram {pct_fat:.0f}% do faturamento com {pct_un:.0f}% das unidades. "
                      "Qual conclusão os dados SUSTENTAM?",
                      ["Acessórios devem ser descontinuados já, pois vendem menos",
                       f"Calçados rendem muito por unidade: vale proteger o estoque e testar ampliar o mix",
                       "Todas as categorias são iguais, não há o que fazer",
                       "O Nordeste não vende nada"], 1,
                      "Boa análise liga o número a uma ação plausível, sem exagerar nem inventar."))
    q.append(multipla("4) Qual a melhor forma de apresentar isso ao dono da loja?",
                      ["Enviar a planilha inteira e deixar ele procurar",
                       "Um resumo: pergunta, 2 ou 3 achados com gráfico simples e uma recomendação",
                       "Um relatório de 40 páginas cheio de termos técnicos",
                       "Só dizer 'os dados mostram que...' sem mostrar nada"], 1,
                      "Comunicar bem = clareza, poucos pontos fortes e uma ação recomendada."))
    return q


CURIOSIDADES = [
    "O estatístico John Tukey, que popularizou a Análise Exploratória de Dados no livro de 1977, "
    "também foi quem criou o termo 'bit'.",
    "Em 2012, a Harvard Business Review chamou 'cientista de dados' de a profissão mais atraente do século XXI.",
    "Se Bill Gates entra em um bar, a renda MÉDIA dos clientes dispara, mas a MEDIANA quase não muda. "
    "É o exemplo clássico de por que olhar só a média pode enganar.",
    "Relatos do mercado costumam estimar que analistas gastam entre 50% e 80% do tempo coletando e limpando dados "
    "e só o restante analisando.",
    "O nome Python NÃO vem da cobra: vem do grupo de humor britânico Monty Python. "
    "A linguagem foi criada por Guido van Rossum e lançada em 1991.",
    "O pandas foi criado por Wes McKinney em 2008, quando trabalhava em um fundo de investimentos. "
    "O nome vem de 'panel data' (dados em painel).",
    "O Quarteto de Anscombe (1973) são 4 conjuntos de dados com quase a mesma média e variância, mas gráficos "
    "completamente diferentes. É a prova de que sempre vale VISUALIZAR os dados.",
    "Florence Nightingale, enfermeira e estatística, usou gráficos circulares criativos para convencer o governo "
    "britânico de que mais soldados morriam por doenças evitáveis do que em batalha. "
    "Foi data storytelling em pleno século XIX!",
]

FASES = [
    {"n": 1, "nome": "O que é Análise de Dados?", "fn": fase1},
    {"n": 2, "nome": "Conhecendo os Dados", "fn": fase2},
    {"n": 3, "nome": "Estatística Descritiva", "fn": fase3},
    {"n": 4, "nome": "Limpeza de Dados", "fn": fase4},
    {"n": 5, "nome": "Python na Prática", "fn": fase5},
    {"n": 6, "nome": "Filtrar e Agrupar", "fn": fase6},
    {"n": 7, "nome": "Visualização de Dados", "fn": fase7},
    {"n": 8, "nome": "CHEFÃO: Projeto Final", "fn": fase8},
]


# ──────────────────────────── LOOP DO JOGO ────────────────────────────
def jogar_fase(f):
    while True:
        limpar()
        status()
        titulo(f"FASE {f['n']}: {f['nome']}")
        resultados = f["fn"]()
        acertos, total = sum(resultados), len(resultados)
        print()
        linha("─")
        print(f"Resultado da fase: {acertos}/{total} acertos (mínimo para passar: 70%)")
        if acertos / total >= 0.7:
            bonus = 20 + 5 * f["n"]
            ESTADO["xp"] += bonus
            ESTADO["concluidas"].append(f["n"])
            salvar()
            print(f"🎉 FASE CONCLUÍDA! Bônus de {bonus} XP  ->  {patente()}")
            print("\n🎁 BÔNUS DE APRENDIZADO - CURIOSIDADE:")
            print(textwrap.fill(CURIOSIDADES[f["n"] - 1], 60, initial_indent="   ", subsequent_indent="   "))
            return True
        print("😅 Quase! Revise a aula e tente de novo.")
        if input("Tentar a fase novamente? (s/n): ").strip().lower() != "s":
            return False


def tela_final():
    limpar()
    titulo("🎓 DIPLOMA DATA QUEST 🎓")
    print(f"\n   {ESTADO['nome']} concluiu todas as fases com {ESTADO['xp']} XP!")
    print(f"   Patente: {patente()}\n")
    texto("""
    O QUE VOCÊ APRENDEU
      ✔ O ciclo do analista e os tipos de análise
      ✔ Tipos de variáveis e leitura de tabelas
      ✔ Média, mediana, moda e outliers
      ✔ Limpeza de dados
      ✔ Python: listas, dicionários, filtros e agrupamentos
      ✔ Escolha de gráficos e comunicação de resultados

    PRÓXIMOS PASSOS
      1. pandas e matplotlib (Python)       4. Estatística (probabilidade, testes)
      2. SQL (essencial para a profissão)   5. Montar 2 ou 3 projetos de portfólio
      3. Power BI ou Tableau (dashboards)      com dados reais (ex.: Kaggle, dados.gov.br)
    """)


def main():
    limpar()
    titulo("📊 DATA QUEST - Aprenda Análise de Dados 📊")
    salvo = carregar()
    if salvo and salvo.get("nome"):
        if input(f"\nEncontrei o progresso de {salvo['nome']}. Continuar? (s/n): ").strip().lower() == "s":
            ESTADO.update(salvo)
    if not ESTADO["nome"]:
        ESTADO["nome"] = input("\nQual é o seu nome, futuro(a) analista? ").strip() or "Jogador"
        texto("""

        COMO JOGAR
         • São 8 fases. Cada uma tem uma mini-aula e um desafio.
         • Precisa de 70% de acertos para passar de fase.
         • 1ª tentativa certa vale mais XP que a 2ª. Dicas custam 3 XP.
         • Ao concluir cada fase: bônus de XP + uma curiosidade da área.
         • Digite 'sair' quando for perguntado se quer seguir para salvar e parar.
        """)
        esperar()
    for f in FASES:
        if f["n"] in ESTADO["concluidas"]:
            continue
        if not jogar_fase(f):
            salvar()
            print("\nProgresso salvo. Até a próxima! 👋")
            return
        if f["n"] < len(FASES):
            if input("\n(Enter para a próxima fase, ou digite 'sair'): ").strip().lower() == "sair":
                salvar()
                print("Progresso salvo. Até a próxima! 👋")
                return
    salvar()
    tela_final()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        salvar()
        print("\n\nProgresso salvo. Até a próxima! 👋")
