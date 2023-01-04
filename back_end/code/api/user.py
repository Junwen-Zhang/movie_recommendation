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
# 连接数据库
def connectDB(tablename:str):
    dbname="movie"
    input_uri = 'mongodb://mongodb:27017/{}.{}'.format(dbname, tablename)
    spark = SparkSession\
    .builder\
    .appName("MyApp")\
    .config("spark.mongodb.input.uri", input_uri)\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
    .getOrCreate()
    return spark,input_uri

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
    # 和数据库的链接
    # 以及查询返回uid对应的username
    df = my_spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    result=df.filter(df.uid == ObjectId(uid))     # 查询
    username=result.collect()[0].uname    #取第一个记录的unam值
    return username

# 注册
@router.get("/register",tags=["register"])
async def register(username:str,password:str):
    spark, input_uri=connectDB("user")
    # user = spark.createDataFrame([("uname":uname,"password":password)])
    columns=['uname','password']
    data=[(username, password)]
    user = spark.createDataFrame(data,columns)
    print(user.collect())
    # 需要查重一下
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    users=df.filter(df.uname == username)     # 查询 
    if(len(users.collect())):
        uid_str=ObjectId(users.collect()[0]._id.oid).__str__()
        return JSONResponse(
        content={
            "code":20000,
            "data":{
                'roles':['student'],
                'name':username,
                "success":False,
                "uid":uid_str
            },
            "message":"注册失败，用户名重复"
        })
    # MongoSpark.save(
    #   user.write.mode(SaveMode.Append)# Append代表追加,Overwrite代表覆盖,写入的模式、
    # )
    user.write.format("com.mongodb.spark.sql.DefaultSource").option("uri",input_uri).mode("append").save()
    users=df.filter(df.uname == username)     # 查询 
    uid_str=ObjectId(users.collect()[0]._id.oid).__str__()
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'roles':['admin',username,uid_str],
                'name':username,
                "success":True,
                "uid":uid_str
            },
            "message":"注册成功"
        })

# 登陆
@router.get("/login",tags=["login"])
async def login(username:str,password:str):
    print(username,password)
    uname=username
    # password=data['password']
    spark,_=connectDB("user")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    users=df.filter(df.uname == uname)     # 查询
    if(len(users.collect())==0):    # 找不到该用户
        return JSONResponse(
        content={
            "code":20000,
            "data":{
                "success":False
            },
            "message":"该用户名不存在"
        })
    if(users.collect()[0].password!=password):
        return JSONResponse(
        content={
            "code":20000,
            "data":{
                "success":False
            },
            "message":"密码错误"
        })
    # print(users.collect()[0])
    # print(users.collect()[0].show())
    uid_str=ObjectId(users.collect()[0]._id.oid).__str__()  # 将objectId类型转化为str
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

# 点击记录
@router.get("/clickMovie",tags=["clickMovie"])
async def clickMovie(uid:str,movieid:str):
    spark=connectDB("clickmovie")
    uid_objectId=ObjectId(uid)
    data=[(uid_objectId,movieid)]
    columns=['uid','movieid']
    oneclick = spark.createDataFrame(data,columns)
    oneclick.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()
    return 1

# 评分
@router.get("/givescore",tags=["givescore"])
async def giveScore(uid:str,movieid:int,score:int):
    uid_objectId=ObjectId(uid)
    spark=connectDB("score")
    data=[(uid_objectId,movieid,score)]
    columns=['uid','movieid','score']
    oneclick = spark.createDataFrame([("uid",uid_objectId), ("movieid", movieid),("score",score)])
    oneclick.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                
            },
            "message":"评分成功"
        })

# 获取评分的电影数量
@router.get("/givescoresnumber",tags=["givescoresnumber"])
async def getScoresNumber(uid:str):
    uid_objectId=ObjectId(uid)
    spark=connectDB("score")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    scores=df.filter(df.uid==uid)     # 查询  这个方式很可能会出错，所以待检查
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                "number":len(scores.collect())
            },
            "message":"查询成功"
        })

