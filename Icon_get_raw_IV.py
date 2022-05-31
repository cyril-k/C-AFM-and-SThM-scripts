# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 13:05:11 2021

@author: kirill.kondratenko
"""

import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt
#from numpy import exp
#from scipy.optimize import curve_fit
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import re

def compile_searchstring(mode = 'current'):
    """ Compiles string array to search in nanoscope file header """
    if mode == 'current':
        searchstring = np.array([
                                 'FV scale: V [Sens. DeflSens]', # Deflection scale (in volts)
                                 'Samps', # Samples per line
                                 'Lines:', #Lines, 1 for a ramp
                                 'Data offset', #Data offset (in bytes) from the beggining of the file 
                                 'Image Data:', #Length of data (in bytes)
                                 'Ramp Begin: V [Sens. biassens]', #Start of ramp (in V, for I-Vs)
                                 'Ramp End: V [Sens. biassens]', #End of ramp (in V, for I-Vs)
                                 '@Sens. tunaSens:', #  @Sens. tunaSens: V # Transimpedance scale (in volts)
                                 'FV scale: V [Sens. tunaSens] ' #Tuna voltage scale (in volts)
                                 ])
    elif mode == 'SThM':
         searchstring = np.array([
                                 'FV scale: V [Sens. DeflSens]', # Deflection scale (in volts)
                                 'Samps', # Samples per line
                                 'Lines:', #Lines, 1 for a ramp
                                 'Data offset', #Data offset (in bytes) from the beggining of the file 
                                 'Image Data:', #Length of data (in bytes)
                                 '@Sens. Zsens:', #Z ramp scale
                                 'Ramp Size Zsweep:', #Size of Z ramp
                                 'FV scale: V [Sens. DeflSens] ', #  Deflection scale (in volts)
                                 'FV scale: V [Sens. Input3] ' #Input 3 (Vs-Vr) voltage scale (in volts)
                                 ])
    return searchstring


# def fetch_file():
#     data_folder = Path("C:/Users/kirill.kondratenko/Desktop")
#     file_to_open = data_folder / "mos2-plasma-e3.0_01397.spm"
#     # root = tk.Tk()
#     # root.withdraw()  #use to hide tkinter window
#     # file_to_open = filedialog.askopenfilename()
#     return file_to_open

#searchstring=compile_searchstring()
#file_to_open = fetch_file()


def read_header_values(file_to_open, mode = 'current'):
    """ Reads the header of raw nanoscope file and returns parameter array """
    searchstring=compile_searchstring(mode)
    #file_to_open = fetch_file()
    fid = open(file_to_open, "r")
    header_end = 0
    eof = 0
    counter = 1
    #byte_location = 0
    nstrings=len(searchstring)
    parcounter=np.ones(nstrings)
    parameters = dict((el, np.array(0, dtype='<U8')) for el in searchstring)
    # parameters = dict.fromkeys(searchstring, 0)
    while  (not(header_end)) and (not(eof)): #( not(eof) , not(header_end) ):
        #byte_location = fid.tell() 
        line = fid.readline()
        for i in searchstring:
            if line.find(i) != -1:
                if re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", line) != -1:
                    b = line.find('LSB')
                    if b>0:
                        if (parameters[i] == np.array(0, dtype='<U8')).all():
                            parameters[i]=np.array(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", line[b:-1]))
                        else:
                            parameters[i]=np.append(parameters[i],re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", line[b:-1]))
                    else:
                        if (parameters[i] == np.array(0, dtype='<U8')).all():
                            parameters[i]=np.array(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", line))
                        else:
                            parameters[i]=np.append(parameters[i],re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", line))
                else:
                    b=re.findall('"([^"]*)"', line)
                    if b != -1:
                         if (parameters[i] == np.array(0, dtype='<U8')).all():
                             parameters[i]=np.array(re.findall('"([^"]*)"', line))
                         else:
                             parameters[i]=np.append(parameters[i],re.findall('"([^"]*)"', line))
                for ij, i in enumerate(searchstring):
                    parcounter[ij]=parcounter[ij]+1
        if( (-1)==line ):
            eof  = 1  
        if line.find('\*File list end') != -1:
            header_end = 1
        counter=counter+1;  
    return parameters

# parameters=read_header_values()

def grab_binary_data_Bruker(file_to_open, mode = 'current'):
    """ Reads data from a raw nanoscope file with parameters extracted from the header: I(V) for mode = 'current' and Vs-Vr for mode = 'SThM' """
    #file_to_open = fetch_file()
    
    #-------------------------------------------------------------------------
    # Get parameters from file header
    #-------------------------------------------------------------------------
    
    searchstring=compile_searchstring(mode)
    parameters=read_header_values(file_to_open, mode)
    Defl_sens_scale = parameters[searchstring[0]].astype(float) # Deflection scale (in volts)
    spl = parameters[searchstring[1]].astype(int) # Samples per line
    spl=spl[1:-1] #first element not needed?
    #linno = parameters[searchstring[2]].astype(int) # No of lines 
    image_pos = parameters[searchstring[3]].astype(int) # Data position
    if mode == 'current':
        ramp_start = parameters[searchstring[5]].astype(float) # Ramp start
        ramp_end = parameters[searchstring[6]].astype(float) # Ramp end
        amplification_scale = parameters[searchstring[7]].astype(float) # Transimpedance scale (in volts)
        TUNAsens_scale = parameters[searchstring[8]].astype(float) # Tuna voltage scale (in volts)
    elif mode == 'SThM':
        ramp_scale = parameters[searchstring[5]].astype(float) # Z ramp scale
        ramp_size = parameters[searchstring[6]].astype(float) # Z ramp size
        deflection_scale = parameters[searchstring[7]].astype(float) # Deflection scale (in volts)
        SThM_voltage_scale = parameters[searchstring[8]].astype(float) # SThM voltage scale (in volts)
    #Z_Sensitivity = param(7).values; # Data position
    #L = len(image_pos); # No of data sets
    
    #-------------------------------------------------------------------------
    # Build X-axis
    #-------------------------------------------------------------------------
    if mode == 'current':
        ramp=np.linspace(ramp_start[1],ramp_end[1],spl[1])
        X_axis=ramp 
    elif mode == 'SThM':
        ramp_length=ramp_scale*ramp_size #calculate tip Z travel
        ramp=np.linspace(0,ramp_length,spl[1])
        X_axis=ramp
    
    #-------------------------------------------------------------------------
    # Get scaling factors
    #-------------------------------------------------------------------------
    
    deflection_scale_factor=Defl_sens_scale/65536 # factor to scale Deflection (per LSB)
    if mode == 'current':
        current_scale_factor=amplification_scale*TUNAsens_scale/65536 # factor to scale current (per LSB)
    elif mode == 'SThM': 
       SThM_voltage_factor=SThM_voltage_scale/65536 # factor to scale SThM voltage (per LSB)
       
    #-------------------------------------------------------------------------
    # Proceed to data readout
    #-------------------------------------------------------------------------
    
    #data_array = np.empty((spl[1]*2, 3))
    with open(file_to_open, "r") as fid:
         #fid = open(file_to_open, "r")   
        for ij, i in enumerate(image_pos): #ij is the channel index
            fid.seek(i)
            data_array = np.empty((spl[ij]*2, 1))
            data_array = np.fromfile(fid, np.int32, count=spl[ij]*2) #[:,ij]
            extend_raw = data_array[:spl[ij]]
            retract_raw = data_array[spl[ij]:]
            if mode == 'current':
                if ij==0:
                   scale_factor=current_scale_factor
                   extend_d=extend_raw*scale_factor
                   retract_d=retract_raw*scale_factor
                elif ij==1:
                   scale_factor=current_scale_factor
                   extend_v=extend_raw*scale_factor
                   retract_v=retract_raw*scale_factor
                elif ij==2:
                   scale_factor=deflection_scale_factor # current_scale_factor
                   extend_v1=extend_raw*scale_factor
                   retract_v1=retract_raw*scale_factor
            elif mode == 'SThM':
                extend_v1=extend_raw*0 #placeholder
                retract_v1=retract_raw*0 #placeholder
                if ij==0:
                   scale_factor=deflection_scale_factor
                   extend_d=extend_raw*scale_factor
                   retract_d=retract_raw*scale_factor
                elif ij==1:
                   scale_factor=SThM_voltage_factor
                   extend_v=extend_raw*scale_factor
                   retract_v=retract_raw*scale_factor
        ramps_total=np.column_stack((X_axis,extend_d,retract_d,extend_v,retract_v, extend_v1,retract_v1)) #all ramps
    return ramps_total

#ramps_total=grab_binary_data_Bruker()