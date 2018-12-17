import csv
import numpy as np
import mysql.connector
import sys
from sklearn.cluster import KMeans
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


if __name__ == "__main__":
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="123456",
        database="elo7_datascience",
        get_warnings=False,
        raise_on_warnings=False
    )
    cursor = mydb.cursor()
    cursor.execute("SELECT idmovie,valuesdata FROM elo7_datascience.genome_scores_at_one_line")
    descriptorsNumber=1128
    descriptorsForAllMovies={}
    for idmovie,valuesdata in cursor:
        descriptors=np.zeros(descriptorsNumber,dtype=np.float)
        descriptorsAtString=list(csv.reader([valuesdata]))[0]
        for j in range(descriptorsNumber):
            descriptors[j]=float(descriptorsAtString[j])

        descriptorsForAllMovies[idmovie]=descriptors

    keys=list(descriptorsForAllMovies.keys())
    descriptorsMat=np.zeros((len(keys),len(descriptorsForAllMovies[keys[0]])))
    i=0
    for key in keys:        
        descriptorsMat[i]=descriptorsForAllMovies[key]
        i=i+1
    for i in range (18):
        kmeans = KMeans(n_clusters=i+3, random_state=0).fit(descriptorsMat)
        i=0
        for key in keys:
            cursor.execute("UPDATE movie SET cluster = {d0} WHERE idmovie={d1} ".format(d0=kmeans.labels_[i],d1=key))        
            i=i+1
        mydb.commit()
        result=selectInDataBase(mydb,"Select cluster, std(rating) as std FROM ratings inner join movie on movie.idmovie=ratings.idmovie where cluster is not null group by cluster ")
        stdRating=[]
        i=0
        for line in result:
            stdRating.append(line["std"])
        
        print(str(i)+":"+str(np.mean(np.array(stdRating))))
        i=i+1''
        sys.stdout.flush()
