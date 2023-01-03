import findspark
findspark.init()

from pyspark import SparkContext
from pyspark.sql import SQLContext, SparkSession
import os
from operator import itemgetter

def get_user_genre(user_list):
    """
    根据用户评分记录计算用户喜欢的类别，然后进行推荐
    user_list: [[mid, rate], [mid, rate], ...]
    返回用户最喜欢的类别str 和推荐列表[mid, mid, ...]
    """
    sc = SparkContext()
    sc.setLogLevel("WARN")

    # 计算用户喜欢的类别
    spark = SparkSession.builder.appName('getTrend').getOrCreate()
    complete_movies_file = os.path.join('datasets', 'ml-latest', 'movies.csv')
    movies = spark.read.csv(complete_movies_file, sep=',', inferSchema=True, header=True)

    G = {}
    genre_list = ["Action","Adventure","Animation","Children's","Comedy",\
        "Crime","Documentary","Drama","Fantasy","Film-Noir","Horror","Musical",\
        "Mystery","Romance","Sci-Fi","Thriller","War","Western"]
    for g in genre_list:
        G.setdefault(g, 0.0)
    
    for m, r in user_list:
        movie = movies.where(movies.movieId == m).collect()
        g_list = movie[0][2].split("|")
        for g in g_list:
            G[g] += r

    user_genre_list = sorted(G.items(), key=itemgetter(1), reverse=True)
    print(user_genre_list)

    user_genre = user_genre_list[0][0]
    print("用户最喜欢的类别为：", user_genre)

    # 进行推荐
    input_uri = 'mongodb://mongodb:27017/{}.{}'.format('movie', 'movie_genre_rank')

    my_spark = SparkSession\
        .builder\
        .appName("MyApp")\
        .config("spark.mongodb.input.uri", input_uri)\
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
        .getOrCreate()

    df = my_spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    df = df.where(df.genre == user_genre).sample(fraction = 1.0*11/50).limit(10)
    df.show()

    id_array = df.select("movieID").rdd.flatMap(lambda x: x).collect()
    print(id_array)

    return user_genre, id_array
