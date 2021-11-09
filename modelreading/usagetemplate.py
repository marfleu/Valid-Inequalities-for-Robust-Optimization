# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 22:50:31 2021

@author: Marius Fleuster

This is a usage template of how to use the python methods from modelreading. 
Deviating from this routine is strongly disencouraged!
"""
import gurobipy as gp
from modelreading import modelreading as mr

####### reading the instance values from files ##########
file2='C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/mod010_g=40_d=95-105_r=0.txt'
file='C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/mod010.mps'
gamma, cHat = mr.readInstance(file2)
m = gp.read(file)

m1=m.copy()
m2=m.copy()
m3=m.copy()
m4=m.copy()
m5=m.copy()
m6=m.copy()
m7=m.copy()


#######  original robust formulation ##########
cHat, pvalues, z = mr.RobustFormulation(m, gamma, False, "none", cHat)
g=m.relax()


#######  default robust formulation with variable reduction ##########
cHat, pvalues, z = mr.RobustFormulation(m1, gamma, True, "default", cHat)
g1=m1.relax()


#######  default robust formulation without variable reduction ##########
cHat, pvalues, z = mr.RobustFormulation(m2, gamma, False, "default", cHat)
g2=m2.relax()


#######  extend a robust formulation one time with separated Conflict Graph (ext1) ##########
val=mr.extendMultipleTimes(m3, gamma, 1, 'z',{}, cHat)
#this is already relaxed and solved within the method


#######  Clique Cover Reformulation (cover) ##########
cHat, pvalues, z = mr.RobustFormulation(m4, gamma, False, "cover", cHat)
g4=m4.relax()


#######  Clique Partition Reformulation based on cover (coverpart) ##########
cHat, pvalues, z = mr.RobustFormulation(m5, gamma, False, "coverpartition", cHat)
g5=m5.relax()


#######  extend Clique Cover Reformulation by normal robust inequalities (coverext) ##########
mr.ExtendCover(m6, gamma, cHat)
g6=m6.relax()


#######  extend original by recycled Knapsack inequalities ##########
cHat, pvalues, z =mr.RobustFormulation(m7, gamma, False, "none", cHat)
ps={}
for var in pvalues:
    ps[var]=pvalues[var].VarName
mr.addKnapsack(m7, gamma, z.VarName, ps, cHat)
g7=m7.relax()


####### optimize the relaxed instances ##########
obj=g.optimize()
#and so on...