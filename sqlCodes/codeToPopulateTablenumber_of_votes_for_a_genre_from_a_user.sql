INSERT INTO number_of_votes_for_a_genre_from_a_user(number_of_votes,idgenre,iduser)
SELECT count(*) as number_of_votes,relation_movie_genre.idgenre as idgenre, ratings.iduser as iduser FROM ratings 
inner join relation_movie_genre  on ratings.idmovie=relation_movie_genre.idmovie
group by relation_movie_genre.idgenre, iduser
