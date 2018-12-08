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
import sys
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


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
        cursor.execute("SELECT idmovie,valuesdata FROM elo7_datascience.genome_scores_at_one_line");
        for idmovie,valuesdata in cursor:
            descriptors=np.zeros(self.descriptorsNumber,dtype=np.float)
            descriptorsAtString=list(csv.reader([valuesdata]))[0]
            for j in range(self.descriptorsNumber):
                descriptors[j]=float(descriptorsAtString[j])

            self.descriptorsForAllMovies[idmovie]=descriptors

    def execute(self,clfFactory,idUsers):
        progress=0
        acuracy=[]
        acuracyMinusProportionForMajorityClass=[]
        for iduser in idUsers:
            progress=progress+1
            sys.stdout.write("\rnumber of users processed: {d0}|{d1}".format(d0=progress,d1=len(idUsers)))
            sys.stdout.flush()            
            
            sqlToKnowLinesReturned = """SELECT count(*) as nLines FROM  ratings r1 
                                        inner join relation_movie_genre rg  on rg.idmovie=r1.idmovie
                                        where  r1.iduser={iduser}  order by r1.idrand """.format(iduser=iduser)        
            #print(sqlToKnowLinesReturned)                                    
            nLinesReturnedBySelect=selectInDataBase(self.sqlConnection, sqlToKnowLinesReturned)[0]["nLines"]

            #sqlSelectAllmoviesThatAUserVoted => Return all movies that a user voted and the genome metrics
            #                                    this metrics are used by clf to train e predict the rate that
            #                                    a user give to a movie based on  genome metrics.
            #                                    each line returned have the movie rate (rating) and the id for 
            #                                    the movie.
            sqlSelectAllmoviesThatAUserVoted =   """SELECT r1.idmovie,rating FROM  ratings r1 
                                                    inner join relation_movie_genre rg  on rg.idmovie=r1.idmovie
                                                    where  r1.iduser={iduser}  order by r1.idrand """.format(iduser=iduser)

            cursor.execute (sqlSelectAllmoviesThatAUserVoted)
            descriptors=np.zeros((nLinesReturnedBySelect,self.descriptorsNumber),dtype=np.float)
            ratings=np.zeros(nLinesReturnedBySelect,dtype=np.int32)
            currentLine=0 #current line for data requested from cursor
            for (idmovie, rating) in cursor:
                if(idmovie in self.descriptorsForAllMovies):
                    descriptors[currentLine]=np.copy(self.descriptorsForAllMovies[idmovie])
                    ratings[currentLine]=(int(float(rating)*2))        
                    currentLine=currentLine+1   

            ratings=ratings[:currentLine]
            descriptors=descriptors[:currentLine]
            X=np.copy(descriptors)
            scaler = StandardScaler()
            scaler.fit(X)
            X=scaler.transform(X)    
            pca = PCA()
            try:
                componentsForObjects = pca.fit_transform(X)
                componentsForObjects=componentsForObjects[:30]
                descriptorsForLearningAlgorithm=np.copy(componentsForObjects)[:30]
            except:
                descriptorsForLearningAlgorithm= descriptors
            kf = KFold(n_splits=4,shuffle=True,random_state=3223)   
            for train_index, test_index in kf.split(descriptorsForLearningAlgorithm):
            
                X_train,X_test,  = descriptorsForLearningAlgorithm[train_index], descriptorsForLearningAlgorithm[test_index]
                y_train,y_test  = ratings[train_index], ratings[test_index]                       
                clf=clfFactory()
                clf.fit(X_train,y_train)

                #get proportion for majority class in test dataset============
                unique, counts =np.unique(y_test, return_counts=True)
                proportionForMajorityClass=float(max(counts))/float(sum(counts))            
                #end==========================================================

                acuracy.append(clf.score(X_test,y_test))
                acuracyMinusProportionForMajorityClass.append(acuracy[len(acuracy)-1]-proportionForMajorityClass) 

        print("") 
        return {"acuracy":acuracy,"acuracyMinusProportionForMajorityClass":acuracyMinusProportionForMajorityClass}

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
    cursor.execute("""SELECT count(*) as qtdVotes ,iduser FROM ratings 
                      group by iduser 
                      order by qtdVotes desc """)
    users=[]
    for qtdVotes,iduser in cursor:
        if(qtdVotes>60 and  qtdVotes<80):
            users.append(iduser)
    shuffleUser=True
    
    #  users================================================   
    if(shuffleUser):
        for i in range(len(users)*4):
            position1ForUsersList=random.randint(0,len(users)-1)
            position2ForUsersList=random.randint(0,len(users)-1)
            userTemp=users[position1ForUsersList]
            users[position1ForUsersList]=users[position2ForUsersList]
            users[position2ForUsersList]=userTemp
    #end==========================================================
    knnFactory  = lambda : neighbors.KNeighborsClassifier(11)
#    svcFactory  = lambda : SVC(gamma='scale')
    svcFactory  = lambda : SVC(degree=3, gamma='auto', kernel='poly')
    treeFactory = lambda : tree.DecisionTreeClassifier(max_leaf_nodes=14)
    MLPFactory  = lambda : MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(50,80, 20), random_state=1)
    classifier=Classifier(mydb)
    acuracyInformation=classifier.execute(treeFactory,users[:140])


    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))