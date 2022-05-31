# -*- coding: utf-8 -*-
"""
Created on Wed May 18 17:13:20 2022

@author: kirill.kondratenko
"""

import numpy as np
import scipy.signal
import ruptures as rpt
from matplotlib.image import NonUniformImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from IPython.core.display import display

from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from matplotlib.offsetbox import AnchoredText

from Icon_get_raw_IV import grab_binary_data_Bruker
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os
from pathlib import Path

class SThM_fit:
    def __init__(self, deltaV = 0, VContact = 0, X_ROI = [], Y_ROI = [], beforeContactX = [], 
                 beforeContactFit = [], afterContactX = [], afterContactFit = [],):
        self.deltaV = deltaV
        self.VContact = VContact
        self.X_ROI = X_ROI
        self.Y_ROI = Y_ROI
        self.beforeContactX = beforeContactX
        self.beforeContactFit = beforeContactFit
        self.afterContactX = afterContactX
        self.afterContactFit = afterContactFit
        
def fit_SThM_extend(ramps):
    """Treats the SThM extend ramp and returns SThM_fit object with voltages and data for plotting"""
    Fit_extend = SThM_fit()
    #-------------------------------------------------------------------------
    # Trim SThM data
    #-------------------------------------------------------------------------
    
    XData = ramps[:,0] #Z ramp data
    YData = ramps[:,3] #SThM Vs-Vr extend data
    cutRight = 20 #trim index from right
    cutLeft = 100 #trim index from left
    YData = np.flip(YData)
    XData = XData[cutLeft:len(XData)-cutRight]
    YData = YData[cutLeft:len(YData)-cutRight]
    
    #-------------------------------------------------------------------------
    # Find changepoint region of interest (ROI)
    #-------------------------------------------------------------------------
    
    YDataSmoothed = scipy.signal.savgol_filter(YData, 31, 2) #Smooth data before differentiation
    YDataSmoothedPrime = np.gradient(YDataSmoothed)/np.gradient(XData)
    step = np.where(YDataSmoothedPrime == min(YDataSmoothedPrime))[0][0] #get the index of step response 
    cutLeftRoi = 30
    Fit_extend.X_ROI = XData[step-cutLeftRoi:]
    Fit_extend.Y_ROI = YData[step-cutLeftRoi:]
    
    #-------------------------------------------------------------------------
    # Find changepoint (jump-to-contact) wit RUPTURES
    #-------------------------------------------------------------------------
    
    #Changepoint detection with the Pelt search method
    model="rbf"
    algo = rpt.Pelt(model=model).fit(Fit_extend.Y_ROI)
    result = algo.predict(pen=10)
    changepoint = result[0] #get first changepoint
    
    #-------------------------------------------------------------------------
    # Linear fit before and after contact to get Vnc and Vc
    #-------------------------------------------------------------------------
    
    Fit_extend.beforeContactX = Fit_extend.X_ROI[:changepoint - 3] #get X before changepoint for fitting
    beforeContactY = Fit_extend.Y_ROI[:changepoint - 3] #get Y before changepoint for fitting
    Fit_extend.afterContactX = Fit_extend.X_ROI[changepoint + 7:] #get X after changepoint for fitting
    afterContactY = Fit_extend.Y_ROI[changepoint + 7:] #get Y after changepoint for fitting
    beforeContactFitCoeffs = np.polyfit(Fit_extend.beforeContactX, beforeContactY, 1)
    Fit_extend.beforeContactFit = np.polyval(beforeContactFitCoeffs, Fit_extend.beforeContactX)
    afterContactFitCoeffs = np.polyfit(Fit_extend.afterContactX, afterContactY, 1)
    Fit_extend.afterContactFit = np.polyval(afterContactFitCoeffs, Fit_extend.afterContactX)
    
    #-------------------------------------------------------------------------
    # Get the deltaV and Vc
    #-------------------------------------------------------------------------
    
    Fit_extend.deltaV = Fit_extend.beforeContactFit[-1] - Fit_extend.afterContactFit[0]
    Fit_extend.VContact = Fit_extend.afterContactFit[0]
    
    return Fit_extend

def fetch_dir():
    """ Returns  directory ID through tkinter UI """
    
    data_folder = Path("C:/Users/kirill.kondratenko/Documents/experimental_data/data_AFM_air/Avril")   #Mars/22-03-24
    
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    root.withdraw()  #use to hide tkinter window
    # file_to_open = filedialog.askopenfilename()
    dir_to_open =  filedialog.askdirectory(parent=root, initialdir=data_folder, title='Select data directory') 
    return dir_to_open

plt.ioff() # interactive mode off to prevent displayong plots

