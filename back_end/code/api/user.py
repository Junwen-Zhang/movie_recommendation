#引入路由管理
from fastapi import APIRouter,UploadFile,File,Request,Body,Form
#让数据以json格式返回所用到的库
from fastapi.responses import JSONResponse,Response

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
# import Seq
# import spark.implicits._

import time
import pymongo
import json
import re
import datetime
import requests


def getPicUrl(movieid):
    # cookie和header根据浏览器实际情况更换
    cookie = 'ga=GA1.2.1317766865.1672031600; ml4_session=b095b1a121e4564f1748a5a7e2834f37035808e1_c4abb100-0ac2-4556-9bd7-6a459d9ba5ea; _gid=GA1.2.444148264.1672828318; uvts=ee871ae3-b33d-4742-6ed6-5e9f575c591c '
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 Safari/537.36',
        'Connection': 'keep-alive',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Cookie': cookie}
    baseurl1 = "https://movielens.org/api/movies/"
    movieurl = baseurl1 + str(movieid)
    moviestr = requests.get(movieurl, headers=header)
    result = open('movie-info.json', 'w')
    result.write(moviestr.text)
    result.close()
    moviedict = json.loads(moviestr.text)
    res = moviedict["data"]["movieDetails"]["movie"]["backdropPaths"][0]
    movie_poster = 'https://image.tmdb.org/t/p/original' + res
    return movie_poster

#上传并返回数据
@router.get("/getusername",tags=["getusername"])
async def getUsername(uid:str):  
    # 连接数据库，查询返回uid对应的username
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user']
    result = collection.find_one({'userId': int(uid)})

    if result == None : # uid不存在
        return JSONResponse(
            content = {
                "code": 9999,
                "data": {},
                "message": "不存在改用户id: "  + uid
            }
        )
    else: #uid存在
        return JSONResponse(
        content={
            "code":20000,
            "data": {
                "username": result["username"]
            },
            "message":"查找用户名成功"
        })

# 注册
@router.get("/register",tags=["register"])
async def register(username:str, password:str):
    # 连接数据库，username查重
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user']
    result = collection.find_one({'username': username})

    if result != None:  # 存在重名，注册失败
        return JSONResponse(
        content={
            "code":20000,
            "data":{
                'roles': ['student'],
                'name': username,
                "success": False,
                "uid": None
            },
            "message":"注册失败，用户名重复"
        })
    else:  # 名字可用，注册成功
        # 在user表中添加新用户的记录
        result = collection.find({}).sort("userId",pymongo.DESCENDING).limit(1)
        userId = result[0]["userId"] + 1 #新用户Id为已有最大Id再加1
        collection.insert_one({"userId": userId,  
                               "username": username,
                               "passwd": password,
                               "rated_movie_list": []})
        uid_str = str(userId)
        return JSONResponse(
            content={
                "code":20000,
                "data":{
                    'roles':['admin', username, uid_str],
                    'name':username,
                    "success":True,
                    "uid":uid_str
                },
                "message":"注册成功"
            })

# 登陆
@router.get("/login",tags=["login"])
async def login(username:str,password:str):
    # 连接数据库，根据username查找user数据
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user']
    result = collection.find_one({'username': username})

    if result == None:    # 用户不存在
        return JSONResponse(
        content={
            "code":9999,
            "data":{
                "success":False
            },
            "message": "“" + username + "”用户不存在"
        })
    elif result["passwd"] != password : # 密码不匹配
        return JSONResponse(
        content={
            "code":9999,
            "data":{
                "success":False
            },
            "message":"密码错误"
        })
    else:   # 成功登录
        uid_str = str(result["userId"])
        return JSONResponse(
            content={
                "code":20000,
                "data":{
                    'roles':['admin',username,uid_str],
                    'name':username,
                    "success":True,
                    "uid":uid_str
                },
                "message":"登陆成功"
            })


# 评分(这个函数稍微有点慢)
@router.get("/givescore",tags=["givescore"])
async def giveScore(uid:str, movieid:int, score:int):
    # 连接数据库
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    # 在user数据表中新增数据
    rated_movie_list = db["user"].find_one({"userId": int(uid)})["rated_movie_list"]
    if movieid not in rated_movie_list: # 若未标记过该电影
        # 在user表中更新rated_movie_list字段
        rated_movie_list.append(movieid)
        db["user"].update_one({"userId": int(uid)}, 
                              {'$set': {'rated_movie_list': rated_movie_list}})
        # 在ratings表中新增一条数据
        db["ratings"].insert_one({"userId": int(uid),
                    "movieId": movieid,
                    "rating": score,
                    "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))})
        return JSONResponse(
            content={
                "code": 20000,
                "data": {},
                "message": "增加评分成功"
            })
    else: # 若已经标记过该电影
        # 在ratings表中更新rating字段
        db["ratings"].update_one({"userId": int(uid), "movieId": movieid}, 
                                 {'$set': {'rating': score,
                    'timestamp': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}})
        return JSONResponse(
            content={
                "code": 20000,
                "data": {},
                "message": "更新评分成功"
            })

# 获取评分的电影数量
@router.get("/givescoresnumber",tags=["givescoresnumber"])
async def getScoresNumber(uid:str):
    # 连接数据库，根据username查找user数据
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['user']
    result = collection.find_one({'userId': int(uid)})
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                "number": len(result["rated_movie_list"])
            },
            "message":"已评分电影数量查询成功"
        })

