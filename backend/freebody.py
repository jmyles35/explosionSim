#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 18:03:02 2018

@author: Coleman
"""
import numpy as np
from numpy import matrix, linalg


class Freebody:
    """
    S=np.matrix([[1,0,0],[0,0,1],[0,1,1]])
    SP=0,0
    """

    def __init__(self, S, xdim, ydim, density ):
        """
        This is the initialization/constructor function
        for the Freebody function
        """

        # Initilize the attributes of the object
        self.S          = S
        self.xdim       = xdim
        self.ydim       = ydim
        self.yveloc     = 0.0
        self.xveloc     = 0.0
        self.omega      = 0.0
        self.xaccel     = 0.0
        self.yaccel     = 0.0
        self.omegaDot   = 0.0
        self.density    = density


        (self.xlen,self.ylen)=self.S.shape
        "print (self.xlen)"
        weight=0.0
        ColumnSum=np.sum(self.S,axis=0)
        "print(ColumnSum)"
        Sum=np.sum(self.S)
        for i in range(0,self.xlen):
            "print(i)"
            weight=weight+i*ColumnSum[i]
        self.xCOM=weight/Sum

        weight=0.0
        RowSum=np.sum(self.S,axis=1)
        for i in range(0,self.xlen):
            weight=weight+i*RowSum[i]
        self.yCOM=weight/Sum
        
        self.xCOMOld=self.xCOM
        self.yCOMOld=self.yCOM

        weight=0.0
        RowSum=np.sum(self.S,axis=1)
        for i in range(0,self.xlen):
            weight=weight+RowSum[i]
        self.mass=self.density*weight

        weight=0.0
        for i in range(0,self.xlen):
            for j in range(0,self.ylen):
                weight=weight+(pow(i-self.xCOM,2)+pow(j-self.yCOM,2))*self.xdim/self.xlen*self.ydim/self.ylen
        self.inertia=self.density*weight

    def getCOM(self):
        """
        returns the current center of mass on the screen, NOT the true center
        of mass which is tracked via the self.xCOM and self.yCOM
        """

        ColumnSum=np.sum(self.S,axis=0)
        Sum=np.sum(self.S)
        weight=0.0
        for i in range(0,self.xlen):
            weight=weight+i*ColumnSum[i]
        xCOM=weight/Sum

        weight=0.0
        RowSum=np.sum(self.S,axis=1)
        for i in range(0,self.xlen):
            weight=weight+i*RowSum[i]
        yCOM=weight/Sum

        return yCOM,xCOM


    def update(self, timestep, explosionMatrix, dt):
        """
        updating all the values of the object: vel, ang vel, positions
        Checks all of the neighbors of a point and determines the angle between them,
        straight up, 45, 90
        Looks around the angle, more object, or empty space with Pressure
        Computes force and forces on the face

        """
        Fx=0
        Fy=0
        T=0
        
        self.checkwalls()
        for i in range(0+1,self.xlen-1):
            for j in range(0+1,self.ylen-1):
                if self.S[j,i]==1:
                    neighbours=self.getNeighbours(i,j)

                    if neighbours[7]==1:

                        if neighbours[8]==0 and neighbours[1]==0:
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                        if neighbours[6]==0 and neighbours[5]==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                    if neighbours[8]==1:

                        if neighbours[7]==0:
                            Fy=Fy+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            T=T-explosionMatrix[timestep,j,i-1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours[1]==0:
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(j-self.yCOM)

                    if neighbours[1]==1:

                        if (neighbours[7]==0 and neighbours[8]==0):
                            Fx=Fx+explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                        if (neighbours[2]==0 and neighbours[3]==0):
                            Fx=Fx+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                    if neighbours[2]==1:

                        if neighbours[3]==0:
                            Fy=Fy+explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2

                            T=T-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours[1]==0:
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(j-self.yCOM)

                    if neighbours[3]==1:

                        if (neighbours[2]==0 and neighbours[1]==0):
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                        if neighbours[4]==0 and neighbours[5]==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                    if neighbours[4]==1:

                        if neighbours[3]==0:
                            Fy=Fy-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2

                            T=T-explosionMatrix[timestep,j,i-1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours[5]==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(j-self.yCOM)

                    if neighbours[5]==1:

                        if (neighbours[7]==0 and neighbours[6]==0):
                            Fx=Fx+explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                        if (neighbours[4]==0 and neighbours[3]==0):
                            Fx=Fx+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                    if neighbours[6]==1:

                        if neighbours[5]==0:
                            Fy=Fy-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2

                            T=T-explosionMatrix[timestep,j,i-1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours[7]==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j-1,i,4]*sqrt(2)*self.xdim/self.xlen*sqrt(2)/2*(j-self.yCOM)

        self.xaccel=Fx/self.mass
        self.yaccel=Fy/self.mass
        self.omegaDot=T/self.inertia
        "print(self.S)"
        (self.yCOMOld,self.xCOMOld)=self.getCOM()
        self.xCOM=(self.xCOM*self.xdim/self.xlen+self.xveloc*dt)/(self.xdim/self.xlen)
        self.yCOM=(self.yCOM*self.xdim/self.xlen+self.yveloc*dt)/(self.xdim/self.xlen)
        self.xveloc=self.xveloc+self.xaccel*dt
        self.yveloc=self.yveloc+self.yaccel*dt
        self.rotate(self.omega*dt,self.xCOMOld,self.yCOMOld)
        self.omega=self.omega+self.omegaDot*dt
        

        if (self.xCOM-self.xCOMOld)>1:
            print("moveright")
            i=self.xlen-1
            while i>0:
                self.S[:,i]=self.S[:,i-1]
                i=i-1
                
            self.S[:,self.xlen-1]=np.zeros((self.xlen))
        if (self.xCOM-self.xCOMOld)<-1:
            print("moveleft")
            for i in range(1,self.xlen-1):
                self.S[:,i]=self.S[:,i+1]
            self.S[:,0]=np.zeros((self.xlen))
            
        if (self.yCOM-self.yCOMOld)>1:
            for i in range(1,self.xlen-1):
                self.S[i,:]=self.S[i-1,:]
            self.S[self.xlen-1,:]=np.zeros((self.xlen))
        if (self.yCOM-self.yCOMOld)<-1:
            for i in range(1,self.xlen-1):
                self.S[i,:]=self.S[i+1,:]
            self.S[0,:]=np.zeros((self.xlen))                
                    

    def checkwalls(self):
        ColumnSum=np.sum(self.S,axis=0)
        "print(ColumnSum)"
        if ((ColumnSum[1] > 0) or ColumnSum[self.xlen-2]>0):
            self.xveloc=-0.6*self.xveloc
            print("rlwall")
        RowSum=np.sum(self.S,axis=1)
        if (RowSum[1] > 0 or RowSum[self.xlen-2]>0):
            self.yveloc=-0.6*self.yveloc
            print("udwall")

        

    def getNeighbours(self, x, y):
        """
        Returns the neighbors (8 verticies) nearest to a point
        """
        return [0,self.S[y+1,x],self.S[y+1,x+1],self.S[y,x+1],self.S[y-1,x+1],self.S[y-1,x],self.S[y-1,x-1],self.S[y,x-1],self.S[y+1,x-1],]


    def rotate(self,theta,xCOM,yCOM, fill=0):
        theta=theta
        "print(theta)"
        sh, sw = self.S.shape
        cx, cy = self.rotate_coords([0, sw, sw, 0], [0, 0, sh, sh], theta, xCOM, yCOM)
        dw, dh= sw, sh
        dx, dy = np.meshgrid(np.arange(dw), np.arange(dh))
        sx, sy = self.rotate_coords(dx + cx.min(), dy + cy.min(), -theta, xCOM, yCOM)
        sx, sy = sx.round().astype(int), sy.round().astype(int)
        mask = (0 <= sx) & (sx < sw) & (0 <= sy) & (sy < sh)
        dest = np.empty(shape=(dh, dw), dtype=int)
        dest[dy[mask], dx[mask]] = self.S[sy[mask], sx[mask]]
        dest[dy[~mask], dx[~mask]] = fill
        self.S=dest


    def rotate_coords(self,x, y, theta, ox, oy):
        """
        Rotate arrays of coordinates x and y by theta radians about the
        point (ox, oy).
        """
        s, c = np.sin(theta), np.cos(theta)
        x, y = np.asarray(x) - ox, np.asarray(y) - oy
        return x * c - y * s + ox, x * s + y * c + oy











"""
freebody takes 2 arrays of equally spaced x vaalues and y values
and the spacing between them. the values must come in pairs of 2 ex in for y we would get
the upper and lower limit of the object for a particular location in x
and in x we would get the leftmost  and right most edge for a particular y"""
