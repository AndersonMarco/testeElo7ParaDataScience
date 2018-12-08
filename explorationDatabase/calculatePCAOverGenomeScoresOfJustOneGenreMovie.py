import mysql.connector
import csv
import numpy as np
from datetime import datetime
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
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

mydb = mysql.connector.connect(
  host="192.168.1.100",
  user="root",
  passwd="123456",
  database="elo7_datascience",
  get_warnings=False,
  raise_on_warnings=False
)

idGenre=9
sql="""SELECT valuesdata, relation_movie_genre.idmovie FROM genome_scores_at_one_line
       inner join relation_movie_genre on relation_movie_genre.idmovie=genome_scores_at_one_line.idmovie
       where relation_movie_genre.idgenre={d0};""".replace("\n"," ").format(d0=idGenre)


genome_scoresAtSqlSelect=selectInDataBase(mydb,sql)

genome_scores=np.zeros((len(genome_scoresAtSqlSelect),len(genome_scoresAtSqlSelect[0]['valuesdata'].split(","))))

converterPostionAtGenome_scoresToIdMovie={}
converterIdMovieToPostionAtGenome_scores={}
for i in range(len(genome_scoresAtSqlSelect)):

    lineForGenomeScore=list(csv.reader([genome_scoresAtSqlSelect[i]['valuesdata']]))[0]
    genome_scores[i]=np.array(lineForGenomeScore,dtype=np.float)
    converterPostionAtGenome_scoresToIdMovie[i]=genome_scoresAtSqlSelect[i]['idmovie']
    converterIdMovieToPostionAtGenome_scores[genome_scoresAtSqlSelect[i]['idmovie']]=i

X=genome_scores
scaler = StandardScaler()
scaler.fit(X)
X=scaler.transform(X)    
pca = PCA()
componentsForObjects = pca.fit_transform(X)

x=[[],[],[],[],[],[],[],[],[],[]]
y=[[],[],[],[],[],[],[],[],[],[]]

sql="""SELECT r1.rating as rating,rg.idmovie as idmovie FROM  ratings r1
       inner join relation_movie_genre rg  on rg.idmovie=r1.idmovie
       where rg.idgenre={d0}  order by idrand limit 50000""".replace("\n"," ").format(d0=idGenre)
cursor = mydb.cursor()
cursor.execute (sql)
for (rating,idmovie) in cursor:
    if(idmovie in converterIdMovieToPostionAtGenome_scores ):
        position=converterIdMovieToPostionAtGenome_scores[idmovie]
        if(rating<4.0):
            x[0].append(componentsForObjects[position][0])
            y[0].append(componentsForObjects[position][1])
        else:
            x[1].append(componentsForObjects[position][0])
            y[1].append(componentsForObjects[position][1])
#        x[int(float(rating)*2)-1].append(componentsForObjects[position][0])
#        y[int(float(rating)*2)-1].append(componentsForObjects[position][1])

colors=["red","green","blue"]
#x=[[2.2,5.0,6.0],[2.2,5.0,6.0]]
#y=[[1.2,5.0,6.0],[2.2,6.0,7.0]]
fig = plt.figure()

ax = fig.add_subplot(1, 1, 1, axisbg="1.0")    

coi=0
volume=[70.0,180.0]
alpha=[1.0,0.01]
coi=0
for i in [0,1]:    
    ax.scatter(x[i], y[i],c=colors[coi],label=i,edgecolors='none', s=volume[coi], alpha=alpha[coi])
    coi=coi+1
plt.title('Matplot scatter plot')
plt.legend(loc=2)
plt.show()
print("oi")