dir_to_open = fetch_dir()
dir_to_save = fetch_dir()
#a1=list(Path(dir_to_open).iterdir())
#file_list = sorted(Path(dir_to_open).iterdir(), key=os.path.getmtime) #sort files by last modified time (upward) os.listdir(dir_to_open) 
heatVoltages = os.listdir(path=dir_to_open)
heatVoltages = list(map(float, heatVoltages)) #convert voltages from string to float

heatVoltageSaveFolders = []
for heatVoltage in heatVoltages:
            heatVoltageSaveFolder = dir_to_save + '/' + str(heatVoltage/10) + '/'
            heatVoltageSaveFolders.append(heatVoltageSaveFolder)
            if os.path.isdir(heatVoltageSaveFolder) == False:
                os.makedirs(heatVoltageSaveFolder)
                

file_list = [os.path.join(dirpath,filename) for dirpath, _, filenames in os.walk(dir_to_open) for filename in filenames]
pointNum = len(file_list)//len(heatVoltages)
# ramps_X=[]
# ramps_deflection_extend=[]
# ramps_voltage_extend=[]
# ramps_all=[]
deltaV = []
VContact = []
VCounter = 0
VParameters = np.empty((0, 4), int)
for i,file in enumerate(file_list):
    ramps=grab_binary_data_Bruker(file, mode = 'SThM')[:,0:5]
    #ramps_X.append(ramps[:,0])
    #ramps_deflection_extend.append(ramps[:,1]) 
    #ramps_voltage_extend.append(ramps[:,3])  
    Fit = fit_SThM_extend(ramps) #get fitted parameters and data
    deltaV.append(Fit.deltaV)
    VContact.append(Fit.VContact)
    
    #-------------------------------------------------------------------------
    # plot ROI with fits and save
    #-------------------------------------------------------------------------
    
    fig = plt.figure(figsize=(7, 5))
    ax1 = plt.gca()    
    ax1.set_title('Extend data',fontweight="bold", size=16) # Title
    ax1.set_ylabel('SThM voltage (V)', fontsize = 16) # Y label
    ax1.set_xlabel('Z scanner displacement (nm)', fontsize = 16) # X label
    ax1.tick_params(axis="x", labelsize=12) 
    ax1.tick_params(axis="y", labelsize=12) 
    cf = plt.plot(Fit.X_ROI, Fit.Y_ROI, color='black')
    cf1 = plt.plot(Fit.beforeContactX, Fit.beforeContactFit, color='red')
    cf2 = plt.plot(Fit.afterContactX, Fit.afterContactFit, color='red')
    annotationString = "dV = %.4f \nVc = %.4f" % (Fit.deltaV, Fit.VContact)
    at = AnchoredText(annotationString, prop=dict(size=15), frameon=True, loc='upper right')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax1.add_artist(at)    
    #plt.show()
    #with open(heatVoltageSaveFolders[VCounter] + 'plot_' + str(i), 'w') as fid:
    plt.savefig(heatVoltageSaveFolders[VCounter] + 'plot_' + str(i))
    plt.close(fig)
    #-------------------------------------------------------------------------
    # Save fitted parameters for a given heating voltage
    #-------------------------------------------------------------------------
    
    pointCounter = len(deltaV) % pointNum
    
    if pointCounter == 0: # loops when all point for a heat voltage are proccessed
        #VCounter += 1
        deltaVperV = deltaV[i-(pointNum-1):(i+1)] #cut piece of deltaV value corresponding to the current heatng voltage
        VContactPerV = VContact[i-(pointNum-1):(i+1)] #idem for Vcontact
        VParameters = np.append(VParameters, np.array([[abs(np.mean(deltaVperV)), np.std(deltaVperV), np.mean(VContactPerV), np.std(VContactPerV)]]), axis = 0) #np.concatenate(([np.mean(deltaVperV)], [np.std(deltaVperV)], [np.mean(VContactPerV)], [np.std(VContactPerV)]), axis=0)
        
        with open(heatVoltageSaveFolders[VCounter] + 'fitted_parameters', 'w') as fid:
            fid.write(' '.join(map(str, VParameters[VCounter,:]))) # np.array2string(VParameters[VCounter,:])
        VCounter += 1

allParameters = np.concatenate((np.array(heatVoltages).reshape(np.array(heatVoltages).shape[0],-1)/10, VParameters), axis = 1)    
with open(dir_to_save + '/' + 'all_fitted_parameters', 'w') as fid:
    np.savetxt(fid, allParameters) #fid.write(' '.join(map(str, allParameters))) 
    
plt.ion() #turn the interactive mode back on
# ramps_X=np.array(ramps_X).T
# ramps_Y_extend=np.array(ramps_Y_extend).T
# ramps_Y_retract=np.array(ramps_Y_retract).T
# ramps_all=np.array(ramps_all).T