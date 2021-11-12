# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 09:22:26 2021

@author: mariu
Test Instance for the robust recycling methods. Mainly used to test the structure of the cliques and recycled Knapsack 
constraints.
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
x8 = m.addVar(vtype=GRB.BINARY, name="x8")
x9 = m.addVar(vtype=GRB.BINARY, name="x9")
x10 = m.addVar(vtype=GRB.BINARY, name="x10")
x11 = m.addVar(vtype=GRB.BINARY, name="x11")
x12 = m.addVar(vtype=GRB.BINARY, name="x12")
x13 = m.addVar(vtype=GRB.BINARY, name="x13")
x14 = m.addVar(vtype=GRB.BINARY, name="x14")
x15 = m.addVar(vtype=GRB.BINARY, name="x15")
x16 = m.addVar(vtype=GRB.BINARY, name="x16")
x17 = m.addVar(vtype=GRB.BINARY, name="x17")
x18 = m.addVar(vtype=GRB.BINARY, name="x18")
x19 = m.addVar(vtype=GRB.BINARY, name="x19")
x20 = m.addVar(vtype=GRB.BINARY, name="x20")
x21 = m.addVar(vtype=GRB.BINARY, name="x21")
x22 = m.addVar(vtype=GRB.BINARY, name="x22")
# Set objective
m.setObjective(-x1 - x2 - 2 * x3 + -x4 -3* x5 - 2 * x6 - x13 + x15 -x16, GRB.MINIMIZE)

# # Add constraint: 
m.addConstr(x1 + x2 + x3 <= 1, "c0")
m.addConstr(x4 + x5 + x6 <= 1, "c1")
m.addConstr(x1 + 2*x5 + 3*x6 <= 3, "c13")
m.addConstr(x1 + x2 + x4 <= 1, "c14")
m.addConstr(x2 + x3 + x5 <= 1, "c15")
m.addConstr(x2 + x3 + x6 <= 1, "c16")
m.addConstr(x4 + 2*x3 <= 2, "c17")
m.addConstr(x6 + x7 + x8 <= 1, "c2")
m.addConstr(x9 + x7 + x8 <= 1, "c3")
m.addConstr(x10 + 2*x11 + 2*x12+ x1 <= 2, "c4")
m.addConstr(x13 + x2 + x3 - x15 <= 1, "c5")
m.addConstr( x2 + x5 <= 1, "c6")
m.addConstr( x4 + x3 +x5 <= 1, "c7")
m.addConstr( x4 + x3 >= 1, "c8")
m.addConstr( x17 + x18 + x19 == 2, "c9")
m.addConstr( x17 + x18 - x20 - 2*x21 <= 1, "c10")
m.addConstr( 2*x17 + x18 + x19 + 3*x20+ 4*x21 + 3*x16 + 5*x9 <= 6, "c11")
m.addConstr( x4 - x18 - x19 <= 2, "c12")





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

#evaluate constraints:
for con in m4.getConstrs():
    print(m4.getRow(con));