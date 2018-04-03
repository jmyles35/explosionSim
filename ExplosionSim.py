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
from scipy.optimize import fsolve, root
import math

import seaborn as sns; sns.set()


class ExplosionSim:
    initV = 0 #m/s C4
    initT = 290 #K no idea
    initPres = 310 * 10**9 #310 kBar?? for C4 (appears to work with 31 bar?)
    initDens = 700 #kg/m^3
    PATM = 101325.0 #pa
    R = 287.05 #air
    DENSITY = PATM/R/initT #kg/m^3
    TAMBIENT = 293.15 #K
    ENERGYFACTOR = 0.0 #although this is multiplied by velocity so idk
    STEELDENS = 8000 #kg/m^3
    
    VMAX = initPres / (2.5 * 10**4 * initDens) * 1.5 #max is 1.2 times calculated max
    PRESMAX = initPres * 4 #let it not be greater than 3x init pressure
    
    
    
    k = 1.0 /120 #multiply by T 
    
    cv = 718 #J/kgK ?
    visc = 50 * 10**(-5) #Pa.s
    
    
    def __init__(self, dt, dx, width, time, numExplosions):
        #intitial Conditions
        #steps and characteristics of simulation
        #seems to be dt< 2 microseconds and dx > 10 cm

        print ExplosionSim.VMAX
        
        self.dt = dt #seconds
        self.dx = dx #m
        self.TOTALSTEPS = int(time / dt)
        self.numExplosions = numExplosions
        
        ##5 variables
        self.finalMatrix = np.zeros((self.TOTALSTEPS, width, width, 5))
        
        
        #testwidth
        self.width = width
        
        
        #realwidth
        #width = int(ExplosionSim.initV * 2 * TOTALSTEPS * dt / dx + 2)
        
        #declare Global Variables
        self.lattice = np.empty( (width, width), dtype=object)
        self.accelx = np.zeros( (width, width))
        self.accely = np.zeros( (width, width))
        
        self.vx = np.zeros( (width, width))
        self.vy = np.zeros( (width, width))
        
        self.vxAvg = np.zeros( (width, width))
        self.vyAvg = np.zeros( (width, width))
        
        self.densNext = np.zeros( (width, width))
        self.densChange = np.zeros( (width, width))
        self.densAvg = np.full( (width, width), ExplosionSim.DENSITY)
        #densHat = np.zeros( (width, width))
        #densBar = np.zeros( (width, width))
        
        #vxTemp = np.zeros( (width, width))
        self.vxAvgADV = np.zeros( (width, width))
        #vxHat = np.zeros( (width, width))
        #vxBar = np.zeros( (width, width))
        
        #vyTemp = np.zeros( (width, width))
        self.vyAvgADV = np.zeros( (width, width))
        #vyHat = np.zeros( (width, width))
        #vyBar = np.zeros( (width, width))
        
        self.tempNext = np.full((width,width), ExplosionSim.TAMBIENT)
        self.tempChange = np.zeros((width,width))
        self.presTemp = np.full((width,width),ExplosionSim.PATM)
        
        self.setup()
        self.runSim()
        
    #######
    def setup(self):
        #(x,y) coordinates of values
        
        for i in range(self.width):
            for j in range(self.width):
                self.lattice[i,j] = GridBox(0,0, ExplosionSim.TAMBIENT, ExplosionSim.DENSITY, ExplosionSim.PATM)
        
            
    #    self.lattice[self.width/2, self.width/2].vx = -1 * ExplosionSim.initV
    #    self.lattice[self.width/2, self.width/2].vy = -1 * ExplosionSim.initV
    #    self.lattice[self.width/2 + 1, self.width/2].vx = ExplosionSim.initV
    #    self.lattice[self.width/2 + 1, self.width/2].vy = -1 * ExplosionSim.initV
    #    self.lattice[self.width/2 + 1, self.width/2 + 1].vx = ExplosionSim.initV
    #    self.lattice[self.width/2 + 1, self.width/2 + 1].vy = ExplosionSim.initV
    #    self.lattice[self.width/2, self.width/2 + 1].vx = -1 * ExplosionSim.initV
    #    self.lattice[self.width/2, self.width/2 + 1].vy = ExplosionSim.initV
        
        ####Init the bombs :) (please ensure that width is divisable by 4)
        ## 1 BOMBBB
        if self.numExplosions == 1 :
            for i in range(0,1):
                for j in range(0,1):
                    self.lattice[self.width/2 -i, self.width/2 - i].vx = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 -i, self.width/2 - i].vy = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i , self.width/2 - i].vx = ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i, self.width/2 - i].vy = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i, self.width/2 + 1].vx = ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i, self.width/2 + 1 + i].vy = ExplosionSim.initV
                    self.lattice[self.width/2 - i, self.width/2 + 1 + i].vx = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 - i, self.width/2 + 1 + i].vy = ExplosionSim.initV
        
            for i in range(0,2):
                for j in range(0,2):
                    self.lattice[self.width/2 -1 + i, self.width/2 -1 + j].temp = ExplosionSim.initT
                    self.lattice[self.width/2 -1 + i, self.width/2 -1 + j].pres = ExplosionSim.initPres
                    self.lattice[self.width/2 -1 + i, self.width/2 -1 + j].dens = ExplosionSim.initDens
        ##2 BOMBS
        if self.numExplosions == 2 :
            for k in range(1,4):
                ##this currently creates a 2x2 bomb (this can be increased)
                if k != 2 :
                    for i in range(0,1):
                        for j in range(0,1):
                            self.lattice[k * self.width/4 -i, self.width/2 - i].vx = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 -i, self.width/2 - i].vy = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i , self.width/2 - i].vx = ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i, self.width/2 - i].vy = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i, self.width/2 + 1].vx = ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i, self.width/2 + 1 + i].vy = ExplosionSim.initV
                            self.lattice[k * self.width/4 - i, self.width/2 + 1 + i].vx = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 - i, self.width/2 + 1 + i].vy = ExplosionSim.initV
        
                    for i in range(0,2):
                        for j in range(0,2):
                #            print 'hi'
                            self.lattice[k * self.width/4 -1 + i, self.width/2 -1 + j].temp = ExplosionSim.initT
                            self.lattice[k * self.width/4 -1 + i, self.width/2 -1 + j].pres = ExplosionSim.initPres
                            self.lattice[k * self.width/4 -1 + i, self.width/2 -1 + j].dens = ExplosionSim.initDens
                            
        ##3 BOMBS
        if self.numExplosions == 3 :
            for k in range(1,4):
                ##this currently creates a 2x2 bomb (this can be increased)
                if k != 2 :
                    if k != 2 :
                        for i in range(0,1):
                            for j in range(0,1):
                                self.lattice[k * self.width/4 -i, self.width/4 - i].vx = -1 * ExplosionSim.initV
                                self.lattice[k * self.width/4 -i, self.width/4 - i].vy = -1 * ExplosionSim.initV
                                self.lattice[k * self.width/4 + 1 + i , self.width/4 - i].vx = ExplosionSim.initV
                                self.lattice[k * self.width/4 + 1 + i, self.width/4 - i].vy = -1 * ExplosionSim.initV
                                self.lattice[k * self.width/4 + 1 + i, self.width/4 + 1].vx = ExplosionSim.initV
                                self.lattice[k * self.width/4 + 1 + i, self.width/4 + 1 + i].vy = ExplosionSim.initV
                                self.lattice[k * self.width/4 - i, self.width/4 + 1 + i].vx = -1 * ExplosionSim.initV
                                self.lattice[k * self.width/4 - i, self.width/4 + 1 + i].vy = ExplosionSim.initV
            
                        for i in range(0,2):
                            for j in range(0,2):
                    #            print 'hi'
                                self.lattice[k * self.width/4 -1 + i, self.width/4 -1 + j].temp = ExplosionSim.initT
                                self.lattice[k * self.width/4 -1 + i, self.width/4 -1 + j].pres = ExplosionSim.initPres
                                self.lattice[k * self.width/4 -1 + i, self.width/4 -1 + j].dens = ExplosionSim.initDens
                            
            for i in range(0,1):
                for j in range(0,1):
                    self.lattice[self.width/2 -i, 3*self.width/4 - i].vx = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 -i, 3*self.width/4 - i].vy = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i , 3*self.width/4 - i].vx = ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i, 3*self.width/4 - i].vy = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i, 3*self.width/4 + 1].vx = ExplosionSim.initV
                    self.lattice[self.width/2 + 1 + i, 3*self.width/4 + 1 + i].vy = ExplosionSim.initV
                    self.lattice[self.width/2 - i, 3*self.width/4 + 1 + i].vx = -1 * ExplosionSim.initV
                    self.lattice[self.width/2 - i, 3*self.width/4 + 1 + i].vy = ExplosionSim.initV

            for i in range(0,2):
                for j in range(0,2):
        #            print 'hi'
                    self.lattice[self.width/2 -1 + i, 3*self.width/4 -1 + j].temp = ExplosionSim.initT
                    self.lattice[self.width/2 -1 + i, 3*self.width/4 -1 + j].pres = ExplosionSim.initPres
                    self.lattice[self.width/2 -1 + i, 3*self.width/4 -1 + j].dens = ExplosionSim.initDens
                    
        ##4 BOMBS
        if self.numExplosions == 4 :
            for k in range(1,4):
                ##this currently creates a 2x2 bomb (this can be increased)
                ## only does at 1,1 and 3,3
                if k != 2 :
                    for i in range(0,1):
                        for j in range(0,1):
                            self.lattice[k * self.width/4 -i, k * self.width/4 - i].vx = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 -i, k * self.width/4 - i].vy = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i , k * self.width/4 - i].vx = ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i, k * self.width/4 - i].vy = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i, k * self.width/4 + 1].vx = ExplosionSim.initV
                            self.lattice[k * self.width/4 + 1 + i, k * self.width/4 + 1 + i].vy = ExplosionSim.initV
                            self.lattice[k * self.width/4 - i, k * self.width/4 + 1 + i].vx = -1 * ExplosionSim.initV
                            self.lattice[k * self.width/4 - i, k * self.width/4 + 1 + i].vy = ExplosionSim.initV
        
                    for i in range(0,2):
                        for j in range(0,2):
                #            print 'hi'
                            self.lattice[k * self.width/4 -1 + i, self.width/4 -1 + j].temp = ExplosionSim.initT
                            self.lattice[k * self.width/4 -1 + i, self.width/4 -1 + j].pres = ExplosionSim.initPres
                            self.lattice[k * self.width/4 -1 + i, self.width/4 -1 + j].dens = ExplosionSim.initDens
                    
                    
        for i in range(2):
             for j in range(self.width):
                 self.lattice[0+i,j].dens = ExplosionSim.STEELDENS
                 self.lattice[j,0+i].dens = ExplosionSim.STEELDENS
                 self.lattice[self.width - 1 - i,j].dens = ExplosionSim.STEELDENS
                 self.lattice[j,self.width - 1 - i].dens = ExplosionSim.STEELDENS
     #######   end init
     
    ######MAIN
    def runSim(self):
        ##### MAIN LOOP
        for t in range(0, self.TOTALSTEPS):
            self.approxAccel()
                
            self.approxVelo()
                
            self.approxTemps()
            #sub in the new temperature
                    
            self.approxDensity() 
            #Sub in the New density       
        #    for i in range(1, self.width - 1):
        #        for j in range(1, self.width - 1):
        #            self.lattice [i,j].dens = densNext[i,j]
            self.advectDensity()
            for i in range(1, self.width - 1):
                for j in range(1, self.width - 1):
                    #set min density as 0.05 kg / m^3
                    self.lattice [i,j].dens = max(max(self.densNext[i,j] + self.densChange[i,j], 0.15), min(self.densNext[i,j] + self.densChange[i,j], 3000))
            self.advectVelo()
                  
            self.advectTemp()
            for i in range(1, self.width - 1):
                for j in range(1, self.width - 1):
                    #set min temp as 20 K
        #            self.lattice [i,j].temp = max(max(tempNext[i,j], 20), min(tempNext[i,j], 5000))
                    ###I really need to find out whats going on with the temp approximation
                   self.lattice [i,j].temp = max(self.tempNext[i,j] + self.tempChange[i,j], 50)
             
            self.gasLaw()
            
