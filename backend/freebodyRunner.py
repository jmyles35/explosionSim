#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 15:05:33 2018

@author: Marian
"""

import numpy as np
import pandas as pd
from ExplosionSim import ExplosionSim
from freebody import Freebody

from scipy import stats, integrate
import matplotlib.pyplot as plt

import seaborn as sns; sns.set()


size=16
dx=.3
xdim=size*dx
ydim=size*dx
dt=.000001
time=.0001
obj=np.zeros((size,size))
for i in range(7,12):
    for j in range(8,13):
        obj[j,i]=1
ColumnSum=np.sum(obj,axis=1)          
           

"                        dt,  dx   #blocks  time num explosion"
freeb=Freebody(obj,xlen,ylen,340)
explosion = ExplosionSim(dt, dx, size, time, 1)




e=explosion.finalMatrix

for i in range(0,int(time/dt-3)):
    freeb.update(i,e,dt)
    plt.clf()
    sns.heatmap(freeb.S)
    plt.pause(0.00001)
    



