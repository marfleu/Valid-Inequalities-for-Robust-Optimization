# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 19:52:59 2021

@author: mariu
"""

import gurobipy as gp
from gurobipy import GRB
import random as rand
from modelreading import robustformulation as mr

try:

    # Create a new model
    #m = gp.read('acc-tight2.mps')
    m=gp.Model('mip1')
    # # Create variables
    x1 = m.addVar(vtype=GRB.BINARY, name="x1")
    x2 = m.addVar(vtype=GRB.BINARY, name="x2")
    x3 = m.addVar(vtype=GRB.BINARY, name="x3")
    x4 = m.addVar(vtype=GRB.BINARY, name="x4")
    x5 = m.addVar(vtype=GRB.BINARY, name="x5")
    x6 = m.addVar(vtype=GRB.BINARY, name="x6")
    x7 = m.addVar(vtype=GRB.BINARY, name="x7")
    z = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="z")
    p1 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="p1")
    p2 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="p2")
    p3 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="p3")
    p4 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="p4")
    p5 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="p5")
    p6 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="p6")
    p7 = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="p7")
    # x9 = m.addVar(vtype=GRB.BINARY, name="x9")
    # x10 = m.addVar(vtype=GRB.BINARY, name="x10")

    # # Set objective
    m.setObjective(-2*x1 -2*x2 - 1 * x3 - 3*x4 - 4*x5 -4*x6 -3*x7 + 2*z + p1 + p2+ p3+ p4+ p5 +p6 +p7, GRB.MINIMIZE)

    # # Add constraint: x + 2 y + 3 z <= 4
    m.addConstr(2*x1 + 2*x2 + 3 * x3+ 3* x4 +3* x5 + 4*x6 + 4*x7 <= 4, "c0")
    m.addConstr(p1+z >= 2*x1)
    m.addConstr(p2+z >= 2*x2)
    m.addConstr(p3+z >= x3)
    m.addConstr(p4+z >= x4)
    m.addConstr(p5+z >= x5)
    m.addConstr(p6+z >= 3*x6)
    m.addConstr(p7+z >= 2*x7)
    #m.addConstr(2*p1 + 2*p2 + 3* p3+ 3* p4+ 3* p5+ 4* p6+ 4* p7+ 4*z >=4*x1+ 4*x2 + 3* x3+3* x4+3* x5+ 12*x6+ 8*x7)
   # m.addConstr(p3 +p4 + p5 + p6+ p7 + z >=x3 +x4+ x5+ 3*x6+ 2*x7)
    #m.addConstr(p4 + p5 + z >= x4 + x5)
    #m.addConstr(p2 + p7+ z >= 2*x2 + 3*x7)
    # # Add constraint: x + y >= 1
    # m.addConstr(4* x1 + 3 * x2 + x10 +x9 +2* x8 <= 3, "c1")
    m.update()
    m.optimize()
    #r=m.relax()
    #r.update()
    # Optimize model
    #r.optimize()
    
    def buildKnapsack(n, m, b):
        g=gp.Model('knap')
        expr=0
        obj=0
        for i in range(0,n):
            var=g.addVar(vtype=GRB.BINARY)
            r=rand.randint(0, b)
            expr=expr+ r*var
            r=rand.randint(-m, 0)
            obj=obj+r*var
        g.setObjective(obj)
        g.addConstr(expr <= b)
        g.update()
        return g
    
    def addRobustKnapsackConstraint(g, constr, cHat, pvalues, z):   
        #receives the whole constraint a^Tx <= b, has to be picked apart
        #also receives cHat, pvalues and z from RobustFormulation(), but without cliques!
        expr2=constr.RHS * z
        expr1=0
        constr=g.getRow(constr)
        for coeff in range(0,constr.size()):
            c=constr.getCoeff(coeff)
            print(c)
            var=constr.getVar(coeff)
            expr1=expr1 + c*cHat[var]*var
            expr2=expr2 + c*pvalues[var]
        print(expr1)
        print(expr2)
        g.addConstr(expr1 <= expr2)
        g.update()
            
    def buildRobustKnapsack(g, withCliques, Gamma, cHat={}):
        #receives as argument a Knapsack instance
        constr=g.getConstrs()[0]
        if not(cHat=={}):
            cHat, pvalues, z=mr.RobustFormulation(g, withCliques, Gamma, cHat)
        else:
            cHat, pvalues, z=mr.RobustFormulation(g, withCliques, Gamma)
        h=g.copy()
        if withCliques:
            return h, cHat
        else:
            addRobustKnapsackConstraint(g, constr, cHat, pvalues, z)
        return h, cHat
        
            
        
    
except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')