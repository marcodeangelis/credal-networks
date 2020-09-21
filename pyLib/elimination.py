
'''
Created on Mon Sep  2 11:11:54 2019
Author: Marco De Angelis
github.com/marcodeangelis

Code for variable elimination.
'''

from pandas import DataFrame # only used to display tables
from numpy import array # used for vector add (multiply and divide)
from graphviz import Digraph # only used to display graph
import itertools # used to obtain variable permutation

class BeliefNetwork():
    def __str__(self): #'return'
        return 'return'
    def __repr__(self):
        return 'print' #'print'
    def __init__(self,*args):
        self.__graph = {}
        self.__nodes = {}
        for a in args:
            self.__nodes[a['ID']] = Node(a, network=self)
            self.__graph[a['ID']] = a['Parents']
        self.n = self.__nodes.copy()
        self.f = self.factors()
    def factors(self):
        f = {}
        for n in self.__nodes.keys():
            f[n] = self.__nodes[n].Factor()
        return f
    def nodes(self):
        return self.__nodes
    def listNodes(self):
        return [ki for ki in self.n.keys()]
    def DAG(self):
        return self.__graph
    def displayGraph(self,nodeattr=None,graphattr=None): # This requires GraphViz
        if nodeattr is None:
            nodeattr={'color': 'blue',
                        'style': 'solid',
                        'shape':'circle', #'plaintext','ellipse'
                        'fontcolor':'green',
                        'fontname':'Arial',
                        'fontsize':'18'}
        if graphattr is None:
            graphattr={'bgcolor':'transparent'}
        u = Digraph('BN_example', filename='BN_example.gv', # https://graphviz.org/doc/info/attrs.html
                    node_attr=nodeattr,
                    graph_attr=graphattr,
                    format='eps')
        u.attr(size='6,6')
        edgecol = 'yellow'
        itergraph = iter(self.__graph)
        for k,v in self.__graph.items():
            destination=next(itergraph)
            origin = self.__graph[destination]
            for o in origin:
                u.edge(o,destination,color=edgecol)
        return u
    def joint(self,*nodes):
        opto = self.optimalOrder(*nodes) # variables not in the query arranged in the optimal order
        ELIMINATED_variables = []
        USED_nodes = []
        f = None
        for v in opto: # proceed with the elimination process
            nodes_containing_v = self.containing(v, butnot=ELIMINATED_variables)
            factors_containing_v = [ncv.Factor() for ncv in nodes_containing_v]
            USED_nodes += [nv._Node__child for nv in nodes_containing_v]
            if f is None:
                factor_v = self.multiply_nary(factors_containing_v)
            else:
                factors_containing_v += [f]
                factor_v = self.multiply_nary(factors_containing_v)
            f = factor_v.sumout(v)
            ELIMINATED_variables.append(v)
        for n in nodes:
            if n not in USED_nodes:
                if f is not None:
                    f *= self.f[n]
                else:
                    f = self.f[n]
        return f
    def marginal(self,node):
        return self.joint(node)
    def multiply_nary(self,args): # static method
        f = args[0]
        for a in args[1:]:
            f = f * a
        return f
    def premultiply_nary(self,args): # static method
        m = Factor()
        for a in args:
            m = m ** a
        return m
    def containing(self,v,butnot=[]): # returns the list of node (Factors) in which the variable v appears
        L = []
        for n in self.__nodes.keys():
            VARS = self.__nodes[n]._Node__VARS
            if len(butnot)>0:
                if (not(any(x in VARS for x in butnot))) & (v in VARS):
                    L.append(self.n[n])
            else:
                if v in VARS:
                    L.append(self.n[n])
        return L
    def querySize(self,*nodes): # This algorithm computes the complexity of all possible permutations of eliminating variables
        everyvars = set([ki for ki in self.n.keys()]) # {'A','B','C','D','E'}
        queryvars = nodes # {'A','C','E'}  # https://stackoverflow.com/questions/12088089/python-list-concatenation-efficiency
        leftovers = everyvars.difference(queryvars) # {'D', 'B'} these the variables to eliminate
        perm = list(itertools.permutations(leftovers))
        if len(leftovers)>10: # more than 3628800 permutations
            print('Cap the nummber of permutaions!')
        SIZE_INFO = {}
        OPTIM = []
        min_f_size = float('inf')
        for p in perm:
            f = Factor()
            tot_f_size = 0
            used_V = []
            SIZES = []
            for v in p:
                nodes_containing_v = self.containing(v, butnot=used_V)
                factors_containing_v = [ncv.Factor() for ncv in nodes_containing_v]
                pre_factor_v = self.premultiply_nary(factors_containing_v)
                f = f ** pre_factor_v
                f_size =  f.size()
                SIZES.append(f_size)
                tot_f_size = tot_f_size + f_size
                f = pre_factor_v.pop(v)
                used_V.append(v)
            if tot_f_size < min_f_size: # update maximum size of factor
                min_f_size = tot_f_size
                OPTIM.append(p)
            SIZE_INFO[p]={'factor sizes':SIZES,'total size':tot_f_size}
        return SIZE_INFO, OPTIM[-1]
    def queryOrdering(self, *nodes):
        everyvars = set([ki for ki in self.n.keys()]) # {'A','B','C','D','E'}
        queryvars = nodes # {'A','C','E'}
        leftovers = everyvars.difference(queryvars) # {'D', 'B'} these the variables to eliminate
        perm = list(itertools.permutations(leftovers))
        return perm
    def optimalOrder(self,*nodes):
        _,b = self.querySize(*nodes)
        return b
    def query(self,target,given):
        querytrain = given+[target] # https://stackoverflow.com/questions/12088089/python-list-concatenation-efficiency
        f = self.joint(*querytrain)
        f = f.normalize(target)
        f = f.order(*querytrain)
        return f




