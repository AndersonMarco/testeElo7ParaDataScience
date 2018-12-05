import matplotlib
import matplotlib.pyplot as plt
import csv
import numpy as np
import sys
def plotMatrix(H,tittle):    
    fig = plt.figure(figsize=(6, 3.2))

    ax = fig.add_subplot(111)
    ax.set_title(tittle)
    plt.imshow(H,cmap='gray')
    ax.set_aspect('equal')

    cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    plt.show()

fp = open(sys.argv[1],"r")

lines=fp.readlines()
mat=np.zeros((len(lines),len(lines)))
i=0
for line in lines:
    elements=line.split(",")
    j=0
    for e in elements:
        try:
            mat[i][j]=float(e)
            j=j+1
        except:
            pass

    i=i+1
for i in range(len(lines)):
    sumLine=sum(mat[i])
    if(sumLine!=0.0):
        mat[i]=mat[i]/sumLine

mat=mat*100
plotMatrix(mat,"")

    
