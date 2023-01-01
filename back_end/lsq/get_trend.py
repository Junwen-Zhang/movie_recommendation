import findspark
findspark.init()

from pyspark import SparkContext
from pyspark.sql import SQLContext, SparkSession
import os

def get_trend():
    sc = SparkContext()
    sc.setLogLevel("WARN")

    # 连接mongodb
    input_uri = 'mongodb://mongodb:27017/{}.{}'.format('movie', 'trend_rank')

    my_spark = SparkSession\
        .builder\
        .appName("MyApp")\
        .config("spark.mongodb.input.uri", input_uri)\
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
        .getOrCreate()

    df = my_spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
    df = df.sample(fraction = 1.0*11/250).limit(10)
    df.show()

    id_array = df.select("movieID").rdd.flatMap(lambda x: x).collect()
    print(id_array)

    return id_array
