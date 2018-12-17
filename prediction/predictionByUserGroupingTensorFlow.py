import random
import sys
import time
import csv
import numpy as np
import mysql.connector

from datetime import datetime
from sklearn.model_selection import KFold


import tensorflow as tf

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
def applyKmeans(data,num_clusters):
    input_fn=lambda :tf.train.limit_epochs(tf.convert_to_tensor(data, dtype=tf.float32), num_epochs=1)


    kmeans = tf.contrib.factorization.KMeansClustering(num_clusters=num_clusters, use_mini_batch=False)
    num_iterations = 10
    previous_centers = None
    for i in range(num_iterations):
        kmeans.train(input_fn)
        cluster_centers = kmeans.cluster_centers()
        if previous_centers is not None:
            
            print ('delta:'+ str(np.mean(np.sqrt(sum(np.transpose((previous_centers-cluster_centers)**2))))))
        previous_centers = cluster_centers
        
        
    # map the input points to their clusters
    cluster_indices = list(kmeans.predict_cluster_index(input_fn))
    return cluster_indices
        

class Classifier:
    def __init__(self,sqlConnection):
        self.ratingsAtRamAdrressUserIdAndMovieId={}        
        self.relationMovieGenre={}
        self.sqlConnection=sqlConnection    
        fp=open("ml-20m/ratings.csv","r")
        fp.readline()
        i=0
        while True:
            i=i+1
            if((i%500000)==0):
                print(i)
            line=fp.readline()
            if(line==""):
                break
            fields=line.split(",")
            userid=int(fields[0])
            if(not(userid in self.ratingsAtRamAdrressUserIdAndMovieId)):
                self.ratingsAtRamAdrressUserIdAndMovieId[userid]={}
            self.ratingsAtRamAdrressUserIdAndMovieId[userid][int(fields[1])]=float(fields[2])

        fp.close()
        cursor = sqlConnection.cursor()    
        self.users={}    
        cursor.execute("SELECT number_of_votes, idgenre, iduser FROM number_of_votes_for_a_genre_from_a_user;")
    
        for number_of_votes, idgenre, iduser in cursor:
            if(not(iduser in self.users)):
                self.users[iduser]=np.zeros(21)
            self.users[iduser][idgenre-1]=number_of_votes        
    
        keys=list(self.users.keys())
        self.converterIdUserToMatrizLine={}
        self.converterMatrizLineToIdUser=[]
        for i in range(len(keys)):
            self.converterIdUserToMatrizLine[keys[i]]=i
            self.converterMatrizLineToIdUser.append(keys[i])

        self.matrixIdUSerXGenreToDisplayNumberOfVotes=np.zeros((len(keys),21))


        

        for i in range(len(keys)):
            for j in range(len(self.users[keys[i]])):
                self.matrixIdUSerXGenreToDisplayNumberOfVotes[i][j]=self.users[keys[i]][j]

        cursor.execute("SELECT idgenre,idmovie FROM relation_movie_genre;")
        for idgenre, idmovie in cursor:
            if(not(idmovie in self.relationMovieGenre)):
                self.relationMovieGenre[idmovie]=[]

            self.relationMovieGenre[idmovie].append(idgenre)

    def execute(self,idUsers):
        cursor = self.sqlConnection.cursor()
        progress=0
        acuracyVector=[]
        acuracyVectorForMajorityClass=[]
        errorToApplyPCA=0

        timeToTrain=[]
        timeToPredict=[]
        for iduser in idUsers:
            progress=progress+1
            #print("number of users processed: {d0}|{d1}".format(d0=progress,d1=len(idUsers)))
            sys.stdout.flush()            
            
            #sqlToKnowLinesReturned = """SELECT count(*) as nLines FROM  ratings r1                                        
            #                            where  r1.iduser={iduser}  order by r1.idrand """.format(iduser=iduser)        
            #print(sqlToKnowLinesReturned)                                    
            
            #nLinesReturnedBySelect=selectInDataBase(self.sqlConnection, sqlToKnowLinesReturned)[0]["nLines"]

            nLinesReturnedBySelect= len(self.ratingsAtRamAdrressUserIdAndMovieId[iduser])
            #sqlSelectAllmoviesThatAUserVoted => Return all movies that a user voted and the genome metrics
            #                                    this metrics are used by clf to train e predict the rate that
            #                                    a user give to a movie based on  genome metrics.
            #                                    each line returned have the movie rate (rating) and the id for 
            #                                    the movie.
            #sqlSelectAllmoviesThatAUserVoted =   """SELECT r1.idmovie,rating FROM  ratings r1 
            #                                       where  r1.iduser={iduser} """.format(iduser=iduser)

            #cursor.execute (sqlSelectAllmoviesThatAUserVoted)
            idsmovies=np.zeros((nLinesReturnedBySelect),dtype=np.int32)
            ratings=np.zeros(nLinesReturnedBySelect,dtype=np.int32)
            currentLine=0 #current line for data requested from cursor
            keys=list(self.ratingsAtRamAdrressUserIdAndMovieId[iduser].keys())
            for idmovie in keys:        
                idsmovies[currentLine]=idmovie                  
                ratings[currentLine]=float(int(float(self.ratingsAtRamAdrressUserIdAndMovieId[iduser][idmovie])*2))        
                currentLine=currentLine+1   
            
            if(currentLine==0):
                continue
            ratings=ratings[:currentLine]
            idsmovies=idsmovies[:currentLine]
            
            
               
            kf = KFold(n_splits=4,shuffle=True,random_state=3223)
            
            for train_index, test_index in kf.split(idsmovies):
                print("---------------------------------------------------------")            
                X_train,X_test,  = idsmovies[train_index], idsmovies[test_index]
                y_train,y_test  = ratings[train_index], ratings[test_index]                       

                matrixIdUSerXGenreToDisplayNumberOfVotesLocal=np.copy(self.matrixIdUSerXGenreToDisplayNumberOfVotes)
                for idmovieToExcludeFromGenres in  X_test:                    
                    for genreToSubtract in self.relationMovieGenre[idmovieToExcludeFromGenres]:
                        matrixIdUSerXGenreToDisplayNumberOfVotesLocal[self.converterIdUserToMatrizLine[iduser]][genreToSubtract-1]=matrixIdUSerXGenreToDisplayNumberOfVotesLocal[self.converterIdUserToMatrizLine[iduser]][genreToSubtract-1]-1
                t1=time.time()                
                clusterThatBelongEachUser=applyKmeans(matrixIdUSerXGenreToDisplayNumberOfVotesLocal,64)         
                t2=time.time()
                timeToTrain.append(t2-t1)
                usersAtSameClusterThatTheUserPointedByiduser=[]
                
                clusterForiduser=clusterThatBelongEachUser[self.converterIdUserToMatrizLine[iduser]]

                lineForMatrixIdUSerXGenreToDisplayNumberOfVotesLocal=0
                for clusterToTheUsers in clusterThatBelongEachUser: 
                    idUserForOthersUsers=self.converterMatrizLineToIdUser[lineForMatrixIdUSerXGenreToDisplayNumberOfVotesLocal]
                    if(idUserForOthersUsers!=iduser and clusterToTheUsers==clusterForiduser ):
                        usersAtSameClusterThatTheUserPointedByiduser.append(idUserForOthersUsers)                    
                    lineForMatrixIdUSerXGenreToDisplayNumberOfVotesLocal=lineForMatrixIdUSerXGenreToDisplayNumberOfVotesLocal+1
                

                 

                #get acuracy to classifier make from majority class===========
                majorityClass =float(np.bincount(np.array(np.array(y_train),dtype=np.int32)).argmax())
                acuracyForMajorityClass=0.0
                for i in range(len(y_test)):
                    if(abs(y_test[i]-majorityClass)<1.0):
                        acuracyForMajorityClass=acuracyForMajorityClass+1.0
                acuracyForMajorityClass=acuracyForMajorityClass/float(len(y_test))
                acuracyVectorForMajorityClass.append(acuracyForMajorityClass)
                #end==========================================================
                t1=time.time()
                #get acuracy from model=======================================
                acuracy=0.0  
                ratingsPredicted=[] 
                print("***********************************************************")            
                for idmovie in X_test:
                    vectorToCalcAvgForRatingOfIdMovie=[]
                    for user in usersAtSameClusterThatTheUserPointedByiduser:                                                          
                        if(idmovie in self.ratingsAtRamAdrressUserIdAndMovieId[user]):
                            vectorToCalcAvgForRatingOfIdMovie.append(float(int(self.ratingsAtRamAdrressUserIdAndMovieId[user][idmovie]*2)))
                    if(len(vectorToCalcAvgForRatingOfIdMovie)==0):
                        ratingsPredicted.append(-1000)
                    else:
                        ratingsPredicted.append(np.mean(np.array(vectorToCalcAvgForRatingOfIdMovie,dtype=float)))

                for i in range(len(X_test)):
                    if(abs(ratingsPredicted[i]-y_test[i])<1.0):
                        acuracy=acuracy+1.0
                acuracyVector.append(acuracy/float(len(X_test)))
                #end==========================================================
                t2=time.time()
                timeToPredict.append(t2-t1)
                
        print("") 
        return {"acuracyForModel":acuracyVector,"acuracyForMajorityClass":acuracyVectorForMajorityClass, "timeToPredict": timeToPredict, "timeToTrain":timeToTrain}





