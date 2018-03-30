# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 18:03:02 2018

@author: Coleman
"""
import numpy as np

from numpy import matrix
from numpy import linalg


class freebody(S, xdim, ydim,StartPoint ):"
    """
    S=np.matrix([[1,0,0],[0,0,1],[0,1,1]])
    SP=0,0
    """
        
    xlen,ylen=S.shape
    weight=0
    ColumnSum=np.sum(S,axis=0)
    Sum=np.sum(S)
    weight=0
    for i in range(0,xlen):
        weight=weight+i*ColumnSum[0,i]
    xCOM=weight/Sum
    
    weight=0
    RowSum=np.sum(S,axis=1)
    for i in range(0,xlen):
        weight=weight+i*RowSum[i,0]
    yCOM=weight/Sum
    
    def update (timstep, explosionMatrix, )




               
               

"""
freebody takes 2 arrays of equally spaced x vaalues and y values"
and the spacing between them. the values must come in pairs of 2 ex in for y we would get 
the upper and lower limit of the object for a particular location in x 
and in x we would get the leftmost  and right most edge for a particular y"""


                 
        
        
        
     
     
    
    