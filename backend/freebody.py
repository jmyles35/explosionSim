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
        self.startPoint = startPoint
        self.yveloc     = 0.0
        self.xveloc     = 0.0
        self.omega      = 0.0
        self.xaccel     = 0.0
        self.yaccel     = 0.0
        self.omegaDot   = 0.0
        self.density    = density


        self.xlen,self.ylen=self.S.shape
        weight=0.0
        ColumnSum=np.sum(S,axis=0)
        Sum=np.sum(S)
        for i in range(0,xlen):
            weight=weight+i*ColumnSum[0,i]
        self.xCOM=weight/Sum

        weight=0.0
        RowSum=np.sum(S,axis=1)
        for i in range(0,xlen):
            weight=weight+i*RowSum[i,0]
        self.yCOM=weight/Sum

        weight=0.0
        RowSum=np.sum(S,axis=1)
        for i in range(0,xlen):
            weight=weight+RowSum[i,0]
        self.mass=self.density*weight

        weight=0.0
        for i in range(0,xlen):
            for j in range(0,ylen):
                weight=weight+(pow(i-self.xCOM,2)+pow(j-self.yCOM,2))*xdim/xlan*ydim/ylen
        self.inertia=self.density*weight

    def getCOM(self):
        """
        returns the current center of mass on the screen, NOT the true center
        of mass which is tracked via the self.xCOM and self.yCOM
        """

        ColumnSum=np.sum(S,axis=0)
        Sum=np.sum(S)
        weight=0.0
        for i in range(0,xlen):
            weight=weight+i*ColumnSum[0,i]
        xCOM=weight/Sum

        weight=0.0
        RowSum=np.sum(S,axis=1)
        for i in range(0,xlen):
            weight=weight+i*RowSum[i,0]
        weight/Sum

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
        for i in range(0,xlen):
            for j in range(0,ylen):
                if self.S[j,i]==1:
                    neighbours=getNeighbours(i,j)

                    if neighbours(7)==1:

                        if neighbours(8)==0 and neighbours(1)==0:
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                        if neighbours(6)==0 and neighbours(5)==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                    if neighbours(8)==1:

                        if neighbours(7)==0:
                            Fy=Fy+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            T=T-explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours(1)==0:
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                    if neighbours(1)==1:

                        if (neighbours(7)==0 and neighbours(8)==0):
                            Fx=Fx+explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                        if (neighbours(2)==0 and neighbours(3)==0):
                            Fx=Fx+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                    if neighbours(2)==1:

                        if neighbours(3)==0:
                            Fy=Fy+explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2

                            T=T-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours(1)==0:
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j+1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                    if neighbours(3)==1:

                        if (neighbours(2)==0 and neighbours(1)==0):
                            Fy=Fy-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j+1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                        if neighbours(4)==0 and neighbours(5)==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*self.xdim/self.xlen/2*(i-self.xCOM)

                    if neighbours(4)==1:

                        if neighbours(3)==0:
                            Fy=Fy-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2

                            T=T-explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours(5)==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                    if neighbours(5)==1:

                        if (neighbours(7)==0 and neighbours(6)==0):
                            Fx=Fx+explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2
                            T=T-explosionMatrix[timestep,j,i-1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                        if (neighbours(4)==0 and neighbours(3)==0):
                            Fx=Fx+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2
                            T=T+explosionMatrix[timestep,j,i+1,4]*self.xdim/self.xlen/2*(j-self.yCOM)

                    if neighbours(4)==1:

                        if neighbours(3)==0:
                            Fy=Fy-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx-explosionMatrix[timestep,j,i+1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2

                            T=T-explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)+explosionMatrix[timestep,j,i-1,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                        if neighbours(5)==0:
                            Fy=Fy+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            Fx=Fx+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2
                            T=T+explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(i-self.Xcom)-explosionMatrix[timestep,j-1,i,4]*sqrt(2)*xdim/xlen*sqrt(2)/2*(j-self.yCOM)

                self.xaccel=Fx/self.mass
                self.yaccel=Fy/self.mass
                self.omegaDot=T/self.Inertia
                yCOMOld,XCOMOld=self.getCOM()
                self.xCOM=(self.xCOM*xdim/xlen+self.xveloc*dt)/(xdim/xlen)
                self.yCOM=(self.yCOM*xdim/xlen+self.yveloc*dt)xdim/xlen
                self.xveloc=self.xveloc+self.xaccel*dt
                self.yveloc=self.yveloc+self.yaccel*dt



    def getNeighbours(self, x, y):
        """
        Returns the neighbors (8 verticies) nearest to a point
        """
       return [0,self.S[y+1,x],self.S[y+1,x+1],self.S[y,x+1],self.S[y-1,x+1],self.S[y-1,x],self.S[y-1,x-1],self.S[y,x-1],self.S[y+1,x-1],]


     def rotate(self,theta,xCOM,yCOM, fill=0):
         theta=theta
         sh, sw = self.S.shape
         cx, cy = rotate_coords([0, sw, sw, 0], [0, 0, sh, sh], theta, xCOM, yCOM)
         dw, dh= sw, sh
         dx, dy = np.meshgrid(np.arange(dw), np.arange(dh))
         sx, sy = rotate_coords(dx + cx.min(), dy + cy.min(), -theta, ox, oy)
         sx, sy = sx.round().astype(int), sy.round().astype(int)
         mask = (0 <= sx) & (sx < sw) & (0 <= sy) & (sy < sh)
         dest = np.empty(shape=(dh, dw), dtype=src.dtype)dest
         dest[dy[mask], dx[mask]] = src[sy[mask], sx[mask]]
         dest[dy[~mask], dx[~mask]] = fill
         self.S=dest


     def rotate_coords(x, y, theta, ox, oy):
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
