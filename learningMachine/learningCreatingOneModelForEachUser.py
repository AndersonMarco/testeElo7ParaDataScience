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

def shuffleVector(vector):
    for i in range(len(vector)*4):
        position1ForUsersList=random.randint(0,len(vector)-1)
        position2ForUsersList=random.randint(0,len(vector)-1)
        userTemp=vector[position1ForUsersList]
        vector[position1ForUsersList]=vector[position2ForUsersList]
        vector[position2ForUsersList]=userTemp
    return vector
        
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
        return {"acuracy":acuracy,"acuracyMinusProportionForMajorityClass":acuracyMinusProportionForMajorityClass,"errorToApplyPCA":errorToApplyPCA}

if __name__ == "__main__":
    mydb = mysql.connector.connect(
        host="192.168.1.100",
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
    
    #  users================================================   
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
#    svcFactory  = lambda : SVC(gamma='scale')
    svcFactory  = lambda : SVC(degree=3, gamma='auto', kernel='poly')
    treeFactory = lambda : tree.DecisionTreeClassifier()
    MLPFactory  = lambda : MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(64,128, 64), random_state=1)
    classifier=Classifier(mydb)
    
    acuracyInformation=classifier.execute(treeFactory,usersWithMoreThan3000Votes[:20])
    print("usersWithMoreThan3000Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))
    
    print("==================================================================")
    acuracyInformation=classifier.execute(treeFactory,usersWithMoreThan2000AndLessThanOrEqualTo3000Votes[:20])
    print("usersWithMoreThan2000AndLessThanOrEqualTo3000Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))
    
    print("==================================================================")    
    acuracyInformation=classifier.execute(treeFactory,usersWithMoreThan1000AndLessThanOrEqualTo2000Votes[:20])
    print("usersWithMoreThan1000AndLessThanOrEqualTo2000Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))
    
    print("==================================================================")    
    acuracyInformation=classifier.execute(treeFactory,usersWithMoreThan500AndLessThanOrEqualTo1000Votes[:20])
    print("usersWithMoreThan500AndLessThanOrEqualTo1000Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))
    
    
    print("==================================================================")    
    acuracyInformation=classifier.execute(treeFactory,usersWithMoreThan250AndLessThanOrEqualTo500Votes[:20])
    print("usersWithMoreThan250AndLessThanOrEqualTo500Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))
    
    
    print("==================================================================")    
    acuracyInformation=classifier.execute(treeFactory,usersWithMoreThan100AndLessThanOrEqualTo250Votes[:20])
    print("usersWithMoreThan100AndLessThanOrEqualTo250Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))

    print("==================================================================")
    acuracyInformation=classifier.execute(treeFactory,usersWithMoreThan50AndLessThanOrEqualTo100Votes[:20])
    print("usersWithMoreThan50AndLessThanOrEqualTo100Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))

    
    print("==================================================================")
    acuracyInformation=classifier.execute(treeFactory,usersWithLessThan50Votes[:20])
    print("usersWithLessThan50Votes")
    print("Average for acuracy:"+ str( np.mean(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("STD for acuracy:"+ str( np.std(np.array(acuracyInformation["acuracy"],dtype=float))))
    print("Average for (acuracy - proportion for majority class):"+ str( np.mean(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("STD for (acuracy - proportion for majority class):"+str( np.std(np.array(acuracyInformation["acuracyMinusProportionForMajorityClass"],dtype=float))))
    print("errorToApplyPCA:"+str(acuracyInformation["errorToApplyPCA"]))
