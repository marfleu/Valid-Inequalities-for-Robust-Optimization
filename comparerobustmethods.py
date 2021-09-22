# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 11:15:03 2021

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

def CompareRobustMethods(file, file2):
    gamma, cHat = mr.readInstance(file2)
    m = gp.read(file)
    originvars=[y.VarName for y in m.getVars()]
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
    for v in originvars:
        weights[v]=g.getVarByName(v).x
    t4=time.time()
    cHat, pvalues, z =mr.RobustFormulation(m2, gamma, True, "dsaturw", cHat, weights)
    p2=len(pvalues)
    t4=time.time()-t4
    g2=m2.relax()
    t5=time.time()
    g2.optimize()
    t5=time.time() -t5
    l=[g.getVarByName(v).x for v in originvars if abs(g.getVarByName(v).x)>0.001]
    l1=[g1.getVarByName(v).x for v in originvars if abs(g1.getVarByName(v).x)>0.001]
    l2=[g2.getVarByName(v).x for v in originvars if abs(g2.getVarByName(v).x)>0.001]
    l3=[g3.getVarByName(v).x for v in originvars if abs(g3.getVarByName(v).x)>0.001]
    data={}
    data['gamma']=gamma
    data['original']={}
    data['original']['Objective value']=g.ObjVal
    data['original']['Building Time']=t0
    data['original']['Computation Time']=t2
    data['original']['p-Values']=p
    data['original']['nonzeroes']=len(l)
    data['defaultwithcliques']={}
    data['defaultwithcliques']['Objective value']=g1.ObjVal
    data['defaultwithcliques']['Building Time']=t1
    data['defaultwithcliques']['Computation Time']=t3
    data['defaultwithcliques']['p-Values']=p1
    data['defaultwithcliques']['nonzeroes']=len(l1)
    data['default']={}
    data['default']['Objective value']=g3.ObjVal
    data['default']['Building Time']=t6
    data['default']['Computation Time']=t7
    data['default']['p-Values']=p3
    data['default']['nonzeroes']=len(l3)
    data['dsatweight']={}
    data['dsatweight']['Objective value']=g2.ObjVal
    data['dsatweight']['Building Time']=t4
    data['dsatweight']['Computation Time']=t5
    data['dsatweight']['p-Values']=p2
    data['dsatweight']['nonzeroes']=len(l2)
    print(data)
    pattern=re.search('\\[^\\]+[^\.]+', file2)
    print(pattern)
    pattern=pattern.group(0) + '_json.json'
    print("\n\n\n\n", pattern, "\n\n\n\n")
    with open(pattern, 'w') as outfile:
        json.dump(data, outfile)
    # print('Objective Value model 0: ',g.ObjVal)
    # print('Times model 0: ',t0, t2)
    # print('Number of nonzeros of model 0:', len(l))
    # print('Number of p-values of model 0:', p)
    # print('Objective Value model 1: ',g1.ObjVal)
    # print('Relative error model 1: ', abs(g1.ObjVal - g.ObjVal)/abs(g.ObjVal))
    # print('Times model 1: ',t1, t3)
    # print('Number of nonzeros of model 1:', len(l1))
    # print('Number of p-values of model 1:', p1)
    # print('Objective Value model 2: ',g3.ObjVal)
    # print('Relative error model 2: ', abs(g3.ObjVal - g.ObjVal)/abs(g.ObjVal))
    # print('Times model 2: ',t6, t7)
    # print('Number of nonzeros of model 2:', len(l3))
    # print('Number of p-values of model 2:', p3)
    # print('Objective Value model 3: ',g2.ObjVal)
    # print('Relative error model 3: ', abs(g2.ObjVal - g.ObjVal)/abs(g.ObjVal))
    # print('Times model 3: ',t4, t5)
    # print('Number of nonzeros of model 3:', len(l2))
    # print('Number of p-values of model 3:', p2)
         
         

i=0
j=0
for file in os.listdir('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen'):
    pattern=re.search('[^\.]+', file)
    i+=1
    if i >=5:
        break
    for file2 in os.listdir('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents'):
        if j >=5:
            j=0
            break
        if fnmatch.fnmatch(str(file2), str(pattern.group(0) + '*')):
            try:
                j+=1
                CompareRobustMethods('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/'+file, 'C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/' + file2)
                print('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen'+file)
                break
            except:
                continue
        # for i in range(len(file)):
        #     #print(file[i])
        #     #print(file2[i])
        #     if file[1]=='a':
        #         print(file)
        #         break
        # else:
            # print(file)
            # print(file2)
        
 #G=ConflictGraph()       
 #[G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(m)
 #G.FindCliquePartitionDSatur()
 #buildConflictGraph(m) 
#CompareRobustMethods(['C:/Users/mariu/OneDrive/Dokumente/Python Scripts/ab71-20-100.mps'])           
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

