import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count
import math
import os
import pandas as pd

def cal_genre():
    
    # 加载数据
    print("-----加载数据-----")

    spark = SparkSession.builder.appName('getTrend').getOrCreate()
    complete_ratings_file = os.path.join('datasets', 'ml-latest', 'ratings.csv')
    rating = spark.read.csv(complete_ratings_file, sep=',', inferSchema=True, header=True)

    complete_movies_file = os.path.join('datasets', 'ml-latest', 'movies.csv')
    movies = spark.read.csv(complete_movies_file, sep=',', inferSchema=True, header=True)

    print("-----加载数据完成-----")

    # 数据处理
    print("-----数据处理-----")

    movies = movies.where(movies.genres != "(no genres listed)")  # 去掉空值
    movies.summary("count").show()

    # 按分类统计
    mlist = []
    rows = movies.collect()
    for row in rows:
        mid = row[0]
        t = row[1]
        gs = row[2].split("|")
        for g in gs:
            l = []
            l.append(mid)
            l.append(t)
            l.append(g)
            mlist.append(l)      
    df = pd.DataFrame (mlist, columns = ["movieID", "title", "genre"])
    movie_genre = spark.createDataFrame(df)
    
    # 计算评分
    rating = rating.groupby("movieId").agg(count("*").alias("cnt_rating"),avg("rating").alias("avg_rating"))

    # 连接类型和评分
    df_join = movie_genre.join(rating, movie_genre.movieID==rating.movieId, "inner")
    df_join = df_join.drop("movieId")

    # 去掉评分人数过少的电影
    df_join = df_join.where(df_join.cnt_rating>=200)
    df_join.show(10)

    print("-----数据处理完成-----")

    # 按类别统计
    print("-----按类别统计-----")

    movie_list = []
    genre_list = ["Action","Adventure","Animation","Children's","Comedy",\
        "Crime","Documentary","Drama","Fantasy","Film-Noir","Horror","Musical",\
        "Mystery","Romance","Sci-Fi","Thriller","War","Western"]

    for g in genre_list:
        l = df_join.where(df_join.genre == g).sort(['avg_rating'], ascending=False).limit(50).collect()
        movie_list.extend(l)

    movie_genre = spark.createDataFrame(movie_list)
    movie_genre.show(10)

    print("-----按类别统计完成-----")
    

    # 连接数据库
    output_uri = 'mongodb://mongodb:27017/{}.{}'.format('movie', 'movie_genre_rank')

    # 存储
    my_spark = SparkSession\
        .builder\
        .appName("MyApp")\
        .config("spark.mongodb.output.uri", output_uri)\
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
        .getOrCreate()
    movie_genre.write.format("com.mongodb.spark.sql.DefaultSource").mode("overwrite").save()
    print("存储完成")


cal_genre()