#            self.wallVelo()
            #periodic time step decrease
            if(t % 500 == 0):
                plt.clf()
#                sns.heatmap(self.vx)
#                plt.pause(2)
#                plt.clf()
#                sns.heatmap(self.accelx)
                sns.heatmap(self.presTemp)
                plt.pause(0.1)
                print t

            
#            we should dissipate some energy along the walls 
            for j in range(self.width):
                self.lattice[2,j].vx = self.lattice[2,j].vx * ExplosionSim.ENERGYFACTOR
                self.lattice[j,2].vx = self.lattice[j,2].vx * ExplosionSim.ENERGYFACTOR
                self.lattice[self.width - 3,j].vx = self.lattice[self.width - 3,j].vx * ExplosionSim.ENERGYFACTOR
                self.lattice[j,self.width - 3].vx = self.lattice[j,self.width - 3].vx * ExplosionSim.ENERGYFACTOR
                
                self.lattice[2,j].vy = self.lattice[2,j].vy * ExplosionSim.ENERGYFACTOR
                self.lattice[j,2].vy = self.lattice[j,2].vy * ExplosionSim.ENERGYFACTOR
                self.lattice[self.width - 3,j].vy = self.lattice[self.width - 3,j].vy * ExplosionSim.ENERGYFACTOR
                self.lattice[j,self.width - 3].vy = self.lattice[j,self.width - 3].vy * ExplosionSim.ENERGYFACTOR
                
                self.lattice[2,j].temp = self.lattice[2,j].temp - (self.lattice[2,j].temp - ExplosionSim.TAMBIENT) * (1.0 - ExplosionSim.ENERGYFACTOR)
                self.lattice[j,2].temp = self.lattice[j,2].temp - (self.lattice[j,2].temp - ExplosionSim.TAMBIENT) * (1.0 - ExplosionSim.ENERGYFACTOR)
                self.lattice[self.width - 3,j].temp = self.lattice[self.width - 3,j].temp - (self.lattice[self.width - 3,j].temp - ExplosionSim.TAMBIENT) * (1.0 - ExplosionSim.ENERGYFACTOR)
                self.lattice[j,self.width - 3].temp = self.lattice[j,self.width - 3].temp - (self.lattice[j,self.width - 3].temp - ExplosionSim.TAMBIENT) * (1.0 - ExplosionSim.ENERGYFACTOR)

                for i in range(self.width):
                    self.lattice[i,j].vx = self.lattice[i,j].vx * 0.99999
                    self.lattice[i,j].vy = self.lattice[i,j].vy * 0.99999
                    
                
            for j in range(self.width):
                for k in range(self.width):
                    self.finalMatrix[t,j,k, 0] = self.lattice[j,k].vx
                    self.finalMatrix[t,j,k, 1] = self.lattice[j,k].vy
                    self.finalMatrix[t,j,k, 2] = self.lattice[j,k].temp
                    self.finalMatrix[t,j,k, 3] = self.lattice[j,k].dens
                    self.finalMatrix[t,j,k, 4] = self.lattice[j,k].pres
            
    ####################
    
    

        
    
    
    #######
    def approxAccel(self):
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                #find dvx/dt via navier-stokes equation and finite differences
                
               
                #If I use 3rd order finite difference's it might make a difference
                self.accelx[i,j] = 1.0 / self.lattice[i,j].dens * ( -1 * (-1.0/12 * self.lattice[i+2,j].pres + 2.0/3 * self.lattice[i+1,j].pres 
                      - 2.0/3 * self.lattice[i-1,j].pres + 1.0/12 * self.lattice[i-2,j].pres)/ self.dx #first derivivitive 3rd order
                               + ExplosionSim.visc / (self.dx)**2 * (self.lattice[i+1,j].vx - 4 * self.lattice[i,j].vx + self.lattice[i-1,j].vx + self.lattice[i,j+1].vx + self.lattice[i,j-1].vx) #2nd order laplacian
                               + ExplosionSim.visc / (3 * self.dx**2) * (self.lattice[i+1,j].vx - 2 * self.lattice[i,j].vx + self.lattice[i-1,j].vx 
                               + 1.0/144 * (8.0*(self.lattice[i+1,j-2].vy + self.lattice[i+2,j-1].vy + self.lattice[i-2,j+1].vy + self.lattice[i-1,j+2].vy)
                               -8.0*(self.lattice[i-1,j-2].vy + self.lattice[i-2,j-1].vy + self.lattice[i+1,j+2].vy + self.lattice[i+2,j+1].vy)
                               -(self.lattice[i+2,j-2].vy + self.lattice[i-2,j+2].vy - self.lattice[i-2,j-2].vy - self.lattice[i+2,j+2].vy)
                               + 64.0 * (self.lattice[i+1,j+1].vy + self.lattice[i-1,j-1].vy - self.lattice[i+1,j-1].vy - self.lattice[i-1,j+1].vy))) #mixed partial
                )
                      
                self.accely[i,j] = 1.0 / self.lattice[i,j].dens * ( -1 * (-1.0/12 * self.lattice[i,j+2].pres + 2.0/3 * self.lattice[i,j+1].pres 
                      - 2.0/3 * self.lattice[i,j-1].pres + 1.0/12 * self.lattice[i,j-2].pres)/ self.dx
                               + ExplosionSim.visc / (self.dx)**2 * (self.lattice[i,j+1].vy - 4 * self.lattice[i,j].vy + self.lattice[i,j-1].vy + self.lattice[i+1,j].vy + self.lattice[i-1,j].vy)
                               + ExplosionSim.visc / (3 * self.dx**2) * (self.lattice[i,j+1].vy - 2 * self.lattice[i,j].vy + self.lattice[i,j-1].vy #2nd order 2nd derivitive
                               + 1.0/144 * (8.0*(self.lattice[i+1,j-2].vx + self.lattice[i+2,j-1].vx + self.lattice[i-2,j+1].vx + self.lattice[i-1,j+2].vx)
                               -8.0*(self.lattice[i-1,j-2].vx + self.lattice[i-2,j-1].vx + self.lattice[i+1,j+2].vx + self.lattice[i+2,j+1].vx)
                               -(self.lattice[i+2,j-2].vx + self.lattice[i-2,j+2].vx - self.lattice[i-2,j-2].vx - self.lattice[i+2,j+2].vx)
                               + 64.0*(self.lattice[i+1,j+1].vx + self.lattice[i-1,j-1].vx - self.lattice[i+1,j-1].vx - self.lattice[i-1,j+1].vx)))
                )
                      
                
    #######
    def approxVelo(self):
        #find squigle velocity and mean velocity, place into 4 matrices
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                self.vx[i,j] = self.bound(self.lattice[i,j].vx + self.accelx[i,j] * self.dt, -1 * ExplosionSim.VMAX, ExplosionSim.VMAX)
                self.vy[i,j] =  self.bound(self.lattice[i,j].vy + self.accely[i,j] * self.dt, -1 * ExplosionSim.VMAX, ExplosionSim.VMAX)
                self.vxAvg[i,j] =  self.bound(self.lattice[i,j].vx + self.accelx[i,j] * self.dt / 2.0, -1 * ExplosionSim.VMAX, ExplosionSim.VMAX)
                self.vyAvg[i,j] =  self.bound(self.lattice[i,j].vy + self.accely[i,j] * self.dt / 2.0, -1 * ExplosionSim.VMAX, ExplosionSim.VMAX)
    
    #######
    def approxTemps(self):
        # just make them smaller cause i dunno
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
        
    #            self.tempNext[i,j] = self.lattice[i,j].temp + self.dt / (cv * self.lattice[i,j].dens) * (
    #                    k * self.lattice[i,j].temp * (self.lattice[i,j+1].temp - 2 * self.lattice[i,j].temp + self.lattice[i,j-1].temp 
    #                               + self.lattice[i+1,j].temp - 2 * self.lattice[i,j].temp + self.lattice[i-1,j].temp) / (self.dx**2) 
    #                    - self.lattice[i,j].pres * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + vyAvg[i,j+1]- self.vyAvg[i,j-1]) / self.dx
    #                    + -2.0 * ExplosionSim.visc / 3 * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + self.vyAvg[i,j+1]- self.vyAvg[i,j-1]) / self.dx
    #                    + ExplosionSim.visc / 2.0 * (self.vyAvg[i+1,j]- self.vyAvg[i-1,j] + self.vxAvg[i,j+1]- self.vxAvg[i,j-1])**2 / (self.dx**2) 
    #                    )
    
    ##REGULAR
                self.tempChange[i,j] = self.dt / (ExplosionSim.cv * self.lattice[i,j].dens) * (
                        ExplosionSim.k * (self.lattice[i,j+1].temp - 2 * self.lattice[i,j].temp + self.lattice[i,j-1].temp 
                                   + self.lattice[i+1,j].temp - 2 * self.lattice[i,j].temp + self.lattice[i-1,j].temp) / (self.dx**2) 
                        - self.lattice[i,j].pres * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + self.vyAvg[i,j+1]- self.vyAvg[i,j-1]) / self.dx
                        -2.0 * ExplosionSim.visc / 3 * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + self.vyAvg[i,j+1]- self.vyAvg[i,j-1]) / self.dx
                        + ExplosionSim.visc * ((self.vyAvg[i+1,j]- self.vyAvg[i-1,j] + self.vxAvg[i,j+1]- self.vxAvg[i,j-1])/4.0)**2 / (self.dx**2) 
                        )
    
