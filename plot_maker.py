import json
import numpy as np
from matplotlib import pyplot as plt
import math


def get_N_RA_DEC():
    with open("joined_area/joined_area.json", "r") as f:
        areas = json.load(f)
    
    N=int(math.sqrt(len(areas)*2))
    N_RA=N
    N_DEC=math.floor(N/2)
    
    sorted_keys=sorted(areas, key=areas.get)
    file1 = open("areas_order.txt","a")
    for key in sorted_keys:
        file1.write("\n"+key+": "+str(areas[key]))
    file1.close()
    
    return N, N_RA, N_DEC
    
    
def get_area(location):
    with open(location, "r") as f:
        areas = json.load(f)
    
    N=int(math.sqrt(len(areas)*2))
    N_RA=N
    N_DEC=math.floor(N/2)
    array_areas=np.full((N_DEC,N_RA),0.0)

    for key in areas.keys():
        co_ords=list(key.split('_'))
        
        RA_j=int(float(co_ords[0]))
        DEC_i=int(float(co_ords[1]))
        
        print(RA_j, DEC_i)
    
        array_areas[DEC_i][RA_j]=areas[key]

    return array_areas


def heat_plotter(array, N_RA, N_DEC, name):
    RA=[str(2*np.pi*(i/8)-np.pi)[:4] for i in range(8)]
    RA_i=[N_RA*i/8 for i in range(8)]
    DEC=[str(np.pi*(j/8)-np.pi/2)[:4] for j in range(8)]
    DEC_j=[ N_DEC*j/8 for j in range(8)]

    harvest = array

    plt.imshow(harvest, origin='lower')

    plt.xlabel('ra',fontsize=15)
    plt.xticks(RA_i, RA)
    plt.xticks(fontsize=10)

    plt.ylabel('dec', fontsize=15)
    plt.yticks(DEC_j,DEC)
    plt.yticks(fontsize=10)

    plt.title(name, fontsize=20)
    plt.tight_layout()

    cbar=plt.colorbar();
    cbar.ax.tick_params(labelsize=10) 

    plt.savefig("plots/{}.png".format(name))
    plt.close()
    
def histo_plotter(array1):
    plt.hist(array1.flatten(), alpha=0.5, label="areas")
    plt.legend(loc='upper right')
    plt.savefig("plots/{}.png".format("histogram"))
    plt.close()
    
if __name__=="__main__":
    N, N_RA, N_DEC = get_N_RA_DEC()

    areas=get_area("joined_area/joined_area.json")

    heat_plotter(areas, N_RA, N_DEC, 'areas_(sqr_degrees)')

    histo_plotter(areas)

    
