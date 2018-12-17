/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=0.5
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=1.0
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=1.5
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=2.0
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=2.5
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=3.0
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/



/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=3.5
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=4.0
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=4.5
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/

/*saber quanto de nota tem um genero*/
SELECT count(*),genre.name from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie  where rating=5.0
group by relation_movie_genre.idgenre 
order by genre.name;
/*======================================*/


use elo7_datascience;
SELECT count(*),genre.name, ratings.timestamp, ratings.iduser from movie 
inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
inner join genre on relation_movie_genre.idgenre=genre.idgenre
inner join ratings on ratings.idmovie=movie.idmovie 
where ratings.iduser=1
group by ratings.timestamp, genre.name, ratings.iduser
order by ratings.timestamp, genre.name, ratings.iduser


