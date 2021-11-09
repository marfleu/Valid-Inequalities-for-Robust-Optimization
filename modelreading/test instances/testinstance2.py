# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 10:07:22 2021

@author: User
"""


import gurobipy as gp
from gurobipy import GRB
from modelreading import robustformulation as mr

#Create a new model

m=gp.Model('mip1')
# Create variables
x1 = m.addVar(vtype=GRB.BINARY, name="x1")
x2 = m.addVar(vtype=GRB.BINARY, name="x2")
x3 = m.addVar(vtype=GRB.BINARY, name="x3")
x4 = m.addVar(vtype=GRB.BINARY, name="x4")
x5 = m.addVar(vtype=GRB.BINARY, name="x5")
x6 = m.addVar(vtype=GRB.BINARY, name="x6")
x7 = m.addVar(vtype=GRB.BINARY, name="x7")
# Set objective
m.setObjective(-x1 - x2 - 2 * x3 + -x4 , GRB.MINIMIZE)

# # Add constraint: 
m.addConstr(x1 + x2 + x5 <= 1, "c0")
m.addConstr(x1 +2*x2 + 2*x3 + 2*x4 + x5 <= 2, "c1")
m.addConstr(x1 +x2 + x3 +2*x7 <= 2, "c2")
m.addConstr(x7+ x6 <= 1, "c3")
m.addConstr(x1+ x6 <= 1, "c3")







m.update()

#Build robust models
m1=m.copy()
m2=m.copy()
m3=m.copy()
m4=m.copy()
gamma=2
dHat={}
for var in m.getVars():
    dHat[var.VarName]=1
    
cHat, pvalues, z = mr.RobustFormulation(m, gamma, False, 'none', dHat)
mr.extendMultipleTimes(m, gamma, 1, z, pvalues, cHat)
m.optimize() 
weights={}
for v in m.getVars():
    weights[v.VarName]=v.x
cHat, pvalues, z =mr.RobustFormulation(m2, gamma, False, "none", dHat)
ps={}
for var in pvalues:
    ps[var]=pvalues[var].VarName
mr.addKnapsack(m2, gamma, z.VarName, ps, dHat)
cHat, pvalues, z =mr.RobustFormulation(m3, gamma, True, "default", dHat)
cHat, pvalues, z =mr.RobustFormulation(m1, gamma, False, "coverpartition", dHat)
cHat, pvalues, z =mr.RobustFormulation(m4, gamma, False, "cover", dHat)
#Relax
g=m.relax()
g1=m1.relax()
g2=m2.relax()
g3=m3.relax()
g4=m4.relax()
#Optimize
m1.optimize()
m2.optimize()
m3.optimize()
m4.optimize()
g.optimize()
g1.optimize()
g2.optimize()
g3.optimize()
g4.optimize()
print('Objective Value model 0: ',m.ObjVal)
print('Objective Value model 1: ',m1.ObjVal)
print('Objective Value model 2: ',m2.ObjVal)
print('Objective Value model 3: ',m3.ObjVal)
print('Objective Value model 4: ',m4.ObjVal)
print('Objective Value relaxed model 0: ',g.ObjVal)
print('Objective Value relaxed model 1: ',g1.ObjVal)
print('Objective Value relaxed model 2: ',g2.ObjVal)
print('Objective Value relaxed model 3: ',g3.ObjVal)
print('Objective Value relaxed model 4: ',g4.ObjVal)