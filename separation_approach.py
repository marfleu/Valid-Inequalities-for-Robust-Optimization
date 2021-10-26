# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 08:46:36 2021

@author: User
"""

def separateConflictGraph(g, z, weights, cutoff, cHat):
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
    #Vars=[y for y in g.getVars() if weights[y.VarName]>cutoff]
    m=len(Vars)
    #initialise map variables <--> indices
    for var in Vars:
        numbering[var]=index
        vartoclique[var]=[]
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
        coefficients={}
        objectives={}
        for i in range(0,c.size()):  
            #permute through all variables in the constraint
            coff=c.getCoeff(i)*typ   
            #inverse the sign of the coefficient
            var=c.getVar(i)
            coefficients[var.VarName]=coff
            coff2=weights[z] + weights['p'+var.VarName] - weights[var.VarName]
            objectives[var.VarName]=coff2
            coff=coff2/coff
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
                elif coff < 0 and weights[var.VarName] >= cutoff:
                    adjustb+=coff
                    #l[n].append([var.VarName,-coff,0])
            except:
                continue
        if encounteredz:
            #go to next constraint, if current constraint contains z-variable
            encounteredz=False
            continue
        l[n]=sorted(l[n],key=lambda x: x[1])
        #initialize links var --> clique, var --> var:
        for k in range(0,len(l[n])):
            try:
                vartoclique[l[n][k][0]].append((n,k))
            except:
                vartoclique[l[n][k][0]]=[(n,k)]

                
        b-=adjustb
        up=len(l[n])-2
        if up < 0:
            C.append(Temp)
            n+=1
            continue
        LHS=0
        OBJ=0
        ind=-1
        mini=(0,coefficients[l[n][0][0]])
        for k in range(0,len(l[n])):
            LHS+=coefficients[l[n][k][0]]
            OBJ+=objectives[l[n][k][0]]
            if LHS > b and OBJ < weights[z]:
                
                if coefficients[l[n][k][0]] < mini[1]:
                    mini[0]=k
                    mini[1]=coefficients[l[n][k][0]]
                ind=k
                break
        if ind>0:
            Temp.append((0, ind))
            cover=sum(cHat[l[n][j][0]]*g.getVarByName(l[n][j][0]) for j in range(0, ind + 1))
            RHS=sum(g.getVarByName('p'+l[n][j][0]) for j in range(0, ind + 1))
            for k in range(ind, len(l[n])):
                if coefficients[l[n][k][0]] > mini[1]:
                    cover+=cHat[l[n][k][0]]*g.getVarByName(l[n][k][0]) 
                    RHS+=g.getVarByName('p'+l[n][k][0])
            RHS+=(ind-1)*g.getVarByName(z)
            g.addConstr(LHS <= RHS)            
        C.append(Temp)
        n+=1
    return [C,l,vartovar,vartoclique, numbering]


def ExtendedRobustFormulation(g, z, pvalues, cHat, weights):
    """
    Extends a given Robust Formulation by Clique Inequalities with Cliques 
    from a weighted Conflict Graph, possibly with weights given by objective values of a 
    previous solution of  g.
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
    [G.Cliques,G.Equations,G.vartovar,G.vartoclique,G.numbering]=separateConflictGraph(g, z, weights, 0.01, cHat)
    #G.FindCliquePartitionDSatur()
    G.FindCliqueCover()
    Cliques=G.Cliques
    for cli in Cliques:
        #print("hier cli ", cli)
        expr1=sum(g.getVarByName(pvalues[v].VarName) for v in cli) +g.getVarByName(z)
        expr2=0
        for i in range(len(cli)):
            #print(cHat[cli[i]])
            #print(g.getVarByName(cli[i]))
            expr2+=cHat[cli[i]]*g.getVarByName(cli[i])
        #expr2=sum(cHat[v]*g.getVarByName(v) for v in cli)
        g.addConstr(expr1 >= expr2)
    g.update()

def extendMultipleTimes(g, gamma, n, z='z', pvalues={}, cHat={}):
"""


Parameters
----------
g : gurobipy instance of non-robust model, non-relaxed, non-optimized
gamma: 'gamma'-value from Robust Formulation 
z : Gurobi variable 'z' from Robust Formulation
pvalues : dictionary of Gurobi variables of all 'p'-variables from Robust Formulation
cHat: dictionary of worst case deviations for Robust Formulation (Gurobi.var.name --> value) 
n : number of extensions to be applied to the model

Returns
-------
None.

"""
ps=set()
if pvalues:
    for t in pvalues:
        ps= ps | set([t])
    originvarnames=[y for y in ps]
#originvarnames=[y for y in originvarnames if not y in ps]
#print(originvarnames)
m=g.copy()
#build a standard robust formulation, without cliques or anything
if not pvalues:
    originvarnames=[y.VarName for y in g.getVars()]
    cHat, pvalues, z = RobustFormulation(g, gamma, False, "none",  cHat)
print(z)
g=g.relax()
g.optimize()
for i in range(n):
    weights={}
    for v in g.getVars():
        # get all objective values of the original formulation and form the dictionary weights
        weights[v.VarName]=(g.getVarByName(v.VarName)).x
    ExtendedRobustFormulation(g, z.VarName, pvalues, cHat, weights)
    g=g.relax()
    g.optimize()
return g.ObjVal