class Node():
    def __str__(self): # return
        hi = iter(self.__hashtable)
        x=[]
        x_append=x.append
        EOF=False
        while not(EOF):
            try:
                hkey = next(hi)
                x_append(str(hkey)+': '+str(self.__hashtable[hkey]))
            except StopIteration: # end of hashtable reached
                EOF=True
        return '\n'.join(x)
    def __repr__(self): # print
        hi = iter(self.__hashtable)
        x=[]
        x_append=x.append
        EOF=False
        while not(EOF):
            try:
                hkey = next(hi)
                x_append(str(hkey)+': '+str(self.__hashtable[hkey]))
            except StopIteration: # end of hashtable reached
                EOF=True
        return '\n'.join(x)
    def __init__(self,*args,network=None):
        self.__network = None
        if network is not None:
            self.__network = network
        self.__input = args[0]
        self.__child = self.__input['ID']    # This property could also be named "node", as this is the name of the node itself
        self.__parents = self.__input['Parents']
        self.__halfCPT = self.__input['CPT']
        self.__VARS = [self.__child]+self.__parents
        self.__N = len(self.__VARS)
        self.__description = self.__input['Description']
        self.__binaryTREE = self.binaryTree()
        self.completeCPT()
        self.__header = ''      # {string}
        self.makeStringHeader()
        self.__hashtable = {}   # {dictionary}
        self.makeHashTable()    # this generates the object hashtable which will be used to inject the evidence
        self.__varIndex = {}    # {dictionary}
        self.makeVarIndex()
        # self.__pandasCPT= None  # {Pandas DataFrame}
        # self.makePandasTABLE()
        self.__Factor = Factor(hashtable=self.__hashtable.copy())
        # End of constructor
    def show(self):
        return self.makePandasTABLE()
    def completeCPT(self):
        CPT1 = self.__halfCPT  # CPT values beginning with child
        CPT2 = [1-p for p in CPT1]
        self.__CPT = CPT1+CPT2
    def binaryTree(self):
            N = self.__N
            TreeTF = []
            for i in range(N):
                j = (N-1)-i
                a = 2**j
                b = 2**(j+1)
                TreeTF.append(([True]*a+[False]*a)*(int(2**N/b)))
            return [tr for tr in zip(*TreeTF)]
    def makeVarIndex(self):
        if len(self.__varIndex)==0:
            d = {}
            for i,v in enumerate(self.__VARS):
                d[v] = i
            self.__varIndex = d
    def makePandasTABLE(self):
        table = self.__table
        header= self.__header
        N = self.__N
        df = DataFrame(table[1:], columns=header, index=[i+1 for i in range(2**N)])
        return df
    def makeStringHeader(self):
        if len(self.__header)==0:
            parents = ''
            for k in self.__parents:
                parents+=k
                parents+=','
            if len(self.__parents)>0:
                lastColu = 'P('+self.__child+'|'+parents[:-1]+')'
            else:
                lastColu = 'P('+self.__child+')'
            self.__header = [self.__child] + self.__parents + [lastColu]
            self.__headerValues = lastColu
    def makeHashTable(self):
        if len(self.__hashtable)==0:
            table = [list(t)+[p] for t,p in zip(self.__binaryTREE,self.__CPT)]
            self.__hashtable = {tuple(self.__VARS):self.__headerValues}
            for t,p in zip(self.__binaryTREE,self.__CPT):
                self.__hashtable[t] = p
            self.__table = [self.__header]+table
    def Factor(self):
        return self.__Factor
    def CPT(self):
        return self.show()
    def Description(self):
        return self.__description
    def __or__(self,other):
        a = self.__child
        b = [o._Node__child for o in other]
        return self.__network.query(a,b)
    def __and__(self,other):
        a = self.__child
        b = other._Node__child
        return self.__network.joint(a,b)