if __name__ == "__main__":
    random.seed(322442)
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="123456",
        database="elo7_datascience",
        get_warnings=False,
        raise_on_warnings=False
    )
    cursor = mydb.cursor()
    cursor.execute("""SELECT count(*) as qtdVotes ,iduser FROM ratings 
                      group by iduser limit 300 """)
    users=[]

    for qtdVotes,iduser in cursor:
     
        users.append(iduser)       

    shuffleUser=False
    
    #shiffle vectors with users===================================
    if(shuffleUser):
        users=shuffleVector(users)     
    #end==========================================================
  
    #algorithmsToLearning=[{"name":'Gaussian',"algorithm":GaussianNBFactory}]

  
    print("==================================================================")

    classifier=Classifier(mydb)
    acuracyInformation=classifier.execute(users[:1])            
    print("    Média para acurácia:"+ str( np.mean(np.array(acuracyInformation["acuracyForModel"],dtype=float))))
    print("    Desvio padrão para acurácia:"+ str( np.std(np.array(acuracyInformation["acuracyForModel"],dtype=float))))
    print("    Média para acurácia usando um modelo baseado classe majoritária:"+ str( np.mean(np.array(acuracyInformation["acuracyForMajorityClass"],dtype=float))))
    print("    Desvio padrão para acurácia usando um modelo baseado classe majoritária:"+str( np.std(np.array(acuracyInformation["acuracyForMajorityClass"],dtype=float))))
    print("    Média tempo para treinar  (s):"+str( np.mean(np.array(acuracyInformation["timeToTrain"],dtype=float))))
    print("    Desvio padrão do tempo para treinar (s):"+str( np.std(np.array(acuracyInformation["timeToTrain"],dtype=float))))
    print("    Média tempo para testar modelo  (s):"+str( np.mean(np.array(acuracyInformation["timeToPredict"],dtype=float))))
    print("    Desvio padrão do tempo para testar modelo (s):"+str( np.std(np.array(acuracyInformation["timeToPredict"],dtype=float))))
    print("==================================================================")
    