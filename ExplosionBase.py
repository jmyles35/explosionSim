#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 16:45:58 2018

@author: Marian
"""


import numpy as np
import pandas as pd
from GridBox import GridBox

from scipy import stats, integrate
import matplotlib.pyplot as plt

#intitial Conditions
initV = 8000 #m/s C4
initT = 600 #K no idea
initPres = 31000000 #310 kBar for C4
initDens = 1750 #kg/m^3
PATM = 101325 #pa
DENSITY = 1.01 #kg/m^3
TAMBIENT = 293.15 #K

R = 287 #air
cv = 718 #J/kgK ?
visc = 50 * 10**(-6) #Pa.s


#steps and characteristics of simulation
dt = 0.001 #seconds
dx = 0.1 #m
TOTALSTEPS = 20 

#testwidth
width = 50

#realwidth
#width = int(initV * 2 * TOTALSTEPS * dt / dx + 2)

#declare Global Variables
lattice = np.empty( (width, width), dtype=object)
accelx = np.empty( (width, width))
accely = np.empty( (width, width))


def init():
    #(x,y) coordinates of values
    
    for i in range(width):
        for j in range(width):
            lattice[i,j] = GridBox(0,0,TAMBIENT, DENSITY, PATM)
    
        
    lattice[width/2, width/2].vx = -1 * initV
    lattice[width/2, width/2].vy = -1 * initV
    lattice[width/2 + 1, width/2].vx = initV
    lattice[width/2 + 1, width/2].vy = -1 * initV
    lattice[width/2 + 1, width/2 + 1].vx = initV
    lattice[width/2 + 1, width/2 + 1].vy = initV
    lattice[width/2, width/2 + 1].vx = -1 * initV
    lattice[width/2, width/2 + 1].vy = initV
    
    for i in range(0,2):
        for j in range(0,2):
            lattice[width/2 + i, width/2 + j].temp = initT
            lattice[width/2 + i, width/2 + j].pres = initPres
            lattice[width/2 + i, width/2 + j].dens = initDens
    
    

def approxAccel():
    for i in range(1, width - 1):
        for j in range(1, width - 1):
            #find dvx/dt via navier-stokes equation and finite differences
            
            accelx[i,j] = 1.0 / lattice[i,j].dens * ( -1 * (lattice[i+1,j].pres - lattice[i-1,j].pres)/ dx / 2.0
                  + visc / (dx)**2 * (lattice[i+1,j].vx - 4 * lattice[i,j].vx + lattice[i-1,j].vx + lattice[i,j + 1].vx + lattice[i,j-1].vx)
                  + visc / (3 * dx**2) * (lattice[i+1,j].vx - 2 * lattice[i,j].vx + lattice[i-1,j].vx 
                           + 0.25 * (lattice[i+1,j+1].vy + lattice[i-1,j-1].vy - lattice[i-1,j+1].vy - lattice[i+1,j-1].vy))
            )
                  
            accely[i,j] = 1.0 / lattice[i,j].dens * ( -1 * (lattice[i,j+1].pres - lattice[i,j-1].pres)/ dx / 2.0
                  + visc / (dx)**2 * (lattice[i,j+1].vy - 4 * lattice[i,j].vy + lattice[i,j-1].vy + lattice[i+1,j].vy + lattice[i-1,j].vy)
                  + visc / (3 * dx**2) * (lattice[i,j+1].vy - 2 * lattice[i,j].vy + lattice[i,j-1].vy 
                           + 0.25 * (lattice[i+1,j+1].vx + lattice[i-1,j-1].vx - lattice[i-1,j+1].vx - lattice[i+1,j-1].vx))
            )
                  
            

#def approxVelo():
#    
#
#def approxTemps():
#    
#    
#def advectDensity():
#    
#    
#def advectVelo():
#    
#    
#def advectTemp():
#    
#    
#def gasLaw():
#    
init()

approxAccel()
#
#for t in range(1, TOTALSTEPS):
#    approxAccel():
#        
#    approxVelo():
#        
#    approxTemps():
#        
#    advectDensity();:
#         
#    advectVelo():
#          
#    advectTemp():
#     
#    gasLaw():