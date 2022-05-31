# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 13:36:26 2021

@author: kirill.kondratenko
"""

import pandas as pd
import matplotlib.pyplot as plt
from numpy import exp
from scipy.optimize import curve_fit
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

pi = 3.14
h = 6.63e-34
q = 1.6e-19
m = 9.11e-31
Mr = 0.35
d = 1e-9
# a1 = 9.61e-21
# b1 = 0.55

def fetchfile():
    # data_folder = Path("C:/Users/kirill.kondratenko/Desktop")
    # file_to_open = data_folder / "Fc_Au.txt"
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    file_to_open = filedialog.askopenfilename()
    return file_to_open


#   print(file_to_open)

def objective(x, a, b):
    return ((a * (q ** 3) * m * (x ** 2)) / (8 * pi * h * (b * q) * (d ** 2) * Mr * m)) * exp(
        -(8 * pi * ((2 * Mr * m) ** (1 / 2)) * ((b * q) ** (3 / 2)) * d) / (3 * h * q * x))


def objective2(x, a, b):
    return ((a * (q ** 3) * m * (x ** 2)) / (8 * pi * h * (b * q) * (d ** 2) * Mr * m)) * exp(
        -(8 * pi * ((2 * Mr * m) ** (1 / 2)) * ((b * q) ** (3 / 2)) * d) / (3 * h * q * x))


def read():
    file_to_open = fetchfile()
    dfpos = pd.read_csv(file_to_open, delim_whitespace=True, header=None, skiprows=257)
    dfneg = pd.read_csv(file_to_open, delim_whitespace=True, header=None, skipfooter=258)

    xpos = dfpos[0]
    ypos = dfpos[1]

    xneg = abs(dfneg[0])
    yneg = abs(dfneg[1])

    return xpos, ypos, xneg, yneg


def fitting():
    xpos, ypos, xneg, yneg = read()
    # xpos, ypos = read()
    popt_pos, pcov_pos = curve_fit(objective, xpos, ypos, p0=[1e-18, 0.1], maxfev=1000)
    popt_neg, pcov_neg = curve_fit(objective2, xneg, yneg, p0=[1e-18, 0.1], maxfev=10000)
    print('popt_pos:{}'.format(popt_pos))
    print('popt_neg:{}'.format(popt_neg))
    a1, b1 = popt_pos
    a2, b2 = popt_neg

    y_line = objective2(xneg, a2, b2)
    plt.scatter(-xneg, -yneg)
    plt.plot(-xneg, -y_line, color='red')

    y_line2 = objective(xpos, a1, b1)
    plt.scatter(xpos, ypos)
    plt.plot(xpos, y_line2, color='black')

    return y_line,xneg,y_line2,xpos
    # return y_line2, xpos


def export_datas():
    y_line , xneg, y_line2,xpos = fitting()
    # y_line2, xpos = fitting()

    df = pd.concat([xneg, xpos], ignore_index=True)
    df1 = pd.concat([y_line, y_line2], ignore_index=True)

    result = pd.concat([df,df1], axis=1, ignore_index= True)
    # result = pd.concat([xpos, y_line2], axis=1, ignore_index=True)

    result.to_csv('Datas-fit.txt', header=None, index=None, sep='\t', mode='a')

    x = result[0]
    y = result[1]

    # plt.plot(x, y)
    plt.show()


export_datas()
