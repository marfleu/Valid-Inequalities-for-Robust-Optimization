# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 21:48:58 2021

@author: mariu
"""

import gurobipy as gp
from gurobipy import GRB
import modelreading as mr
import time
import os
import fnmatch
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

gamma, cHat = mr.readInstance('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/tbfp-network_g=40_d=45-55_r=0.txt')
dHat=cHat
m4 = gp.read('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/tbfp-network.mps')

m6=m4.copy()
m5=m4.copy()


t0=time.time()

t0=time.time()-t0

t1=time.time()
cHat, pvalues, z =mr.RobustFormulation(m4, gamma, False, "none", cHat)
ps={}
for var in pvalues:
    ps[var]=pvalues[var].VarName
mr.addKnapsack(m4, gamma, z.VarName, ps, cHat)
t1=time.time()-t1

cHat, pvalues, z =mr.RobustFormulation(m5, gamma, False, "default", cHat)
g4=m4.relax()
g5=m5.relax()
t3=time.time()
g4.optimize()
t3= time.time()-t3
t2=time.time()
g5.optimize()
t2=time.time()-t2
print('Default ObJ:\n\n', g5.ObjVal)
print('Default Modeltime:\n\n', t2)
print('Knapsack ObJ:\n\n', g4.ObjVal)
print('Knapsack Modeltime:\n\n', t3)
print('Quotient:\n\n', t3/t2)