# 加标签
@router.get("/givetag",tags=["givetage"])
async def giveTags(uid:str,movieid:str,tag:str):
    uid_objectId=ObjectId(uid)
    spark=connectDB("tag2")
    data=[(uid_objectId,movieid,tag)]
    columns=['uid','movieid','tag']
    oneclick = spark.createDataFrame([("uid",uid_objectId), ("movieid", movieid),("tag",tag)])
    oneclick.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()
    return 1

# 搜索影片
@router.get("/searchmovie",tags=["searchmovie"])
async def searchMovie(name:str):
    spark=connectDB("movies")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    movies=df.filter(df.title.find(name))     # 查询  这个方式很可能会出错，所以待检查
    return movies.collect()

# 返回movie的相关信息
@router.get("/getmovieinfor",tags=["getmovieinfor"])
async def getMovieInfor(movieIdListStr):
    # print(movieIdListStr)
    movieIdList=movieIdListStr[1:-1].split(',')
    # print(movieIdList)
    # print(type(movieIdList))
    # print(0 in movieIdList)
    spark1,_=connectDB("movies")
    movieIdList=[1,2]
    df = spark1.read.format('com.mongodb.spark.sql.DefaultSource').load()
    moviesList=[]
    spark2,_=connectDB("movie_rate")  
    df2 = spark2.read.format('com.mongodb.spark.sql.DefaultSource').load()
    for i in range(len(movieIdList)):
        movies=df.filter(df.movieId ==int(movieIdList[i]))
        moviesList.append(movies.collect()[0].asDict())
        # print("moviesList",moviesList)
        # print(moviesList[i]['movieId'])
        # print("111111111",df2.collect())
        movieRate=df2.filter(df2.movieId==str(moviesList[i]['movieId']))
        # print("moviesList",type(moviesList[i]))
        if(len(movieRate.collect())):
            moviesList[i]["rate"]=movieRate.collect()[0]['avg_rating']
        else:
            moviesList[i]["rate"]=0
    # print(moviesList)
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'movies':moviesList
            },
            "message":"success"
        })



# 返回number篇movie的信息
@router.get("/getmovies",tags=["getmovies"])
async def searchMovie(number:int):
    spark,_=connectDB("movies")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    movies=df.collect()[0:number]     # 查询  这个方式很可能会出错，所以待检查
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'movies':movies
            },
            "message":"success"
        })

# 返回movieid的movie图片地址
@router.get("/getpic",tags=["getpic"])
async def getpic(movieId:int):
    picUrl=getPicUrl(movieId)
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'picture':picUrl
            },
            "message":"success"
        })


# 查询点评记录
@router.get("getcomments",tags=["getcomments"])
async def getComments(uid:str):
    spark,_=connectDB("comments")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    # print(df.collect()[0].uid)
    # print(type(df.collect()[0].uid))
    comments=df.filter(df.uid==uid )     # 查询
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'comments':comments.collect()
            },
            "message":"success"
        })
# 增加点评记录
@router.get("addcomments",tags=["addcomments"])
async def addComments(uid:str,movieid:str,content:str,date:str):
    spark,input_uri=connectDB("comments")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    columns=['uid','movieid','comment','date']
    data=[(uid, movieid,content,date)]
    comment = spark.createDataFrame(data,columns)
    comment.write.format("com.mongodb.spark.sql.DefaultSource").option("uri",input_uri).mode("append").save()
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                # 'movies':movies
            },
            "message":"success"
        })

# 根据movieid查找moviename
@router.get("getmoviename",tags=["getmoviename"])
async def getMovieName(movieid:int):
    spark,input_uri=connectDB("movies")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    movies=df.filter(df.movieId==movieid )     # 查询
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'movies':movies.collect()[0].title
            },
            "message":"success"
        })

# 根据uid查找评分记录
@router.get("getratings",tags=["getratings"])
async def getRatings(uid:str):
    spark,input_uri=connectDB("new_ratings")
    df = spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    ratings=df.filter(df.userId==uid )     # 查询
    return JSONResponse(
        content={
            "code":20000,
            "data":{
                'movies':ratings.collect()
            },
            "message":"success"
        })

