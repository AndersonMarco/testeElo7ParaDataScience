import numpy as np
import mysql.connector
import csv
from datetime import datetime
from sklearn import tree
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn.neural_network import MLPClassifier
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import random
import tensorflow as tf
import sys
import pandas as pd

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

def getPCAsAppliedAtGenres(mydb,idGenre):
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
    pcaRet={}
    for  i in range(len(genome_scoresAtSqlSelect)):
        pcaRet[genome_scoresAtSqlSelect[i]['idmovie']]=componentsForObjects[i]
    return pcaRet

#idGenre=str(sys.argv[1])
idGenre="9"
genreName=selectInDataBase(mydb,"SELECT * from genre where idgenre="+idGenre)[0]["name"]
#genomeScoresPCASelect=selectInDataBase(mydb,"SELECT * FROM genome_scores_pca_at_one_line")
genomeScoresInformation=selectInDataBase(mydb,"SELECT * FROM genome_tags")
genomeScoresAverage=np.zeros(len(genomeScoresInformation),dtype=np.float32)
genomeScoresStd=np.zeros(len(genomeScoresInformation),dtype=np.float32)
i=0
for line in genomeScoresInformation:
    genomeScoresAverage[i]=line['avg']
    genomeScoresStd[i]=line['std']
    i=i+1
descritorNumber=256
genomeScoresPCAIndexByMovieId=getPCAsAppliedAtGenres(mydb,idGenre)
#for line in genomeScoresPCASelect:
#    valuesdata=line['valuesdata']
#    genomeScoresPCAIndexByMovieId[line['idmovie']]=(np.array(list(csv.reader([valuesdata]))[0], dtype=np.float)[:descritorNumber])
cursor = mydb.cursor()

nLinesForTrain=50000

descriptorsTrain=np.zeros((nLinesForTrain,descritorNumber),dtype=np.float32)
ratingsTrain=np.zeros(nLinesForTrain,dtype=np.int8)







sql = """SELECT ra.rating as rating,ra.idrand as idrand, ra.idmovie as idmovie FROM ratings ra
         inner join relation_movie_genre rg  on rg.idmovie=ra.idmovie
         inner join genome_scores_pca_at_one_line gp  on gp.idmovie=ra.idmovie
         where idgenre={d0}  order by idrand
         limit 500000 """.replace("\n"," ").format(d0=idGenre)

cursor.execute (sql)
sqlReturn={}
sqlReturn["idmovie"]=np.zeros(500000,dtype=np.int)
sqlReturn["idrand"]=np.zeros(500000,dtype=np.int)
sqlReturn["rating"]=np.zeros(500000,dtype=np.float)
line=0
print("=============================================")
for (rating,idrand,idmovie) in cursor:
     sqlReturn["idmovie"][line]=idmovie
     sqlReturn["idrand"][line]=idrand
     sqlReturn["rating"][line]=rating
     line=line+1
     if((line%1000)==0):
        print(line)
print("=============================================")
sqlColumns=["rating","idrand","idmovie"]
df = pd.DataFrame(sqlReturn)
maxIdrand=0
line=0
for rate in [0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5]:
        print("rate="+str(rate))
        rateFilter=df[df["rating"].isin([rate])]
        for row in rateFilter.iterrows():            
            if(maxIdrand<int(row[1]['idrand'])):
                maxIdrand=(row[1]['idrand'])
            if(float(row[1]['rating'])>=3):
                ratingsTrain[line]=1
            else:
                ratingsTrain[line]=0
                                     
            descriptorsT=genomeScoresPCAIndexByMovieId[int(row[1]['idmovie'])]
            for i in range(descritorNumber):
                descriptorsTrain[line][i]=descriptorsT[i]
            if((line%1000)==0):
                print(line)
            line=line+1
            if(line%5000==0):                
                break
           

sql = """SELECT ra.rating as rating,ra.idrand as idrand, ra.idmovie as idmovie FROM ratings ra
         inner join relation_movie_genre rg  on rg.idmovie=ra.idmovie
         inner join genome_scores_pca_at_one_line gp  on gp.idmovie=ra.idmovie
         where idgenre={d0} and idrand>{d1} order by idrand         
         limit 50000""".replace("\n"," ").format(d0=idGenre,d1=maxIdrand)
print(sql)
print(sql)
cursor.execute (sql)
line=0
descriptorsTest=np.zeros((50000,descritorNumber),dtype=np.float32)
ratingsTest=np.zeros(500000,dtype=np.int8)
for rating,idrand,idmovie in cursor:
    if(rating>=3.0):
        ratingsTest[line]=1
    else:
        ratingsTest[line]=0
    
    descriptorsT=genomeScoresPCAIndexByMovieId[idmovie]
    for i in range(descritorNumber):
        descriptorsTest[line][i]=descriptorsT[i]
    if((line%1000)==0):
        print(line)
    line=line+1
    
ratingsTest=ratingsTest[:line]
descriptorsTest=descriptorsTest[:line]
fold=0
fp=open("logForTraningOfModelsOfGenre_"+genreName+".csv","w")

print("===========================================================================")
print("fold:"+str(fold))
model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(256, activation=tf.nn.relu),                
    tf.keras.layers.Dense(256, activation=tf.nn.relu),
    tf.keras.layers.Dense(256, activation=tf.nn.relu),
    tf.keras.layers.Dropout(0.2),            
    tf.keras.layers.Dense(10, activation=tf.nn.softmax)
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(descriptorsTrain,ratingsTrain, epochs=3)
    
       
unique, counts =np.unique(ratingsTest, return_counts=True)
evaluate=model.evaluate(descriptorsTest, ratingsTest)
fp.write("fold:"+str(fold)+"\n")
fp.write("Majority classes:"+str(float(max(counts))/float(sum(counts)))+"\n")
fp.write("evaluate[0]:"+str(evaluate[0])+"\n")
fp.write("evaluate[1]:"+str(evaluate[1])+"\n")


fold=fold+1

tf.keras.models.save_model(model,"model_fold_"+str(fold)+"_for_genre_"+genreName+".hdf5",overwrite=True,include_optimizer=True)
fp.flush()
fp.close()
