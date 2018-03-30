#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 17:01:09 2018

@author: Marian
"""


import numpy as np
import pandas as pd

from scipy import stats, integrate
import matplotlib.pyplot as plt
import seaborn as sns



class GridBox:
   def __init__(self, vx, vy, temp, dens, pres):
      self.vx = vx
      self.vy = vy
      self.temp= temp
      self.dens = dens
      self.pres = pres
