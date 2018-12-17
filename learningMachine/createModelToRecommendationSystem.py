import random
import sys
import time
import csv
import pickle
import codecs
import numpy as np
import mysql.connector

from datetime import datetime
from sklearn import tree
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn.neural_network import MLPClassifier



def shuffleVector(vector):
    vectorT=np.copy(vector)
    for i in range(len(vectorT)*4):
        position1ForUsersList=random.randint(0,len(vectorT)-1)
        position2ForUsersList=random.randint(0,len(vectorT)-1)
        userTemp=vectorT[position1ForUsersList]
        vectorT[position1ForUsersList]=vectorT[position2ForUsersList]
        vectorT[position2ForUsersList]=userTemp
    return vectorT
        
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

class Classifier:
    def __init__(self,sqlConnection):
        self.sqlConnection=sqlConnection
        self.descriptorsNumber= selectInDataBase(sqlConnection, "SELECT count(*) as descriptorsNumber FROM elo7_datascience.genome_tags;" )[0]["descriptorsNumber"]
        cursor = sqlConnection.cursor()
        self.descriptorsForAllMovies={}
        cursor.execute("SELECT idmovie,valuesdata FROM elo7_datascience.genome_scores_pca_at_one_line");
        for idmovie,valuesdata in cursor:
            descriptors=np.zeros(self.descriptorsNumber,dtype=np.float)
            descriptorsAtString=list(csv.reader([valuesdata]))[0]
            for j in range(self.descriptorsNumber):
                descriptors[j]=float(descriptorsAtString[j])

            self.descriptorsForAllMovies[idmovie]=descriptors

    def createClassifierForUsers(self,clfFactory,idUsers):
        cursor = self.sqlConnection.cursor()
        progress=0        
        #descriptorsNumber=self.descriptorsNumber
        descriptorsNumber=64
        for iduser in idUsers:
            progress=progress+1
            print("number of users processed: {d0}|{d1}".format(d0=progress,d1=len(idUsers)))
            sys.stdout.flush()            
            
            sqlToKnowLinesReturned = """SELECT count(*) as nLines FROM  ratings r1                                         
                                        where  r1.iduser={iduser}  """.format(iduser=iduser)        
            #print(sqlToKnowLinesReturned)                                    
            nLinesReturnedBySelect=selectInDataBase(self.sqlConnection, sqlToKnowLinesReturned)[0]["nLines"]

            #sqlSelectAllmoviesThatAUserVoted => Return all movies that a user voted and the genome metrics
            #                                    this metrics are used by clf to train e predict the rate that
            #                                    a user give to a movie based on  genome metrics.
            #                                    each line returned have the movie rate (rating) and the id for 
            #                                    the movie.
            sqlSelectAllmoviesThatAUserVoted =   """SELECT r1.idmovie,rating FROM  ratings r1                                                    
                                                    where  r1.iduser={iduser} """.format(iduser=iduser)

            cursor.execute (sqlSelectAllmoviesThatAUserVoted)
            descriptors=np.zeros((nLinesReturnedBySelect,descriptorsNumber),dtype=np.float)
            ratings=np.zeros(nLinesReturnedBySelect,dtype=np.int32)
            currentLine=0 #current line for data requested from cursor
            for (idmovie, rating) in cursor:
                if(idmovie in self.descriptorsForAllMovies):
                    descriptors[currentLine]=np.copy(self.descriptorsForAllMovies[idmovie])[:descriptorsNumber]
                    ratings[currentLine]=(int(float(rating)*2))        
                    currentLine=currentLine+1   
            
            if(currentLine==0):
                continue
            ratings=ratings[:currentLine]
            descriptors=descriptors[:currentLine]
            
            descriptorsForLearningAlgorithm= descriptors
               
            kf = KFold(n_splits=4,shuffle=True,random_state=3223)
     
            bestModel=None
            bestAcurracy=-1
            for train_index, test_index in kf.split(descriptorsForLearningAlgorithm):
            
                X_train,X_test,  = descriptorsForLearningAlgorithm[train_index], descriptorsForLearningAlgorithm[test_index]
                y_train,y_test  = ratings[train_index], ratings[test_index]                       
                clf=clfFactory()
                
                clf.fit(X_train,y_train)
                acurracy=clf.score(X_test,y_test)
                if(acurracy>bestAcurracy):
                    bestAcurracy=acurracy
                    bestModel=clf

            
            pickled = codecs.encode(pickle.dumps(bestModel), "base64").decode()
            print(len(pickled))
            

                

                
        
        

if __name__ == "__main__":
    random.seed(322442)
    mydb = mysql.connector.connect(
        host="localhost,
        user="root",
        passwd="123456",
        database="elo7_datascience",
        get_warnings=False,
        raise_on_warnings=False
    )
    
    knnFactory  = lambda : neighbors.KNeighborsClassifier(11)
    svcFactory  = lambda : SVC(degree=3, gamma='auto', kernel='poly')
    treeFactory = lambda : tree.DecisionTreeClassifier()
    MLPFactory  = lambda : MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(64,128,128, 64), random_state=1)
    
    classifier=Classifier(mydb)
    acuracyInformation=classifier.createClassifierForUsers(treeFactory,[1,2,3])            
    