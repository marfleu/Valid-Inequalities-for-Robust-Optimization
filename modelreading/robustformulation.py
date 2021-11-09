# -*- coding: utf-8 -*-
"""
Script contains all methods to compute robust formulations. It is advisable to only apply the methods as described 
in the python script 'usagetemplate.py'.   
"""

import gurobipy as gp
from gurobipy import GRB
import random as rand
from modelreading import mappedqueue as mapq
import time
from bidict import bidict
import re

##############################################################################
#                     Helper functions                                       #
##############################################################################                   
def readInstance(file):  
    # reading the data from the file
    with open(file) as f:
        data = f.read()
    lis=re.findall(".*:.*", data)
    l=[re.split(":", y) for y in lis]
    l=[[y[0], float(y[1])] for y in l]
    dic={}
    for i in range(len(l)-1):
        i+=1
        dic[l[i][0]]=float(l[i][1])
    gamma=l[0][1]   
    return gamma, dic
    
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
        expr=expr- r*var
    g.setObjective(expr, GRB.MINIMIZE)
    g.update()
    return expr


##############################################################################
#                     Conflict Graph                                         #
##############################################################################    
    

def buildConflictGraph(g, adjacency=True):
    """
    Builds a partial Conflict Graph on variables of a combinatorial linear program g.
    By default also creates the adjacency matrix of this 
    graph (should be avoided for bigger instances). Iterates over all constraints of g
    and tries to find obvious conflicts.

    Parameters
    ----------
    g : Gurobipy combinatorial (non! robust formulation) ILP 
    adjacency : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    list of
        several important datastructures for a Conflict Graph:
            C --> list, with entries for every inequality from g;
                  every entry is again a list of cliques in the 
                  Conflict Graph extracted from the inequality, either 
                  as a tuple (i, i), coressponding to a clique of
                  variables x_i, x_{i+1}, ..., x_n, variables being 
                  numbered in increasing order defined by their coefficients
                  in the inequality, or a tuple (j, i) with j < i, corresponding
                  to a clique of x_j, x_i, x_{i+1}, ..., x_n;
            l --> list of lists, with entries for every inequality from g;
                  every entry is a list of tuples of three;
                  tuple entry 0 --> variable name
                  tuple entry 1 --> coefficient of this variable in adjusted inequality
                  tuple entry 2 --> 0: if variable appears negated in adjusted ineq.
                                    1: if variable appears unnegated in adjusted ineq.
            vartoclique --> dictionary: variable --> list of tuples with two entries each
                                                     first of which points to an inequality n
                                                     second pointing to the index in the ordering
                                                     by coefficients of the variable in this ineq.
            vartoclique --> dictionary: variable --> list of tuples with two entries each
                                                     first of which points to an inequality n
                                                     second pointing to the index in the ordering
                                                     by coefficients of the variable in this ineq.
            numbering --> a bidirectional dictionary: variable <--> unique number; mostly used if adjacency=True
                                                                    to be more efficient
            vartovar --> dictionary: variable --> adjacency matrix row; is empty, if adjacency=False                
                  

    """
    constrs=g.getConstrs()
    n=0
    l=[]
    C=[]
    vartoclique={}
    vartovar={}
    index=0
    m=len(g.getVars())
    numbering=bidict({})
    #initialise map variables <--> indices
    for var in g.getVars():
        numbering[var.VarName]=index
        vartoclique[var.VarName]=[]
        if adjacency:
            vartovar[index]=[0]*m
        index+=1
    for con in range(0,len(constrs)):
        adjustb=0
        b=constrs[con].RHS
        l.append([])
        Temp=[]
        c=g.getRow(constrs[con])
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
            #inverse the sign of the coefficient if necessary
            if coff > 0:
                l[n].append([c.getVar(i).VarName,coff, 1]) 
                #l[n][i] contains variable at position 0, coefficinet at 1 and 0 at 2, if we consider the complement
            elif coff < 0:
                adjustb+=coff
                l[n].append([c.getVar(i).VarName,-coff,0])
        l[n]=sorted(l[n],key=lambda x: x[1])
        #initialize links var --> clique, var --> var:
        for k in range(0,len(l[n])):
            try:
                vartoclique[l[n][k][0]].append((n,k))
            except:
                vartoclique[l[n][k][0]]=[(n,k)]
                if adjacency:
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
            #if many variables occur in one clique inequality, better avoided
            for k in range(up,len(l[n])):
                for j in range(k+1,len(l[n])):
                        if l[n][k][2]==1 and l[n][j][2]==1:
                            vartovar[numbering[l[n][k][0]]][numbering[l[n][j][0]]] =1
                            vartovar[numbering[l[n][j][0]]][numbering[l[n][k][0]]] =1

        s=up
        for j in range(0,s):
            up=len(l[n])-1
            down=s
            t = int((up+down)/2)
            if (equality and l[n][up][1]+l[n][j][1] <= b) or (not equality and l[n][up][1]+l[n][j][1] < b):
                #variable j does not occur in any clique of this inequality
                vartoclique[l[n][j][0]].pop()
                continue
            while not (up==down):
                if (not equality and l[n][t][1]+l[n][j][1] >= b) or (equality and l[n][t][1]+l[n][j][1] > b):
                    up=t
                    t=int((up+down)/2)
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
        n+=1
    return [C,l,vartovar,vartoclique, numbering]

