import mysql.connector
import csv
from datetime import datetime
import random
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123456",
  database="elo7_datascience2",
  get_warnings=False,
  raise_on_warnings=False
)

def loadUserAndRatting(mydb):
    #DELETE FROM user WHERE iduser>=0; 
    #DELETE FROM ratings WHERE iduser>=0; 
    mycursor = mydb.cursor()
    fp = open('ml-20m/ratings.csv',"r")
    fp.readline()
    sqlCommands=0
    usersHash={}
    randIds={}
    keys=np.zeros(22000000,dtype=np.int32)
    while(len(randIds)<22000000):
        key=int(random.random()*float(((2**31)-100)))    
        if(not(key in randIds)):
            keys[len(randIds)]=key
            randIds[key]=key       
            if(len(randIds)%1000==0):
                print("len(randIds):"+str(len(randIds)))
                sys.stdout.flush()
   
    while True:
        line=fp.readline()
        if(line==""):
            break
        fields=list(csv.reader([line]))[0]
        userId=int(fields[0])
        if(not(userId in usersHash)):
            sql = "INSERT INTO user (iduser)  VALUES ({d0})".format(d0=userId)     
            mycursor.execute(sql)    
            usersHash[userId]=0
        try:
            sql="INSERT INTO ratings (iduser,idmovie,rating,timestamp,idrand)  VALUES ({d0},{d1},{d2},STR_TO_DATE('{d3}','%Y-%m-%d %H:%i:%S'),{d4})".format(d0=userId,d1=fields[1],d2=fields[2],d3=datetime.utcfromtimestamp(int(fields[3])).strftime('%Y-%m-%d %H:%M:%S'),d4=keys[sqlCommands])       
            mycursor.execute(sql)   
        except:#because of daylight saving this happen
            sql="INSERT INTO ratings (iduser,idmovie,rating,timestamp,idrand)  VALUES ({d0},{d1},{d2},STR_TO_DATE('{d3}','%Y-%m-%d %H:%i:%S'),{d4})".format(d0=userId,d1=fields[1],d2=fields[2],d3=datetime.utcfromtimestamp(int(fields[3])+3800).strftime('%Y-%m-%d %H:%M:%S'),d4=keys[sqlCommands])       
            mycursor.execute(sql)   

        sqlCommands=sqlCommands+1
        if((sqlCommands%1000)==0):
            print(sqlCommands)
            mydb.commit()

    fp.close()
    mydb.commit()

def loadMoviesGenresAndRelationMovieGenre(mydb):
    #DELETE FROM relation_movie_genre WHERE idgenre>=0;
    #DELETE FROM movie WHERE idmovie>=0; 
    #DELETE FROM genre WHERE idgenre>=0; 

    mycursor = mydb.cursor()
    fp = open('ml-20m/movies.csv',"r")
    fp.readline()
    categoriesHash={}
    sqlCommands=0
    
    while True:
        line=fp.readline()
        if(line==""):
            break
            
        fields=list(csv.reader([line]))[0]
        fields[1]=fields[1].replace("\xe8\xb2\x9e\xe5\xad\x903D"," carac")
        yearT=fields[1].split("(")
        if(len(yearT)>1):
            year=yearT[len(yearT)-1].split(")")[0]
            try:
                sql = "INSERT INTO movie (idmovie,tittle,year)  VALUES ({d0},\"{d1}\",{d2})".format(d0=fields[0], d1=fields[1].replace("\"",'\\"'),d2=year)
                mycursor.execute(sql)                                
            except:
                sql = "INSERT INTO movie (idmovie,tittle)  VALUES ({d0},\"{d1}\")".format(d0=fields[0], d1=fields[1].replace("\"",'\\"')) 
                mycursor.execute(sql)    
        else:
            sql = "INSERT INTO movie (idmovie,tittle)  VALUES ({d0},\"{d1}\")".format(d0=fields[0], d1=fields[1].replace("\"",'\\"')) 
            mycursor.execute(sql)    
        categories=fields[2].split("|")
        lastCategorie=categories[len(categories)-1]
        if(lastCategorie[len(lastCategorie)-1]=='\r' or lastCategorie[len(lastCategorie)-1]=='\n'):
            lastCategorie=lastCategorie[:-1]
        if(lastCategorie[len(lastCategorie)-1]=='\r' or lastCategorie[len(lastCategorie)-1]=='\n'):
            lastCategorie=lastCategorie[:-1]
        categories[len(categories)-1]=lastCategorie

        for category in categories:
            idCategory=-1
            if(not(category in categoriesHash)):
                categoriesHash[category]=len(categoriesHash)+1
                idCategory=categoriesHash[category]
                sql = "INSERT INTO genre (idgenre,name)  VALUES ({d0},'{d1}')".format(d0=idCategory, d1=category)     
                mycursor.execute(sql)    
            else:
                idCategory=categoriesHash[category]
            
            sql = "INSERT INTO relation_movie_genre (idmovie,idgenre)  VALUES ({d0},'{d1}')".format(d0=fields[0], d1=idCategory)     
            mycursor.execute(sql)    

        sqlCommands=sqlCommands+1
        if((sqlCommands%1000)==0):
            print(sqlCommands)
            mydb.commit()

    fp.close()
    mydb.commit()

def loadtags(mydb):
    mycursor = mydb.cursor()
    fp = open('ml-20m/genome-tags.csv',"r")
    fp.readline()
    sqlCommands=0
    while True:
        line=fp.readline()
        if(line==""):
            break
        fields=list(csv.reader([line]))[0]
        fields[1]=fields[1].replace("'","\\'")
        sql = "INSERT INTO genome_tags (idtag,tag)  VALUES ({d0},'{d1}')".format(d0=fields[0],d1=fields[1])
        mycursor.execute(sql)
        sqlCommands=sqlCommands+1
        if((sqlCommands%1000)==0):
            print(sqlCommands)
            mydb.commit()

    fp.close()
    mydb.commit()

def loadtagsScore(mydb):
    mycursor = mydb.cursor()
    fp = open('ml-20m/genome-scores.csv',"r")
    fp.readline()
    sqlCommands=0
    while True:
        line=fp.readline()
        if(line==""):
            break
        fields=list(csv.reader([line]))[0]    
        sql = "INSERT INTO genome_scores (idmovie,idtag,relevance)  VALUES ({d0},{d1},{d2})".format(d0=fields[0],d1=fields[1],d2=fields[2])        
        mycursor.execute(sql)
        sqlCommands=sqlCommands+1
        if((sqlCommands%1000)==0):
            print(sqlCommands)
            mydb.commit()

    fp.close()
    mydb.commit()

#loadMovies(mydb)
#loadRatting(mydb)
#loadtags(mydb)
#loadMoviesGenresAndRelationMovieGenre(mydb)
#loadUserAndRatting(mydb)
#loadtags(mydb)
l#oadtagsScore(mydb)