# 加标签
@router.get("/givetag",tags=["givetage"])
async def giveTags(uid:str,movieid:str,tag:str):
    return JSONResponse(
        content={
            "code":20000,
            "data":{},
            "message":"标签添加成功"
        })

# 搜索影片
@router.get("/searchmovie",tags=["searchmovie"])
async def searchMovie(name:str):
    # 连接数据库，根据username查找user数据
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['movies']
    # 模糊查询电影名
    pat = re.compile(r"\w*"+name+"\w*", re.I)
    result = list(collection.find({ "Title": {'$regex': pat}}))
    if len(result) == 0:
        return JSONResponse(
            content={
                "code":9999,
                "data":{},
                "message":"未找到匹配结果"
            })
    else:
        movie_info_list = []
        num = 0
        for movie_info_dict in result:
            num = num + 1
            movie_info_dict.pop("_id", None)
            movie_info_list.append(str(movie_info_dict))
            if num >= 10 :
                break
        return JSONResponse(
            content={
                "code":20000,
                "data":{
                    "number": movie_info_list
                },
                "message":"查询成功"
            })

# 返回movie的相关信息
@router.get("/getmovieinfor",tags=["getmovieinfor"])
async def getMovieInfor(movieIdListStr):
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['movies']

    movieIdList=movieIdListStr[:].split(',')
    movie_info_list = []
    for movieId in movieIdList:
        result = collection.find_one({"movieId": int(movieId)})
        avg_rating = db["movie_rate"].find_one({"movieId": int(movieId)})["avg_rating"]
        result.pop("_id", None)
        result["avg_rating"] = avg_rating
        movie_info_list.append(str(result))
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'movies': movie_info_list
            },
            "message":"success"
        })



# # 返回number篇movie的信息
# @router.get("/getmovies",tags=["getmovies"])
# async def searchMovie(number:int):
#     spark,_=connectDB("movies")
#     df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
#     movies=df.collect()[0:number]     # 查询  这个方式很可能会出错，所以待检查
#     return JSONResponse(
#         content={
#             "code":20000,
#             "data":{
#                 'movies':movies
#             },
#             "message":"success"
#         })

# 返回movieid的movie图片地址
@router.get("/getpic",tags=["getpic"])
async def getpic(movieId:int):
    picUrl=getPicUrl(movieId)
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'picture': picUrl,
                'movieId': movieId
            },
            "message":"success"
        })


# 查询点评记录
@router.get("getcomments",tags=["getcomments"])
async def getComments(uid:str):
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['comments']
    results = collection.find({"uid": int(uid)})
    if results == None:
        return JSONResponse(
        content={
            "code":9999,
            "data":{},
            "message":"用户没有影评记录"
        })
    comment_info_list = []
    for comment_info_dict in results:
        comment_info_dict.pop("_id", None)
        comment_info_list.append(str(comment_info_dict))
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'comments': comment_info_list
            },
            "message":"success"
        })

# 查询电影点评记录
@router.get("getmvcomments",tags=["getmvcomments"])
async def getMvComments(mvid:str):
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['comments']
    results = collection.find({"movieid": int(mvid)})
    if results == None:
        return JSONResponse(
        content={
            "code":9999,
            "data":{},
            "message":"该电影没有影评记录"
        })
    comment_info_list = []
    for comment_info_dict in results:
        comment_info_dict.pop("_id", None)
        username = db["user"].find_one({"userId": comment_info_dict["uid"]})["username"]
        comment_info_dict["username"] = username
        comment_info_list.append(str(comment_info_dict))
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'comments': comment_info_list
            },
            "message":"success"
        })

# 增加点评记录
@router.get("addcomments",tags=["addcomments"])
async def addComments(uid:str,movieid:str,content:str):
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    print("add comments uid", uid)
    db = client['movie']
    collection = db['comments']
    item = {
        "uid": int(uid),
        "movieid": int(movieid),
        "comment": content,
        "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    }
    collection.insert_one(item)
    return JSONResponse(
        content={
            "code":20000,
            "data": str(item),
            "message":"评论添加成功"
        })

# 根据movieid查找moviename （下面都要改）
@router.get("getmoviename",tags=["getmoviename"])
async def getMovieName(movieid:int):
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['movies']

    result = collection.find_one({"movieId": int(movieid)})
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'movies': result["Title"]
            },
            "message":"success"
        })

# 根据uid查找评分记录
@router.get("getratings",tags=["getratings"])
async def getRatings(uid:str):
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    db = client['movie']
    collection = db['ratings']
    results = collection.find({"userId": int(uid)})
    user_rating_infos = []
    for result in results:
        result.pop("_id", None)
        user_rating_infos.append(str(result))

    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'movies': user_rating_infos
            },
            "message":"success"
        })
