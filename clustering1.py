# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 15:20:12 2022

@author: kirill.kondratenko
"""

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
#import torch 

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import umap

data_folder = Path("C:/Users/kirill.kondratenko/Documents/MATLAB/cluster")
file_to_open = data_folder / "SPI-FC-hysteresis.txt"

data = pd.read_csv(file_to_open, sep="\t", header = None)
#print(data.head())
voltage = data.iloc[:, 0].values
current_up = data.iloc[:, 1::4].values
current_down = data.iloc[:, 3::4].values

numVoltage = len(voltage)

N_spectra = current_up.shape[1]

numX = 10 #arbitrary? for mapping 
numY = N_spectra//numX #arbitrary? for mapping 

data_idx_up = np.arange(1, N_spectra+1)
data_idx_up = np.reshape(data_idx_up, (numY, numX))

data_mapI_up = np.reshape(current_up, (numVoltage, numY, numX))
data_mapI_up = np.transpose(data_mapI_up, (1, 2, 0))

data_mapI_down = np.reshape(current_down, (numVoltage, numY, numX))
data_mapI_down = np.transpose(data_mapI_down, (1, 2, 0))

BIAS = [-2, -1, 1, 2]

for bias_i in BIAS:
    Bias_idx = np.where(min(abs(bias_i - voltage)) == abs(bias_i - voltage))[0]
    
    #Bias_idx=511

    fig, ax = plt.subplots(1, 2)
    
    ax[0].imshow(data_mapI_up[:,:,Bias_idx]) #,extent=[0, 1, 0, 1]
    ax[0].set_title('Ramp up')
    ax[1].imshow(data_mapI_down[:,:,Bias_idx])
    ax[1].set_title('Ramp down')

# fig = plt.figure() # create figure

# ax0 = fig.add_subplot(1, 2, 1) # add subplot 1 (1 row, 2 columns, first plot)
# ax1 = fig.add_subplot(1, 2, 2) # add subplot 2 (1 row, 2 columns, second plot). See tip below**

# voltage_data = voltage.values
# current_up_data = current_up.values
# current_down_data = current_down.values

#sns.lineplot(data=current_up.iloc[:, ::10]) # add to subplot 1

# fig, axs = plt.subplots(2, 1)
# axs[0, 0].plot(x=voltage, y=current_up[:, ::10])
# axs[0, 0].set_title('Ramp up')
# axs[0, 1].plot(x=voltage, y=current_down[:, ::10])
# axs[0, 1].set_title('Ramp down')

#current_up_plot = pd.concat([voltage, current_up.iloc[:, ::10]], axis=1)
#a = current_up_plot.iloc[:, 1::]

#--------------------------------------------
# Reduce dimensionality

reducer = umap.UMAP(n_epochs = 1000, metric='cosine', n_neighbors=20, n_components=3)
scaled_current_up_data = StandardScaler().fit_transform(current_up)

embedding = reducer.fit_transform(scaled_current_up_data)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

plt.scatter(
    embedding[:, 0],
    embedding[:, 1],
    embedding[:, 2]
    )
plt.gca().set_aspect('auto', 'datalim')
plt.title('UMAP projection', fontsize=24)
