import findspark
findspark.init()

from pyspark import SparkContext
from pyspark.sql import SQLContext, SparkSession
from pyspark.sql.functions import desc, avg, count
import os

sc = SparkContext()
sc.setLogLevel("WARN")
sqlContext = SQLContext(sc)

# 连接mongodb，并存入dataframe
input_uri = 'mongodb://mongodb:27017/{}.{}'.format('movie', 'rating_rank')
my_spark = SparkSession\
    .builder\
    .appName("MyApp")\
    .config("spark.mongodb.input.uri", input_uri)\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
    .getOrCreate()

df = my_spark.read.format('com.mongodb.spark.sql.DefaultSource').load()
df = df.sample(fraction = 1.0*11/250).limit(10)
df.show()
