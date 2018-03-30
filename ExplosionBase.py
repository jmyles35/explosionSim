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

import seaborn as sns; sns.set()

#intitial Conditions
initV = 0 #m/s C4
initT = 290 #K no idea
initPres = 31000*100000 #310 kBar?? for C4 (appears to work with 31 bar?)
initDens = 1750 #kg/m^3
PATM = 101325.0 #pa
R = 287.05 #air
DENSITY = PATM/R/initT #kg/m^3
TAMBIENT = 293.15 #K
ENERGYFACTOR = 0.5 #although this is multiplied by velocity so idk


k = 1.0 /120 #multiply by T 

cv = 718 #J/kgK ?
visc = 50 * 10**(-6) #Pa.s


#steps and characteristics of simulation
#seems to be dt< 2 microseconds and dx > 10 cm
dt = 0.0000002 #seconds
dx = 0.2 #m
TOTALSTEPS = 6000

#testwidth
width = 16


#realwidth
#width = int(initV * 2 * TOTALSTEPS * dt / dx + 2)

#declare Global Variables
lattice = np.empty( (width, width), dtype=object)
accelx = np.zeros( (width, width))
accely = np.zeros( (width, width))

vx = np.zeros( (width, width))
vy = np.zeros( (width, width))

vxAvg = np.zeros( (width, width))
vyAvg = np.zeros( (width, width))

densNext = np.zeros( (width, width))
densChange = np.zeros( (width, width))
densAvg = np.full( (width, width), DENSITY)
#densHat = np.zeros( (width, width))
#densBar = np.zeros( (width, width))

#vxTemp = np.zeros( (width, width))
vxAvgADV = np.zeros( (width, width))
#vxHat = np.zeros( (width, width))
#vxBar = np.zeros( (width, width))

#vyTemp = np.zeros( (width, width))
vyAvgADV = np.zeros( (width, width))
#vyHat = np.zeros( (width, width))
#vyBar = np.zeros( (width, width))

tempNext = np.full((width,width), TAMBIENT)
tempChange = np.zeros((width,width))
presTemp = np.full((width,width),PATM)

#######
def init():
    #(x,y) coordinates of values
    
    for i in range(width):
        for j in range(width):
            lattice[i,j] = GridBox(0,0,TAMBIENT, DENSITY, PATM)
    
        
#    lattice[width/2, width/2].vx = -1 * initV
#    lattice[width/2, width/2].vy = -1 * initV
#    lattice[width/2 + 1, width/2].vx = initV
#    lattice[width/2 + 1, width/2].vy = -1 * initV
#    lattice[width/2 + 1, width/2 + 1].vx = initV
#    lattice[width/2 + 1, width/2 + 1].vy = initV
#    lattice[width/2, width/2 + 1].vx = -1 * initV
#    lattice[width/2, width/2 + 1].vy = initV
    
    #16 blocks should make the initial derivites better
    for i in range(0,1):
        for j in range(0,1):
            lattice[width/2 -i, width/2 - i].vx = -1 * initV
            lattice[width/2 -i, width/2 - i].vy = -1 * initV
            lattice[width/2 + 1 + i , width/2 - i].vx = initV
            lattice[width/2 + 1 + i, width/2 - i].vy = -1 * initV
            lattice[width/2 + 1 + i, width/2 + 1].vx = initV
            lattice[width/2 + 1 + i, width/2 + 1 + i].vy = initV
            lattice[width/2 - i, width/2 + 1 + i].vx = -1 * initV
            lattice[width/2 - i, width/2 + 1 + i].vy = initV

    for i in range(0,2):
        for j in range(0,2):
#            print 'hi'
            lattice[width/2 -1 + i, width/2 -1 + j].temp = initT
            lattice[width/2 -1 + i, width/2 -1 + j].pres = initPres
            lattice[width/2 -1 + i, width/2 -1 + j].dens = initDens
 #######   end init
    


