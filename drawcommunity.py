import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import Louvain

if __name__=='__main__':
    path=(r'data\trust.csv')
    G = Louvain.load_graph(path)
    algorithm = Louvain.Louvain(G)
    communities = algorithm.execute()
    G1=nx.Graph()
    for c in communities:
        for i in c:
            G1.add_node(i)
            for j in c:
                if i==j:
                    continue
                G1.add_edge(i,j)

    nx.draw(G1,node_size=10,width=2)
    plt.show()