class Factor():
    def __str__(self):
        hi = iter(self.__hashtable)
        x=[]
        x_append=x.append
        EOF=False
        while not(EOF):
            try:
                hkey = next(hi)
                l = [str(hkey),': ',str(self.__hashtable[hkey])]
                x_append(''.join(l))
            except StopIteration: # end of hashtable reached
                EOF=True
        return '\n'.join(x)
    def __repr__(self):
        hi = iter(self.__hashtable)
        x=[]
        x_append=x.append
        EOF=False
        while not(EOF):
            try:
                hkey = next(hi)
                x_append(str(hkey)+': '+str(self.__hashtable[hkey]))
            except StopIteration: # end of hashtable reached
                EOF=True
        return '\n'.join(x)
    def __init__(self,**kwargs):
        if len(kwargs)>0:
            for key,val in kwargs.items():
                if key.lower() in {'hashtable'}:
                    self.__hashtable = val
            self.__firstKey = next(iter(self.__hashtable))
        else: # this is an empty object
            self.__hashtable = {}
            self.__firstKey = ''
        self.__hashtable[self.__firstKey] = 'f('+','.join(self.__firstKey)+')' # only on first line
        self.__VARS = [v for v in self.__firstKey]
        self.__N = len(self.__VARS)
        self.__binaryTREE = self.binaryTree(self.__N)
        self.__varIndex = {}    # {dictionary}
        self.makeVarIndex()
        self.__values = self.getValues()
    def show(self):
        return self.makePandasTABLE()
    def makePandasTABLE(self):
        ht = self.__hashtable.copy()
        table = [list(ki) + [ht[ki]] for ki in ht]
        N = self.__N
        return DataFrame(table[1:], columns=table[0], index=[i+1 for i in range(2**N)])
    def makeVarIndex(self):
        if len(self.__varIndex)==0:
            d = {}
            for i,v in enumerate(self.__VARS):
                d[v] = i
            self.__varIndex = d
    def getValues(self,*args):
        if len(args) < 1:
            ht_ = self.__hashtable.copy()
        else:
            ht_ = args[0].copy() # needs to be a dictionary
        ht_.pop(next(iter(ht_)))
        return [v for _,v in ht_.items()]
    def binaryTree(self,N):
            TreeTF = []
            for i in range(N):
                j = (N-1)-i
                a = 2**j
                b = 2**(j+1)
                TreeTF.append(([True]*a+[False]*a)*(int(2**N/b)))
            return [tr for tr in zip(*TreeTF)]
    def size(self):
        return 2**len(self.__VARS)
    def pop(self,var):
        ht = self.__hashtable.copy()
        vars = set(next(iter(ht)))
        vars_minus_v = vars.difference(set([var]))
        HT = {tuple(vars_minus_v): ''}
        return Factor(hashtable=HT)
    def premultiply(self,other):
        ht_Left = self.__hashtable.copy()
        ht_Right = other._Factor__hashtable.copy()
        varInLeft = next(iter(ht_Left))
        varInRight = next(iter(ht_Right))
        varNotInLeft = set(varInRight).difference(set(varInLeft)) # variable not in Left that need to be added to Left
        base = list(varInLeft)
        top = sorted(varNotInLeft, key=varInRight.index)
        allvars = tuple(base+top)
        HT = {allvars: ''}
        return Factor(hashtable=HT)
    def reordering(self,newOrdering):  # list of variables in the new order
        originalOrdering = self.__VARS # list of variables in the original order
        oldInd = self.__varIndex
        newInd = {}
        arrInd = []
        for i,n in enumerate(newOrdering):
            o = oldInd[n]
            newInd[n]=i
            arrInd.append([o,i])
        newOrder = [i for i in zip(*arrInd)][0] # transpose and get the first element
        revInd = []
        for i,n in enumerate(originalOrdering):
            r = newInd[n]
            revInd.append([r,i])
        revOrder = [i for i in zip(*revInd)][0] # transpose and get the first element
        return revOrder, newOrder
    def order(self,*args):
        revIndexes,_ = self.reordering(args)
        ht_old = self.__hashtable.copy()
        ht_new = {tuple(args):''}
        iter_ht_old = iter(ht_old)
        varOld=next(iter_ht_old) # skip header
        EOF=False
        while not(EOF):
            try:
                hk = next(iter_ht_old) # tuple of boolean
                ht_new[hk] = ht_old[tuple([hk[i] for i in revIndexes])]
            except StopIteration: # end of hashtable reached
                EOF=True
        return Factor(hashtable=ht_new)
    def filter(self,*args):
        var = args[0]
        boo = args[1]
        position = self.__varIndex[var]  # allvar = set(self.__VARS)
        ht = self.__hashtable.copy()
        hi = iter(ht)
        ht.pop((next(hi))) # remove header from hashtable
        hi_1 = iter(ht.copy())
        def select(x):
            if boo: # select True
                return(x[position])
            else:   # select False
                return(not(x[position]))
        filtiter = filter(select,hi_1)
        firstrow = next(iter(self.__hashtable))
        ht_new = {}
        ht_new[firstrow] = self.__hashtable[firstrow]
        EOF=False
        while not(EOF):
            try:
                nnit = next(filtiter) # tuple of boolean
                ht_new[nnit] = self.__hashtable[nnit]
            except StopIteration: # end of hashtable reached
                EOF=True
        return ht_new
    def sumout(self,var):
        ht_T = self.filter(var,True)
        ht_F = self.filter(var,False)
        vT = self.getValues(ht_T)
        vF = self.getValues(ht_F)
        values = array(vT) + array(vF) # Summation done between numpy arrays
        allvars = next(iter(self.__hashtable))
        varRemain = set(allvars).difference(set([var]))
        newHeader = tuple(sorted(varRemain, key=allvars.index))
        indexes = tuple([self.__varIndex[var] for var in newHeader])
        HT_sumout = {newHeader: ''}
        iterHT = iter(ht_T)
        next(iterHT) # skip header
        for val in values:
            current = next(iterHT)
            queryRemain = tuple([current[i] for i in indexes])
            HT_sumout[queryRemain] = val  # this should be optimised
        return Factor(hashtable=HT_sumout)
    def normalize(self,var):
        f_without_var = self.sumout(var)
        f = self / f_without_var
        return f
    def multiply(self,other):
        ht_Left = self.__hashtable.copy()
        ht_Right = other._Factor__hashtable.copy()
        varInLeft = next(iter(ht_Left))
        varInRight = next(iter(ht_Right))
        varNotInLeft = set(varInRight).difference(set(varInLeft)) # variable not in Left that need to be added to Left
        base = list(varInLeft)
        top = sorted(varNotInLeft, key=varInRight.index)
        allvars = tuple(base+top)
        d = {}
        for i,v in enumerate(allvars):
            d[v] = i # create new indexes
        N = len(allvars)
        BTN = self.binaryTree(N)
        it_BTN = iter(BTN)
        indexLeft = [d[v] for v in varInLeft]  # list comprehension
        indexRight = [d[v] for v in varInRight]
        EOF = False
        HT_multiply = {allvars: ''}
        while not(EOF):
            try:
                current=next(it_BTN)
                queryLeft = tuple([current[i] for i in indexLeft])
                queryRight= tuple([current[i] for i in indexRight])
                HT_multiply[current] = ht_Left[queryLeft] * ht_Right[queryRight]  # this should be optimised
            except StopIteration: # end of hashtable reached
                EOF=True
        return Factor(hashtable=HT_multiply)
    def divide(self,other):
        ht_Left = self.__hashtable.copy()
        ht_Right = other._Factor__hashtable.copy()
        varInLeft = next(iter(ht_Left))
        varInRight = next(iter(ht_Right))
        varNotInLeft = set(varInRight).difference(set(varInLeft)) # variable not in Left that need to be added to Left
        base = list(varInLeft)
        top = sorted(varNotInLeft, key=varInRight.index)
        allvars = tuple(base+top)
        d = {}
        for i,v in enumerate(allvars):
            d[v] = i # create new indexes
        N = len(allvars)
        BTN = self.binaryTree(N)
        it_BTN = iter(BTN)
        indexLeft = [d[v] for v in varInLeft]  # list comprehension
        indexRight = [d[v] for v in varInRight]
        EOF = False
        HT_divide = {allvars: ''}
        while not(EOF):
            try:
                current=next(it_BTN)
                queryLeft = tuple([current[i] for i in indexLeft])
                queryRight= tuple([current[i] for i in indexRight])
                HT_divide[current] = ht_Left[queryLeft] / ht_Right[queryRight]  # this should be optimised
            except StopIteration: # end of hashtable reached
                EOF=True
        return Factor(hashtable=HT_divide)
    def __mul__(self,other): #https://docs.python.org/3/reference/datamodel.html
        return self.multiply(other)
    def __truediv__(self,other):
        return self.divide(other)
    def __pow__(self,other):
        return self.premultiply(other)

# https://stackoverflow.com/questions/3013449/list-comprehension-vs-lambda-filter
