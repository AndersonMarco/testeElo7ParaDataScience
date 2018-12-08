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
  host="localhost",
  user="root",
  passwd="123456",
  database="elo7_datascience",
  get_warnings=False,
  raise_on_warnings=False
)

idUser=61
sql="""SELECT gs.valuesdata as valuesdata, gs.idmovie as idmovie FROM genome_scores_at_one_line as gs
       inner join ratings as ra on ra.idmovie=gs.idmovie
       WHERE ra.iduser = {d0};""".replace("\n"," ").format(d0=idUser)


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

sql="""SELECT rating, idmovie FROM ratings 
       where iduser={d0}  """.replace("\n"," ").format(d0=idUser)
cursor = mydb.cursor()
cursor.execute (sql)
for (rating,idmovie) in cursor:
    if(idmovie in converterIdMovieToPostionAtGenome_scores ):
        position=converterIdMovieToPostionAtGenome_scores[idmovie]
        #if(rating<4.0):
            #x[0].append(componentsForObjects[position][0])
            #y[0].append(componentsForObjects[position][1])
        #else:
            #x[1].append(componentsForObjects[position][0])
            #y[1].append(componentsForObjects[position][1])
        x[int(float(rating))-1].append(componentsForObjects[position][0])
        y[int(float(rating))-1].append(componentsForObjects[position][1])

colors=["red","green","blue","cyan","magenta"]
#x=[[2.2,5.0,6.0],[2.2,5.0,6.0]]
#y=[[1.2,5.0,6.0],[2.2,6.0,7.0]]
fig = plt.figure()

ax = fig.add_subplot(1, 1, 1, axisbg="1.0")    

coi=0
volume=[70.0,70.0,70,70,70,70,70]
alpha=[0.3,0.3,0.3,0.3,0.3]
coi=0
for i in [0,1,2,3,4]:    
    ax.scatter(x[i], y[i],c=colors[coi],label=i,edgecolors='none', s=volume[coi], alpha=alpha[coi])
    coi=coi+1
plt.title('Matplot scatter plot')
plt.legend(loc=2)
plt.show()
print("oi")
