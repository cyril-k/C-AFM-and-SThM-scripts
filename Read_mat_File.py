# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 14:30:43 2021

@author: cecile.huez
"""

import scipy.io as scio
import numpy as np
from matplotlib import pyplot
from matplotlib import cm

## import data
Data1 = scio.loadmat('C:/Users/kirill.kondratenko/Documents/MATLAB/cluster/SPI-Fc-n2 + 2h sans tri i.txt.mat')
Data = Data1['Data'];

Cluster = Data['Cluster'];  Cluster = Cluster[0][0]
Current = Data['current'];  Current = Current[0][0]
MapCurrent = Data['mapI'];  MapCurrent = MapCurrent[0][0]
coordsUMAP = Data['coordsUMAP'];  coordsUMAP = coordsUMAP[0][0]
Map = Data['map'];  Map = Map[0][0]

Cluster_up = Cluster['up']; Cluster_up = Cluster_up[0][0]
Cluster_down = Cluster['down']; Cluster_down = Cluster_down[0][0]
Cluster_up_all = Cluster['up_all']; Cluster_up_all = Cluster_up_all[0][0]
Cluster_down_all = Cluster['down_all']; Cluster_down_all = Cluster_down_all[0][0]
Cluster_all = Cluster['all']; Cluster_all = Cluster_all[0][0]

Current_up = Current['up']; Current_up = Current_up[0][0]
Current_down = Current['down']; Current_down = Current_down[0][0]

Voltage = Data1['Voltage']
numVoltage = len(Voltage)
 

## get clusters
Cluster_up = np.array(Cluster_up)
maxCluster = np.max(Cluster_up)
Average = np.zeros((numVoltage, maxCluster-1, maxCluster))
Population = np.zeros((maxCluster-1, maxCluster))
Selected_IVs_all = {}

for i in range(0, maxCluster-1):
    for j in range(0, maxCluster):
        Selected_IVs = Current_up[:, Cluster_up[:,i] == j+1]
        Average[:,i,j] = np.mean(Selected_IVs, axis = 1)
        Population[i,j] = sum(Cluster_up[:,i] == j+1) / len(Cluster_up[:,i])
        Selected_IVs_all[i,j] = Selected_IVs 
        
        
       
# plot mean IV per clusters
numY = int(np.floor(np.sqrt(maxCluster-1)))
numX = int(np.ceil(maxCluster/numY))

fig, axs = pyplot.subplots(numY, numX)
for i in range(0, maxCluster-1):
    cmap = cm.get_cmap('viridis', i+2)
    leg = []
    idx_X = int(np.mod(i, numX))
    idx_Y = int(np.floor(i/numX))
    for j in range(0, i+2):
        axs[idx_Y, idx_X].plot(Voltage, Average[:,i,j],color=cmap.colors[j,:] )
        leg.append('%1.1f%%' % (Population[i,j]*100))
    axs[idx_Y, idx_X].legend(leg,prop={"size":7},loc=2)

# plot all IV per clusters
fig, axs = pyplot.subplots(numY, numX)
for i in range(0, maxCluster-1):
    cmap = cm.get_cmap('viridis', i+2)
    leg = []
    idx_X = int(np.mod(i, numX))
    idx_Y = int(np.floor(i/numX))
    for j in range(0, i+2):
        axs[idx_Y, idx_X].plot(Voltage, Selected_IVs_all[i,j],color=cmap.colors[j,:] )
   
