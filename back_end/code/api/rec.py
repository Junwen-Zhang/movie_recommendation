#引入路由管理
from fastapi import APIRouter,UploadFile,File,Request,Body,Form
#让数据以json格式返回所用到的库
from fastapi.responses import JSONResponse,Response

import numpy as np
import random
import pandas as pd
import pymongo
from time import time
from gensim.models import word2vec,Word2Vec
import os
from operator import itemgetter

router = APIRouter()

# 数据库连接相关
#添加此代码
import findspark
findspark.init()
#添加此代码

import pyspark
from pyspark import SparkContext, SQLContext, SparkConf
import time, sys, warnings

from pyspark.sql import SparkSession
from bson.objectid import ObjectId
import pymongo

# 高分电影推荐
@router.get("/recbytop",tags=["recbytop"])
async def recByTop(uid:str):  
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['top250']
    result = collection.aggregate([{'$sample': {'size': 10}}])
    rec_movie_list = [doc['movieId'] for doc in result]
    return JSONResponse(
        content={
            "code":200,
            "data":{
                'movie_list':rec_movie_list
            },
            "message":"success"
        })


# 热门电影推荐
@router.get("/recbytrend",tags=["recbytrend"])
async def recByTrend(uid:str):  
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['trend_rank']
    result = collection.aggregate([{'$sample': {'size': 10}}])
    rec_movie_list = [doc['movieID'] for doc in result]
    return JSONResponse(
        content={
            "code":200,
            "data":{
                'movie_list':rec_movie_list
            },
            "message":"success"
        })


# 基于流派推荐
@router.get("/recbygenre",tags=["recbygenre"])
async def recByGenre(uid:str):
     # 取出user的movie list
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user_movielist']
    result = collection.find_one({'userId': uid})
    # 待补充! 需要处理数据使得user_list格式为[[mid,rate],[mid,rate],...]
    user_list = [[296, 5.0], [79132, 5.0], [2959, 5.0]]

    # 计算用户喜欢的类别
    G = {}
    genre_list = ["Action","Adventure","Animation","Children's","Comedy",\
        "Crime","Documentary","Drama","Fantasy","Film-Noir","Horror","Musical",\
        "Mystery","Romance","Sci-Fi","Thriller","War","Western"]
    for g in genre_list:
        G.setdefault(g, 0.0)
    
    collection = db['movies']
    for m, r in user_list:
        movie = collection.find_one({"movieId":m})
        g_list = movie["genres"].split("|")
        for g in g_list:
            try:
                G[g] += r
            except KeyError:
                G[g] = r
            

    user_genre_list = sorted(G.items(), key=itemgetter(1), reverse=True)
    user_genre = user_genre_list[0][0]
    print("用户最喜欢的类别为：", user_genre)

    # 进行电影推荐
    collection = db['movie_genre_rank']
    myquery = {"genre": user_genre}
    result = collection.find(myquery)
    result = collection.aggregate([{'$sample': {'size': 10}}])
    rec_movie_list = [doc['movieID'] for doc in result]

    return JSONResponse(
        content={
            "code":200,
            "data":{
                'movie_list':rec_movie_list
            },
            "message":"success"
        })


# 基于标签推荐
@router.get("/recbytag",tags=["recbytag"])
async def recByTag(uid:str):  
    # 加载训练好的数据和处理过的数据
    TagRec_model = Word2Vec.load('./rec_model_save/TagRec.model')
    mv_tags_vectors = TagRec_model.docvecs.vectors_docs
    movieId_index = pd.read_csv('./rec_model_save/df_save.csv')

    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user']
    result = collection.find_one({'userId': int(uid)})
    user_movies_index = result["rated_movie_list"]

    # 将用户向量计算为该用户所看到的电影向量的平均值(用户兴趣向量)
    user_movie_vector = np.zeros(shape = mv_tags_vectors.shape[1])
    for mv_index in user_movies_index:
        user_movie_vector += mv_tags_vectors[mv_index]
    user_movie_vector /= len(user_movies_index)  

    # 寻找与用户向量相似的电影，生成电影推荐
    sims = TagRec_model.docvecs.most_similar(positive = [user_movie_vector], topn = 30)

    movie_rec_list = []
    for i, j in sims:
        movie_sim = movieId_index.loc[int(i), "movieId"]
        if movie_sim not in user_movies_index:
            movie_rec_list.append(int(movie_sim))

    return JSONResponse(
        content={
            "code":200,
            "data":{
                'movie_list': movie_rec_list[0:10]
            },
            "message":"success"
        })


# 基于矩阵SVD的协同推荐
@router.get("/recbycf",tags=["recbycf"])
async def recByGenre(uid:str):
    k = 5
    m_cnt = 1000

    # 取出user的movie list
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user_movielist']
    result = collection.find_one({'userId': uid})
    # 待补充! 需要处理数据使得user_list格式为[[mid,rate],[mid,rate],...]
    user_list = [[1, 5.0], [2, 5.0], [3, 4.0]]

    # 取出用户向量
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['model']
    user_col = db['user_matrix']

    count = user_col.count_documents({'uid': uid})
    if count == 0:  # 用户无记录 生成随机数解决冷启动问题
        ulist = []
        for i in range(k):
            ulist.append({'uid': uid, 'index': i+1, 'num':random.random()})
        user_col.insert_many(ulist)
    user_data = user_col.find({'uid': uid})
    ul = []
    for i in user_data:
        ul.append(i['num'])
    user_array = np.array(ul)

    # 遍历物品向量 计算
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['model']
    item_col = db['movie_matrix']

    pred_dict = {}
    for i in range(m_cnt):
        iid = i+1
        count = item_col.count_documents({'iid': iid})
        if count == 0:
            ilist = []
            for i in range(k):
                ilist.append({'iid': iid, 'index': i+1, 'num':random.random()})
            item_col.insert_many(ilist)
        item_data = item_col.find({'iid': iid})
        il = []
        for i in item_data:
            il.append(i['num'])
        item_array = np.array(il)
        ans = np.dot(user_array, item_array)
        if ans > 5:
            ans = 5.0
        if ans < 0.5:
            ans = 0.5
        pred_dict[iid] = ans  
    # print(pred_dict)
        
    # 对已有评价的物品 向梯度方向移动一步
    lr = 0.5
    for i in user_list:
        iid = i[0]
        item_data = item_col.find({'iid': iid})
        il = []
        for j in item_data:
            il.append(j['num'])
        i_array = np.array(il)

        rate = i[1]
        eui = rate - pred_dict[iid]
        temp = user_array
        user_array += lr * eui * i_array
        i_array += lr * eui * temp

        # 保存
        for x in range(k):
            user_col.update_one(filter={'uid':uid, 'index':x+1},\
                update={"$set":{'num':user_array[x]}})
            item_col.update_one(filter={'iid':iid, 'index':x+1},\
                update={"$set":{'num':i_array[x]}})


    # 高分排序
    pred_dict = sorted(pred_dict.items(), key=lambda d:d[1], reverse = True)
    l = []
    for key in pred_dict:
        l.append(key[0])
        rec_movie_list = l[:10]

    return JSONResponse(
        content={
            "code":200,
            "data":{
                'movie_list':rec_movie_list
            },
            "message":"success"
        })