import mysql.connector
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


sql = """SELECT g1.idgenre,m1.idmovie FROM elo7_datascience.movie m1 
         inner join elo7_datascience.relation_movie_genre mg on m1.idmovie=mg.idmovie
         inner join elo7_datascience.genre g1 on g1.idgenre=mg.idgenre
         ORDER BY m1.idmovie """.replace("\n"," ")        

data=selectInDataBase(mydb,sql)
previousIdMovie=-1
matrix=num
for line in data:
    if(previousIdMovie==-1):
        previousIdMovie=data["idmovie"]
    elif(previousIdMovie!=data["idmovie"]):
        previousIdMovie=data["idmovie"]
    else:
        
