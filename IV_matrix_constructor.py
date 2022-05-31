# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 19:35:43 2021

@author: kirill.kondratenko
"""

import numpy as np
from matplotlib.image import NonUniformImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from IPython.core.display import display

from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

from Icon_get_raw_IV import grab_binary_data_Bruker
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os

# def fetchfile():
#     data_folder = Path("C:/Users/kirill.kondratenko/Desktop")
#     file_to_open = data_folder / "mos2-plasma-e3.0_01397.spm"
#     # root = tk.Tk()
#     # root.withdraw()  #use to hide tkinter window
#     # file_to_open = filedialog.askopenfilename()
#     return file_to_open

#searchstring=compile_searchstring()
#file_to_open = fetchfile()

def fetch_dir():
    """ Returns  directory ID through tkinter UI """
    # data_folder = Path("C:/Users/kirill.kondratenko/Desktop")  
    data_folder = Path("C:/Users/kirill.kondratenko/Documents/experimental_data/data_AFM_air/Avril")   #Mars/22-03-24
    # file_to_open = data_folder / "mos2-plasma-e3.0_01397.spm"
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    root.withdraw()  #use to hide tkinter window
    # file_to_open = filedialog.askopenfilename()
    dir_to_open =  filedialog.askdirectory(parent=root, initialdir=data_folder, title='Select data directory') 
    return dir_to_open


dir_to_open = fetch_dir()
#a1=list(Path(dir_to_open).iterdir())
file_list = sorted(Path(dir_to_open).iterdir(), key=os.path.getmtime) #sort files by last modified time (upward)
ramps_X=[]
ramps_Y_extend=[]
ramps_Y_retract=[]
ramps_all=[]
remove_vertical_offset=True # False  remove vertical ofset at zero
for i,file in enumerate(file_list):
    ramps=grab_binary_data_Bruker(file)
    ramps_X.append(ramps[:,0])
    #ramps_all.append(ramps[:,0])
    if remove_vertical_offset:
        ramps_Y_extend.append((ramps[:,1]-ramps[255,1])*1e-9) #offset_subtract
        ramps_Y_retract.append((ramps[:,2]-ramps[255,2])*1e-9)  #offset_subtract
    else:
        ramps_Y_extend.append((ramps[:,1])*1e-9)
        ramps_Y_retract.append((ramps[:,2])*1e-9)
        
    ramps_all.append(ramps_X[i])
    ramps_all.append(ramps_Y_extend[i])
    ramps_all.append(ramps_X[i])
    ramps_all.append(ramps_Y_retract[i])

ramps_X=np.array(ramps_X).T
ramps_Y_extend=np.array(ramps_Y_extend).T
ramps_Y_retract=np.array(ramps_Y_retract).T
ramps_all=np.array(ramps_all).T
# data_folder = Path("C:/Users/kirill.kondratenko/Desktop")
# file_to_open = data_folder / "mos2-plasma-e3.0_01397.spm"

mean_retract=np.mean(ramps_Y_retract, axis=1)
mean_extend=np.mean(ramps_Y_extend, axis=1)

rampsX1=ramps_X.T.flatten()
ramps_Y_extend_abs=np.abs(ramps_Y_extend.T.flatten()) #np.log10()
ramps_Y_extend_log10 = np.where(ramps_Y_extend_abs > 1.0e-14, np.log10(np.where(ramps_Y_extend_abs > 1.0e-14, ramps_Y_extend_abs, 1.0e-14)), -12.5) #replace 0 by 1e-10 and take log10
ramps_Y_retract_abs=np.abs(ramps_Y_retract.T.flatten())
ramps_Y_retract_log10 = np.where(ramps_Y_retract_abs > 1.0e-14, np.log10(np.where(ramps_Y_retract_abs > 1.0e-14, ramps_Y_retract_abs, 1.0e-14)), -12.5) #replace 0 by 1e-10 and take log10
rampsX1_both=np.concatenate((rampsX1, rampsX1))
rams_Y_both_log10=np.concatenate((ramps_Y_extend_log10, ramps_Y_retract_log10))
#np.histogram2d(rampsX1, ramps_Y_extend1, bins=100)
#H, xedges, yedges=np.histogram2d(rampsX1, ramps_Y_extend_log10, bins=100) #2D histo for extend data
#H, xedges, yedges=np.histogram2d(rampsX1, ramps_Y_retract_log10, bins=100) #2D histo for retract data
H, xedges, yedges=np.histogram2d(rampsX1_both, rams_Y_both_log10, bins=100) #2D histo for both ways data



xcenters = (xedges[:-1] + xedges[1:]) / 2
ycenters = (yedges[:-1] + yedges[1:]) / 2
# plt.plot(ramps_X[:,0], ramps_Y_extend[:,0], color='black')
# plt.plot(ramps_X[:,0], ramps_Y_retract[:,0], color='red')
# fig = plt.figure(figsize=(7, 3))
# ax = fig.add_subplot(133, title='NonUniformImage: interpolated',
#         aspect='equal', xlim=xedges[[0, -1]], ylim=yedges[[0, -1]])
# im = NonUniformImage(ax, interpolation='bilinear')
xcenters = (xedges[:-1] + xedges[1:]) / 2
ycenters = (yedges[:-1] + yedges[1:]) / 2
# im.set_data(xcenters, ycenters, H)
# ax.images.append(im)
# plt.show()
#heatmap, xedges, yedges = np.histogram2d(x, y, bins=50)
#extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

#plt.imshow(H.T,origin='lower')
#plt.imshow(heatmap,origin='lower', extent=extent)

#plt.title("How to plot a 2d histogram with matplotlib ?")

#plt.savefig("histogram_2d_07.png", bbox_inches='tight')

#plt.close()
X, Y = np.meshgrid(xedges, yedges)
# fig3, ax3 = plt.subplots()
# ax3.pcolormesh(X, Y, H.T)

	
# fig = Figure(figsize=(12,9))
# FigureCanvas(fig)
# axs = fig.add_subplot(111)
# levels = MaxNLocator(nbins=50).tick_values(H.min(), (H.max())*0.75)
# histo = axs.contourf(xcenters, ycenters, H.T ,cmap='turbo', levels=levels)
# #histo = axs.pcolormesh(X, Y, H.T ,cmap='hot', vmin=0, vmax=400)
# fig.colorbar(histo)

# axs.set(title='2D histogramm')
# fontd = {'fontsize': 16,
#          'fontweight': 'bold',
#          'rotation': 45}

# axs.set_xticklabels(corr.columns, fontdict=fontd)
# axs.set_yticklabels(corr.columns)

#display(fig)
levels = MaxNLocator(nbins=50).tick_values(H.min(), (H.max())*0.75)
fig = plt.figure(figsize=(7, 5))
ax1 = plt.gca()    
#ax1 = fig.add_subplot(111, title='I(V) 2D histogramm', xlabel='Sample bias (V)', ylabel='log(Current)')
ax1.set_title('I(V) 2D histogramm',fontweight="bold", size=16) # Title
ax1.set_ylabel('log(Current)', fontsize = 16) # Y label
ax1.set_xlabel('Sample bias (V)', fontsize = 16) # X label
ax1.tick_params(axis="x", labelsize=12) 
ax1.tick_params(axis="y", labelsize=12) 
cf=ax1.contourf(xcenters, ycenters, H.T ,cmap='turbo', levels=levels)
cb1=fig.colorbar(cf, ax=ax1)
cb1.ax.tick_params(labelsize=12)

plt.show()

H1=H.T
#fig.show()