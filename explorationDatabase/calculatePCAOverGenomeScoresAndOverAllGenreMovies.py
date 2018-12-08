import mysql.connector
import csv
import numpy as np
from datetime import datetime
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
#use elo7_datascience;
#SELECT sum(rating),genre.name from movie 
#inner join relation_movie_genre  on relation_movie_genre.idmovie=movie.idmovie
#inner join genre on relation_movie_genre.idgenre=genre.idgenre
#inner join ratings on ratings.idmovie=movie.idmovie 
#group by relation_movie_genre.idgenre
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123456",
  database="elo7_datascience",
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

ntags=1128
movieList=selectInDataBase(mydb,"SELECT DISTINCT(idmovie) from genome_scores_at_one_line order by idmovie")
movieIdsToPosition={}
positionToIdMovie={}
for movie in movieList:
    lenPositionToIdMovie=len(positionToIdMovie)
    movieIdsToPosition[movie["idmovie"]]=lenPositionToIdMovie
    positionToIdMovie[lenPositionToIdMovie]=movie["idmovie"]
    
nmovies=len(positionToIdMovie)
genome_scores=np.zeros((nmovies,ntags))

mycursor = mydb.cursor()
sql = "Select idmovie,valuesdata from genome_scores_at_one_line  order by idmovie "
cursor = mydb.cursor()
cursor.execute (sql)

for (idmovie,valuesdata) in cursor:
    genome_scores[movieIdsToPosition[idmovie]]=np.array(list(csv.reader([valuesdata]))[0], dtype=np.float)


X=genome_scores
scaler = StandardScaler()
scaler.fit(X)
X=scaler.transform(X)    
pca = PCA()
componentsForObjects = pca.fit_transform(X)
i=0
print("====================================")
cursor = mydb.cursor()
sqlCommands=0
for moviePosition in range(nmovies):    
    VIstring = ','.join(['%.5f' % num for num in componentsForObjects[moviePosition]])
    sql = "INSERT INTO genome_scores_pca_at_one_line (idmovie,valuesdata)  VALUES ({d0},'{d1}')".format(d0=(positionToIdMovie[moviePosition]),d1=VIstring)
    mycursor.execute(sql)
    sqlCommands=sqlCommands+1
   
    print(sqlCommands)
    mydb.commit()


mydb.commit()

#for i in range(len(pca.explained_variance_ratio_)):
#    sumForPCAComponents=sum(pca.explained_variance_ratio_[0:i+1])
   
#    print(str(i)+":"+str(sumForPCAComponents))
#    if(sumForPCAComponents>0.9):
#         break
