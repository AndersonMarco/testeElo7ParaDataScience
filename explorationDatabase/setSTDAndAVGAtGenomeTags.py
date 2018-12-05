import mysql.connector
import csv
import numpy as np
from datetime import datetime
import numpy as np
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123456",
  database="elo7_datascience2",
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


ntags=1128
mycursor = mydb.cursor()

for i in range(ntags):
    avgAndStdForTag=selectInDataBase(mydb,"SELECT avg(relevance) as avg,std(relevance) as std from genome_scores where idtag="+str(i+1))[0]
    sql = "UPDATE genome_tags SET avg={d0}, std={d1} WHERE idtag={d2}".format(d0=avgAndStdForTag["avg"],d1=avgAndStdForTag["std"],d2=(i+1))
    mycursor.execute(sql)
    print(i)

mydb.commit()    