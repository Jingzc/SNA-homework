import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
def loaddata(path):
    data=pd.read_csv(path,header=None,sep=' ')
    datapre=[]
    for i in range(len(data)):
        lst=list(data.iloc[i])
        datapre.append(lst)
    return datapre

if __name__=='__main__':
    path=(r'data\ratings.csv')
    data=loaddata(path)
    data1=[]
    data2=[]
    count=0
    for line in data:
        if data1==[] and count==0:
            i=line[0]
        if i==line[0]:
            count+=1
        else:
            data1.append([i,count])
            count=1
            i=line[0]
    for line in data:
        data2.append(line[2])
    y=[]
    x=[]
    for line in data1:
        y.append(line[1])
    y.sort(reverse=True)
    x=[(i+1) for i in range(len(y))]
    x1=[math.log(i) for i in x]
    y1=[math.log(i) for i in y]
    plt.figure()
    plt.plot(x,y)
    #plt.plot(x1,y1)
    plt.show()
    



        