def buildWeightedConflictGraph(g, z, weights, cutoff, adjacency=True):
    """
    Builds a Conflict Graph on variables with weights above a certain 
    cutoff value. By default also creates the adjacency matrix of this 
    graph.
    Method in particular ignores inequalities with the variable z.

    Parameters
    ----------
    g : Gurobipy combinatorial (possibly robust formulation) ILP 
    z : name of the z variable in the robust model (if existant)
    weights : dictionnary from combinatorial variables of g --> weight 
    cutoff : value which defines the cutoff for the variable weights
    adjacency : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    list of
        several important datastructures for a Conflict Graph:
            C --> list, with entries for every inequality from g;
                  every entry is again a list of cliques in the 
                  Conflict Graph extracted from the inequality, either 
                  as a tuple (i, i), coressponding to a clique of
                  variables x_i, x_{i+1}, ..., x_n, variables being 
                  numbered in increasing order defined by their coefficients
                  in the inequality, or a tuple (j, i) with j < i, corresponding
                  to a clique of x_j, x_i, x_{i+1}, ..., x_n;
            l --> list, with entries for every inequality from g;
                  every entry is a tuple of three;
                  tuple entry 0 --> variable name
                  tuple entry 1 --> coefficient of this variable in adjusted inequality
                  tuple entry 2 --> 0: if variable appears negated in adjusted ineq.
                                    1: if variable appears unnegated in adjusted ineq.
            vartoclique --> dictionary: variable --> list of tuples with two entries each
                                                     first of which points to an inequality n
                                                     second pointing to the index in the ordering
                                                     by coefficients of the variable in this ineq.
            numbering --> a bidirectional dictionary: variable <--> unique number; mostly used if adjacency=True
                                                                    to be more efficient
            vartovar --> dictionary: variable --> adjacency matrix row; is empty, if adjacency=False

    """
    constrs=g.getConstrs()
    n=0
    l=[]
    C=[]
    vartoclique={}
    vartovar={}
    index=0
    numbering=bidict({})
    Vars=[]
    encounteredz=False
    for y in g.getVars():
        try:
            if weights[y.VarName]>cutoff:
                Vars.append(y.VarName)
        except:
            continue
    m=len(Vars)
    #initialise map variables <--> indices
    for var in Vars:
        numbering[var]=index
        vartoclique[var]=[]
        if adjacency:
            vartovar[index]=[0]*m
        index+=1
    for con in range(0,len(constrs)):
        adjustb=0
        b=constrs[con].RHS
        l.append([])
        Temp=[]
        c=g.getRow(constrs[con])
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
            #permute through all variables in the constraint
            coff=c.getCoeff(i)*typ   
            #inverse the sign of the coefficient
            var=c.getVar(i)
            if var.VarName == z:
                # constraints, which  contain z variable, shall be ignored
                l.pop()
                encounteredz=True
                break
            try:
                if coff > 0 and weights[var.VarName] > cutoff:
                    #variable with positive coefficient is only considered, if its predefined
                    #weight exceeds a given cutoff value
                    l[n].append([var.VarName,coff, 1]) 
                    #l[n][i] contains variable at position 0, coefficinet at 1 and 0 at 2, if we consider the complement
                elif coff < 0 and weights[var.VarName] > cutoff:
                    adjustb+=coff
                    l[n].append([var.VarName,-coff,0])
            except:
                continue
        if encounteredz:
            #go to next constraint, if current constraint contains z-variable
            encounteredz=False
            continue
        l[n]=sorted(l[n],key=lambda x: x[1])
        print(l[n])
        #initialize links var --> clique, var --> var:
        for k in range(0,len(l[n])):
            try:
                vartoclique[l[n][k][0]].append((n,k))
            except:
                vartoclique[l[n][k][0]]=[(n,k)]
                if adjacency:
                    vartovar[numbering[l[n][k][0]]]=[0]*index
        b-=adjustb
        up=len(l[n])-2
        if up < 0:
            C.append(Temp)
            n+=1
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
                            vartovar[numbering[l[n][k][0]]][numbering[l[n][j][0]]] =1
                            vartovar[numbering[l[n][j][0]]][numbering[l[n][k][0]]] =1
                     
        s=up
        for j in range(0,s):
            up=len(l[n])-1
            down=s
            t = int((up+down)/2)
            if (equality and l[n][up][1]+l[n][j][1] <= b) or (not equality and l[n][up][1]+l[n][j][1] < b):
                #variable j does not occur in any clique of this inequality
                vartoclique[l[n][j][0]].pop()
                continue
            while not (up==down):
                if (not equality and l[n][t][1]+l[n][j][1] >= b) or (equality and l[n][t][1]+l[n][j][1] > b):
                    up=t
                    t=int((up+down)/2)
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
        n+=1
    return [C,l,vartovar,vartoclique, numbering]


