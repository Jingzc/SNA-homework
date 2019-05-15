import numpy as np
import pandas as pd
import math
import random
from scipy.sparse.linalg import gmres,lgmres
from scipy.sparse import csr_matrix
 
def genData():
    data=pd.read_csv(r'data\user_item_rating_community_communitylength.csv',header=None,sep=',')
    print("genData successed!")
    return data
 
def datapreprocess(data):
    datapre=[]
    for i in range(len(data)):
        lst=list(data.iloc[i])
        datapre.append(lst)
    print("datapre successed!")
    return datapre 
 
def SplitData(Data,M,k,seed):
    '''
    划分训练集和测试集
    :param data:传入的数据
    :param M:测试集占比
    :param k:一个任意的数字，用来随机筛选测试集和训练集
    :param seed:随机数种子，在seed一样的情况下，其产生的随机数不变
    :return:train:训练集 test：测试集，都是字典，key是用户id,value是电影id集合
    '''
    test=[]
    train=[]
    random.seed(seed)
    # 在M次实验里面我们需要相同的随机数种子，这样生成的随机序列是相同的
    for line in Data:
        if random.randint(0,M)==k:
            # 相等的概率是1/M，所以M决定了测试集在所有数据中的比例
            # 选用不同的k就会选定不同的训练集和测试集
            test.append(line)
        else:
            train.append(line)
    print("splitData successed!")
    #print(test)
    return train,test
 
def getTU(user,test,N):
    items=set()
    for line in test:
        if line[0]!=user:
            continue
        if line[0]==user:
            items.add(line[1])
    return list(items)
 
def Recall(train,test,AA,M,G,alpha,N,user_items):
    '''
    :param train: 训练集
    :param test: 测试集
    :param N: TopN推荐中N数目
    :param k:
    :return:返回召回率
    '''
    hit=0# 预测准确的数目
    totla=0# 所有行为总数
    for line in train:
        tu=getTU(line[0],test,N)
        rank=GetRecommendation(AA,M,G,alpha,line[0],N,user_items)
        for line[1] in rank:
            if line[1] in tu:
                hit+=1
        totla+=len(tu)
    print("Recall successed!",hit/(totla*1.0))
    return hit/(totla*1.0)
 
def Precision(train,test,AA,M,G,alpha,N,user_items):
    '''
    :param train:
    :param test:
    :param N:
    :param k:
    :return:
    '''
    hit=0
    total=0
    for line in train:
        tu = getTU(line[0], test, N)
        rank =GetRecommendation(AA,M,G,alpha,line[0],N,user_items)
        for line[1] in rank:
            if line[1] in tu:
                hit += 1
        total += N
    print("Precision successed!",hit / (total * 1.0))
    return hit / (total * 1.0)
 
def Coverage(train,test,AA,M,G,alpha,N,user_items):
    '''
    计算覆盖率
    :param train:训练集 字典user->items
    :param test: 测试机 字典 user->items
    :param N: topN推荐中N
    :param k:
    :return:覆盖率
    '''
    recommend_items=set()
    all_items=set()
    #print(train)
    for line in train:
        all_items.add(line[1])
    for line in test:
        all_items.add(line[1])
    for line in train:
        #print(line)
        rank=GetRecommendation(AA,M,G,alpha,line[0],N,user_items)
        #print(rank)
        for item in rank:
            if item in all_items:
                recommend_items.add(item)
        #print(all_items)
    #print(rank)
    #print(len(recommend_items))
    #print(len(all_items))
    print("Coverage successed!",len(recommend_items)/(len(all_items)*1.0))
    return len(recommend_items)/(len(all_items)*1.0)
 
