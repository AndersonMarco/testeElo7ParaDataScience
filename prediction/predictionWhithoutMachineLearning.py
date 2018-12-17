import numpy as np
import mysql.connector
import random
def shuffleVector(vector):
    vectorT=np.copy(vector)
    for i in range(len(vectorT)*4):
        position1ForUsersList=random.randint(0,len(vectorT)-1)
        position2ForUsersList=random.randint(0,len(vectorT)-1)
        userTemp=vectorT[position1ForUsersList]
        vectorT[position1ForUsersList]=vectorT[position2ForUsersList]
        vectorT[position2ForUsersList]=userTemp
    return vectorT

def getMovieSuggedtedForTheUser(mydb,iduser):
    movieTittle=""
    sqlToGetGenresMoreVoted="""SELECT count(*) as number_of_votes,relation_movie_genre.idgenre as idgenre FROM ratings 
                               inner join relation_movie_genre  on ratings.idmovie=relation_movie_genre.idmovie
                               where iduser={d0}
                               group by relation_movie_genre.idgenre
                               order by number_of_votes desc 
                               limit 3""".format(d0=iduser)

    cursor = mydb.cursor()
    cursor.execute(sqlToGetGenresMoreVoted)
    genres=[]
    for number_of_votes, idgenre in cursor:
        genres.append(idgenre)
    
    movieWasFound=False
    for i in range(6):
        if(len(genres)==0):
            break
        genreChoosed=genres[random.randint(0,len(genres)-1)]

        sqlToGetTheVotesAverageAndSTDForAGenre="""SELECT  avg(number_of_votes_greater_or_equal_three), std(number_of_votes_greater_or_equal_three) FROM votes_computed_for_movies as vo
                                                   inner join relation_movie_genre re on re.idmovie=vo.idmovie
                                                   where re.idgenre={d0}
                                               """.format(d0=genreChoosed)
        cursor.execute(sqlToGetTheVotesAverageAndSTDForAGenre)
        returnFromCursor=list(cursor)
        averagePlusSTDForNumberOfVotesOfAGenre=round(float(returnFromCursor[0][1])+ float(returnFromCursor[0][0]))
        sqlToGetMoviesMoreVotedForAGenre="""SELECT * FROM (
                                                            SELECT re.idmovie as idmovie, number_of_votes_greater_or_equal_three FROM votes_computed_for_movies as vo
                                                            inner join relation_movie_genre re on re.idmovie=vo.idmovie
                                                            where re.idgenre={d0} and number_of_votes_greater_or_equal_three>={d1}
                                                            order by number_of_votes_greater_or_equal_three desc
                                                            limit 1000
                                                        ) as temp
                                                        ORDER BY RAND() 
                                            """.format(d0=genreChoosed,d1=averagePlusSTDForNumberOfVotesOfAGenre)
        
        cursor.execute(sqlToGetMoviesMoreVotedForAGenre)
        moviesToRecommend=[]
        for idmovie, number_of_votes_greater_or_equal_three in cursor:
            moviesToRecommend.append(idmovie)
            
        for idmovie in moviesToRecommend:            
            sqlToCheckIfTheMoviesWasvotedByUser="""SELECT count(*) as nlines  FROM ratings
                                                    WHERE iduser={d0} and idmovie={d1}""".format(d0=iduser,d1=idmovie)            
            cursor.execute(sqlToCheckIfTheMoviesWasvotedByUser)
            nLinesReturnedBySqlToCheckIfTheMoviesWasvotedByUser= list(cursor)[0][0]
            if(nLinesReturnedBySqlToCheckIfTheMoviesWasvotedByUser==0):
                sqlToGetMovieTittle=""" SELECT tittle  FROM movie
                                      WHERE idmovie={d0}""".format(d0=idmovie)
                cursor.execute(sqlToGetMovieTittle)
                movieName=list(cursor)[0][0]
                movieTittle=movieName
                movieWasFound=True
                break
                
        if(movieWasFound):
            break
            
    if(movieWasFound==False):
        cursor.execute("SELECT idmovie,tittle FROM elo7_datascience.movie ORDER BY RAND() limit 1000;")
        movies=[]
        for idmovie,tittle in cursor:
            movies.append({'idmovie':idmovie, 'tittle': tittle})
            
        for movie in movies:
            sqlToCheckIfTheMoviesWasvotedByUser="""SELECT count(*) as nlines  FROM ratings
                                                   WHERE iduser={d0} and idmovie={d1}""".format(d0=iduser,d1=movie["idmovie"])
            cursor.execute(sqlToCheckIfTheMoviesWasvotedByUser)
            nLinesReturnedBySqlToCheckIfTheMoviesWasvotedByUser=list(cursor)[0][0]
            if(nLinesReturnedBySqlToCheckIfTheMoviesWasvotedByUser==0):
                movieWasFound=True
                movieTittle=movie["tittle"]
                break
                
            
            
    if(movieWasFound==False):
        movieTittle="****Erro não foi encontrado nenhum filme cujo o usuario já não tenha visto*****"        
    return movieTittle

if __name__ == "__main__":
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="123456",
        database="elo7_datascience",
        get_warnings=False,
        raise_on_warnings=False
    )

    print(getMovieSuggedtedForTheUser(mydb,5))