##############################################################################
#                     Clique Partitions/Covers                               #
##############################################################################


class ConflictGraph:
    """ Conflict Graph object. Owns all methods to compute Clique Partitions/Clique Covers. Has to be filled by method buildConflictGraph(), which is
        not a method of this object (but maybe will be in a future update). 
    
        Attributes:
            vartovar: dictionnary; if Conflict Graph is computed with adjacency : var (number) --> row of adjacency matrix
                                   if Conflict Graph is computed without adjacency : var.VarName --> list of var.VarName, that are neighbours
                      variable is only used for algorithms, that need a maximal clique (i.e. FindCliqueCover, FindCliquePartitionFromCover)             
            vartoclique: dictionnary, filled by variable vartoclique from buildConflictGraph();
                         var.VarName --> list of tuples (n,k) where n indicates the number of a constraint, that var is part of and
                                         k is the number in the ordering of the variables from the constraints computed by buildConflictGraph();
                                         strongly intertwined with Equations and Cliques, as number n points to entry n of Equations and Cliques (initially)
            Cliques: should be initialized with the variable C from buildConflictGraph(), after applying any of the Clique Partition/Cover algorithms 
                     it will be a list of all cliques computed by these algorithms, i.e. each clique is again a list of names of gurobipy variables;
                     before the application of one of the algorithms it contains a list of lists of tuples. Look at buildConflictGraph() documentation of the variable C
                     for more details. vartoclique's tuples entry n points to the n'th entry  of Cliques.
            Equations: should be initialized with the variable l from buildConflictGraph(), thus is a list of lists of tuples; each entry corresponds 
                       to a constraint of the nominal IP and is a list of the variables represented by a tuple of three entries. The variables are ordered
                       by magnitude of their coefficients. For more details, look at the documentation of the variable l from buildConflictGraph().
                       vartoclique's tuples entry n points to the n'th entry  of Equations.
            vartobestclique: dictionnary; var.VarName --> best clique, i.e. the clique var will be contained in after the application of any Clique Partition/Cover algorithm
            vardegree: is only used by DSatur algorithm, is not tested extensively.
            vartovalue: same as with vardegree.
            numbering: should be initialized by variable numbering from buildConflictGraph(); bidirectional dictionnary var.VarName <--> number. is mainly
                       used as an attribute to keep track of all the variables of the nominal IP.
        
        Methods:
            FindCliqueCover: computes a Clique Cover based on the data derived by method buildConflictGraph(). tries to find maximal cliques. Needs a Conflict Graph computed by buildConflictGraph with 
                             adjacency=False.
            FindCliquePartitionFromCover: basically FindCliqueCover, but computes a clique partition instead of the cover, so already covered variables
                                          are not considered after being assigned to an "optimal" clique. Needs a Conflict Graph computed by buildConflictGraph with 
                                          adjacency=False.
            FindCliquePartitionDefault: computes the default clique partition, described in the master's thesis. Needs a Conflict Graph computed by buildConflictGraph with 
                                        adjacency=False.
            FindCliquePartitionDSatur: not fully tested, should not be relied upon. Needs a Conflict Graph computed by buildConflictGraph with 
                             adjacency=True.
            FindCliquePartitionDSaturWeighted: the same as FindCliquePartitionDSatur. 
    """
    def __init__(self):
        self.vartovar={}
        self.vartoclique={}
        self.Cliques=[]
        self.Equations=[]
        self.vartobestclique={}
        self.vardegree={}
        self.vartovalue={}
        self.numbering=bidict({})
    def FindCliqueCover(self):
        C=self.Cliques
        self.Cliques=[]
        l=self.Equations
        for var in self.numbering:
            try: 
                a=self.vartoclique[var]
            except:
                self.Cliques.append([var])
        for var in self.vartoclique:
            try:
                a=self.vartobestclique[var]
                #it can be assumed that the maximal clique of var has already been found
                continue
            except:
                self.vartobestclique[var]=[var]
                if len(self.vartoclique[var])>0:
                    for tup in self.vartoclique[var]:
                        k=tup[1]
                        n=tup[0]
                        if C[n]==[] or l[n][k][2]==0:    
                            #in C[n] is no maximal clique for the row available; for example x1+x2+x3<=2
                            continue
                        else:
                            for clis in C[n]:
                                #clis are tuples of integers, either (j, j) (all indices >=j are in clique)
                                #or (s, j_s) (s and all indices >=j_s are in clique).
                                #indices j_s are always part of a maximal clique in that row, i.e. (j,j).
                                #the situtation (s, j_s), where k>=j_s needs not be considered. the clique
                                #(j,j) will always be greater or equal in that case.
                                cliqueindex=clis[1]
                                if k >= cliqueindex:
                                    #k>=cliqueindex says var is in biggest clique
                                    length=len(l[n])
                                    clique=[]
                                    for i in range(cliqueindex, length):
                                        if l[n][i][2]==1:
                                            #append non-negated variable to clique only 
                                            clique.append(l[n][i][0])
                                    clique=list(set(clique))        
                                    if len(clique)> len(self.vartobestclique[var]):
                                        self.vartobestclique[var]=clique
                                elif k==clis[0]:
                                    clique=[]
                                    clique.append(l[n][k][0])
                                    length=len(l[n])
                                    for i in range(cliqueindex, length):
                                        if l[n][i][2]==1:
                                            clique.append(l[n][i][0])
                                    clique=list(set(clique)) 
                                    if len(clique)> len(self.vartobestclique[var]):
                                        self.vartobestclique[var]=clique
            #trying to find a maximal clique containing the current clique.
            #difficulties: often there is only a relation var1 --> var2 known, but not var2 --> var1
            #and the adjacency relation is only revealed piece by piece. 
            elems=[(v, len(self.vartoclique[v])) for v in self.vartobestclique[var]]
            elems=sorted(elems, key=lambda x: x[1])
            neighbours=set()
            cli=set(self.vartobestclique[var])
            #determine all neighbours of clique members as far as possible
            for w in elems:
                if abs(len(neighbours)-len(cli))/len(cli) < 0.005:
                    #interrupt search for maximal clique if said clique
                    #can at most be 0.5% larger, than current clique, it is for speedup
                    neighbours = cli
                    break
                try:
                    if type(self.vartovar[w[0]])==list:
                        pass
                except:
                    self.vartovar[w[0]]=[]
                t=time.time()
                for tup in self.vartoclique[w[0]]:
                    k=tup[1]
                    n=tup[0]    
                    if C[n]==[] or l[n][k][2]==0:    
                            #in C[n] is no maximal clique for the row available; for example if corresp. ineq. is x1+x2+x3<=2
                            continue
                    else:
                        for clis in C[n]:
                            cliqueindex=clis[1]
                            if k >= cliqueindex and cliqueindex == clis[0]:
                                # k>=cliqueinde and (clis[1]=)cliqueindex==clis[0] says var
                                # is in biggest clique (cliqueindex, cliqueindex)
                                length=len(l[n])
                                for i in range(cliqueindex, length):
                                    if l[n][i][2]==1:
                                        #determine all neighbours of w[0] (including w[0] itself)
                                        self.vartovar[w[0]].append(l[n][i][0])
                            elif k==clis[0]:
                                self.vartovar[w[0]].append(l[n][k][0])
                                length=len(l[n])
                                for i in range(cliqueindex, length):
                                    if l[n][i][2]==1:
                                        #add new neighbours to w[0] and vice versa 
                                        self.vartovar[w[0]].append(l[n][i][0])
                                        try:
                                            self.vartovar[l[n][i][0]].append(w[0])
                                        except:
                                            self.vartovar[l[n][i][0]] = [w[0]]
                            elif k >= cliqueindex and not cliqueindex==clis[0]:
                                if l[n][clis[0]][2]==1:
                                        #add new neighbours to w[0] and vice versa 
                                        try:
                                            self.vartovar[w[0]].append(l[n][clis[0]][0])
                                        except:
                                            self.vartovar[w[0]]=[l[n][clis[0]][0]]
                if neighbours==set():
                    neighbours=set(self.vartovar[w[0]])
                else:
                    #compute all intersections between neighbours
                    neighbours=neighbours & set(self.vartovar[w[0]])

                
            
            self.vartobestclique[var]=list(neighbours)

            for w in self.vartobestclique[var]:
                self.vartobestclique[w]=self.vartobestclique[var]
            if self.vartobestclique[var]==[]:
                self.vartobestclique[var]=[var]
            self.Cliques.append(self.vartobestclique[var])
    
    def FindCliquePartitionFromCover(self):
        C=self.Cliques
        self.Cliques=[]
        l=self.Equations
        for var in self.numbering:
            # assign a default best clique to every variable
            #if said variable does not occur in any constraint
            try: 
                a=self.vartoclique[var]
            except:
                self.Cliques.append([var])
        for var in self.vartoclique:
            # vartoclique points variables to their constraints, and indirectly to their cliques
            try:
                a=self.vartobestclique[var]
                #it can be assumed that the best clique of var has already been found
                # so var is already covered by partition
                continue
            except:
                self.vartobestclique[var]=[var]
                if len(self.vartoclique[var])>0:
                    for tup in self.vartoclique[var]:
                        k=tup[1]
                        n=tup[0]
                        if C[n]==[] or l[n][k][2]==0:    
                            #in C[n] is no maximal clique for the row available; for example x1+x2+x3<=2
                            #or var occurs only negated in constraint number n
                            continue
                        else:
                            for clis in C[n]:
                                #clis are tuples of integers, either (j, j) (all indices >=j are in clique)
                                #or (s, j_s) (s and all indices >=j_s are in clique).
                                #indices j_s are always part of a maximal clique in that row (j,j).
                                #the situtation (s, j_s), where k>=j_s needs not be considered. the clique
                                #(j,j) will alway be greater or equal in that case. 
                                cliqueindex=clis[1]
                                if k >= cliqueindex:
                                    #k>=cliqueindex says var is in biggest clique
                                    length=len(l[n])
                                    clique=[]
                                    for i in range(cliqueindex, length):
                                        if l[n][i][2]==1:
                                            #only consider unnegated variables from the clique
                                            try:
                                                #if the considered variable is already covered by an optimal clique
                                                #it must not be appended to current clique
                                                #exception is var itself!!
                                                a=self.vartobestclique[l[n][i][0]]
                                                if l[n][i][0]==var:
                                                    clique.append(l[n][i][0])
                                            except:    
                                                #append non-negated variable to clique only 
                                                #this variable is not yet covered by an optimal clique
                                                clique.append(l[n][i][0])
                                    #remove duplicates
                                    clique=list(set(clique))        
                                    if len(clique)> len(self.vartobestclique[var]):
                                        self.vartobestclique[var]=clique
                                elif k==clis[0]:
                                    #situation where tuple is (s, j_s), s index of var, so the clique is
                                    # {s, j_s, j_s + 1, ...}, without indices of negated variables
                                    clique=[]
                                    clique.append(l[n][k][0])
                                    length=len(l[n])
                                    for i in range(cliqueindex, length):
                                        if l[n][i][2]==1:
                                            try:
                                                a=self.vartobestclique[l[n][i][0]]
                                            except:
                                                clique.append(l[n][i][0])
                                    clique=list(set(clique)) 
                                    if len(clique)> len(self.vartobestclique[var]):
                                        self.vartobestclique[var]=clique
            #trying to find the maximal clique containing the current clique.
            #difficulties: often there is only a relation var1 --> var2 known, but not var2 --> var1
            #and the adjacency relation is only revealed piece by piece.
            elems=[(v, len(self.vartoclique[v])) for v in self.vartobestclique[var]]
            elems=sorted(elems, key=lambda x: x[1])
            neighbours=set()
            cli=set(self.vartobestclique[var])
            #determine all neighbours of clique members as far as possible
            #the order of computations is hopefully chosen such that
            #an interruption of the loop below is early, if no maximal clique exists
            for w in elems:
                if abs(len(neighbours)-len(cli))/len(cli) < 0.005:
                    #interrupt search for maximal clique if said clique
                    #can at most be 0.5% larger, than current clique.
                    #this is for speed up.
                    neighbours = cli
                    break
                #the following exception makes sure, that var is always in the neighbourhood
                #because otherwise it might be a problem, that vartobestclique[var] is already set
                try:
                    if type(self.vartovar[w[0]])==list:
                        pass
                except:
                    self.vartovar[w[0]]=[var]
                t=time.time()
                for tup in self.vartoclique[w[0]]:
                    k=tup[1]
                    n=tup[0]    
                    if C[n]==[] or l[n][k][2]==0:    
                        #in C[n] is no maximal clique for the row available; for example if corresp. ineq. is x1+x2+x3<=2
                        continue
                    else:
                        for clis in C[n]:
                            cliqueindex=clis[1]
                            if k >= cliqueindex and cliqueindex == clis[0]:
                                # k>=cliqueinde and (clis[1]=)cliqueindex==clis[0 says var
                                # is in biggest clique (cliqueindex, cliqueindex)
                                length=len(l[n])
                                for i in range(cliqueindex, length):
                                    if l[n][i][2]==1:
                                        try:
                                            #this statement is non-sensical, but if the best clique of the variable
                                            #l[n][i][0] is already found, there will not be an exception; 
                                            #if not the ecept statement will be executed
                                            if not self.vartobestclique[l[n][i][0]]==var:
                                                a=self.vartobestclique[l[n][i][0]]
                                        except:
                                            #determine all neighbours of w[0] (including w[0] itself)
                                            self.vartovar[w[0]].append(l[n][i][0])
                            elif k==clis[0]:
                                self.vartovar[w[0]].append(l[n][k][0])
                                length=len(l[n])
                                for i in range(cliqueindex, length):
                                    if l[n][i][2]==1:
                                        try:
                                            if not self.vartobestclique[l[n][i][0]]==var:
                                                a=self.vartobestclique[l[n][i][0]]
                                        except:
                                            #add new neighbours to w[0] and vice versa 
                                            self.vartovar[w[0]].append(l[n][i][0])
                                            try:
                                                self.vartovar[l[n][i][0]].append(w[0])
                                            except:
                                                self.vartovar[l[n][i][0]] = [w[0]]
                            elif k >= cliqueindex and not cliqueindex==clis[0]:
                                if l[n][clis[0]][2]==1:
                                    try:
                                        if not self.vartobestclique[l[n][i][0]]==var:
                                            a=self.vartobestclique[l[n][i][0]]
                                    except:
                                        #add new neighbours to w[0] and vice versa 
                                        try:
                                            self.vartovar[w[0]].append(l[n][clis[0]][0])
                                        except:
                                            self.vartovar[w[0]]=[l[n][clis[0]][0]]

                if neighbours==set():
                    neighbours=set(self.vartovar[w[0]]) | set([var])
                else:
                    #neighbours is the set of common neighbours of all current clique members
                    #so here the set intersection is formed
                    neighbours=neighbours & set(self.vartovar[w[0]])



            self.vartobestclique[var]=list(neighbours)

            for w in self.vartobestclique[var]:
                self.vartobestclique[w]=self.vartobestclique[var]
            if self.vartobestclique[var]==[]:
                #may occur, if var is not in any constraint, or is not in any clique
                #of any constraint. is actually already caught several times, but best to be safe.
                self.vartobestclique[var]=[var]
            self.Cliques.append(self.vartobestclique[var])
            
    def FindCliquePartitionDefault(self):
        C=self.Cliques
        self.Cliques=[]
        l=self.Equations
        for var in self.numbering:
            #if the variable does not show up in any inequality
            #there will not be any entry var-->clique.
            #this is caught in exception
            try: 
                a=self.vartoclique[var]
            except:
                self.Cliques.append([var])
        for var in self.vartoclique:
            t=time.time()
            try:
                a=self.vartobestclique[var]
                #maximal clique of var has already been found
                continue
            except:
                self.vartobestclique[var]=[var]
                if len(self.vartoclique[var])>0:
                    for tup in self.vartoclique[var]:
                        k=tup[1]
                        n=tup[0]
                        if C[n]==[] or l[n][k][2]==0:    
                            #in C[n] is no maximal clique for the row available; for example x1+x2+x3<=2;
                            #or the variable appears only negated, i.e. x1 + (1-x2) <= 1
                            continue
                        else:
                            cliqueindex=C[n][0][0]
                            #C[n][0] is the first and biggest clique extracted from an inequality;
                            #for example {x2, x3} from x1+2x2+2x3<=3
                            if k >= cliqueindex:
                                #k>=cliqueindex says var is in biggest clique
                                length=len(l[n])
                                clique=[]
                                for i in range(cliqueindex, length):
                                    if l[n][i][2]==1:
                                        try: 
                                            #if the best clique has already been found
                                            #the variable will not be added to the clique
                                            a=self.vartobestclique[l[n][i][0]]
                                            if l[n][i][0] == var:
                                                clique.append(l[n][i][0])  
                                        except:
                                            #append variable to clique only 
                                            clique.append(l[n][i][0])
                                if len(clique)> len(self.vartobestclique[var]):
                                    self.vartobestclique[var]=clique
            best=set(self.vartobestclique[var])
            lis=self.vartobestclique[var]
            self.vartobestclique[var]=best 
            for w in lis:
                #set the best clique for the other variables from that clique as well
                try:
                    a=self.vartobestclique[w]
                    po=best-a
                    if po:
                        #if po is not empty, that means that w has a best clique
                        #assigned to it. remove this clique from var's best clique
                        self.vartobestclique[var]=po | set([var])
                    else:
                        self.vartobestclique[w]=self.vartobestclique[var]        
                except:
                    self.vartobestclique[w]=self.vartobestclique[var]
            self.Cliques.append(list(self.vartobestclique[var]))   
                                    
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
            n=[]
            for v in range(len(self.vartovar[self.numbering[mini[2]]])):
                #print(v)
                #print(self.vartovar[self.numbering[mini[2]]][v])
                if self.vartovar[self.numbering[mini[2]]][v] == 1:
                    n.append(v)
            
            n=set(n)
            #n=set([v for v in range(len(self.vartovar[self.numbering[mini[2]]])) if self.vartovar[self.numbering[mini[2]]][v] == 1])
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
            self.vartobestclique[mini[2]]=mi
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

            
            
