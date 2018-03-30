#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 15:05:33 2018

@author: Marian
"""

import numpy as np
import pandas as pd
from ExplosionSim import ExplosionSim

from scipy import stats, integrate
import matplotlib.pyplot as plt

import seaborn as sns; sns.set()

explosion = ExplosionSim(0.0000002, 0.15, 12, 0.00002)




