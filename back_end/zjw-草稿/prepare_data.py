import findspark
findspark.init()

from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, SparkSession
from pyspark.sql.functions import desc, avg, count
import os

sc = SparkContext()
sc.setLogLevel("WARN")
sqlContext = SQLContext(sc)

# 读取数据
complete_ratings_file = os.path.join('datasets', 'ml-latest', 'ratings.csv')
complete_ratings_raw_data = sc.textFile(complete_ratings_file)
complete_ratings_raw_data_header = complete_ratings_raw_data.take(1)[0]

# 解析数据
userId_movieId_data = complete_ratings_raw_data.filter(lambda line: line!=complete_ratings_raw_data_header)\
    .map(lambda line: line.split(",")).map(lambda tokens: (int(tokens[0]),int(tokens[1]))).cache()
print("There are %s recommendations in the complete dataset" % (userId_movieId_data.count()))

# 合并每个user的movieId，形成一个列表
userId_movie_list = userId_movieId_data.groupByKey().mapValues(list)

df = sqlContext.createDataFrame(userId_movie_list,['userId','rated_movie_list'])
df.show(10)


# 连接mongodb，并存入dataframe
output_uri = 'mongodb://mongodb:27017/{}.{}'.format('movie', 'user_movielist')
my_spark = SparkSession\
    .builder\
    .appName("MyApp")\
    .config("spark.mongodb.output.uri", output_uri)\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.1') \
    .getOrCreate()
df.write.format("com.mongodb.spark.sql.DefaultSource").mode("overwrite").save()
