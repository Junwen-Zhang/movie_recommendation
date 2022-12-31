import findspark
findspark.init()
from pyspark import SparkConf, SparkContext
from pyspark.mllib.recommendation import ALS
from pyspark.mllib.recommendation import MatrixFactorizationModel
import math
import os
from time import time

sc = SparkContext("local", "first app")

# Load the complete dataset file
datasets_path = os.path.join('.', 'datasets')
complete_ratings_file = os.path.join(datasets_path, 'ml-latest', 'ratings.csv')
t0 = time()
complete_ratings_raw_data = sc.textFile(complete_ratings_file)
complete_ratings_raw_data_header = complete_ratings_raw_data.take(1)[0]
print("(1)Load time: ", time() - t0)

# Parse rating data
t0 = time()
complete_ratings_data = complete_ratings_raw_data.filter(lambda line: line!=complete_ratings_raw_data_header)\
    .map(lambda line: line.split(",")).map(lambda tokens: (int(tokens[0]),int(tokens[1]),float(tokens[2]))).cache()
print("(2)Parse rating data time: ", time() - t0)
print("There are %s recommendations in the complete dataset" % (complete_ratings_data.count()))

# Train
training_RDD, test_RDD = complete_ratings_data.randomSplit([8, 2], seed=0)
best_rank = 8
seed = 5
iterations = 10
regularization_parameter = 0.1
t0 = time()
complete_model = ALS.train(training_RDD, best_rank, seed=seed, 
                           iterations=iterations, lambda_=regularization_parameter)
print("(3)train time: ", time() - t0)
t0 = time()
model_path = os.path.join('.', 'models', 'movie_lens_train')
complete_model.save(sc, model_path)
print("(4)model save time: ", time() - t0)

# Test
t0 = time()
test_for_predict_RDD = test_RDD.map(lambda x: (x[0], x[1]))
predictions = complete_model.predictAll(test_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
print("(5)test time: ", time() - t0)
rates_and_preds = test_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
print('For testing data the RMSE is %s' % (error))

complete_movies_file = os.path.join(datasets_path, 'ml-latest', 'movies.csv')
complete_movies_raw_data = sc.textFile(complete_movies_file)
complete_movies_raw_data_header = complete_movies_raw_data.take(1)[0]

# Parse movie data
complete_movies_data = complete_movies_raw_data.filter(lambda line: line!=complete_movies_raw_data_header)\
    .map(lambda line: line.split(",")).map(lambda tokens: (int(tokens[0]),tokens[1],tokens[2])).cache()

complete_movies_titles = complete_movies_data.map(lambda x: (int(x[0]),x[1]))
    
print("There are %s movies in the complete dataset" % (complete_movies_titles.count()))

# compute average
def get_counts_and_averages(ID_and_ratings_tuple):
    nratings = len(ID_and_ratings_tuple[1])
    return ID_and_ratings_tuple[0], (nratings, float(sum(x for x in ID_and_ratings_tuple[1]))/nratings)
t0 = time()
movie_ID_with_ratings_RDD = (complete_ratings_data.map(lambda x: (x[1], x[2])).groupByKey())
movie_ID_with_avg_ratings_RDD = movie_ID_with_ratings_RDD.map(get_counts_and_averages)
movie_rating_counts_RDD = movie_ID_with_avg_ratings_RDD.map(lambda x: (x[0], x[1][0]))
print("(6)compute average time: ", time() - t0)

# add new user ratings
new_user_ID = 0
new_user_ratings = [ # (userID, movieID, rating)
     (0,260,9), # Star Wars (1977)
     (0,1,8), # Toy Story (1995)
     (0,16,7), # Casino (1995)
     (0,25,8), # Leaving Las Vegas (1995)
     (0,32,9), # Twelve Monkeys (a.k.a. 12 Monkeys) (1995)
     (0,335,4), # Flintstones, The (1994)
     (0,379,3), # Timecop (1994)
     (0,296,7), # Pulp Fiction (1994)
     (0,858,10) , # Godfather, The (1972)
     (0,50,8) # Usual Suspects, The (1995)
    ]
new_user_ratings_RDD = sc.parallelize(new_user_ratings)
print('New user ratings: %s' % new_user_ratings_RDD.take(10))

complete_data_with_new_ratings_RDD = complete_ratings_data.union(new_user_ratings_RDD)


# count the time for ALS training
t0 = time()
new_ratings_model = ALS.train(complete_data_with_new_ratings_RDD, best_rank, seed=seed, 
                              iterations=iterations, lambda_=regularization_parameter)
tt = time() - t0
print("(7)New model trained in %s seconds" % round(tt,3))


# get top recommendations
new_user_ratings_ids = map(lambda x: x[1], new_user_ratings) # get just movie IDs
# keep just those not on the ID list (thanks Lei Li for spotting the error!)
new_user_unrated_movies_RDD = (complete_movies_data.filter(lambda x: x[0] not in new_user_ratings_ids).map(lambda x: (new_user_ID, x[0])))

# Use the input RDD, new_user_unrated_movies_RDD, with new_ratings_model.predictAll() to predict new ratings for the movies
t0 = time()
new_user_recommendations_RDD = new_ratings_model.predictAll(new_user_unrated_movies_RDD)
print("(8)predict all time: ", time() - t0)

# Transform new_user_recommendations_RDD into pairs of the form (Movie ID, Predicted Rating)
t0 = time()
new_user_recommendations_rating_RDD = new_user_recommendations_RDD.map(lambda x: (x.product, x.rating))
new_user_recommendations_rating_title_and_count_RDD = \
    new_user_recommendations_rating_RDD.join(complete_movies_titles).join(movie_rating_counts_RDD)
new_user_recommendations_rating_title_and_count_RDD.take(3)

new_user_recommendations_rating_title_and_count_RDD = \
    new_user_recommendations_rating_title_and_count_RDD.map(lambda r: (r[1][0][1], r[1][0][0], r[1][1]))

top_movies = new_user_recommendations_rating_title_and_count_RDD.filter(lambda r: r[2]>=25).takeOrdered(25, key=lambda x: -x[1])
print("(9)get top movie time: ", time() - t0)

# get individual rating
print ('TOP recommended movies (with more than 25 reviews):\n%s' %
        '\n'.join(map(str, top_movies)))

my_movie = sc.parallelize([(0, 500)]) # Quiz Show (1994)
individual_movie_rating_RDD = new_ratings_model.predictAll(new_user_unrated_movies_RDD)
individual_movie_rating_RDD.take(1)


# save the model
model_path = os.path.join('.', 'models', 'movie_lens_als')
new_ratings_model.save(sc, model_path)
# same_model = MatrixFactorizationModel.load(sc, model_path)