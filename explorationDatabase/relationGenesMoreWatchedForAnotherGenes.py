import numpy as np
import mysql.connector
import csv
import numpy as np

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123456",
  database="elo7_datascience2",
  get_warnings=False,
  raise_on_warnings=False
)
def selectInDataBase(sqlConnection, select):
    cursor = sqlConnection.cursor()
    cursor.execute (select)
    fields = map(lambda x:x[0], cursor.description)
    fields=[]
    for x in cursor.description:
        fields.append(x[0])
    ret=[]
    for data in cursor.fetchall():
        line={}
        for i in range(len(fields)):
            line[fields[i]]=data[i]
        ret.append(line)
    return ret

sqlCountOfVotesEqualOrGreaterThanThreeForOneGenreByUser="""SELECT count(*) as numberOfVotes,genre.name as name,ratings.iduser as iduser from movie 
                                                           inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
                                                           inner join genre on relation_movie_genre.idgenre=genre.idgenre
                                                           inner join ratings on ratings.idmovie=movie.idmovie 
                                                           where ratings.rating>=3.0
                                                           group by relation_movie_genre.idgenre,ratings.iduser
                                                           order by  ratings.iduser,count(*) DESC;
                                                       """.replace("\n"," ")

sqlCountOfVotesLowerThanThreeForOneGenreByUser="""SELECT count(*) as numberOfVotes,genre.name as name,ratings.iduser as iduser from movie 
                                                  inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
                                                  inner join genre on relation_movie_genre.idgenre=genre.idgenre
                                                  inner join ratings on ratings.idmovie=movie.idmovie 
                                                  where ratings.rating<3.0
                                                  group by relation_movie_genre.idgenre,ratings.iduser
                                                  order by  ratings.iduser,count(*) DESC;
                                               """.replace("\n"," ")                                                       

genresMat={}
genresList=selectInDataBase(mydb,"select * from genre order by name;")
i=0
while(i<len(genresList)):
    genreNameLine=genresList[i]['name']
    j=0
    lineGenres={}
    while(j<len(genresList)):
        lineGenres[genresList[j]['name']]=0
        j=j+1
    genresMat[genresList[i]['name']]=lineGenres
    i=i+1
cursor = mydb.cursor()
cursor.execute (sqlCountOfVotesEqualOrGreaterThanThreeForOneGenreByUser)


previousIdUser=-1
listOfGenresMoreVotedByUser={}
for (numberOfVotes, name,iduser) in cursor:
    if(previousIdUser==-1):
        previousIdUser=iduser
    elif(previousIdUser!=iduser):
        genresMoreVoted=[]
        for v in listOfGenresMoreVotedByUser:
            if(len(genresMoreVoted)==0):
                genresMoreVoted.append(v)
            elif(listOfGenresMoreVotedByUser[genresMoreVoted[0]]<listOfGenresMoreVotedByUser[v]):
                genresMoreVoted=[v]
            elif(listOfGenresMoreVotedByUser[genresMoreVoted[0]]==listOfGenresMoreVotedByUser[v]):
                genresMoreVoted.append(v)
        for genre in genresMoreVoted:
            for columnForGenresMat in listOfGenresMoreVotedByUser:
                genresMat[genre][columnForGenresMat]=genresMat[genre][columnForGenresMat]+listOfGenresMoreVotedByUser[columnForGenresMat]
                
        listOfGenresMoreVotedByUser={}
        previousIdUser=iduser

    listOfGenresMoreVotedByUser[name]=numberOfVotes
    
genreMoreVoted=max(listOfGenresMoreVotedByUser)
for columnForGenresMat in listOfGenresMoreVotedByUser:
    genresMat[genreMoreVoted][columnForGenresMat]=genresMat[genreMoreVoted][columnForGenresMat]+listOfGenresMoreVotedByUser[columnForGenresMat]
    

mat=np.zeros((len(genresMat),len(genresMat)))
keys=genresMat.keys()
i=0
for keyI in keys:
    j=0
    for keyJ in keys:
        mat[i][j]=float(genresMat[keyI][keyJ])
        j=j+1
    i=i+1


for line in mat:
    lineStr=""
    for v in line:
        lineStr=lineStr+","+str(v)
    print(lineStr)
