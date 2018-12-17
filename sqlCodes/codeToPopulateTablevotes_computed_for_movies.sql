INSERT INTO votes_computed_for_movies(idmovie,number_of_votes_greater_or_equal_three) 
SELECT idmovie, count(*) as number_of_votes_greater_or_equal_three FROM ratings
where rating>3.0 group by idmovie