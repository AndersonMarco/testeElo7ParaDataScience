import mysql.connector
import numpy as np
import sys
import math

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

movies={}
sql="""SELECT count(*) as qtyVotes ,idmovie, rating FROM ratings            
            group by idmovie,rating            
        """
cursor = mydb.cursor()

cursor.execute(sql)
line=0
for qtyVotes,idmovie, rating in cursor:
    line=line+1
    if(line%1000==0):
        print(line)
        sys.stdout.flush()
    
    
    if(not(idmovie in movies )):
        movies[idmovie]={}
        movies[idmovie]["qtyRates"]={}
    if(not (rating in  movies[idmovie]["qtyRates"]) ):
        movies[idmovie]["qtyRates"][rating]=0.0
    movies[idmovie]["qtyRates"][rating]=movies[idmovie]["qtyRates"][rating]+rating


entropies=[]
for movieId in movies.keys():
    totalRate=0.0
    entropy=0.0
    for rateId in movies[movieId]['qtyRates'].keys():
        totalRate=float(movies[movieId]['qtyRates'][rateId])+totalRate
    for rateId in movies[movieId]['qtyRates'].keys():
        prob=float(movies[movieId]['qtyRates'][rateId])/totalRate
        entropy=entropy+((math.log(prob)/math.log(2))*prob)
    if(len(movies[movieId]['qtyRates'].keys())>1):
        entropy=-entropy/(math.log(len(movies[movieId]['qtyRates'].keys()))/math.log(2))
    else:
        entropy=0
    entropies.append(entropy)

print("average entropies"+str(np.average(np.array(entropies))))
print("std entropies"+str(np.std(np.array(entropies))))
