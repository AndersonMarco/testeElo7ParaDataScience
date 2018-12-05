import mysql.connector
import random
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
sql = "Select component,movieid,value_component from genome_scores_pca  order by movieid,component "
mycursor.execute (sql)
previousMovieid=-1
pcaComponents=""
sqlInserts=0
for (component,movieid, value_component) in mycursor:
    if(previousMovieid==-1):
        previousMovieid=movieid
    elif(previousMovieid!=movieid):
        while True:
            sql = "INSERT INTO genome_scores_pca_at_one (movieid,valuesdata) VALUES({d0},'{d1}')".format(d0=previousMovieid,d1=pcaComponents[1:])
            try:
                mycursor2.execute(sql)
                break
            except:
                pass
        previousMovieid=movieid
        pcaComponents=""
        if(sqlInserts%500==0):
            mydb2.commit()
            print(sqlInserts)
        sqlInserts=sqlInserts+1
    pcaComponents=pcaComponents+","+str(value_component)


sql = "INSERT INTO genome_scores_pca_at_one_line (movieid,valuesdata) VALUES({d0},'{d1}')".format(d0=previousMovieid,d1=pcaComponents[1:])
mycursor2.execute(sql)

mydb2.commit()


