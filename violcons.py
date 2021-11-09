# -*- coding: utf-8 -*-
"""
Routine to find violated constraints. (Paths have to be adjusted manually!)
"""

import gurobipy as gp
import modelreading as mr
import time
import pandas as pd


gamma, cHat = mr.readInstance('C:/Users/User/Documents/Masterarbeit/data/air03_g=40_d=45-55_r=0.txt')
dHat=cHat
m4 = gp.read('C:/Users/User/Documents/Masterarbeit/air03.mps')
# # #     m5 = m4.copy()
# #     originvars=[y.VarName for y in m4.getVars()]   
m5=m4.copy()
cHat, pvalues, z =mr.RobustFormulation(m4, gamma, False, "none", cHat)
#m5=m4.copy()
# #     #val=extendMultipleTimes(m5, gamma, 3, 'z', {} , cHat)
#     #print('Länge von p:', len(pvalues))
t1=time.time()
cHat, pvalues, z =mr.RobustFormulation(m5, gamma, True, "dsatur", cHat)
t1=time.time()-t1
#     #extendMultipleTimes(m4, gamma, 3, 'z', {}, cHat)
# ps={}
# for var in pvalues:
#     ps[var]=pvalues[var].VarName
# mr.addKnapsack(m5, gamma, z.VarName, ps, cHat)
# # #     #violcons, m=ExtendCover(m5, gamma, cHat)
# # #    cHat, pvalues, z =RobustFormulation(m5, gamma, False, "coverpartition", cHat)
g4=m4.relax()
g5=m5.relax()
g4.optimize()
t2=time.time()
g5.optimize()
t2=time.time()-t2
#Difference p's capture the inequality's difference z+sum_Q pq for both solutions    
df1=pd.DataFrame(columns=['LHS', 'RHS', 'Sense', 'NbrVars', 'NbrVarsNonzero', 'Difference p'])
cons=g5.getConstrs()
violcons=[]
for con in cons:
    c=g5.getRow(con)
    expr1=0
    expr2=0
    expr3=0
    k=0
    for t in range(0,c.size()):
        var=c.getVar(t)
        coff=c.getCoeff(t)
        if var.VarName[0]=='p' or var.VarName[0]=='p':
            expr2+=coff*var.x
            expr3+=g4.getVarByName(var.VarName).x
                        
        if g4.getVarByName(var.VarName).x > 0.0001:
            k+=1
        expr1+=coff*g4.getVarByName(var.VarName).x
    if con.sense == '<':
        if expr1 - con.RHS > 0.00001:
            violcons.append(c)
            df1.loc[len(df1)] = [expr1,con.RHS,con.sense, c.size(), k, expr2-expr3]
    else:
        if expr1 - con.RHS < -0.00001 :
            violcons.append(c)
            df1.loc[len(df1)] = [expr1,con.RHS,con.sense, c.size(), k, expr2-expr3]

#df1.to_csv('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Tables/cons_n2seq36q_40_45.csv')
