import findspark
findspark.init()

from pyspark.sql import SparkSession
import math
import os

# 加载数据
spark = SparkSession.builder.appName('getTrend').getOrCreate()

complete_ratings_file = os.path.join('datasets', 'ml-latest', 'ratings.csv')
df = spark.read.csv(complete_ratings_file, sep=',', inferSchema=True, header=True)

df.show(10)

# 获取热门(评论数最多)
df = df.groupBy("movieID").count()
df.show(10)

df = df.sort(['count'], ascending=False)
df.show(10)
