# -*- coding: utf-8 -*-
"""
First sketch of a separation approach based on general Cover Inequalities.
"""
from modelreading import modelreading as mr
import gurobipy as gp


def separateConflictGraph(g, z, weights, cutoff, cHat):

    constrs=g.getConstrs()
    n=0
    l=[]
    C=[]
    vartoclique={}
    vartovar={}
    index=0
    # numbering=bidict({})
    Vars=[]
    encounteredz=False
    for y in g.getVars():
        try:
            if weights[y.VarName]>cutoff:
                Vars.append(y.VarName)
        except:
            continue
    #Vars=[y for y in g.getVars() if weights[y.VarName]>cutoff]
    #initialise map variables <--> indices
    # for var in Vars:
    #     numbering[var]=index
    #     vartoclique[var]=[]
    #     index+=1
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

            if var.VarName == z.VarName:
                # constraints, which  contain z variable, shall be ignored
                l.pop()
                encounteredz=True
                break
            coefficients[var.VarName]=coff
            coff2=weights[z.VarName] + weights['p'+var.VarName] - cHat[var.VarName]*weights[var.VarName]
            objectives[var.VarName]=coff2
            coff=coff2/coff
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
            if coefficients[l[n][k][0]] < mini[1]:
                    mini[0]=k
                    mini[1]=coefficients[l[n][k][0]]
            if LHS > b and OBJ < weights[z.VarName]:
                ind=k
                break
            elif LHS > b:
                ind=k
        if ind>0:
            Temp.append((0, ind))
            cover=sum(cHat[l[n][j][0]]*g.getVarByName(l[n][j][0]) for j in range(0, ind + 1))
            RHS=sum(g.getVarByName('p'+l[n][j][0]) for j in range(0, ind + 1))
            for k in range(ind, len(l[n])):
                if coefficients[l[n][k][0]] >= mini[1]:
                    cover+=cHat[l[n][k][0]]*g.getVarByName(l[n][k][0]) 
                    RHS+=g.getVarByName('p'+l[n][k][0])
            RHS+=(ind)*g.getVarByName(z.VarName)
            g.addConstr(cover <= RHS)            
        C.append(Temp)
        n+=1
    g.update()
    return [C,l,vartovar,vartoclique]


def ExtendedRobustFormulation(g, z, pvalues, cHat, weights):
    G=mr.ConflictGraph()
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
        cHat, pvalues, z = mr.RobustFormulation(g, gamma, False, "none",  cHat)
    print(z)
    g=g.relax()
    g.optimize()
    for i in range(n):
        weights={}
        for v in g.getVars():
            # get all objective values of the original formulation and form the dictionary weights
            weights[v.VarName]=(g.getVarByName(v.VarName)).x
        G=mr.ConflictGraph()
        [G.Cliques,G.Equations,G.vartovar,G.vartoclique]=separateConflictGraph(g, z, weights, -0.01, cHat)
        g=g.relax()
        g.optimize()
    return g.ObjVal

gamma, cHat = mr.readInstance('C:/Users/User/Documents/Masterarbeit/data/neos-780889_g=40_d=45-55_r=0.txt')
dHat=cHat
m4 = gp.read('C:/Users/User/Documents/Masterarbeit/neos-780889.mps')
m5=m4.copy()
obj=extendMultipleTimes(m4, gamma, 6, 'z', {}, cHat)
mr.RobustFormulation(m5, gamma, False, 'default', cHat)
g5=m5.relax()
g5.optimize()