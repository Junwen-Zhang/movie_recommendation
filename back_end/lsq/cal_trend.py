import findspark
findspark.init()

from pyspark.sql import SparkSession
import math
import os

def cal_trend():
    
    # 加载数据
    print("-----加载数据-----")
    spark = SparkSession.builder.appName('getTrend').getOrCreate()
    complete_ratings_file = os.path.join('datasets', 'ml-latest', 'ratings.csv')
    df = spark.read.csv(complete_ratings_file, sep=',', inferSchema=True, header=True)
    df.show(10)
    print("-----加载数据完成-----")

    # 获取热门(评论数最多)
    print("-----获取热门-----")
    df = df.groupBy("movieID").count().sort(['count'], ascending=False)
    df.show(10)
    print("-----获取热门完成-----")

    df = df.limit(250)  # 保存top250热门

    # 连接数据库
    output_uri = 'mongodb://mongodb:27017/{}.{}'.format('movie', 'trend_rank')

    # 存储
    my_spark = SparkSession\
        .builder\
        .appName("MyApp")\
        .config("spark.mongodb.output.uri", output_uri)\
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
        .getOrCreate()
    df.write.format("com.mongodb.spark.sql.DefaultSource").mode("overwrite").save()
    print("存储完成")

