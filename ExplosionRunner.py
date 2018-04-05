#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 15:05:33 2018

@author: Marian
"""

import numpy as np
import pandas as pd
from ExplosionSim import ExplosionSim
import json

from scipy import stats, integrate
import matplotlib.pyplot as plt

import seaborn as sns; sns.set()

explosion = ExplosionSim(0.0000002, 0.5, 32, 0.0024, 1)

mat = explosion.finalMatrix

params = ["T", "p", "P"]

shape = mat.shape
data = {str(t): {str(x): {str(y): dict(zip(params, mat[t][x][y])) for y in range(shape[2])} for x in range(shape[1])} for t in range(shape[0])}

with open('data1bomb_02us_2_4ms_30GPaDAMP1.json', 'w') as outfile:
    json.dump(data, outfile)