#######
def approxAccel():
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            #find dvx/dt via navier-stokes equation and finite differences
            
            ##If I use 3rd order finite difference's it might make a difference
            accelx[i,j] = 1.0 / lattice[i,j].dens * ( -1 * (-1.0/12 * lattice[i+2,j].pres + 2.0/3 * lattice[i+1,j].pres 
                  - 2.0/3 * lattice[i-1,j].pres + 1.0/12 * lattice[i-2,j].pres)/ dx #first derivivitive 3rd order
                  + visc / (dx)**2 * (lattice[i+1,j].vx - 4 * lattice[i,j].vx + lattice[i-1,j].vx + lattice[i,j+1].vx + lattice[i,j-1].vx) #2nd order laplacian
                  + visc / (3 * dx**2) * (lattice[i+1,j].vx - 2 * lattice[i,j].vx + lattice[i-1,j].vx 
                           + 1.0/144 * (8.0*(lattice[i+1,j-2].vy + lattice[i+2,j-1].vy + lattice[i-2,j+1].vy + lattice[i-1,j+2].vy)
                           -8.0*(lattice[i-1,j-2].vy + lattice[i-2,j-1].vy + lattice[i+1,j+2].vy + lattice[i+2,j+1].vy)
                           -(lattice[i+2,j-2].vy + lattice[i-2,j+2].vy - lattice[i-2,j-2].vy - lattice[i+2,j+2].vy)
                           + 64.0 * (lattice[i+1,j+1].vy + lattice[i-1,j-1].vy - lattice[i+1,j-1].vy - lattice[i-1,j+1].vy))) #mixed partial
            )
                  
            accely[i,j] = 1.0 / lattice[i,j].dens * ( -1 * (-1.0/12 * lattice[i,j+2].pres + 2.0/3 * lattice[i,j+1].pres 
                  - 2.0/3 * lattice[i,j-1].pres + 1.0/12 * lattice[i,j-2].pres)/ dx
                  + visc / (dx)**2 * (lattice[i,j+1].vy - 4 * lattice[i,j].vy + lattice[i,j-1].vy + lattice[i+1,j].vy + lattice[i-1,j].vy)
                  + visc / (3 * dx**2) * (lattice[i,j+1].vy - 2 * lattice[i,j].vy + lattice[i,j-1].vy #2nd order 2nd derivitive
                           + 1.0/144 * (8.0*(lattice[i+1,j-2].vx + lattice[i+2,j-1].vx + lattice[i-2,j+1].vx + lattice[i-1,j+2].vx)
                           -8.0*(lattice[i-1,j-2].vx + lattice[i-2,j-1].vx + lattice[i+1,j+2].vx + lattice[i+2,j+1].vx)
                           -(lattice[i+2,j-2].vx + lattice[i-2,j+2].vx - lattice[i-2,j-2].vx - lattice[i+2,j+2].vx)
                           + 64.0*(lattice[i+1,j+1].vx + lattice[i-1,j-1].vx - lattice[i+1,j-1].vx - lattice[i-1,j+1].vx)))
            )
                  
            
#######
def approxVelo():
    #find squigle velocity and mean velocity, place into 4 matrices
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            vx[i,j] = lattice[i,j].vx + accelx[i,j]*dt
            vy[i,j] = lattice[i,j].vy + accely[i,j]*dt
            vxAvg[i,j] = lattice[i,j].vx + accelx[i,j]*dt / 2.0
            vyAvg[i,j] = lattice[i,j].vy + accely[i,j]*dt / 2.0

#######
def approxTemps():
    # just make them smaller cause i dunno
    for i in range(2, width - 2):
        for j in range(2, width - 2):
    
#            tempNext[i,j] = lattice[i,j].temp + dt / (cv * lattice[i,j].dens) * (
#                    k * lattice[i,j].temp * (lattice[i,j+1].temp - 2 * lattice[i,j].temp + lattice[i,j-1].temp 
#                               + lattice[i+1,j].temp - 2 * lattice[i,j].temp + lattice[i-1,j].temp) / (dx**2) 
#                    - lattice[i,j].pres * (vxAvg[i+1,j]- vxAvg[i-1,j] + vyAvg[i,j+1]- vyAvg[i,j-1]) / dx
#                    + -2.0 * visc / 3 * (vxAvg[i+1,j]- vxAvg[i-1,j] + vyAvg[i,j+1]- vyAvg[i,j-1]) / dx
#                    + visc / 2.0 * (vyAvg[i+1,j]- vyAvg[i-1,j] + vxAvg[i,j+1]- vxAvg[i,j-1])**2 / (dx**2) 
#                    )
            tempChange[i,j] = + dt / (cv * lattice[i,j].dens) * (
                    k * (lattice[i,j+1].temp - 2 * lattice[i,j].temp + lattice[i,j-1].temp 
                               + lattice[i+1,j].temp - 2 * lattice[i,j].temp + lattice[i-1,j].temp) / (dx**2) 
                    - lattice[i,j].pres * (vxAvg[i+1,j]- vxAvg[i-1,j] + vyAvg[i,j+1]- vyAvg[i,j-1]) / dx
                    -2.0 * visc / 3 * (vxAvg[i+1,j]- vxAvg[i-1,j] + vyAvg[i,j+1]- vyAvg[i,j-1]) / dx
                    + visc * ((vyAvg[i+1,j]- vyAvg[i-1,j] + vxAvg[i,j+1]- vxAvg[i,j-1])/4.0)**2 / (dx**2) 
                    )
 
#######           
def approxDensity():
    for i in range(2, width - 2):
        for j in range(2, width - 2):
