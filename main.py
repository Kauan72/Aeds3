import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def menorElemento(a, b):
    if a<b:
        return a
    else:
        return b

#Separa os partidos a serem análisados em uma lista e retorna_a
def lista_de_partidos_em_análise(partidos_de_analise : str, arquivo_politicians):
    #Caso não haja nenhum partido desejado, todos são adicionados a lista de desejados
    arquivo_politicians.seek(0)
    if len(partidos_de_analise)==0:
        for line in arquivo_politicians:
            line = line.strip()
            elementos = line.split(";")
            if elementos[1] not in partidos:
                partidos.append(elementos[1])
    else:
        partidos_de_analise = partidos_de_analise.strip()
        elementos = partidos_de_analise.split(" ")
        for e in elementos:
            partidos.append(e)
    return partidos

def return_politicians_dict(partidos : list, arquivo_politicians):
    arquivo_politicians.seek(0)
    politicians_dict = {}
    #o politicians_dict é um dicionário de politicos que estão nos partidos desejados, os politicos são dicionários da quantidade de participações, que por sua vez são dicionários de partidos
    for line in arquivo_politicians:
        line = line.strip()
        elementos = line.split(";")
        if elementos[1] in partidos:
            politicians_dict[elementos[0]] = {}
            politicians_dict[elementos[0]][int(elementos[2])] = elementos[1]
    return politicians_dict

#op - 1 obtem o grafo com pesos normalizados com treshold e invertido
#op - 0 obtem o grafo com pesos normalizados
def make_graph(politicians_dict, arquivo_graph, threshold, g, op):
    g.clear()
    arquivo_graph.seek(0)
    #Cria o grafo somente com os partidos desejados verificando se a aresta corresponde a relação entre 2 integrantes desses partidos
    for line in arquivo_graph:
        line = line.strip()
        elementos = line.split(";")
        if elementos[0] in politicians_dict and elementos[1] in politicians_dict:
            #adquiri a quantidade de votações que cada um participou, esse valor está armazenado como uma key de dicionario que aponta pra um partido
            for key in politicians_dict[elementos[0]]:
                a = int(key)
            for key in politicians_dict[elementos[1]]:
                b = int(key)
            #Resgata o inteiro relacionado a quantidade de participações de votações do politico menos participativo entre os 2 e normaliza
            menor_participacao = menorElemento(a, b)
            normalizacao = int(elementos[2]) / menor_participacao

            if op == 1:
                #Caso a normalização esteja acima do trashhold, adiciona a aresta ao gráfico, já realizando a inversão de pesos para funções de caminho mínimo (1-normalização)
                if normalizacao > threshold:
                    peso = float(1-normalizacao)
                    for key in politicians_dict[elementos[0]]:
                        elementos[0] = elementos[0] + " " + f"({politicians_dict[elementos[0]][key]})"
                    for key in politicians_dict[elementos[1]]:
                        elementos[1] = elementos[1] + " " + f"({politicians_dict[elementos[1]][key]})"
                    g.add_edge(elementos[0], elementos[1], weight = peso)
            if op == 0:
                #adiciona os partidos na frente dos deputados
                for key in politicians_dict[elementos[0]]:
                    elementos[0] = elementos[0] + " " + f"({politicians_dict[elementos[0]][key]})"
                for key in politicians_dict[elementos[1]]:
                    elementos[1] = elementos[1] + " " + f"({politicians_dict[elementos[1]][key]})"
                g.add_edge(elementos[0], elementos[1], weight = normalizacao)

def betweeness_bar_graphic(centrality_dict):
    plt.clf()
    plt.figure()
    plt.title("Betweeness graphic")
    #Contrução de grafico de barras com os deputados e suas respectivas centralidades pelo betwenness
    fig, ax = plt.subplots()
    deputados = []
    deputados_centralidade = []
    
    for deputado in centrality_dict:
        deputados_centralidade.append(centrality_dict[deputado])
        deputados.append(deputado)    

    deputados_centralidade, deputados = zip(*sorted(zip(deputados_centralidade, deputados)))

    ax.bar(deputados, deputados_centralidade, label='blue', color='blue', align='center')
    plt.xticks(range(len(deputados)), deputados, rotation=45, ha='right', fontsize=2.25, y=0.01)
    plt.yticks(fontsize=2.25)
    
    ax.set_ylabel('centralidade')
    ax.set_title('deputados')

    plt.tight_layout()
    plt.savefig("betweenessGraphic.png", dpi=400)
    plt.close()

def heatmap_graphic(g):
    plt.clf()
    plt.figure()
    plt.title("HeatMap")
    # Crie uma matriz de adjacência ponderada a partir do grafo
    nodes = list(g.nodes())
    num_nodes = len(nodes)
    nodes = sorted(nodes, key=lambda x: x.rsplit(' ', 1)[-1])

    adj_matrix = np.zeros((num_nodes, num_nodes))
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes):
            if g.has_edge(node1, node2):
                weight = g[node1][node2]['weight']
                adj_matrix[i, j] = weight
    
    # Crie o mapa de calor usando a matriz de adjacência ponderada
    plt.figure(figsize=(8, 6))
    heatmap = plt.imshow(adj_matrix, cmap='hot', vmin=0, vmax=1)
    plt.colorbar(heatmap)
    plt.xticks(np.arange(num_nodes), nodes, rotation=55, ha="right", fontsize = 2.55, y=0.01)
    plt.yticks(np.arange(num_nodes), nodes, fontsize = 2.55)

    plt.savefig("heatMap.png", dpi=400)
    plt.close()

def plotGraphic(g):
    # Crie um dicionário de grupos para as cores
    group_colors = {}

    pos = nx.spring_layout(g)
    # Associe cores a cada grupo único
    for node in g.nodes():
        group = node.split("(")[-1].strip(")")
        if group not in group_colors:
            group_colors[group] = plt.cm.tab20(len(group_colors))
            
    # Atribua uma cor a cada nó com base no seu grupo
    node_colors = [group_colors[node.split("(")[-1].strip(")")] for node in g.nodes()]

    # Desenhe o grafo com as posições e cores dos nós
    nx.draw(g, pos, with_labels=True, node_size=200, node_color=node_colors, font_size=8)

    # Crie uma legenda para os grupos
    plt.legend(handles=[plt.Line2D([0], [0], marker='o', color='w', label=group, markersize=10, markerfacecolor=color)for group, color in group_colors.items()])
    plt.savefig("plotMap.png", dpi=400)
    plt.close()



partidos = []
politicians_dict = {}

ano = input("Qual o ano da análise? ")
threshold = float(input("Qual o threshold?"))
partidos_de_analise = input("Quais partidos serão analizados? formato exemplo(PT PSOL MDB), vazio caso queira todos os partidos em análise.")

g = nx.Graph()

arquivo_graph = open(f"datasets\graph{ano}.txt", "r", encoding="utf-8")
arquivo_politicians = open(f"datasets\politicians{ano}.txt", "r", encoding="utf-8")

partidos = lista_de_partidos_em_análise(partidos_de_analise, arquivo_politicians)
politicians_dict = return_politicians_dict(partidos, arquivo_politicians)

make_graph(politicians_dict, arquivo_graph, threshold, g, 1)
centrality_dict = nx.betweenness_centrality(g)
betweeness_bar_graphic(centrality_dict)

make_graph(politicians_dict, arquivo_graph, threshold, g, 0)
heatmap_graphic(g)

make_graph(politicians_dict, arquivo_graph, threshold, g, 1)
plotGraphic(g)