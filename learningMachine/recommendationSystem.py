import random
import sys
import time
import csv
import numpy as np
import mysql.connector

from datetime import datetime
from sklearn import tree
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn.neural_network import MLPClassifier

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


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

    def execute(self,clfFactory,idUsers):
        progress=0
        acuracy=[]
        acuracyMinusProportionForMajorityClass=[]
        errorToApplyPCA=0
#        descriptorsNumber=self.descriptorsNumber
        descriptorsNumber=64
        for iduser in idUsers:
            progress=progress+1
            #print("number of users processed: {d0}|{d1}".format(d0=progress,d1=len(idUsers)))
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
            timeToTrain=[]
            timeToPredict=[]
            for train_index, test_index in kf.split(descriptorsForLearningAlgorithm):
            
                X_train,X_test,  = descriptorsForLearningAlgorithm[train_index], descriptorsForLearningAlgorithm[test_index]
                y_train,y_test  = ratings[train_index], ratings[test_index]                       
                clf=clfFactory()
                t1=time.time()
                clf.fit(X_train,y_train)
                t2=time.time()
                timeToTrain.append(t2-t1)

                #get proportion for majority class in test dataset============
                unique, counts =np.unique(y_test, return_counts=True)
                proportionForMajorityClass=float(max(counts))/float(sum(counts))            
                #end==========================================================
                t1=time.time()
                acuracy.append(clf.score(X_test,y_test))
                t2=time.time()
                timeToPredict.append(t2-t1)
                acuracyMinusProportionForMajorityClass.append(acuracy[len(acuracy)-1]-proportionForMajorityClass)                
        print("") 
        return {"acuracy":acuracy,"acuracyMinusProportionForMajorityClass":acuracyMinusProportionForMajorityClass,"errorToApplyPCA":errorToApplyPCA, "timeToPredict": timeToPredict, "timeToTrain":timeToTrain}

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
                      group by iduser """)
    users=[]
    usersWithMoreThan3000Votes=[]
    usersWithMoreThan2000AndLessThanOrEqualTo3000Votes=[]
    usersWithMoreThan1000AndLessThanOrEqualTo2000Votes=[]
    usersWithMoreThan500AndLessThanOrEqualTo1000Votes=[]
    usersWithMoreThan250AndLessThanOrEqualTo500Votes=[]
    usersWithMoreThan100AndLessThanOrEqualTo250Votes=[]
    usersWithMoreThan50AndLessThanOrEqualTo100Votes=[]
    usersWithLessThan50Votes=[]
    for qtdVotes,iduser in cursor:
        if(qtdVotes>3000):    
            usersWithMoreThan3000Votes.append(iduser)
            
        elif(qtdVotes>2000 and qtdVotes<=3000):
            usersWithMoreThan2000AndLessThanOrEqualTo3000Votes.append(iduser)           
        elif(qtdVotes>1000 and qtdVotes<=2000):
            usersWithMoreThan1000AndLessThanOrEqualTo2000Votes.append(iduser)         
        elif(qtdVotes>500 and qtdVotes<=1000):
            usersWithMoreThan500AndLessThanOrEqualTo1000Votes.append(iduser)            
        elif(qtdVotes>250 and qtdVotes<=500):
            usersWithMoreThan250AndLessThanOrEqualTo500Votes.append(iduser)            
        elif(qtdVotes>100 and qtdVotes<=250):
            usersWithMoreThan100AndLessThanOrEqualTo250Votes.append(iduser)     
        elif(qtdVotes>50 and qtdVotes<=100):
            usersWithMoreThan50AndLessThanOrEqualTo100Votes.append(iduser)
        elif(qtdVotes<50):
            usersWithLessThan50Votes.append(iduser)

    shuffleUser=False
    
    #shiffle vectors with users===================================
    if(shuffleUser):
        usersWithMoreThan3000Votes=shuffleVector(usersWithMoreThan3000Votes)
        usersWithMoreThan2000AndLessThanOrEqualTo3000Votes=shuffleVector(usersWithMoreThan2000AndLessThanOrEqualTo3000Votes)
        usersWithMoreThan1000AndLessThanOrEqualTo2000Votes=shuffleVector(usersWithMoreThan1000AndLessThanOrEqualTo2000Votes)
        usersWithMoreThan500AndLessThanOrEqualTo1000Votes=shuffleVector(usersWithMoreThan500AndLessThanOrEqualTo1000Votes)
        usersWithMoreThan250AndLessThanOrEqualTo500Votes=shuffleVector(usersWithMoreThan250AndLessThanOrEqualTo500Votes)
        usersWithMoreThan100AndLessThanOrEqualTo250Votes=shuffleVector(usersWithMoreThan100AndLessThanOrEqualTo250Votes)
        usersWithMoreThan50AndLessThanOrEqualTo100Votes=shuffleVector(usersWithMoreThan50AndLessThanOrEqualTo100Votes)
        usersWithLessThan50Votes=shuffleVector(usersWithLessThan50Votes)
    #end==========================================================
    knnFactory  = lambda : neighbors.KNeighborsClassifier(11)
    svcFactory  = lambda : SVC(degree=3, gamma='auto', kernel='poly')
    treeFactory = lambda : tree.DecisionTreeClassifier()
    MLPFactory  = lambda : MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(64,128,128, 64), random_state=1)
    
    classifier=Classifier(mydb)
    algorithmsToLearning=[{"name":'KNN',"algorithm":knnFactory},
                          {"name":'SVM',"algorithm":svcFactory},
                          {"name":'Arvore de decisão',"algorithm":treeFactory},
                          {"name":'Redes neurais',"algorithm":MLPFactory}
                          ]

    dataSets=[{"name":"Usuários com mais do que 3000 votos","data": usersWithMoreThan3000Votes},
              {"name":"Usuários com mais do que 2000 votos e igual ou menos que 3000","data": usersWithMoreThan2000AndLessThanOrEqualTo3000Votes},
              {"name":"Usuários com mais do que 1000 votos e igual ou menos que 2000","data":usersWithMoreThan1000AndLessThanOrEqualTo2000Votes},
              {"name":"Usuários com mais do que 500 votos e igual ou menos que 1000","data":usersWithMoreThan500AndLessThanOrEqualTo1000Votes},
              {"name":"Usuários com mais do que 250 votos e igual ou menos que 500","data":usersWithMoreThan250AndLessThanOrEqualTo500Votes},
              {"name":"Usuários com mais do que 100 votos e igual ou menos que 250","data":usersWithMoreThan100AndLessThanOrEqualTo250Votes},
              {"name":"Usuários com mais do que 50 votos e igual ou menos que 100","data":usersWithMoreThan50AndLessThanOrEqualTo100Votes},
              {"name":"Usuários com menos do que 50","data":usersWithLessThan50Votes}]
    for algorithmToLearning in algorithmsToLearning:
        print("==================================================================")
        print("nome do algoritmo:"+algorithmToLearning['name'])

        for dataSet in dataSets:

            acuracyInformation=classifier.execute(algorithmToLearning["algorithm"],dataSet["data"][:20])            
            print(dataSet["name"]+":")
            print("    Média para acurácia:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
            print("    Desvio padrão para acurácia:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
            print("    Média para (acuracia - porcentagem da classe majoritária):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
            print("    Desvio padrão  (acurácia - porcentagem da classe majoritária):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
            print("    Média tempo para treinar  (s):"+str( np.mean(np.array(acuracyInformation["timeToTrain"],dtype=float))))
            print("    Desvio padrão do tempo para treinar (s):"+str( np.std(np.array(acuracyInformation["timeToTrain"],dtype=float))))
            print("    Média tempo para testar modelo  (s):"+str( np.mean(np.array(acuracyInformation["timeToPredict"],dtype=float))))
            print("    Desvio padrão do tempo para testar modelo (s):"+str( np.std(np.array(acuracyInformation["timeToPredict"],dtype=float))))
        print("==================================================================")
    