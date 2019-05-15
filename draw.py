import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
def loaddata(path):
    data=pd.read_csv(path,header=None,sep=' ')
    datapre=[]
    for i in range(len(data)):
        lst=list(data.iloc[i])
        datapre.append(lst)
    return datapre

if __name__=='__main__':
    path=(r'data\trust.csv')
    data=loaddata(path)
    G=nx.DiGraph()
    for line in data:
        del line[2]
        G.add_node(line[0])
        G.add_node(line[1])
        G.add_edge(line[0],line[1])
    nx.draw(G,node_size=10)
    plt.show()
