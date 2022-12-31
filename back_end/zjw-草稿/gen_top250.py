import findspark
findspark.init()

from pyspark import SparkContext
from pyspark.sql import SQLContext, SparkSession
from pyspark.sql.functions import desc, avg, count
import os

sc = SparkContext()
sc.setLogLevel("WARN")
sqlContext = SQLContext(sc)

# 读取csv数据
complete_ratings_file = os.path.join('datasets', 'ml-latest', 'ratings.csv')
df = sqlContext.read\
    .format('com.databricks.spark.csv')\
    .options(header='true', inferschema='true')\
    .load(complete_ratings_file)

# 处理数据
df.show(5)
df = df.groupby('movieId')\
    .agg(count("*").alias("cnt_rating"),avg("rating").alias("avg_rating"))
df.show(20)
df = df.filter(df.cnt_rating>=200).orderBy(desc("avg_rating"))
df.show(10)
df = df.limit(250)


# 连接mongodb，并存入dataframe
output_uri = 'mongodb://mongodb:27017/{}.{}'.format('movie', 'rating_rank')
my_spark = SparkSession\
    .builder\
    .appName("MyApp")\
    .config("spark.mongodb.output.uri", output_uri)\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
    .getOrCreate()
df.write.format("com.mongodb.spark.sql.DefaultSource").mode("overwrite").save()
