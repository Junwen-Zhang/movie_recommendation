#引入路由管理
from fastapi import APIRouter,UploadFile,File,Request,Body,Form
#让数据以json格式返回所用到的库
from fastapi.responses import JSONResponse,Response

import numpy as np
import pandas as pd
import pymongo
from time import time
from gensim.models import word2vec,Word2Vec

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

# 基于标签推荐
@router.get("/recbytag",tags=["recbytag"])
async def recByTag(uid:str):  
    # t0 = time()
    # 加载训练好的数据和处理过的数据
    TagRec_model = Word2Vec.load('./rec_model_save/TagRec.model')
    mv_tags_vectors = TagRec_model.docvecs.vectors_docs
    movieId_index = pd.read_csv('./rec_model_save/df_save.csv')
    # t1 = time()
    # print("记载数据耗时：", t1 - t0)

    # 从数据库中取出user的movie list
    # user_id = 1
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user_movielist']
    result = collection.find_one({'userId': uid})
    # user_movies_index = result["rated_movie"]
    user_movies_index=[307,481,1091,1257,1449,1590,1591,2134,2478,2840,2986,3020,3424,3698,3826,3893]
    # t2 = time()
    # print("查询电影列表耗时：", t2 - t1)

    # 将用户向量计算为该用户所看到的电影向量的平均值
    user_movie_vector = np.zeros(shape = mv_tags_vectors.shape[1])
    print(user_movie_vector)
    for mv_index in user_movies_index:
        user_movie_vector += mv_tags_vectors[mv_index]

    user_movie_vector /= len(user_movies_index)  
    

    # 寻找与用户向量相似的电影，生成电影推荐
    print('Movie Recommendations:')

    sims = TagRec_model.docvecs.most_similar(positive = [user_movie_vector], topn = 30)
    # t3 = time()
    # print("寻找相似电影耗时：", t3 - t2)

    movie_rec_list = []
    for i, j in sims:
        movie_sim = movieId_index.loc[int(i), "movieId"]
        if movie_sim not in user_movies_index:
            movie_rec_list.append(int(movie_sim))

    # print(movie_rec_list[0:10])
    # print(type(movie_rec_list[0:10]))
    result2=movie_rec_list[0:10]
    # print(type([1,2]))
    # print("标签推荐共耗时：", time() - t0)
    return JSONResponse(
        content={
            "code":200,
            "data":{
                'movie_list': result2
            },
            "message":"success"
        })