#            densNext[i,j] = lattice[i,j].dens + -1 * dt * lattice[i,j].dens * (vxAvg[i+1,j]- vxAvg[i-1,j] + vyAvg[i,j+1] - vyAvg[i,j-1]) / dx / 2.0
            densChange[i,j] = -1 * dt * lattice[i,j].dens * (vxAvg[i+1,j]- vxAvg[i-1,j] + vyAvg[i,j+1] - vyAvg[i,j-1]) / dx / 2.0
       
#######
def advectDensity():
    # 5 loops of back and forth error elimination?? doesnt appear to work
#    for k in range(5):
    
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            densAvg[i,j] = lattice[i,j].dens - dt * (vxAvg[i,j] * (-1.0/12 *lattice[i+2,j].dens + 2.0/3 * lattice[i+1,j].dens 
                   - 2.0/3 * lattice[i-1,j].dens + 1.0/12 * lattice[i-2,j].dens)/ dx 
                   + vyAvg[i,j] * (-1.0/12 *lattice[i,j+2].dens + 2.0/3 *lattice[i,j+1].dens 
                          - 2.0/3 * lattice[i,j-1].dens + 1.0/12 * lattice[i,j-2].dens)/ dx)
            
            ###ADVECTION SUCKS :(
#            densHat[i,j] = densAvg[i,j] + dt * (vxAvg[i,j] * (densAvg[i+1,j] - densAvg[i-1,j])/ dx / 2.0 
#                   + vyAvg[i,j] * (densAvg[i,j+1] - densAvg[i,j-1])/ dx / 2.0)
#            densBar[i,j] = 3.0 / 2 * densAvg[i,j] - 0.5 * densHat[i,j]
#            densNext[i,j] = lattice[i,j].dens - dt * (vxAvg[i,j] * (densBar[i+1,j] - densBar[i-1,j])/ dx / 2.0 
#                   + vyAvg[i,j] * (densBar[i,j+1] - densBar[i,j-1])/ dx / 2.0)
    for i in range( width):
        for j in range(width):
            densNext[i,j] = densAvg[i,j]
#               lattice [i,j].dens = densNext[i,j]    
            
def advectVelo():
    
    #TRY to do vx, vy seperately
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            
            #3RD ORDER
            vxAvgADV[i,j] = vx[i,j] - dt * (vxAvg[i,j] * (-1.0/12 *vx[i+2,j] + 2.0/3 *vx[i+1,j] - 2.0/3 * vx[i-1,j] + 1.0/12 * vx[i-2,j])/ dx 
                   + vyAvg[i,j] * (-1.0/12 *vx[i,j+2] + 2.0/3 *vx[i,j+1] - 2.0/3 * vx[i,j-1] + 1.0/12 * vx[i,j-2])/ dx)
            ####This is the problem line
            ####IMPROVE ALGORITHM TO CONVECT
#            vxHat[i,j] = vxAvgADV[i,j] + dt * (vxAvg[i,j] * (vxAvgADV[i+1,j] - vxAvgADV[i-1,j])/ dx / 2.0 
#                   + vyAvg[i,j] * (vxAvgADV[i,j+1] - vxAvgADV[i,j-1])/ dx / 2.0)
#            vxBar[i,j] = 3.0 / 2 * vxAvgADV[i,j] - 0.5 * vxHat[i,j]
#            vxTemp[i,j] = vxBar[i,j] - dt * (vxAvg[i,j] * (vxBar[i+1,j] - vxBar[i-1,j])/ dx / 2.0 
#                   + vyAvg[i,j] * (vxBar[i,j+1] - vxBar[i,j-1])/ dx / 2.0)
            
            
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            ####IMPROVE   
#            lattice [i,j].vx = vxTemp[i,j] 
            lattice[i,j].vx = vxAvgADV[i,j]
            
    ##vy
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            
            #3RD ORDER
            vyAvgADV[i,j] = vy[i,j] - dt * (vxAvg[i,j] * (-1.0/12 *vy[i+2,j] + 2.0/3 *vy[i+1,j] - 2.0/3 * vy[i-1,j] + 1.0/12 * vy[i-2,j])/ dx 
                   + vyAvg[i,j] * (-1.0/12 *vy[i,j+2] + 2.0/3 *vy[i,j+1] - 2.0/3 * vy[i,j-1] + 1.0/12 * vy[i,j-2])/ dx)
            
            ######IMPROVE
#            vyHat[i,j] = vy[i,j] + dt * (vxAvg[i,j] * (vy[i+1,j] - vy[i-1,j])/ dx / 2.0 
#                   + vyAvg[i,j] * (vy[i,j+1] - vy[i,j-1]) / dx / 2.0)
            
            #using vyavg