def Popularity(train,AA,M,G,alpha,N,user_items):
    '''
    计算平均流行度
    :param train:训练集 字典user->items
    :param test: 测试机 字典 user->items
    :param N: topN推荐中N
    :param k:
    :return:覆盖率
    '''
    item_popularity=dict()
    for line in train:
        #print(line)
        if line[1] not in item_popularity:
            item_popularity[line[1]]=0
        item_popularity[line[1]]+=1
    ret=0
    n=0
    for line in train:
        rank= GetRecommendation(AA,M,G,alpha,line[0],N,user_items)
        for line[1] in rank:
            if line[1]!=0 and line[1] in item_popularity:
                ret+=math.log(1+item_popularity[line[1]])
                n+=1
    if n==0:return 0.0
    ret/=n*1.0
    print("Popularity successed!",ret)
    return ret
def buildGrapha(record):
    graph=dict()
    user_tags = dict()
    user_items = dict()
    for line in record:
        if line[0] not in graph:
            graph[line[0]]=dict()
        if line[1] not in graph[line[0]]:
            graph[line[0]][line[1]]=1#用户电影之间边的权重为1
            #graph[line[0]][line[1]]=line[2]用户电影之间边的权重为用户的评分
        if line[3] not in graph[line[0]]:
            graph[line[0]][line[3]]=1
        if line[0] not in user_items:
            user_items[line[0]]=dict()
        if line[1] not in user_items[line[0]]:
            user_items[line[0]][line[1]]=1
            #user_items[line[0]][line[1]]=line[2]
        if line[0] not in user_tags:
            user_tags[line[0]]=dict()
        if line[3] not in user_tags[line[0]]:
            user_tags[line[0]][line[3]]=1 
    print("buildGrapha successed!")
    return graph,user_items,user_tags
 
def buildMatrix_M(G):
    M=[]
    for key in G.keys():
        lst = []
        key_out = len(G[key])
        for key1 in G.keys():
            if key1 in G[key]:
                w=G[key][key1]
                lst.append(w/(1.0*key_out))
            else:
                lst.append(0)
        M.append(lst)
    print("buildMatrix_M successed!")
    return np.matrix(M)
 
def before_GetRec(M):
    n = M.shape[0]
    A = np.eye(n) - alpha * M.T
    data = list()
    row_ind = list()
    col_ind = list()
    for row in range(n):
        for col in range(n):
            if (A[row, col] != 0):
                data.append(A[row, col])
                row_ind.append(row)
                col_ind.append(col)
    AA = csr_matrix((data, (row_ind, col_ind)), shape=(n, n))
    print("before_GetRec successed!")
    return AA
 
def GetRecommendation(AA,M,G,alpha,root,N,user_items):
    items=[]
    vertex=list(G.keys())
    index=list(G.keys()).index(root)
    n = M.shape[0]
    zeros=np.zeros((n,1))
    zeros[index][0]=1
    r0=np.matrix(zeros)
    b = (1 - alpha) * r0
 
    r = gmres(AA, b, tol=1e-08, maxiter=1)[0]
    rank = {}
    for j in range(n):
        rank[vertex[j]] = r[j]
    li = sorted(rank.items(), key=lambda x: x[1], reverse=True)
    for i in range(N):
        item=li[i][0]
        #print(user_items[root])
        #if '/' in item and item not in user_items[root]:
        if item not in user_items[root]:
            items.append(item)
    return items
 
def evaluate(train,test,AA,M,G,alpha,N,item_tags,user_items):
    ##计算一系列评测标准
    recall=Recall(train,test,AA,M,G,alpha,N,user_items)
    precision=Precision(train,test,AA,M,G,alpha,N,user_items)
    coverage=Coverage(train,test,AA,M,G,alpha,N,user_items)
    popularity=Popularity(train,AA,M,G,alpha,N,user_items)
    return recall,precision,coverage,popularity
 
if __name__=='__main__':
    data=genData()
    datapre = datapreprocess(data)
    (train, test) = SplitData(datapre, 10, 5, 10)
    N=16;max_depth=50;alpha=0.8
    G, user_items, user_tags=buildGrapha(train)
    M=buildMatrix_M(G)
    AA=before_GetRec(M)
    recall, precision, coverage, popularity=evaluate(train, test, AA, M, G, alpha, N, user_tags, user_items)