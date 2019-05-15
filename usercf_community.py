#-*- coding: utf-8 -*-
'''
Created on 2015-06-22

@author: Lockvictor
'''
import sys
import random
import math
import os
from operator import itemgetter
import Louvain

from collections import defaultdict

random.seed(0)


class UserBasedCF(object):
    ''' TopN recommendation - User Based Collaborative Filtering '''

    def __init__(self):
        self.trainset = {}
        self.testset = {}
        self.socialset={}

        self.n_sim_user =40
        self.n_rec_movie =16

        self.user_sim_mat = {}
        self.user_simf_mat={}
        self.movie_popular = {}
        self.movie_count = 0

        print ('Similar user number = %d' % self.n_sim_user, file=sys.stderr)
        print ('recommended movie number = %d' %
               self.n_rec_movie, file=sys.stderr)

    @staticmethod
    def loadfile(filename):
        ''' load a file, return a generator. '''
        fp = open(filename, 'r')
        for i, line in enumerate(fp):
            yield line.strip('\r\n')
            if i % 100000 == 0:
                print ('loading %s(%s)' % (filename, i), file=sys.stderr)
        fp.close()
        print ('load %s succ' % filename, file=sys.stderr)

    def social_network(self,filename):
        for line in self.loadfile(filename):
            if len(line.split(' '))!=3:
                continue
            user,friend,_=line.split(' ')
            self.socialset.setdefault(user, {})
            self.socialset[user][friend]=1
       # print(self.socialset)
        print ('creat social network set succ', file=sys.stderr)



    def generate_dataset(self, filename, pivot=0.7):
        ''' load rating data and split it to training set and test set '''
        #将数据集分为训练集和测试集，比例为7：3
        trainset_len = 0
        testset_len = 0
        for line in self.loadfile(filename):
            if len(line.split(' '))!=3:
                continue
            user, movie, rating= line.split(' ')
            # split the data by pivot
            if random.random() < pivot:
                self.trainset.setdefault(user, {})
                #user为下属1级菜单，并创建二级菜单
                self.trainset[user][movie] = float(rating)
                #二级菜单为movie，值为打分值
                trainset_len += 1
            else:
                self.testset.setdefault(user, {})
                self.testset[user][movie] = float(rating)
                testset_len += 1   

        print ('split training set and test set succ', file=sys.stderr)
        print ('train set = %s' % trainset_len, file=sys.stderr)
        print ('test set = %s' % testset_len, file=sys.stderr)

    def calc_user_sim(self,commun):
        ''' calculate user similarity matrix '''
        # build inverse table for item-users
        # key=movieID, value=list of userIDs who have seen this movie
        print ('building movie-users inverse table...', file=sys.stderr)
        movie2users = dict()
        usercommunity={}
        for user, movies in self.trainset.items():
            for movie in movies:
                # inverse table for item-users
                if movie not in movie2users:
                    movie2users[movie] = set()
                movie2users[movie].add(user)
                #一级菜单是电影，二级菜单为用户
                # count item popularity at the same time
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1
        print ('build movie-users inverse table succ', file=sys.stderr)

        # save the total movie number, which will be used in evaluation
        self.movie_count = len(movie2users)
        print ('total movie number = %d' % self.movie_count, file=sys.stderr)

        # count co-rated items between users
        usersim_mat = self.user_sim_mat
        usersimf_mat=self.user_simf_mat
        print ('building user co-rated movies matrix...', file=sys.stderr)
        print ('building user co-rated friends matrix...', file=sys.stderr)
        for movie, users in movie2users.items():
            for u in users:
                usersim_mat.setdefault(u, defaultdict(int))
                for v in users:
                    if u == v:
                        continue
                    usersim_mat[u][v] += 1/math.log(1+len(users))
                    #usersim_mat[u][v] += 1
                    #给同一部电影打过分的用户之间建立关系

        for user,movies in self.socialset.items():
            count=0
            usersimf_mat.setdefault(user,defaultdict(int))
            #print(commun)
            for c in commun:
                if int(user) in c:
                    count+=1
                   # print(count)                    
                    for v in c:
                        if int(user)==v:
                            continue 
                        usersimf_mat[user][v]+=1/math.log(1+len(c))      
            usercommunity[user]=count
        
        print ('build user co-rated movies matrix succ', file=sys.stderr)
        print ('build user co-rated friends matrix succ', file=sys.stderr)

        # calculate similarity matrix
        print ('calculating user similarity matrix...', file=sys.stderr)
        simfactor_count = 0
        PRINT_STEP = 2000000
        a=0.3
        #社区信息占相似度的权重
        for u, related_users in usersim_mat.items():
            for v, count in related_users.items():                
                if u not in usersimf_mat.keys():
                    usersim_mat[u][v] = (1-a)*count / math.sqrt(len(self.trainset[u]) * len(self.trainset[v]))
                elif int(v) not in usersimf_mat[u].keys():
                    usersim_mat[u][v] = (1-a)*count / math.sqrt(len(self.trainset[u]) * len(self.trainset[v]))
                elif u not in self.socialset or v not in self.socialset:
                    usersim_mat[u][v] = (1-a)*count / math.sqrt(len(self.trainset[u]) * len(self.trainset[v]))
                else:                
                    usersim_mat[u][v] = (1-a)*count / math.sqrt(len(self.trainset[u]) * len(self.trainset[v]))+a*usersimf_mat[u][int(v)]
                simfactor_count += 1
                if simfactor_count % PRINT_STEP == 0:
                    print ('calculating user similarity factor(%d)' %
                           simfactor_count, file=sys.stderr)

        print ('calculate user similarity matrix(similarity factor) succ',
               file=sys.stderr)
        print ('Total similarity factor number = %d' %
               simfactor_count, file=sys.stderr)

    def recommend(self, user):
        ''' Find K similar users and recommend N movies. '''
        K = self.n_sim_user
        N = self.n_rec_movie
        rank = dict()
        watched_movies = self.trainset[user]
        for similar_user, similarity_factor in sorted(self.user_sim_mat[user].items(),
                                                      key=itemgetter(1), reverse=True)[0:K]:
            for movie in self.trainset[similar_user]:
                if movie in watched_movies:
                    continue
                # predict the user's "interest" for each movie
                rank.setdefault(movie, 0)
                rank[movie] += similarity_factor
        # return the N best movies
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    def evaluate(self):
        ''' print evaluation result: precision, recall, coverage and popularity '''
        print ('Evaluation start...', file=sys.stderr)

        N = self.n_rec_movie
        #  varables for precision and recall
        hit = 0
        rec_count = 0
        test_count = 0
        # varables for coverage
        all_rec_movies = set()
        # varables for popularity
        popular_sum = 0
        for i, user in enumerate(self.trainset):
            if i % 500 == 0:
                print ('recommended for %d users' % i, file=sys.stderr)
            test_movies = self.testset.get(user, {})
            rec_movies = self.recommend(user)
            for movie, _ in rec_movies:
                if movie in test_movies:
                    hit += 1
                all_rec_movies.add(movie)
                popular_sum += math.log(1 + self.movie_popular[movie])
                #popular_sum += self.movie_popular[movie]
            rec_count += N
            test_count += len(test_movies)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        popularity = popular_sum / (1.0 * rec_count)

        print ('precision=%.4f\trecall=%.4f\tcoverage=%.4f\tpopularity=%.4f' %
               (precision, recall, coverage, popularity), file=sys.stderr)


if __name__ == '__main__':
    ratingfile = os.path.join(r'data\ratings.csv')
    friendfile = os.path.join(r'data\trust.csv')
    usercf = UserBasedCF()
    usercf.generate_dataset(ratingfile)
    usercf.social_network(friendfile)
    G = Louvain.load_graph(friendfile)
    algorithm = Louvain.Louvain(G)
    communities = algorithm.execute()
    usercf.calc_user_sim(communities)
    usercf.evaluate()
    

    