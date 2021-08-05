# -*- coding: utf-8 -*-
"""
Created on Tue May 18 09:18:51 2021

@author: mariu
"""

import gurobipy as gp
from gurobipy import GRB
import random as rand
import mappedqueue as mapq
import time
from bidict import bidict

try:

    # Create a new model
    m = gp.read('C:/Users/mariu/OneDrive/Dokumente/Python Scripts/ab71-20-100.mps')
    #m=gp.Model('mip1')
    # # Create variables
    # x1 = m.addVar(vtype=GRB.BINARY, name="x1")
    # x2 = m.addVar(vtype=GRB.BINARY, name="x2")
    # x3 = m.addVar(vtype=GRB.BINARY, name="x3")
    # x4 = m.addVar(vtype=GRB.BINARY, name="x4")
    # x5 = m.addVar(vtype=GRB.BINARY, name="x5")
    # x6 = m.addVar(vtype=GRB.BINARY, name="x6")
    # x7 = m.addVar(vtype=GRB.BINARY, name="x7")
    # x8 = m.addVar(vtype=GRB.BINARY, name="x8")
    # x9 = m.addVar(vtype=GRB.BINARY, name="x9")
    # x10 = m.addVar(vtype=GRB.BINARY, name="x10")
    # x11 = m.addVar(vtype=GRB.BINARY, name="x11")
    # x12 = m.addVar(vtype=GRB.BINARY, name="x12")
    # x13 = m.addVar(vtype=GRB.BINARY, name="x13")
    # x14 = m.addVar(vtype=GRB.BINARY, name="x14")
    # x15 = m.addVar(vtype=GRB.BINARY, name="x15")
    # # Set objective
    # m.setObjective(-x1 - x2 - 2 * x3, GRB.MINIMIZE)

    # # Add constraint: x + 2 y + 3 z <= 4
    # m.addConstr(x1 + x2 + x3 <= 1, "c0")
    # m.addConstr(x4 + x5 + x6 <= 1, "c1")
    # m.addConstr(x6 + x7 + x8 <= 1, "c2")
    # m.addConstr(x9 + x7 + x8 <= 1, "c3")
    # m.addConstr(x10 + 2*x11 + 2*x12+ x1 <= 2, "c4")
    # m.addConstr(x13 + x2 + x3 - x15 <= 1, "c5")
    # m.addConstr( x2 + x5 <= 1, "c6")
    # m.addConstr( x4 + x3 +x5 <= 1, "c0")
    # Add constraint: x + y >= 1
    #m.addConstr(4* x1 + 3 * x2 + x10 +x9 +2* x8 <= 3, "c1")
    #m.update()
    
    # Optimize model
    #m.optimize()
                   
            
    def determineTyp(typ):
        if typ == '<=' or typ=='>=' or typ =='==':
            equality=True
        else:
            equality=False
        if typ == '>' or typ=='>=':
            typ=-1
        else:
            typ=1 
            
    def buildObjectiveFunction(g,n):
        expr=0
        for var in g.getVars():
            r=rand.randint(0, n)
            expr=expr+ r*var
        g.setObjective(expr, GRB.MINIMIZE)
        g.update()
        return expr
        

    def buildConflictGraph(g, adjacency=True):
        constrs=g.getConstrs()
        n=0
        l=[]
        C=[]
        vartoclique={}
        vartovar={}
        index=0
        numbering=bidict({})
        #initialise map variables <--> indices
        for var in g.getVars():
            numbering[var]=index
            index+=1
        for con in range(0,len(constrs)):
            adjustb=0
            b=constrs[con].RHS
            l.append([])
            Temp=[]
            c=g.getRow(constrs[con])
            #print(n, c)
            typ=constrs[con].sense
            #handle the different kinds of (in)equalities possible; in particular the order has to be changed
            if typ == '<=' or typ=='>=' or typ =='==':
                equality=True
            else:
                equality=False
            if typ == '>' or typ=='>=':
                typ=-1
            else:
                typ=1
            #there are only equalities
            equality=True
            #inverse all signs, if the inequalities are > or >=:
            b=b*typ
            #initialize the variables and adjust the right hand sides:
            for i in range(0,c.size()):  
                #permute through all elements of the constraint
                coff=c.getCoeff(i)*typ   
                #inverse the sign of the coefficient
                if coff > 0:
                    l[n].append([c.getVar(i),coff, 1]) 
                    #l[n][i] contains variable at position 0, coefficinet at 1 and 0 at 2, if we consider the complement
                elif coff < 0:
                    adjustb+=coff
                    l[n].append([c.getVar(i),-coff,0])
            l[n]=sorted(l[n],key=lambda x: x[1])
            #initialize links var --> clique, var --> var:
            for k in range(0,len(l[n])):
                try:
                    vartoclique[l[n][k][0]].append((n,k))
                except:
                    vartoclique[l[n][k][0]]=[(n,k)]
                    vartovar[numbering[l[n][k][0]]]=[0]*index
            b-=adjustb
            up=len(l[n])-2
            if up < 0:
                continue
            down=0
            if (equality and l[n][up][1]+l[n][up+1][1] <= b) or (not equality and l[n][up][1]+l[n][up+1][1] < b):
                n+=1
                C.append(Temp)
                continue
            s = int((up)/2)
            #interval nesting starts
            while not (up==down):
                if (not equality and l[n][s][1]+l[n][s+1][1] >= b) or (equality and l[n][s][1]+l[n][s+1][1] > b):
                    up=s
                    s=int((up+down)/2)
                    if s==down:
                        break
                else:
                    down=s
                    s=int((up+down)/2)
                    if s==down:
                        s=up
                        break
            Temp.append((up,up))
            #Cliques are saved in the form: index from start element, uninterrupted 
            if adjacency:
                #this is very costly in some instances, as for this may take m*n^2 operations,
                #if many variables occur in one clique inequality
                for k in range(up,len(l[n])):
                    for j in range(k+1,len(l[n])):
                            if l[n][k][2]==1 and l[n][j][2]==1:
                                #vartovar[l[n][k][0]].append(l[n][j][0].VarName)
                                #vartovar[l[n][j][0]].append(l[n][k][0].VarName)
                                vartovar[numbering[l[n][k][0]]][numbering[l[n][j][0]]] =1
                                vartovar[numbering[l[n][j][0]]][numbering[l[n][k][0]]] =1
                                #vartovar[l[n][k][0]]=list(set(vartovar[l[n][k][0]]))
                                #vartovar[l[n][j][0]]=list(set(vartovar[l[n][j][0]]))
            s=up
            for j in range(0,s):
                up=len(l[n])-1
                down=s
                t = int((up+down)/2)
                if (equality and l[n][up][1]+l[n][j][1] <= b) or (not equality and l[n][up][1]+l[n][j][1] < b):
                    continue
                while not (up==down):
                    if (not equality and l[n][t][1]+l[n][j][1] >= b) or (equality and l[n][t][1]+l[n][j][1] > b):
                        up=t
                        t=int((up+down)/2)
                        if t==down:
                            break
                    else:
                        down=t
                        t=int((up+down)/2)
                        if t==down:
                            t=up
                            break
                Temp.append((j,up)) 
                if adjacency:
                    for k in range(up,len(l[n])):
                        if l[n][k][2]==1 and l[n][j][2]==1:
                            vartovar[numbering[l[n][k][0]]][numbering[l[n][j][0]]] =1
                            vartovar[numbering[l[n][j][0]]][numbering[l[n][k][0]]] =1
            C.append(Temp)
            #if n % 1 == 0:
             #   print(C[n], n)
            n+=1
        return [C,l,vartovar,vartoclique, numbering]
    
    
    class ConflictGraph:
        def __init__(self):
            self.vartovar={}
            self.vartoclique={}
            self.Cliques=[]
            self.Equations=[]
            self.vartobestclique={}
            self.vardegree={}
            self.vartovalue={}
            self.numbering=bidict({})
        def FindCliquePartitionDefault(self):
            C=self.Cliques
            self.Cliques=[]
            l=self.Equations
            for var in self.vartoclique:
                print(var)
                try:
                    a=self.vartobestclique[var]
                    #it can be assumed that the maximal clique of var has already been cound
                    continue
                except:
                    self.vartobestclique[var]=[var]
                    if len(self.vartoclique[var])>0:
                        for tup in self.vartoclique[var]:
                            print(tup)
                            k=tup[1]
                            n=tup[0]
                            if C[n]==[]:    
                                #in C[n] is no maximal clique for the row available; for example x1+x2+x3<=2
                                continue
                            else:
                                cliqueindex=C[n][0][0]
                                #C[n][0][0] is the first and biggest clique from the largest coefficients;
                                #for example {x2, x3} from x1+2x2+2x3<=3
                                if k >= cliqueindex:
                                    #k>=cliqueindex says var is in biggest clique
                                    length=len(l[n])
                                    clique=[]
                                    for i in range(cliqueindex, length):
                                        if l[n][i][2]==1:
                                            #append variable to clique only 
                                            clique.append(l[n][i][0])
                                            if len(clique)> len(self.vartobestclique[var]):
                                                self.vartobestclique[var]=clique
                for w in self.vartobestclique[var]:
                    #set the best clique already for the other variables
                    try:
                        po=set(self.vartobestclique[w]) - set(self.vartobestclique[var])
                        if po:
                            self.vartobestclique[w]=list(po)
                    except:
                        self.vartobestclique[w]=self.vartobestclique[var]
                self.Cliques.append(self.vartobestclique[var])                                           
        def FindCliquePartitionDSatur(self):
            self.Cliques=[]
            coloredneigh=[]
            vartoentry={}
            possvertices=[]
            posscliques={}
            i=0
            for var in self.vartovar:
                #first entry is sorted upon, second entry is only for avoiding problems with the priority queue
                coloredneigh.append((0,i,self.numbering.inverse[var]))
                vartoentry[var]=i
                posscliques[var]=[]
                #the vertex with the least number of neighbours is found here
                if i==0:
                    mini=self.numbering.inverse[var]
                    leng=sum(self.vartovar[var])
                else:
                    if sum(self.vartovar[var]) < leng:
                        mini=self.numbering.inverse[var]
                        leng=sum(self.vartovar[var])
                    
                i+=1
            #this is the priority queue
            q=mapq.MappedQueue(coloredneigh)
            q.remove(mini)
            #cliques are numbered starting from 0
            self.vartobestclique[mini]=0
            self.Cliques.append([mini])
            #possvertices is a list with indices for every available clique, and entries a set of vertices available for this clique 
            possvertices.append(set())
            nextclique=1
            possvertices.append(set())
            for v in range(len(self.vartovar[self.numbering[mini]])):
                #update(v) increases the value of variable v by 1 in queue, so it moves down the queue
                if self.vartovar[self.numbering[mini]][v]==1:
                    q.update(self.numbering.inverse[v])
                    possvertices[0]=possvertices[0]|set([v])
                    de=set(posscliques[v])
                    de=de|set([0])
                    posscliques[v]=list(de)
            while len(q.h) > 0:
                mini=q.pop()
                mi=nextclique
                #here is the choice of cliques; can be changed to a procedure where not the clique
                #with smallest number but clique with other criterion is chosen, maybe try priority queue here as well
                for cli in posscliques[self.numbering[mini[2]]]:
                    if cli < mi:
                        mi=cli
                if mi==nextclique:
                    nextclique+=1
                    self.vartobestclique[mini[2]]=mi
                    possvertices.append(set())
                    self.Cliques.append([mini[2]])
                    for v in range(len(self.vartovar[self.numbering[mini[2]]])):
                        try:
                            if self.vartovar[self.numbering[mini[2]]][v]==1:
                                q.update(self.numbering.inverse[v])
                                possvertices[mi]=possvertices[mi]|set([v])
                                de=set(posscliques[v])
                                de=de|set([mi])
                                posscliques[v]=list(de)
                        except:
                            continue
                    continue
                for cli in posscliques[self.numbering[mini[2]]]:
                    #remove the current vertex from all cliques as possible vertex
                    possvertices[cli]=possvertices[cli]-set([self.numbering[mini[2]]])
                    #posscliques.pop(mini[2])
                n=set([v for v in range(len(self.vartovar[self.numbering[mini[2]]])) if self.vartovar[self.numbering[mini[2]]][v]==1])
                #remove all possible vertices for the best clique, which are not neighbours of mini
                rest=possvertices[mi]-n 
                possvertices[mi]=possvertices[mi] & n
                #check this part again; why only update the rest?
                for v in n:
                    try:
                        q.update(v)
                    except:
                        continue
                for v in rest:
                    #this may be slower than O(n) in the worst case, but sets are easier to handle and more space
                    #efficient than an indicator function
                    posscliques[v]=list(set(posscliques[v])-set([mi]))
                self.vartobestclique[self.numbering[mini[2]]]=mi
                self.Cliques[mi].append(mini[2])
        def FindCliquePartitionDSaturWeighted(self):
            self.Cliques=[]
            coloredneigh=[]
            vartoentry={}
            possvertices=[]
            cliquetoweight=[]
            posscliques={}
            i=0
            for var in self.vartovar:
                #first entry is sorted upon, second entry is only for avoiding problems with the priority queue
                coloredneigh.append((0,i,var))
                vartoentry[var]=i
                posscliques[var]=[]
                #the vertex with the least number of neighbours is found here
                if i==0:
                    mini=var
                    leng=len(self.vartovar[var])
                else:
                    if len(self.vartovar[var]) < leng:
                        mini=var
                        leng=len(self.vartovar[var])
                    
                i+=1
            #this is the priority queue
            q=mapq.MappedQueue(coloredneigh)
            q.remove(mini)
            #cliques are numbered starting from 0
            self.vartobestclique[mini]=0
            self.Cliques.append([mini])
            #possvertices is a list with indices for every available clique, and entries a set of vertices available for this clique 
            possvertices.append(set())
            cliquetoweight.append(self.vartoweight[mini])
            nextclique=1
            possvertices.append(set())
            for v in self.vartovar[mini]:
                #update(v) increases the value of variable v by 1 in queue, so it moves down the queue
                q.update(v)
                possvertices[0]|set([v])
                de=set(posscliques[v])
                de=de|set([0])
                posscliques[v]=list(de)
            while len(q.h) > 0:
                mini=q.pop()
                mi=nextclique
                #here is the choice of cliques; can be changed to a procedure where not the clique
                #with smallest number but clique with other criterion is chosen, maybe try priority queue here as well
                for cli in posscliques[mini[2]]:
                    try:
                        #choose the clique for which the average weight, after adding the new vertex does differ the least
                        #this is to compute cliques with vertices of similar weight
                        if (cliquetoweight[cli] + self.vartoweight[mini[2]])/(len(self.Cliques[cli])+1) < (cliquetoweight[mi] + self.vartoweight[mini[2]])/(len(self.Cliques[mi])+1):
                            mi=cli
                    except:
                        mi=cli
                if mi==nextclique:
                    nextclique+=1
                    self.vartobestclique[mini[2]]=mi
                    possvertices.append(set())
                    cliquetoweight.append(self.vartoweight[mini[2]])
                    self.Cliques.append([mini[2]])
                    for v in self.vartovar[mini[2]]:
                        try:
                            q.update(v)
                            possvertices[mi]|set([v])
                            de=set(posscliques[v])
                            de=de|set([mi])
                            posscliques[v]=list(de)
                        except:
                            continue
                    continue
                for cli in posscliques[mini[2]]:
                    #remove the current vertex from all cliques as possible vertex
                    possvertices[cli]=possvertices[cli]-{mini[2]}
                    #posscliques.pop(mini[2])
                n=set(self.vartovar[mini[2]])
                #remove all possible vertices for the best clique, which are not neighbours of mini
                possvertices[mi]=possvertices[mi] & n
                #check this part again; why only update the rest?
                rest=n-possvertices[mi]
                for v in rest:
                    try:
                        q.update(v)
                        posscliques[v]-set([mi])
                    except:
                        continue
                self.vartobestclique[mini[2]]=mi
                self.Cliques[mi].append(mini[2])

                
                
        
    
        
    def RobustFormulation(g, gamma, withcliques=False, cliquemethod="default" , cHat={}):
        #[C,l]=ConflictGraph(g)
        z=g.addVar(lb=0.0,vtype=GRB.CONTINUOUS)
        pvalues={}
        robEq={}
        #originvar=g.getVars()
        objective=g.getObjective()
        objective=g.ModelSense*objective    
        Vars=g.getVars()
        Cliques=[]
        if withcliques:
            if cliquemethod=="default":
                G=ConflictGraph()
                [G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(g)
                G.FindCliquePartitionDefault()
                Cliques=G.Cliques
            elif cliquemethod=="dsatur":
                G=ConflictGraph()
                [G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(g)
                G.FindCliquePartitionDSatur()
                Cliques=G.Cliques       
        else:
            Cliques=Vars
        objVars={}
        i=0
        while True:
            try:
                objVars[objective.getVar(i)]=objective.getCoeff(i)
                i+=1
            except:
                break
        for var in Vars:
            pvalues[var]=g.addVar(lb=0.0, vtype=GRB.CONTINUOUS)
            expr1=pvalues[var]+z
            try:
                if cHat[var.VarName] >= 0:
                    pass
            except:
                try:
                    r=rand.random()
                    if abs(objVars[var]) > 0:
                        cHat[var.VarName]=abs(r*objVars[var])
                    else:
                        cHat[var.VarName]=abs(r)
                        
                except:
                    r=rand.random()
                    cHat[var.VarName]=r
            expr2=cHat[var.VarName]*var
            robEq[var]=g.addConstr(expr1 >= expr2)
            g.update()
        for cli in Cliques:
            if withcliques:
                pvalues[cli[0]]=g.addVar(lb=0.0, vtype=GRB.CONTINUOUS)
                expr1=pvalues[cli[0]]+z
                expr2=0
                for v in cli:
                    expr2=expr2+cHat[v.VarName]*v
            else:
                pvalues[cli]=g.addVar(lb=0.0, vtype=GRB.CONTINUOUS)
                expr1=pvalues[cli]+z
                expr2=0
                expr2=cHat[cli.varName]*cli
            g.addConstr(expr1 >= expr2)
            g.update()
        expr=sum(pvalues.values())
        objective=g.setObjective(objective+gamma*z+expr, GRB.MINIMIZE)
        g.update()
        return cHat, pvalues, z
        #Now set the 
    
    def CompareRobustMethods(scenarios):
        for sce in scenarios:
            m = gp.read(sce)
            #objective=buildObjectiveFunction(m, 1)
            m1=m.copy()
            t0=time.time()
            cHat, pvalues, z = RobustFormulation(m, 20)
            t0=time.time()-t0
            t1=time.time()
            RobustFormulation(m1, 20, True, "dsatur", cHat)
            t1=time.time() -t1
            g=m.relax()
            g1=m1.relax()
            t2=time.time()
            g.optimize()
            t2=time.time() -t2
            t3=time.time()
            g1.optimize()
            t3=time.time() -t3
            print('Objective Value model 0: ',g.ObjVal)
            print('Times model 0: ',t0, t2)
            print('Objective Value model 1: ',g1.ObjVal)
            print('Times model 1: ',t1, t3)
     
    #G=ConflictGraph()       
    #[G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(m)
    #G.FindCliquePartitionDSatur()
    #buildConflictGraph(m) 
    CompareRobustMethods(['C:/Users/mariu/OneDrive/Dokumente/Python Scripts/ab71-20-100.mps'])           
                            
except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')