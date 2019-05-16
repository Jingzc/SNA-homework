本项目对传统基于用户的协同过滤系统进行了改进，加入了惩罚、用户间的社交网络信息和社区信息。除此之外还考虑的基于图的推荐算法，在社区-用户-电影关系图上进行personalrank随机游走，分为无权图和有权图。    
该项目的数据集来自于Filmtrust网站，下载链接：https://www.librec.net/datasets.html    
关于数据集:    
ratings.csv:    
分为3列，分别是user_id,movie_id,rating。  
trust.csv:  
分为3列，分别是userA_id,user_id,trust，trust列为1，表明用户A和用户B间的信任关系。  
user_item_rating_community_communitylength.csv:  
分为5列，分别是user_id,movie_id,rating,community number,community length,第4列表明该用户属于的社区编号，第5列表明该用户属于社区的总人数。  
关于代码：  
usercf_social.py：可计算基于用户的传统协同过滤算法、加入惩罚和考虑社交网络信息后的推荐正确率，回归率和覆盖率。  
usercf_community.py ：可计算考虑社区信息后的推荐正确率，回归率和覆盖率。  
Louvain.py:使用Louvain算法发现用户社交网络中的社区。  
personalrank.py：基于图的随机游走推荐算法。  
plotdata.py, draw.py和drawcommunity.py分别是数据集信息，社交网络信息和社区信息的可视化。  