#            vyHat[i,j] = vyAvgADV[i,j] + dt * (vxAvg[i,j] * (vyAvgADV[i+1,j] - vyAvgADV[i-1,j])/ dx / 2.0 
#                   + vyAvg[i,j] * (vyAvgADV[i,j+1] - vyAvgADV[i,j-1])/ dx / 2.0)
#            vyBar[i,j] = 3.0 / 2 * vyAvgADV[i,j] - 0.5 * vyHat[i,j]
            
            #commented out until a better advection algorithm can be developed
#            vyBar[i,j] = vy[i,j] + 0.5 * (vyAvgADV[i,j] - vyHat[i,j])
#            vyTemp[i,j] = vyBar[i,j] - dt * (vxAvg[i,j] * (vyBar[i+1,j] - vyBar[i-1,j])/ dx / 2.0 
#                   + vyAvg[i,j] * (vyBar[i,j+1] - vyBar[i,j-1])/ dx / 2.0)
            
            
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            ####commented until better algorithm
#               lattice [i,j].vy = vyTemp[i,j] 
            lattice[i,j].vy = vyAvgADV[i,j]
    
def advectTemp():
    for i in range(2, width - 2):
        for j in range(2, width - 2):
            tempNext[i,j] = lattice[i,j].temp - dt * (vxAvg[i,j] * (-1.0/12 *lattice[i+2,j].temp + 2.0/3 *lattice[i+1,j].temp 
                    - 2.0/3 * lattice[i-1,j].temp + 1.0/12 * lattice[i-2,j].temp)/ dx 
                   + vyAvg[i,j] * (-1.0/12 *lattice[i,j+2].temp + 2.0/3 *lattice[i,j+1].temp 
                          - 2.0/3 * lattice[i,j-1].temp + 1.0/12 * lattice[i,j-2].temp)/ dx)
            
            
def gasLaw():
    for i in range(width):
        for j in range(width):
            presTemp[i,j] = lattice[i,j].dens * R * lattice[i,j].temp
    for i in range(1,width-1):
        for j in range(width):
            lattice[i,j].pres = max(max(presTemp[i,j], -100000000), min(presTemp[i,j], 310000*100000))
            
## Will it work if I just do this at the end?? 
def wallVelo():
    
    ##top wall
    for i in range(width):
        lattice[i,width - 3].vx = ENERGYFACTOR * lattice[i,width - 3].vx
        if (lattice[i,width - 3].vy > 0) :
            lattice[i,width - 3].vy = -1 * ENERGYFACTOR * lattice[i,width - 3].vy
        else:
            lattice[i,width - 3].vy = ENERGYFACTOR * lattice[i,width - 3].vy
    
    ##left wall
    for i in range(width):
        lattice[2,i].vy =  ENERGYFACTOR * lattice[2,i].vy
        if (lattice[2,i].vx < 0) :
            lattice[2,i].vx = -1 * ENERGYFACTOR * lattice[2,i].vx
        else:
            lattice[2,i].vx = ENERGYFACTOR * lattice[2,i].vx
    ##bottom wall
    for i in range(width):
        lattice[i,2].vx = ENERGYFACTOR * lattice[i,2].vx
        if (lattice[i,2].vy < 0) :
            lattice[i,2].vy = -1 * ENERGYFACTOR * lattice[i,2].vy
        else:
            lattice[i,2].vy = ENERGYFACTOR * lattice[i,2].vy
    ##right wall
    for i in range(width):
        lattice[width-3,i].vy = ENERGYFACTOR * lattice[width-3,i].vy
        if (lattice[width-3,i].vx > 0) :
            lattice[width-3,i].vx = -1 * ENERGYFACTOR * lattice[width-3,i].vx
        else:
            lattice[width-3,i].vx = ENERGYFACTOR * lattice[width-3,i].vx
init()


##### MAIN LOOP
for t in range(0,TOTALSTEPS):
    approxAccel()
        
    approxVelo()
        
    approxTemps()
    #sub in the new temperature
            
    approxDensity() 
    #Sub in the New density       
#    for i in range(1, width - 1):
#        for j in range(1, width - 1):
#            lattice [i,j].dens = densNext[i,j]
    advectDensity()
    for i in range(1, width - 1):
        for j in range(1, width - 1):
            #set min density as 0.05 kg / m^3
            lattice [i,j].dens = max(max(densNext[i,j] + densChange[i,j], 0.15), min(densNext[i,j] + densChange[i,j], 3000))
    advectVelo()
          
    advectTemp()
    for i in range(1, width - 1):
        for j in range(1, width - 1):
            #set min temp as 20 K
#            lattice [i,j].temp = max(max(tempNext[i,j], 20), min(tempNext[i,j], 5000))
            ###I really need to find out whats going on with the temp approximation
           lattice [i,j].temp = max(tempNext[i,j] + tempChange[i,j], 50)
     
    gasLaw()
    
    if(t % 200 == 0):
        plt.clf()
        sns.heatmap(presTemp)
        plt.pause(0.05)
        print t
    

