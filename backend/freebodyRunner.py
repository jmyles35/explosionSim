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
import json
from pprint import pprint


size=32
dx=.2
xdim=size*dx
ydim=size*dx
dt=.0000002*20
time=0.002
obj=np.zeros((size,size))
for i in range(18,21):
    for j in range(11,14):
        obj[j,i]=1
ColumnSum=np.sum(obj,axis=1)          
           

"                        dt,  dx   #blocks  time num explosion"
freeb=Freebody(obj,xdim,ydim,.0000000005)
"explosion = ExplosionSim(dt, dx, size, time, 1)"



e = json.load(open('data3bomb_02us_2ms_15GPaTEST.json'))



"e=explosion.finalMatrix"
plt.figure()



for i in range(1,int(time/dt-3)):
    freeb.update(i,e,dt)
    "print i"
    if (i%1==0):
        
        plt.clf()
        sns.heatmap(freeb.S)
        plt.show()
        plt.pause(.000001)
a=freeb.finalPos
        
freeb.makeJSON()




