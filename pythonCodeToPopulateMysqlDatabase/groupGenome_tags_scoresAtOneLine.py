import mysql.connector
import csv
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123456",
  database="elo7_datascience",
  get_warnings=False,
  raise_on_warnings=False
)
mydb2 = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123456",
  database="elo7_datascience",
  get_warnings=False,
  raise_on_warnings=False
)
mycursor = mydb.cursor()
mycursor2 = mydb2.cursor()
fp = open('ml-20m/genome-scores.csv',"r")
fp.readline()
previousIdMovie=-1
relevanceArray=""
sqlInserts=0
while True:
    line=fp.readline()
    if(line==""):
        break
    fields=list(csv.reader([line]))[0]  
    idmovie=int(fields[0])
    relevance=float(fields[2])
    if(previousIdMovie==-1):
        previousIdMovie=int(fields[0])
    elif(previousIdMovie!=idmovie):
        sql = "INSERT INTO genome_scores_at_one_line (idmovie,valuesdata) VALUES({d0},'{d1}')".format(d0=previousIdMovie,d1=relevanceArray[1:])
        mycursor2.execute(sql)
        previousIdMovie=idmovie
        relevanceArray=""
        if(sqlInserts%500==0):
            mydb2.commit()
            print(sqlInserts)
        sqlInserts=sqlInserts+1
    relevanceArray=relevanceArray+","+str(relevance)

sql = "INSERT INTO genome_scores_at_one_line (idmovie,valuesdata) VALUES({d0},'{d1}')".format(d0=previousIdMovie,d1=relevanceArray[1:])
mycursor2.execute(sql)
mydb2.commit()


