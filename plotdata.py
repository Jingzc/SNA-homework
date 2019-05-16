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
def floatrange(start,stop,steps):
    ''' Computes a range of floating value.

        Input:
            start (float)  : Start value.
            end   (float)  : End value
            steps (integer): Number of values

        Output:
            A list of floats

        Example:
            >>> print floatrange(0.25, 1.3, 5)
            [0.25, 0.51249999999999996, 0.77500000000000002, 1.0375000000000001, 1.3]
    '''
    return [start+float(i)*(stop-start)/(float(steps)-1) for i in range(steps)]

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
    '''
    setdata=set(data2)
    dictdata={}
    for item in setdata:
        dictdata.update({item:data2.count(item)})
    '''    
    plt.figure()
    #plt.scatter(x,y,color='red')
    #plt.scatter(x1,y1,color='red')
    bins=[0.25,0.75,1.25,1.75,2.25,2.75,3.25,3.75,4.25]
    plt.hist(data2,bins,rwidth=0.5)
    plt.xlabel('ratings',size=18)
    plt.ylabel('rating numbers',size=18)
    plt.show()
    



        