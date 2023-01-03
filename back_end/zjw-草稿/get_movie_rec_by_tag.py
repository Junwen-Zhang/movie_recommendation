from gensim.models import word2vec,Word2Vec
import numpy as np
import pandas as pd

TagRec_model = Word2Vec.load('TagRec.model')
mv_tags_vectors = TagRec_model.docvecs.vectors_docs
movieId_index = pd.read_csv('df_save.csv')

# history of movies the user watched and liked
user_id = 1
# 这里在实际应用中要从`ratings.csv`中获得用户标记过的movieid
user_movies_index = [307,
481,
1091,
1257,
1449,
1590,
1591,
2134,
2478,
2840,
2986,
3020,
3424,
3698,
3826,
3893
]  

# compute user vector as an average of movie vectors seen by that user
user_movie_vector = np.zeros(shape = mv_tags_vectors.shape[1])
for mv_index in user_movies_index:
  user_movie_vector += mv_tags_vectors[mv_index]

user_movie_vector /= len(user_movies_index)  
  

#  find movies similar to user vector to generate movie recommendations
print('Movie Recommendations:')

sims = TagRec_model.docvecs.most_similar(positive = [user_movie_vector], topn = 30)

for i, j in sims:
  movie_sim = movieId_index.loc[int(i), "movieId"]
  if movie_sim not in user_movies_index:
    print(movie_sim, movieId_index.loc[int(i), "Title"])