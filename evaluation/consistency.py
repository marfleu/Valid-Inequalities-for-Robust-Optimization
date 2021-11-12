# -*- coding: utf-8 -*-
"""
Script to test the consistency of the Clique Partitions and Covers computed by mr.buildConflictGraph
"""

import gurobipy as gp
from modelreading import robustformulation as mr
import random as rand

gamma, cHat = mr.readInstance('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/mod010_g=40_d=95-105_r=0.txt')
dHat=cHat
m5 = gp.read('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/mod010.mps')
G=mr.ConflictGraph()
[G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=mr.buildConflictGraph(m5, False)
G.FindCliquePartitionFromCover()
Cliques=G.Cliques 
G1=mr.ConflictGraph()
[G1.Cliques,G1.Equations,G1.vartovar,G1.vartoclique, G1.numbering]=mr.buildConflictGraph(m5, False)
G1.FindCliquePartitionDefault()
Cliques1=G1.Cliques
contained=True
disjoint=True
differclique=[]
for var in G.vartobestclique:
    if not var in G.vartobestclique[var]:
        contained=False
        break
    for w in G.vartobestclique[var]:
        if not var in G.vartobestclique[w]:
            disjoint=False
            break
    if len(G.vartobestclique[var]) != len(G1.vartobestclique[var]):
        differclique.append(var)
        
    
cons=m5.getConstrs()
violcons=[]
randcliques={}
for var in m5.getVars():
    randcliques[var.VarName]=rand.sample(G.vartobestclique[var.VarName], 1)
for con in cons:
    c=m5.getRow(con)
    expr1=0
    expr2=0
    expr3=0
    k=0
    for t in range(0,c.size()):
        var=c.getVar(t)
        coff=c.getCoeff(t)
        try:
            if randcliques[var.VarName]:
                for s in range(0, c.size()):
                    var2=c.getVar(s)
                    if var2.VarName in randcliques[var.VarName]:
                        print(var.VarName)
                        if con.sense == '<':
                            if c.getCoeff(t) + c.getCoeff(s) > con.RHS:
                                randcliques.pop(var.VarName)
                        elif con.sense == '=':
                            if abs(c.getCoeff(t) + c.getCoeff(s) - con.RHS) > 0.00001 :
                                randcliques.pop(var.VarName)
                        else:
                            if c.getCoeff(t) + c.getCoeff(s) < con.RHS:
                                randcliques.pop(var.VarName)
        except:
            continue


