import numpy as np
import csv
import matplotlib.pyplot as plt
import mysql.connector
mydb = mysql.connector.connect(
  host="192.168.1.100",
  user="root",
  passwd="123456",
  database="elo7_datascience",
  get_warnings=False,
  raise_on_warnings=False
)
descritorNumber=10
x=[[],[],[],[],[],[],[],[],[],[]]
y=[[],[],[],[],[],[],[],[],[],[]]
sql = "SELECT valuesdata,rating FROM elo7_datascience.genome_scores_pca_at_one_line  g1 inner join ratings r1 on g1.idmovie= r1.idmovie inner join relation_movie_genre rg  on rg.idmovie=g1.idmovie where rg.idgenre=9  order by idrand limit 50000"
cursor = mydb.cursor()

cursor.execute (sql)
line=0

for (valuesdata, rating) in cursor:
    
    descriptorsAtString=list(csv.reader([valuesdata]))[0]
    if(rating<4.0):
        x[0].append(float(descriptorsAtString[0]))
        y[0].append(float(descriptorsAtString[1]))
    else:
        x[1].append(float(descriptorsAtString[0]))
        y[1].append(float(descriptorsAtString[1]))
    #x[int(float(rating)*2)-1].append(float(descriptorsAtString[0]))
    #y[int(float(rating)*2)-1].append(float(descriptorsAtString[1]))
    
    if((line%1000)==0):
        print(line)
    line=line+1
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, axisbg="1.0")    
colors=["red","green","blue"]
#x=[[2.2,5.0,6.0],[2.2,5.0,6.0]]
#y=[[1.2,5.0,6.0],[2.2,6.0,7.0]]
coi=0
volume=[70.0,90.0]
alpha=[1.0,0.1]
for i in [0,1]:    
    ax.scatter(x[i], y[i],c=colors[coi],label=i,edgecolors='none', s=volume[coi], alpha=alpha[coi])
    coi=coi+1

plt.title('Matplot scatter plot')
plt.legend(loc=2)
plt.show()