import math  
import csv
import pymysql
import pandas as pd
  
class ItemBasedCF:  
    def __init__(self,train_file):  
        self.train_file = train_file  
        self.readData()  
    
    def readData(self):  
        #读取文件，并生成用户-物品的评分表和测试集  
        self.train = dict()     #用户-物品的评分表  
        for line in open(self.train_file):  
            # user,item,score = line.strip().split(",")  
            tmp_line = line.strip().split(",") 
            user = tmp_line[2]
            item = tmp_line[1]
            score = tmp_line[3]
            if score == "score":
                continue
            self.train.setdefault(user,{})  
            self.train[user][item] = int(float(score))  
              
    def ItemSimilarity(self):  
        #建立物品-物品的共现矩阵  
        C = dict()  #物品-物品的共现矩阵  
        N = dict()  #物品被多少个不同用户购买  
        for user,items in self.train.items():  
            for i in items.keys():  
                N.setdefault(i,0)  
                N[i] += 1  
                C.setdefault(i,{})  
                for j in items.keys():  
                    if i == j :  continue  
                    C[i].setdefault(j,0)  
                    C[i][j] += 1  
        #计算相似度矩阵  
        self.W = dict()  
        for i,related_items in C.items():  
            self.W.setdefault(i,{})  
            for j,cij in related_items.items():  
                self.W[i][j] = cij / (math.sqrt(N[i] * N[j])) 
        self.create_movie_rela()
        return self.W  
  
    #给用户user推荐，前K个相关物品  
    def Recommend(self,user,K=3, N=10):  
        rank = dict()  
        action_item = self.train[user]     #用户user产生过行为的item和评分  
        for item,score in action_item.items():  
            for j,wj in sorted( self.W[item].items(),key=lambda x:x[1],reverse=True)[ 0:K]:  
                if j in action_item.keys():  
                    continue  
                rank.setdefault(j,0)  
                rank[j] += score * wj  
        return dict(sorted(rank.items(),key=lambda x:x[ 1],reverse=True)[0:N])  
    

    def create_movie_rela(self):
        relation_set = set()
        for movie in self.W:
            for other in self.W[movie]:
                if self.W[movie][other] > 0.7 and {movie,other} not in relation_set:
                    relation_set.add((movie,other))

        with open("movie_rela.csv","w") as f:
            f.write("{},{}\n".format("id1","id2"))
            for rela in relation_set:
                f.write("{},{}\n".format(rela[0],rela[1]))



#声明一个ItemBased推荐的对象      
Item = ItemBasedCF("rating.csv")  
Item.ItemSimilarity()  
recommedDic = Item.Recommend("20")  
for k,v in recommedDic.items():  
    print(k,"\t",v)  




def get_ratings():
    conn = pymysql.connect(user='root',password='lv23623600', \
    db='movie_infor',use_unicode=True)

    sql = 'select * from rating'
    df = pd.read_sql(sql, con=conn)
    df.to_csv("rating.csv")
    conn.close()


def get_user():
    conn = pymysql.connect(user='root',password='lv23623600', \
    db='movie_infor',use_unicode=True)

    sql = 'select * from user'
    df = pd.read_sql(sql, con=conn)
    print(df.head())
    df.to_csv("user.csv")
    conn.close()



def get_movie():
    conn = pymysql.connect(user='root',password='lv23623600', \
    db='movie_infor',use_unicode=True)

    sql = 'SELECT * FROM movies WHERE movie_id in (SELECT movie_id FROM rating)'
    df = pd.read_sql(sql, con=conn)
    print(df.head())
    df.to_csv("movies.csv")
    conn.close()



get_ratings()
get_user()
get_movie()


