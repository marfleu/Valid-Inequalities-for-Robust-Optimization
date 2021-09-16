# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 11:15:03 2021

@author: mariu
"""
import gurobipy as gp
from gurobipy import GRB
import modelreading as mr
import time

def CompareRobustMethods(scenarios):
     for sce in scenarios:
         gamma, cHat = mr.readInstance('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/RobustnessComponents/ab51-40-100_g=100_d=5-15_r=0.txt')
         m = gp.read(sce)
         #objective=buildObjectiveFunction(m, 1)
         m1=m.copy()
         m2=m.copy()
         m3=m.copy()
         t0=time.time()
         cHat, pvalues, z = mr.RobustFormulation(m, gamma, True, "none", cHat)
         p=len(pvalues)
         t0=time.time()-t0
         t1=time.time()
         cHat, pvalues, z = mr.RobustFormulation(m1, gamma, True, "default", cHat)
         p1=len(pvalues)
         t1=time.time() -t1
         g=m.relax()
         g1=m1.relax()
         t2=time.time()
         g.optimize()
         t2=time.time() -t2
         t3=time.time()
         g1.optimize()
         t3=time.time() -t3
         t6=time.time()
         cHat, pvalues, z = mr.RobustFormulation(m3, gamma, False, "default", cHat)
         p3=len(pvalues)
         t6=time.time() -t6
         g3=m3.relax()
         t7=time.time()
         g3.optimize()
         t7=time.time()-t7
         weights={}
         for v in g.getVars():
             weights[v.VarName]=v.x
         t4=time.time()
         cHat, pvalues, z =mr.RobustFormulation(m2, gamma, True, "dsaturw", cHat, weights)
         p2=len(pvalues)
         t4=time.time()-t4
         g2=m2.relax()
         t5=time.time()
         g2.optimize()
         t5=time.time() -t5
         l=[y for y in g.X if abs(y)>0.001]
         l1=[y for y in g1.X if abs(y)>0.001]
         l2=[y for y in g2.X if abs(y)>0.001]
         l3=[y for y in g3.X if abs(y)>0.001]
         print('Objective Value model 0: ',g.ObjVal)
         print('Times model 0: ',t0, t2)
         print('Number of nonzeros of model 0:', len(l))
         print('Number of p-values of model 0:', p)
         print('Objective Value model 1: ',g1.ObjVal)
         print('Relative error model 1: ', abs(g1.ObjVal - g.ObjVal)/abs(g.ObjVal))
         print('Times model 1: ',t1, t3)
         print('Number of nonzeros of model 1:', len(l1))
         print('Number of p-values of model 1:', p1)
         print('Objective Value model 2: ',g3.ObjVal)
         print('Relative error model 2: ', abs(g3.ObjVal - g.ObjVal)/abs(g.ObjVal))
         print('Times model 2: ',t6, t7)
         print('Number of nonzeros of model 2:', len(l3))
         print('Number of p-values of model 2:', p3)
         print('Objective Value model 3: ',g2.ObjVal)
         print('Relative error model 3: ', abs(g2.ObjVal - g.ObjVal)/abs(g.ObjVal))
         print('Times model 3: ',t4, t5)
         print('Number of nonzeros of model 3:', len(l2))
         print('Number of p-values of model 3:', p2)
 #G=ConflictGraph()       
 #[G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(m)
 #G.FindCliquePartitionDSatur()
 #buildConflictGraph(m) 
CompareRobustMethods(['C:/Users/mariu/OneDrive/Dokumente/Python Scripts/ab51-40-100.mps'])           
 #m = gp.read('C:/Users/mariu/OneDrive/Dokumente/Python Scripts/30_70_45_05_100.mps')
#  # #buildObjectiveFunction(m, 3)
 #gamma, cHat = readInstance('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/RobustnessComponents/30_70_45_05_100_g=10_d=45-55_r=0.txt')
 #m1=m.copy()
#  # m2=m.copy()
#  # gamma=10
 # cHat, pvalues, z = RobustFormulation(m, 5) 
 # g=m.copy()
 # g=g.relax()
 # g.optimize()
 # print(len(g.getConstrs()))
 # weights={}
 # for v in m1.getVars():
 #     weights[v.VarName]=(g.getVarByName(v.VarName)).x
 # print("Extend\n")
 # ExtendedRobustFormulation(g, z, pvalues, cHat, weights)
 # g.optimize()
 # print(len(g.getConstrs()))
#  # cHat, pvalues, z =RobustFormulation(m2, gamma, False, "default", cHat)
#  # cHat, pvalues, z =RobustFormulation(m1, gamma, True, "dsaturw", cHat, weights)
#  # g1=m1.copy()
#  # g2=m2.copy()
#  # g1=g1.relax()
#  # g2=g2.relax()
#  # g1.optimize()
#  # g2.optimize()
#  # print('Objective Value model 0: ',g.ObjVal)
#  # print('Objective Value model 1: ',g1.ObjVal)
#  # print('Objective Value model 2: ',g2.ObjVal)
# gamma, cHat = mr.readInstance('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/RobustnessComponents/30_70_45_05_100_g=100_d=45-55_r=0.txt')
# m = gp.read('C:/Users/mariu/OneDrive/Dokumente/Python Scripts/30_70_45_05_100.mps')
# i=0
# weights={}
# for v in m.getVars():
#     if i < 300:
#         weights[v.VarName]=0.5
#     i+=1
# cHat, pvalues, z =mr.RobustFormulation(m, gamma, True, "dsaturw", cHat, weights)