##############################################################################
#                     Robust Formulations                                    #
##############################################################################    

    
def RobustFormulation(g, gamma, withcliques=False, cliquemethod="none" , cHat={}, weights={}):
    """
    Creates a Robust Formulation from a combinatorial integer program, from a
    clique partition/cover computed with the help of the ConflictGraph object 
    min c^T*x
    s.t. A*x <= b
        x in {0,1}^n
    
    -->
    
    min c^T*x + gamma*z + p1 + ... + pn
    s.t. A*x
        cHat[xi]*xi <= z + pi ; for all i=1,..,n 
      ( sum_{q in Clique Q} cHat[xq]*xq <= z + sum_{q in Clique Q} pq ; for a Clique Partition/Cover Q)
         x in {0,1}^n , z, pi >= 0 
         
    Parameters
    ----------
    g : combinatorial ILP (integer linear program)
    gamma : parameter from robust objective function 
    withcliques : if True, one variable p_Q replaces sum_{q in Clique Q} pq in the robust formulation
     The default is False.
    cliquemethod : Describes the kind of method to compute a clique partition/cover
                   "none": clique partition {{pi} : i=1,...,n} --> standard robust formulation
                   "default": clique partition computed by ConflictGraph.FindCliquePartitionDefault()
                   "dsatur": clique partition computed by ConflictGraph.FindCliquePartitionDSatur(), based on DSatur-Algorithm (not advised to use)
                   "cover":clique cover computed by ConflictGraph.FindCliqueCover()
                   "coverpartition": clique partition computed by ConflictGraph.FindCliquePartitionFromCover(); it is the clique partition
                                     computed from the clique cover ConflictGraph.FindCliqueCover() 
         The default is "none".
    cHat : Dictionnary which maps gurobipi variable name --> cHat value from the robust formulation
         The default is {}. If cHat={} is given, cHat is then set to 0 for all variables 
    weights : dictionnary with gurobipi variable name --> real number, used to build a Conflict Graph on variables with a weight above cutoff
         The default is {}. Only used for dsaturw, so better not use. 

    Returns
    -------
    cHat 
    pvalues : if withcliques is False : a dictionnary variable name --> p variable corresponding to that variable, for every variable.
              if withcliques is True : a dictionnary with variable name --> p variable, for every clique from the clique partition.
              p variables will have a naming convention, if withcliques=False. they will be 'p' + <combinatorial variable name>.
    z : z-variable from robust formulation, variable name is 'z'.

    """
    originvars=g.getVars()
    pvalues={}
    robEq={}
    objective=g.getObjective()
    objective=g.ModelSense*objective    
    Cliques=[]
    if cliquemethod=="none":
        Cliques=[[v.VarName] for v in originvars]
    elif cliquemethod=="default":
        G=ConflictGraph()
        [G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(g, False)
        G.FindCliquePartitionDefault()
        Cliques=G.Cliques
    elif cliquemethod=="dsatur":
        G=ConflictGraph()
        [G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(g)
        G.FindCliquePartitionDSatur()
        Cliques=G.Cliques
    elif cliquemethod=="cover":
        G=ConflictGraph()
        [G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(g, False)
        G.FindCliqueCover()
        Cliques=G.Cliques  
    elif cliquemethod=="coverpartition":
        G=ConflictGraph()
        [G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildConflictGraph(g, False)
        G.FindCliquePartitionFromCover()
        Cliques=G.Cliques 
    elif cliquemethod=="dsaturw":
        G=ConflictGraph()
        [G.Cliques,G.Equations,G.vartovar,G.vartoclique, G.numbering]=buildWeightedConflictGraph(g, 'z', weights, 0.01)
        G.FindCliquePartitionDSatur()
        Cliques=G.Cliques
        #weigthed Conflict Graphs only compute the CG on variables of relevant weight, so G.Cliques is not an actual 
        #Clique partition
        for var in originvars:
            try:
                a=G.vartobestclique[var.VarName]
            except:
                Cliques.append([var.VarName])
            
    objVars={}
    i=0
    while True:
        try:
            objVars[objective.getVar(i).VarName]=objective.getCoeff(i)
            i+=1
        except:
            break
    for var in originvars:
        try:
            if cHat[var.VarName] >= 0:
                pass
        except:
            try:
                ####keep this random option for now
                r=rand.choice([0.2,0.4,0.6,0.8])
                if abs(objVars[var]) > 0:
                    cHat[var.VarName]=abs(r*objVars[var.VarName])
                    cHat[var.VarName]=0
                else:
                    cHat[var.VarName]=abs(r)
                    cHat[var.VarName]=0
                    
            except:
                r=rand.random()
                cHat[var.VarName]=r
                cHat[var.VarName]=0

    z=g.addVar(lb=0.0,vtype=GRB.CONTINUOUS, name='z')
    g.update()
    for cli in Cliques:
        if withcliques:
            pvalues[cli[0]]=g.addVar(lb=0.0, vtype=GRB.CONTINUOUS)
            expr1=pvalues[cli[0]]+z
            expr2=0
            for v in cli:
                expr2=expr2+cHat[v]*g.getVarByName(v)
        else:
            for v in cli:
                try:
                    a=pvalues[v]
                except:
                    nam=str('p'+v)
                    pvalues[v]=g.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=nam)
            expr1=sum(pvalues[v] for v in cli) +z
            expr2=0
            expr2=sum(cHat[v]*g.getVarByName(v) for v in cli)
        g.addConstr(expr1 >= expr2)
    expr=sum(pvalues.values())
    objective=g.setObjective(objective+gamma*z+expr, GRB.MINIMIZE)
    g.update()
    return cHat, pvalues, z

def ExtendedRobustFormulation(g, z, pvalues, cHat, weights):
    """
    Extends a given Robust Formulation by Clique Inequalities with Cliques 
    from a separated Conflict Graph. is designed to work with weights given by objective values of a 
    previous solution of g. should not be called directly.
    Parameters
    ----------
    g : Gurobi model of a Robust Formulation
    z : Gurobi variable 'z' from Robust Formulation
    pvalues : dictionnary of Gurobi variables of all 'p'-variables from Robust Formulation
    cHat : dictionary of worst case deviations for Robust Formulation (Gurobi.var.name --> value)
    weights : dictionary of weights to compute a weighted Conflict Graph (Gurobi.var.name --> value) 

    Extends a given Robust Formulation g by Clique Inequalities with Cliques 
    from a weighted Conflict Graph, possibly with weights given by objective values of a 
    previous solution of  g.

    """
    G=ConflictGraph()
    [G.Cliques,G.Equations,G.vartovar,G.vartoclique,G.numbering]=buildWeightedConflictGraph(g, z, weights, 0.01, False)
    G.FindCliqueCover()
    Cliques=G.Cliques
    for cli in Cliques:
        expr1=sum(g.getVarByName(pvalues[v].VarName) for v in cli) +g.getVarByName(z)
        expr2=0
        for i in range(len(cli)):
            expr2+=cHat[cli[i]]*g.getVarByName(cli[i])
        g.addConstr(expr1 >= expr2)
    g.update()
    

def extendMultipleTimes(g, gamma, n, z='z', pvalues={}, cHat={}):
    """
    Extends a given nominal combinatorial integer instance with Clique Inequalities from the separated Conflict Graph n-times.
    

    Parameters
    ----------
    g : gurobipy instance of non-robust model, non-relaxed, non-optimized
    gamma: 'gamma'-value from Robust Formulation 
    z : Gurobi variable 'z' from Robust Formulation
    pvalues : dictionary of Gurobi variables of all 'p'-variables from Robust Formulation.
              it is not advised to use pvalues other than {}, because only then the program expects g to be robust. 
              was supposed to be a feature, but is more of a bug now. 
    cHat: dictionary of worst case deviations for Robust Formulation (Gurobi.var.name --> value) 
    n : number of extensions to be applied to the model

    Returns
    -------
    The objective value after the final extension. 

    """
    ps=set()
    if pvalues:
        for t in pvalues:
            ps= ps | set([t])
        originvarnames=[y for y in ps]
    m=g.copy()
    #build a standard robust formulation, without cliques or anything
    if not pvalues:
        originvarnames=[y.VarName for y in g.getVars()]
        cHat, pvalues, z = RobustFormulation(g, gamma, False, "none",  cHat)
    g=g.relax()
    g.optimize()
    for i in range(n):
        weights={}
        for v in originvarnames:
            # get all objective values of the original formulation and form the dictionary weights
            weights[v]=(g.getVarByName(v)).x
        ExtendedRobustFormulation(g, z.VarName, pvalues, cHat, weights)
        g=g.relax()
        g.optimize()
    return g.ObjVal

def addKnapsack(g, gamma, z, pvalues, cHat):
    """
    Extends a given Robust Formulation g by recycled Knapsack Inequalities from its nominal problem. 
    Parameters
    ----------
    g : Gurobi model of a Robust Formulation
    gamma: gamma value of robust formulation
    z : Gurobi variable name(!) of 'z' from Robust Formulation 
    pvalues : dictionnary of Gurobi variable names(!) of all 'p'-variables from Robust Formulation (var.VarName --> 'p'+var.VarName)
    cHat : dictionary of worst case deviations for Robust Formulation (Gurobi.var.name --> value)

    """
    constrs=g.getConstrs()
    for con in range(0,len(constrs)):
        adjustb=0
        b=constrs[con].RHS
        c=g.getRow(constrs[con])
        #print(c, b)
        expr1=0
        expr2=0
        #print(n, c)
        typ=constrs[con].sense
        encounteredz=False
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
            var=c.getVar(i)
            if var.VarName==z:
                #ignore robust constraints
                encounteredz=True
                break
            #inverse the sign of the coefficient
            if coff > 0:
                try:
                    expr1+=cHat[var.VarName]*coff*var
                    expr2+=coff*g.getVarByName(pvalues[var.VarName])
                except:
                    # if var is a p-variable, ignore constraint as well
                    encounteredz=True
                    break
            elif coff < 0:
                adjustb+=coff
        if encounteredz:
            continue
        expr2+=(b - adjustb)*g.getVarByName(z)
        g.addConstr(expr1 <= expr2)
    g.update()
                
def ExtendCover(g, gamma, cHat):
    """
    Builds a Robust Formulation and extends it by recycled Clique Inequalities, that form a Clique Cover of Conflict Graph. 
    Parameters
    ----------
    g : Gurobi model of a combinatorial integer program.
    gamma: gamma value of robust formulation
    cHat : dictionary of worst case deviations for Robust Formulation (Gurobi.var.name --> value)

    """
    cHat, pvalues, z = RobustFormulation(g, gamma, False, "cover", cHat)
    m=g.relax()
    m.optimize()
    for var in pvalues:
        expr1=g.getVarByName(pvalues[var].VarName) +g.getVarByName(z.VarName)
        expr2=0
        expr2=cHat[var]*g.getVarByName(var)
        g.addConstr(expr1 >= expr2)
    g.update()
    violcons=[]
    return violcons, m

                          