#    ##implicit
#                def equations(T):
#                    
#                    for i in range(self.width):
#                        for j in range(self.width):
#                            if(i < 2) or (j < 2) or (i > self.width - 3) or (j > self.width - 3):
#                                return 0.0
#                            else:
#                                return  -1.0 * T[i,j] +  self.dt / (ExplosionSim.cv * self.lattice[i,j].dens) * (
#                                        ExplosionSim.k * (T[i,j+1] - 2 * T[i,j] + T[i,j-1] 
#                                                   + T[i+1,j] - 2 * T[i,j] + T[i-1,j]) / (self.dx**2) 
#                                        - self.lattice[i,j].pres * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + self.vyAvg[i,j+1]- self.vyAvg[i,j-1]) / self.dx
#                                        -2.0 * ExplosionSim.visc / 3 * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + self.vyAvg[i,j+1]- self.vyAvg[i,j-1]) / self.dx
#                                        + ExplosionSim.visc * ((self.vyAvg[i+1,j]- self.vyAvg[i-1,j] + self.vxAvg[i,j+1]- self.vxAvg[i,j-1])/4.0)**2 / (self.dx**2)
#                                        )
#                            
#                self.tempChange = root(equations, np.zeros((self.width, self.width)), method = "lm")
                
        
            
     
    #######           
    def approxDensity(self):
        for i in range(2):
             for j in range(self.width):
                 self.lattice[0+i,j].dens = ExplosionSim.DENSITY
                 self.lattice[j,0+i].dens = ExplosionSim.DENSITY
                 self.lattice[self.width - 1 - i,j].dens = ExplosionSim.DENSITY
                 self.lattice[j,self.width - 1 - i].dens = ExplosionSim.DENSITY                
                 
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
    #            self.densNext[i,j] = self.lattice[i,j].dens + -1 * self.dt * self.lattice[i,j].dens * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + self.vyAvg[i,j+1] - self.vyAvg[i,j-1]) / self.dx / 2.0
                self.densChange[i,j] = -1 * self.dt * self.lattice[i,j].dens * (self.vxAvg[i+1,j]- self.vxAvg[i-1,j] + self.vyAvg[i,j+1] - self.vyAvg[i,j-1]) / self.dx / 2.0
           
    #######
    def advectDensity(self):
        # 5 loops of back and forth error elimination?? doesnt appear to work
    #    for k in range(5):
        
    
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                self.densAvg[i,j] = self.lattice[i,j].dens - self.dt * (self.vxAvg[i,j] * (-1.0/12 *self.lattice[i+2,j].dens + 2.0/3 * self.lattice[i+1,j].dens 
                       - 2.0/3 * self.lattice[i-1,j].dens + 1.0/12 * self.lattice[i-2,j].dens)/ self.dx 
                       + self.vyAvg[i,j] * (-1.0/12 *self.lattice[i,j+2].dens + 2.0/3 *self.lattice[i,j+1].dens 
                              - 2.0/3 * self.lattice[i,j-1].dens + 1.0/12 * self.lattice[i,j-2].dens)/ self.dx)
                
                ###ADVECTION SUCKS :(
    #            densHat[i,j] = densAvg[i,j] + self.dt * (self.vxAvg[i,j] * (densAvg[i+1,j] - densAvg[i-1,j])/ self.dx / 2.0 
    #                   + self.vyAvg[i,j] * (densAvg[i,j+1] - densAvg[i,j-1])/ self.dx / 2.0)
    #            densBar[i,j] = 3.0 / 2 * densAvg[i,j] - 0.5 * densHat[i,j]
    #            self.densNext[i,j] = self.lattice[i,j].dens - self.dt * (self.vxAvg[i,j] * (densBar[i+1,j] - densBar[i-1,j])/ self.dx / 2.0 
    #                   + self.vyAvg[i,j] * (densBar[i,j+1] - densBar[i,j-1])/ self.dx / 2.0)
        for i in range( self.width):
            for j in range(self.width):
                self.densNext[i,j] = self.densAvg[i,j]
    #               self.lattice [i,j].dens = self.densNext[i,j]   
        for i in range(2):
             for j in range(self.width):
                 self.lattice[0+i,j].dens = ExplosionSim.STEELDENS
                 self.lattice[j,0+i].dens = ExplosionSim.STEELDENS
                 self.lattice[self.width - 1 - i,j].dens = ExplosionSim.STEELDENS
                 self.lattice[j,self.width - 1 - i].dens = ExplosionSim.STEELDENS
                
    def advectVelo(self):
        
        #TRY to do self.vx, self.vy seperately
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                
                #3RD ORDER
                self.vxAvgADV[i,j] = self.vx[i,j] - self.dt * (self.vxAvg[i,j] * (-1.0/12 *self.vx[i+2,j] + 2.0/3 *self.vx[i+1,j] - 2.0/3 * self.vx[i-1,j] + 1.0/12 * self.vx[i-2,j])/ self.dx 
                       + self.vyAvg[i,j] * (-1.0/12 *self.vx[i,j+2] + 2.0/3 *self.vx[i,j+1] - 2.0/3 * self.vx[i,j-1] + 1.0/12 * self.vx[i,j-2])/ self.dx)
                ####This is the problem line
                ####IMPROVE ALGORITHM TO CONVECT
    #            self.vxHat[i,j] = self.vxAvgADV[i,j] + self.dt * (self.vxAvg[i,j] * (self.vxAvgADV[i+1,j] - self.vxAvgADV[i-1,j])/ self.dx / 2.0 
    #                   + self.vyAvg[i,j] * (self.vxAvgADV[i,j+1] - self.vxAvgADV[i,j-1])/ self.dx / 2.0)
    #            self.vxBar[i,j] = 3.0 / 2 * self.vxAvgADV[i,j] - 0.5 * self.vxHat[i,j]
    #            self.vxTemp[i,j] = self.vxBar[i,j] - self.dt * (self.vxAvg[i,j] * (self.vxBar[i+1,j] - self.vxBar[i-1,j])/ self.dx / 2.0 
    #                   + self.vyAvg[i,j] * (self.vxBar[i,j+1] - self.vxBar[i,j-1])/ self.dx / 2.0)
                
                
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                ####IMPROVE   
    #            self.lattice [i,j].vx = vxTemp[i,j] 
                self.lattice[i,j].vx = self.vxAvgADV[i,j]
                
        ##self.vy
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                
                #3RD ORDER
                self.vyAvgADV[i,j] = self.vy[i,j] - self.dt * (self.vxAvg[i,j] * (-1.0/12 *self.vy[i+2,j] + 2.0/3 *self.vy[i+1,j] - 2.0/3 * self.vy[i-1,j] + 1.0/12 * self.vy[i-2,j])/ self.dx 
                       + self.vyAvg[i,j] * (-1.0/12 *self.vy[i,j+2] + 2.0/3 *self.vy[i,j+1] - 2.0/3 * self.vy[i,j-1] + 1.0/12 * self.vy[i,j-2])/ self.dx)
                
                ######IMPROVE
    #            self.vyHat[i,j] = self.vy[i,j] + self.dt * (self.vxAvg[i,j] * (self.vy[i+1,j] - self.vy[i-1,j])/ self.dx / 2.0 
    #                   + self.vyAvg[i,j] * (self.vy[i,j+1] - self.vy[i,j-1]) / self.dx / 2.0)
                
                #using self.vyavg
    #            self.vyHat[i,j] = self.vyAvgADV[i,j] + self.dt * (self.vxAvg[i,j] * (self.vyAvgADV[i+1,j] - self.vyAvgADV[i-1,j])/ self.dx / 2.0 
    #                   + self.vyAvg[i,j] * (self.vyAvgADV[i,j+1] - self.vyAvgADV[i,j-1])/ self.dx / 2.0)
    #            self.vyBar[i,j] = 3.0 / 2 * self.vyAvgADV[i,j] - 0.5 * self.vyHat[i,j]
                
                #commented out until a better advection algorithm can be developed
    #            self.vyBar[i,j] = self.vy[i,j] + 0.5 * (self.vyAvgADV[i,j] - self.vyHat[i,j])
    #            self.vyTemp[i,j] = self.vyBar[i,j] - self.dt * (self.vxAvg[i,j] * (self.vyBar[i+1,j] - self.vyBar[i-1,j])/ self.dx / 2.0 
    #                   + self.vyAvg[i,j] * (self.vyBar[i,j+1] - self.vyBar[i,j-1])/ self.dx / 2.0)
                
                
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                ####commented until better algorithm
    #               self.lattice [i,j].vy = self.vyTemp[i,j] 
                self.lattice[i,j].vy = self.vyAvgADV[i,j]
        
    def advectTemp(self):
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                self.tempNext[i,j] = self.lattice[i,j].temp - self.dt * (self.vxAvg[i,j] * (-1.0/12 *self.lattice[i+2,j].temp + 2.0/3 *self.lattice[i+1,j].temp 
                        - 2.0/3 * self.lattice[i-1,j].temp + 1.0/12 * self.lattice[i-2,j].temp)/ self.dx 
                       + self.vyAvg[i,j] * (-1.0/12 *self.lattice[i,j+2].temp + 2.0/3 *self.lattice[i,j+1].temp 
                              - 2.0/3 * self.lattice[i,j-1].temp + 1.0/12 * self.lattice[i,j-2].temp)/ self.dx)
                
                
    def gasLaw(self):
        for i in range(2, self.width - 2):
            for j in range(2, self.width - 2):
                self.presTemp[i,j] = self.lattice[i,j].dens * ExplosionSim.R * self.lattice[i,j].temp
        for i in range(1,self.width-1):
            for j in range(self.width):
                self.lattice[i,j].pres = self.bound(self.presTemp[i,j], -0.2 * ExplosionSim.PRESMAX, ExplosionSim.PRESMAX)
                
    ## Will it work if I just do this at the end?? 
    def wallVelo(self):
        
        ##top wall
        for i in range(self.width):
            self.lattice[i,self.width - 3].vx = ExplosionSim.ENERGYFACTOR * self.lattice[i,self.width - 3].vx
            if (self.lattice[i,self.width - 3].vy > 0) :
                self.lattice[i,self.width - 3].vy = -1 * ExplosionSim.ENERGYFACTOR * self.lattice[i,self.width - 3].vy
            else:
                self.lattice[i,self.width - 3].vy = ExplosionSim.ENERGYFACTOR * self.lattice[i,self.width - 3].vy
        
        ##left wall
        for i in range(self.width):
            self.lattice[2,i].vy =  ExplosionSim.ENERGYFACTOR * self.lattice[2,i].vy
            if (self.lattice[2,i].vx < 0) :
                self.lattice[2,i].vx = -1 * ExplosionSim.ENERGYFACTOR * self.lattice[2,i].vx
            else:
                self.lattice[2,i].vx = ExplosionSim.ENERGYFACTOR * self.lattice[2,i].vx
        ##bottom wall
        for i in range(self.width):
            self.lattice[i,2].vx = ExplosionSim.ENERGYFACTOR * self.lattice[i,2].vx
            if (self.lattice[i,2].vy < 0) :
                self.lattice[i,2].vy = -1 * ExplosionSim.ENERGYFACTOR * self.lattice[i,2].vy
            else:
                self.lattice[i,2].vy = ExplosionSim.ENERGYFACTOR * self.lattice[i,2].vy
        ##right wall
        for i in range(self.width):
            self.lattice[self.width-3,i].vy = ExplosionSim.ENERGYFACTOR * self.lattice[self.width-3,i].vy
            if (self.lattice[self.width-3,i].vx > 0) :
                self.lattice[self.width-3,i].vx = -1 * ExplosionSim.ENERGYFACTOR * self.lattice[self.width-3,i].vx
            else:
                self.lattice[self.width-3,i].vx = ExplosionSim.ENERGYFACTOR * self.lattice[self.width-3,i].vx
                
    def bound(self, val, lower, upper):
        if val < lower:
            val = lower
        if val > upper:
            val = upper
        return val
        
    

