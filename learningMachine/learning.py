import numpy as np
import mysql.connector
import csv
from datetime import datetime
from sklearn import tree
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn.neural_network import MLPClassifier
import random


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



movieList=selectInDataBase(mydb,"SELECT * from movie order by idmovie")
movieIdsToPosition={}
positionToIdMovie={}
for movie in movieList:
    lenPositionToIdMovie=len(positionToIdMovie)
    movieIdsToPosition[movie["idmovie"]]=lenPositionToIdMovie
    positionToIdMovie[lenPositionToIdMovie]=movie["idmovie"]

cursor = mydb.cursor()
descritorNumber=40
descriptors=np.zeros((45000,descritorNumber))
ratings=np.zeros(45000,dtype=np.int32)
line=0
for rate in ["0.5","1.0","1.5","2.5","3.0","3.5","4.0","4.5","5"]:
    sql = "SELECT valuesdata,rating FROM elo7_datascience.genome_scores_pca_at_one_line  g1 inner join ratings r1 on g1.idmovie= r1.idmovie inner join relation_movie_genre rg  on rg.idmovie=g1.idmovie where rg.idgenre=5 and rating={d0} limit 5000".format(d0=rate)
    cursor.execute (sql)
    
    for (valuesdata, rating) in cursor:
        descriptorsAtString=list(csv.reader([valuesdata]))[0]
        ratings[line]=(int(float(rating)*2))
        for j in range(descritorNumber):
            descriptors[line][j]=float(descriptorsAtString[j])
        if((line%1000)==0):
            print(line)
        line=line+1

for i in range(100000):
    aux=0
    auxLine=np.zeros(descritorNumber)
    id0=random.randint(0,len(ratings)-1)
    id1=random.randint(0,len(ratings)-1)
    auxLine=np.copy(descriptors[id1])
    aux=ratings[id1]
    descriptors[id1]=np.copy(descriptors[id0])
    ratings[id1]=ratings[id0]
    descriptors[id0]=auxLine
    ratings[id0]=aux

kf = KFold(n_splits=10,shuffle=True,random_state=3223)
for k in [7,5]:
    print("K="+str(k))
    for train_index, test_index in kf.split(descriptors):
        X_train, X_test = descriptors[train_index], descriptors[test_index]
        y_train, y_test = ratings[train_index], ratings[test_index]
        #clf = tree.DecisionTreeClassifier().fit(X_train, y_train)
        #clf = SVC(gamma='scale').fit(X_train, y_train)
        #clf=  neighbors.KNeighborsClassifier(k).fit(X_train,y_train)
        clf=MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(50,80, 20), random_state=1)
        clf.fit(X_train,y_train)
        unique, counts =np.unique(y_test, return_counts=True)
        
        print(str(float(max(counts))/float(sum(counts)))+"*")
        print(clf.score(X_test,y_test))
