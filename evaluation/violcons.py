# -*- coding: utf-8 -*-
"""
Routine to find violated constraints. (Paths have to be adjusted manually!)
"""

import gurobipy as gp
import robustformulation as mr
import time
import pandas as pd


gamma, cHat = mr.readInstance('C:/Users/User/Documents/Masterarbeit/data/opm2-z6-s1_g=100_d=45-55_r=0.txt')
dHat=cHat
m4 = gp.read('C:/Users/User/Documents/Masterarbeit/opm2-z6-s1.mps')
  
m5=m4.copy()
cHat, pvalues, z =mr.RobustFormulation(m4, gamma, False, "coverpartition", cHat)

t1=time.time()
mr.ExtendCover(m5, gamma, cHat)
t1=time.time()-t1

g4=m4.relax()
g5=m5.relax()
g4.optimize()
t2=time.time()
g5.optimize()
t2=time.time()-t2
print(g4.ObjVal)
print(g5.ObjVal)   
# df1=pd.DataFrame(columns=['LHS', 'RHS', 'Sense', 'NbrVars', 'NbrVarsNonzero', 'Difference p'])
# cons=g5.getConstrs()
# violcons=[]
# for con in cons:
#     c=g5.getRow(con)
#     expr1=0
#     expr2=0
#     expr3=0
#     k=0
#     for t in range(0,c.size()):
#         var=c.getVar(t)
#         coff=c.getCoeff(t)
#         if var.VarName[0]=='p' or var.VarName[0]=='p':
#             expr2+=coff*var.x
#             expr3+=g4.getVarByName(var.VarName).x
                        
#         if g4.getVarByName(var.VarName).x > 0.0001:
#             k+=1
#         expr1+=coff*g4.getVarByName(var.VarName).x
#     if con.sense == '<':
#         if expr1 - con.RHS > 0.00001:
#             violcons.append(c)
#             df1.loc[len(df1)] = [expr1,con.RHS,con.sense, c.size(), k, expr2-expr3]
#     else:
#         if expr1 - con.RHS < -0.00001 :
#             violcons.append(c)
#             df1.loc[len(df1)] = [expr1,con.RHS,con.sense, c.size(), k, expr2-expr3]

# df1.to_csv('C:/Users/User/Documents/Masterarbeit/Tables/cons_air03_40_45.csv')
