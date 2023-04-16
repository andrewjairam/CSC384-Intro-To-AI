import sys
import copy

global solution_list
solution_list = []

class Variable:
    '''Class for defining CSP variables.

      On initialization the variable object can be given a name and a
      list containing variable's domain of values. You can reset the
      variable's domain if you want to solve a similar problem where
      the domains have changed.

      To support CSP propagation, the class also maintains a current
      domain for the variable. Values pruned from the variable domain
      are removed from the current domain but not from the original
      domain. Values can be also restored.
    '''

    undoDict = dict()             #stores pruned values indexed by a
                                        #(variable,value) reason pair
    def __init__(self, name, domain):
        '''Create a variable object, specifying its name (a
        string) and domain of values.
        '''
        self._name = name                #text name for variable
        self._dom = list(domain)         #Make a copy of passed domain
        self._curdom = list(domain)      #using list
        self._value = None

    def __str__(self):
        return "Variable {}".format(self._name)

    def domain(self):
        '''return copy of variable domain'''
        return(list(self._dom))

    def domainSize(self):
        '''Return the size of the domain'''
        return(len(self.domain()))

    def resetDomain(self, newdomain):
        '''reset the domain of this variable'''
        self._dom = newdomain

    def getValue(self):
        return self._value

    def setValue(self, value):
        if value != None and not value in self._dom:
            print("Error: tried to assign value {} to variable {} that is not in {}'s domain".format(value,self._name,self._name))
        else:
            self._value = value    

    def unAssign(self):
        self.setValue(None)

    def isAssigned(self):
        return self.getValue() != None

    def name(self):
        return self._name

    def curDomain(self):
        '''return copy of variable current domain. But if variable is assigned
           return just its assigned value (this makes implementing hasSupport easier'''
        if self.isAssigned():
            return([self.getValue()])
        return(list(self._curdom))

    def curDomainSize(self):
        '''Return the size of the current domain'''
        if self.isAssigned():
            return(1)
        return(len(self._curdom))

    def inCurDomain(self, value):
        '''check if value is in current domain'''
        if self.isAssigned():
            return(value==self.getValue())
        return(value in self._curdom)

    def pruneValue(self, value, reasonVar, reasonVal):
        '''Remove value from current domain'''
        try:
            self._curdom.remove(value)
        except:
            print("Error: tried to prune value {} from variable {}'s domain, but value not present!".format(value, self._name))
        dkey = (reasonVar, reasonVal)
        if not dkey in Variable.undoDict:
            Variable.undoDict[dkey] = []
        Variable.undoDict[dkey].append((self, value))

    def restoreVal(self, value):
        self._curdom.append(value)

    def restoreCurDomain(self):
        self._curdom = self.domain()

    def reset(self):
        self.restoreCurDomain()
        self.unAssign()

    def dumpVar(self):
        print("Variable\"{}={}\": Dom = {}, CurDom = {}".format(self._name, self._value, self._dom, self._curdom))

    @staticmethod
    def clearUndoDict():
        undoDict = dict()

    @staticmethod
    def restoreValues(reasonVar, reasonVal):
        dkey = (reasonVar, reasonVal)
        if dkey in Variable.undoDict:
            for (var,val) in Variable.undoDict[dkey]:
                var.restoreVal(val)
            del Variable.undoDict[dkey]



#implement various types of constraints
class Constraint:
    '''Base class for defining constraints. Each constraint can check if
       it has been satisfied, so each type of constraint must be a
       different class. For example a constraint of notEquals(V1,V2)
       must be a different class from a constraint of
       greaterThan(V1,V2), as they must implement different checks of
       satisfaction.

       However one can define a class of general table constraints, as
       below, that can capture many different constraints.

       On initialization the constraint's name can be given as well as
       the constraint's scope. IMPORTANT, the scope is ordered! E.g.,
       the constraint greaterThan(V1,V2) is not the same as the
       contraint greaterThan(V2,V1).
    '''
    def __init__(self, name, scope):
        '''create a constraint object, specify the constraint name (a
        string) and its scope (an ORDERED list of variable
        objects).'''
        self._scope = list(scope)
        self._name = "baseClass_" + name  #override in subconstraint types!

    def scope(self):
        return list(self._scope)

    def arity(self):
        return len(self._scope)

    def numUnassigned(self):
        i = 0
        for var in self._scope:
            if not var.isAssigned():
                i += 1
        return i

    def unAssignedVars(self):
        return [var for var in self.scope() if not var.isAssigned()]

    # def check(self):
    #     util.raiseNotDefined()

    def name(self):
        return self._name

    def __str__(self):
        return "Cnstr_{}({})".format(self.name(), map(lambda var: var.name(), self.scope()))

    def printConstraint(self):
        print("Cons: {} Vars = {}".format(
            self.name(), [v.name() for v in self.scope()]))


#object for holding a constraint problem
class CSP:
    '''CSP class groups together a set of variables and a set of
       constraints to form a CSP problem. Provides a usesful place
       to put some other functions that depend on which variables
       and constraints are active'''

    def __init__(self, name, variables, constraints):
        '''create a CSP problem object passing it a name, a list of
           variable objects, and a list of constraint objects'''
        self._name = name
        self._variables = variables
        self._constraints = constraints
        self.size = None # size = N given an NxN board

        #some sanity checks
        varsInCnst = set()
        for c in constraints:
            varsInCnst = varsInCnst.union(c.scope())
        for v in variables:
            if v not in varsInCnst:
                print("Warning: variable {} is not in any constraint of the CSP {}".format(v.name(), self.name()))
        for v in varsInCnst:
            if v not in variables:
                print("Error: variable {} appears in constraint but specified as one of the variables of the CSP {}".format(v.name(), self.name()))

        self.constraints_of = [[] for i in range(len(variables))]
        for c in constraints:
            for v in c.scope():
                i = variables.index(v)
                self.constraints_of[i].append(c)

    def name(self):
        return self._name

    def variables(self):
        return list(self._variables)

    def constraints(self):
        return list(self._constraints)

    def constraintsOf(self, var):
        '''return constraints with var in their scope'''
        try:
            i = self.variables().index(var)
            return list(self.constraints_of[i])
        except:
            print("Error: tried to find constraint of variable {} that isn't in this CSP {}".format(var, self.name()))

    def unAssignAllVars(self):
        '''unassign all variables'''
        for v in self.variables():
            v.unAssign()

    def check(self, solutions):
        '''each solution is a list of (var, value) pairs. Check to see
           if these satisfy all the constraints. Return list of
           erroneous solutions'''

        #save values to restore later
        current_values = [(var, var.getValue()) for var in self.variables()]
        errs = []

        for s in solutions:
            s_vars = [var for (var, val) in s]

            if len(s_vars) != len(self.variables()):
                errs.append([s, "Solution has incorrect number of variables in it"])
                continue

            if len(set(s_vars)) != len(self.variables()):
                errs.append([s, "Solution has duplicate variable assignments"])
                continue

            if set(s_vars) != set(self.variables()):
                errs.append([s, "Solution has incorrect variable in it"])
                continue

            for (var, val) in s:
                var.setValue(val)

            for c in self.constraints():
                if not c.check():
                    errs.append([s, "Solution does not satisfy constraint {}".format(c.name())])
                    break

        for (var, val) in current_values:
            var.setValue(val)

        return errs
    
    def __str__(self):
        return "CSP {}".format(self.name())

class TableConstraint(Constraint):
    '''General type of constraint that can be use to implement any type of
       constraint. But might require a lot of space to do so.

       A table constraint explicitly stores the set of satisfying
       tuples of assignments.'''

    def __init__(self, name, scope, satisfyingAssignments):
        '''Init by specifying a name and a set variables the constraint is over.
           Along with a list of satisfying assignments.
           Each satisfying assignment is itself a list, of length equal to
           the number of variables in the constraints scope.
           If sa is a single satisfying assignment, e.g, sa=satisfyingAssignments[0] 
           then sa[i] is the value that will be assigned to the variable scope[i].


           Example, say you want to specify a constraint alldiff(A,B,C,D) for
           three variables A, B, C each with domain [1,2,3,4]
           Then you would create this constraint using the call
           c = TableConstraint('example', [A,B,C,D],
                               [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4],
                                [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2],
                                [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4],
                                [2, 3, 4, 1], [2, 4, 1, 3], [2, 4, 3, 1],
                                [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4],
                                [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1],
                                [4, 1, 2, 3], [4, 1, 3, 2], [4, 2, 1, 3],
                                [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]])
          as these are the only assignments to A,B,C respectively that
          satisfy alldiff(A,B,C,D)
        '''

        Constraint.__init__(self,name, scope)
        self._name = "TableCnstr_" + name
        self.satAssignments = satisfyingAssignments

    def check(self):
        '''check if current variable assignments are in the satisfying set'''
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        return assignments in self.satAssignments

    def hasSupport(self, var,val):
        '''check if var=val has an extension to an assignment of all variables in
           constraint's scope that satisfies the constraint. Important only to
           examine values in the variable's current domain as possible extensions'''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        vindex = self.scope().index(var)
        found = False
        for assignment in self.satAssignments:
            if assignment[vindex] != val:
                continue   #this assignment can't work it doesn't make var=val
            found = True   #Otherwise it has potential. Assume found until shown otherwise
            for i, v in enumerate(self.scope()):
                if i != vindex and not v.inCurDomain(assignment[i]):
                    found = False  #Bummer...this assignment didn't work it assigns
                    break          #a value to v that is not in v's curDomain
                                   #note we skip checking if val in in var's curDomain
            if found:     #if found still true the assigment worked. We can stop
                break
        return found     #either way found has the right truth value

def findvals(remainingVars, assignment, finalTestfn, partialTestfn=lambda x: True):
    '''Helper function for finding an assignment to the variables of a constraint
       that together with var=val satisfy the constraint. That is, this
       function looks for a supporing tuple.

       findvals uses recursion to build up a complete assignment, one value
       from every variable's current domain, along with var=val.

       It tries all ways of constructing such an assignment (using
       a recursive depth-first search).

       If partialTestfn is supplied, it will use this function to test
       all partial assignments---if the function returns False
       it will terminate trying to grow that assignment.

       It will test all full assignments to "allVars" using finalTestfn
       returning once it finds a full assignment that passes this test.

       returns True if it finds a suitable full assignment, False if none
       exist. (yes we are using an algorithm that is exactly like backtracking!)'''

    # print "==>findvars([",
    # for v in remainingVars: print v.name(), " ",
    # print "], [",
    # for x,y in assignment: print "({}={}) ".format(x.name(),y),
    # print ""

    #sort the variables call the internal version with the variables sorted
    remainingVars.sort(reverse=True, key=lambda v: v.curDomainSize())
    return findvals_(remainingVars, assignment, finalTestfn, partialTestfn)

def findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
    '''findvals_ internal function with remainingVars sorted by the size of
       their current domain'''
    if len(remainingVars) == 0:
        return finalTestfn(assignment)
    var = remainingVars.pop()
    for val in var.curDomain():
        assignment.append((var, val))
        if partialTestfn(assignment):
            if findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
                return True
        assignment.pop()   #(var,val) didn't work since we didn't do the return
    remainingVars.append(var)
    return False


class NValuesConstraint(Constraint):
    '''NValues constraint over a set of variables.  Among the variables in
       the constraint's scope the number that have been assigned
       values in the set 'required_values' is in the range
       [lower_bound, upper_bound] (lower_bound <= #of variables
       assigned 'required_value' <= upper_bound)

       For example, if we have 4 variables V1, V2, V3, V4, each with
       domain [1, 2, 3, 4], then the call
       NValuesConstraint('test_nvalues', [V1, V2, V3, V4], [1,4], 2,
       3) will only be satisfied by assignments such that at least 2
       the V1, V2, V3, V4 are assigned the value 1 or 4, and at most 3
       of them have been assigned the value 1 or 4.

    '''

    def __init__(self, name, scope, required_values, lower_bound, upper_bound):
        Constraint.__init__(self,name, scope)
        self._name = "NValues_" + name
        self._required = required_values
        self._lb = lower_bound
        self._ub = upper_bound

    def check(self):
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        rv_count = 0

        #print "Checking {} with assignments = {}".format(self.name(), assignments)

        for v in assignments:
            if v in self._required:
                rv_count += 1

        #print "rv_count = {} test = {}".format(rv_count, self._lb <= rv_count and self._ub >= rv_count)


        return self._lb <= rv_count and self._ub >= rv_count

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint

           HINT: check the implementation of AllDiffConstraint.hasSupport
                 a similar approach is applicable here (but of course
                 there are other ways as well)
        '''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in

        #define the test functions for findvals
        def valsOK(l):
            '''tests a list of assignments which are pairs (var,val)
               to see if they can satisfy this sum constraint'''
            rv_count = 0
            vals = [val for (var, val) in l]
            for v in vals:
                if v in self._required:
                    rv_count += 1
            least = rv_count + self.arity() - len(vals)
            most =  rv_count
            return self._lb <= least and self._ub >= most
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], valsOK, valsOK)
        return x

class IfAllThenOneConstraint(Constraint):
    '''if each variable in left_side equals each value in left_values 
    then one of the variables in right side has to equal one of the values in right_values. 
    hasSupport tested only, check() untested.'''
    def __init__(self, name, left_side, right_side, left_values, right_values):
        Constraint.__init__(self, name, left_side+right_side)
        self._name = "IfAllThenOne_" + name
        self._ls = left_side
        self._rs = right_side
        self._lv = left_values
        self._rv = right_values

    def hasSupport(self, var, val):
        '''
        check if var=val has an extension to an assignment of the other variable in the constraint that satisfies the constraint
        THE FIX: need to make sure that the first elem of LS is an M: otherwise, return true for the constraint

        #testing: only do the check if val = M and var is located @ _ls[0]
        '''

        if var not in self.scope():
            return True
        if val != 'M':
            return True #only check for 'M' values
        if var != self._ls[0]:
            return True
        for i, v in enumerate(self._ls):
            if not v.inCurDomain(self._lv[i]):
                return True # no need to check: this would mean the constraint is being called on a other-direction facing ship, will get checked in another instance
        # now, left side is satisfied. If right side is not satisfied, return false, else return  true
            for i, v in enumerate(self._rs):
                for potentialValue in self._rv:
                    if v.inCurDomain(potentialValue):
                        return True
            return False # rs not satisfied
    
        # if var in self._ls:
        #     var_idx = self._ls.index(var)
        #     # if var_idx == 0:
        #     #     if val != 'M':
        #     #         return True # no need to check this constraint if first elem is not assigned M
        #     if self._lv[var_idx] != val:
        #         return True # No need to check this constraint
        #     for i,v in  enumerate(self._lv):
        #         if i != var_idx:

        #     for i, v in enumerate(self._rs):
        #         for potentialValue in self._rv:
        #             if v.inCurDomain(potentialValue):
        #                 Right = True
        #                 break
        # elif var in self._rs: # there is only one variable in right side
        #     if val not in self._rv:
        #         return True # no need to check this constraint
        #     for i, v in enumerate(self._ls):
        #         if not v.inCurDomain(self._lv[i]):
        #             return False # constraint not satisfied
        #     return True # all in left side are satisfied: valid cosntraint

        


#################################################################### implemented functions ##################################################################################
def read_from_file(filename):
    '''
    Reads a given file and returns the corresponding board and constraints
    '''
    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()
    row_cnsts = board.pop(0)
    col_cnsts = board.pop(0)
    ship_nmbrs = board.pop(0)

    return board, row_cnsts, col_cnsts, ship_nmbrs

def initialize_vars(board):
    '''
    Takes in a board list object, assigns each square as a variable, and returns a dict + list of the variables
    '''
    size = len(board) # board is size x size
    varlist = []
    varn = {}
    # define variables
    for i in range(size):
        for j in range(size):
            v = None
            if board[i][j] != '0':
                v = Variable(str(i*size+j), [board[i][j]])
            else:
                potentialDomain = {'.', 'S', '<', '>', '^', 'v', 'M'}
                if i == 0: # row 0
                    potentialDomain.discard('v')
                    if j == 0:
                        potentialDomain.discard('M')
                    elif j == size-1:
                        potentialDomain.discard('M')
                elif i == size-1: # row size
                    potentialDomain.discard('^')
                    if j == 0:
                        potentialDomain.discard('M')
                    elif j == size-1:
                        potentialDomain.discard('M')
                if j == 0: # col 0
                    potentialDomain.discard('>')
                elif j == size-1: # col size
                    potentialDomain.discard('<')
                v = Variable(str((i*size+j)), list(potentialDomain))
            varlist.append(v)
            varn[str(i*size+j)] = v
    return varn, varlist

def make_conslist(board, varn, row_nums, col_nums):
    '''
    Takes in the board. the dictionary of variables varn, and the list of row/column constraints and returns a list of all constraints for the csp EXCEPT:
    NOTE: the 'ships match the valid set of ships' constraint IS NOT implemented here
    '''
    # define row and col constraints
    size = len(board)
    conslist = []
    for i in range(size):
        rowi = []
        coli = []
        for j in range(size):

            # for row and col constraints: ships match given number of ship parts in that row/col
            rowi.append(varn[str(i*size+j)])
            coli.append(varn[str(i+size*j)])

            ##### valid ship constraints: valid ships aree formed and they are surrounded by water

            ### base checks: corners of the board

            if i == 0 and j == 0:
                # botright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i+1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['^', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # botmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i+1)*size+j)]], [ ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '<'], ['^', 'v'], ['^', 'M'], ['S', '.'], ['<', '.']]))
                # midright
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[str(i*size+j+1)]], [ ['.', '.'], ['.', 'S'], ['.', '<'], ['.', '^'], ['<', '>'], ['<', 'M'], ['S', '.'], ['^', '.']]))
            elif i == 0 and j == size-1:
                # botleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i+1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['>', '.'], ['^', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # botmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i+1)*size+j)]], [ ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '>'], ['^', 'v'], ['^', 'M'], ['S', '.'], ['>', '.']]))
                # midleft
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[str(i*size+j-1)]], [ ['.', '.'], ['.', 'S'], ['.', '>'], ['.', '^'], ['>', '<'], ['>', 'M'], ['S', '.'], ['^', '.']]))
            elif i == size-1 and j == 0:
                # topright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i-1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['v', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # topmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i-1)*size+j)]], [ ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['v', '^'], ['v', 'M'], ['S', '.'], ['<', '.']]))
                # midright
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[str(i*size+j+1)]], [ ['.', '.'], ['.', 'S'], ['.', '<'], ['.', 'v'], ['<', '>'], ['<', 'M'], ['S', '.'], ['v', '.']]))
            elif i == size-1 and j == size-1:
                # topleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i-1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['>', '.'], ['v', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # topmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i-1)*size+j)]], [ ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '>'], ['v', '^'], ['v', 'M'], ['S', '.'], ['>', '.']]))
                # midleft
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[str(i*size+j-1)]], [ ['.', '.'], ['.', 'S'], ['.', '>'], ['.', 'v'], ['>', '<'], ['>', 'M'], ['S', '.'], ['v', '.']]))
            
            # top row of the board checks that arent corners

            elif i == 0 and j not in [0,size-1]:
                # botleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i+1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # botright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i+1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # midleft
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[str(i*size+j-1)]], [['S', '.'], ['.', '^'], ['.', '>'], ['.', 'S'], ['.', '.'], ['>', '<'], ['>', 'M'], ['^', '.'], ['<', '.'], ['M', '<'], ['M', 'M']]))
                # midright
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[str(i*size+j+1)]], [['S', '.'], ['.', '^'], ['.', '<'], ['.', 'S'], ['.', '.'], ['<', '>'], ['<', 'M'], ['^', '.'], ['>', '.'], ['M', '>'], ['M', 'M']]))
                # botmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i+1)*size+j)]], [['S', '.'], ['.', '^'], ['.', '>'], ['.', '<'], ['.', 'S'], ['.', '.'], ['.', 'M'], ['>', '.'], ['^', 'v'], ['^', 'M'], ['<', '.'], ['M', '.']]))
            
            ### bot row of the board checks that arent corners

            elif i == size-1 and j not in [0,size-1]:
                # topleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i-1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # topright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i-1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # midleft
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[str(i*size+j-1)]], [['S', '.'], ['.', 'v'], ['.', '>'], ['.', 'S'], ['.', '.'], ['>', '<'], ['>', 'M'], ['v', '.'], ['<', '.'], ['M', '<'], ['M', 'M']]))
                # midright
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[str(i*size+j+1)]], [['S', '.'], ['.', 'v'], ['.', '<'], ['.', 'S'], ['.', '.'], ['<', '>'], ['<', 'M'], ['v', '.'], ['>', '.'], ['M', '>'], ['M', 'M']]))
                # topmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i-1)*size+j)]], [['S', '.'], ['.', 'v'], ['.', '>'], ['.', '<'], ['.', 'S'], ['.', '.'], ['.', 'M'], ['>', '.'], ['<', '.'], ['v', '^'], ['v', 'M'], ['M', '.']]))

            ### left col of the board checks that arent corners

            elif i not in [0,size-1] and j == 0:
                # topright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i-1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # botright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i+1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # topmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i-1)*size+j)]], [['S', '.'], ['.', 'v'], ['.', '<'], ['.', 'S'], ['.', '.'], ['v', '^'], ['v', 'M'], ['<', '.'], ['M', 'M'], ['M', '^'], ['^', '.']]))
                # botmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i+1)*size+j)]], [['S', '.'], ['.', '^'], ['.', '<'], ['.', 'S'], ['.', '.'], ['^', 'v'], ['^', 'M'], ['<', '.'], ['M', 'M'], ['M', 'v'], ['v', '.']]))
                # midright
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[str(i*size+j+1)]], [['S', '.'], ['.', 'v'], ['.', '<'], ['.', 'S'], ['.', '.'], ['<', '>'], ['<', 'M'], ['v', '.'], ['^', '.'], ['.', '^'], ['M', '.'], ['.', 'M']]))
            
            ### right col of the board checks that arent corners

            elif i not in [0, size-1] and j == size-1:
                # topleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i-1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # botleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i+1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # topmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i-1)*size+j)]], [['S', '.'], ['.', 'v'], ['.', '>'], ['.', 'S'], ['.', '.'], ['v', '^'], ['v', 'M'], ['>', '.'], ['M', 'M'], ['M', '^'], ['^', '.']]))
                # botmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i+1)*size+j)]], [['S', '.'], ['.', '^'], ['.', '>'], ['.', 'S'], ['.', '.'], ['^', 'v'], ['^', 'M'], ['>', '.'], ['M', 'M'], ['M', 'v'], ['v', '.']]))
                # midleft
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[str(i*size+j-1)]], [['S', '.'], ['.', 'v'], ['.', '>'], ['.', 'S'], ['.', '.'], ['>', '<'], ['>', 'M'], ['v', '.'], ['^', '.'], ['.', '^'], ['M', '.'], ['.', 'M']]))
             
            ### else: no restrictions, add arc formed with this square and all 8 surrounding squares, done with table constraints
            
            else:
                # topleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i-1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # topright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i-1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # botleft: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[str((i+1)*size+j-1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # botright: corner
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[str((i+1)*size+j+1)]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']]))
                # topmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i-1)*size+j)]], [ ['.', '.'], ['.', 'M'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['.', '>'], ['v', '^'], ['M', '^'], ['v', 'M'], ['M', 'M'], ['S', '.'], ['^', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ]))
                # botmid
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[str((i+1)*size+j)]], [ ['.', '.'], ['.', 'M'], ['.', 'S'], ['.', '^'], ['.', '<'], ['.', '>'], ['^', 'v'], ['M', 'v'], ['^', 'M'], ['M', 'M'], ['S', '.'], ['v', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ]))
                # midleft
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[str(i*size+j-1)]], [ ['.', '.'], ['.', 'M'], ['.', 'S'], ['.', '>'], ['.', '^'], ['.', 'v'], ['>', '<'], ['M', '<'], ['>', 'M'], ['M', 'M'], ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ]))
                # midright
                conslist.append(TableConstraint('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[str(i*size+j+1)]], [ ['.', '.'], ['.', 'M'], ['.', 'S'], ['.', '<'], ['.', '^'], ['.', 'v'], ['<', '>'], ['M', '>'], ['<', 'M'], ['M', 'M'], ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ]))

                # ### deal with the M's
                # # water above and below: right has to be M or >
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str((i-1)*size+j)], varn[str((i+1)*size+j)]], [varn[str(i*size+j+1)]], ['M', '.', '.'], ['M', '>']))
                # # left also has to be M or < 
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str((i-1)*size+j)], varn[str((i+1)*size+j)] ], [varn[str(i*size+j-1)]], ['M', '.', '.'], ['M', '<']))
                # # Ending ships: M on home square and M to the right: left is <
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str(i*size+j+1)] ], [varn[str(i*size+j-1)]], ['M', 'M'], ['<']))
                # # M on home square and M to the left: right is > 
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str(i*size+j-1)] ], [varn[str(i*size+j+1)]], ['M', 'M'], ['>']))
                # # water left and right: top has to be ^ or M 
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str(i*size+j-1)], varn[str(i*size+j+1)]], [varn[str((i-1)*size+j)] ], ['M', '.', '.'], ['M', '^']))
                # # and bot has to be v or M
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str(i*size+j-1)], varn[str(i*size+j+1)]], [varn[str((i+1)*size+j)]], ['M', '.', '.'], ['M', 'v']))
                # # M on home and M above: bottom = v
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str((i-1)*size+j)]], [varn[str((i+1)*size+j)] ], ['M', 'M'], ['v']))
                # # M on home and M below: top = ^ 
                # conslist.append(IfAllThenOneConstraint('placeholder', [varn[str(i*size+j)], varn[str((i+1)*size+j)]],  [varn[str((i-1)*size+j)]], ['M', 'M'], ['^']))
                
        ##### row and col constraints
        conslist.append(NValuesConstraint('row'+str(i), rowi, ['M', '<', '>', '^', 'v', 'S'], row_nums[i], row_nums[i]))
        conslist.append(NValuesConstraint('col'+str(i), coli, ['M', '<', '>', '^', 'v', 'S'], col_nums[i], col_nums[i]))
    
    return conslist

### AC3 == GAC algorithms, following pseudocode

def GacEnforce(cnstrs, assignedvar, assignedval, battle_csp):
    '''
    cnstrs is a list of constraints not known GAC: establish GAC on them and on all affected constraints
    Type(cnstrs) = List, Type(cnstr) = Constraint
    '''
    while not len(cnstrs) == 0:
        cnstr = cnstrs.pop(0) # we will make cnstr GAC: inspect cnstrs from start of list to end
        for var in cnstr.scope():
            for val in var.curDomain():
                if not cnstr.hasSupport(var,val):
                    var.pruneValue(val, assignedvar, assignedval)
                    if var.curDomainSize() == 0:
                        return 'DWO' # domain wipeout
                    for recheck in battle_csp.constraintsOf(var):
                        if recheck != cnstr and not recheck in cnstrs:
                            cnstrs.append(recheck) # add the cnstr to recheck to the end of the cnstrs list
    return 'OK'

def GAC(unAssignedVars, battle_csp):
    if len(unAssignedVars) == 0:
        solution_list.append(make_solution(battle_csp))
        return
    var = unAssignedVars.pop(0)
    for val in var.curDomain():
        var.setValue(val)
        noDWO = True
        if GacEnforce(battle_csp.constraintsOf(var), var, val, battle_csp) == 'DWO':
            noDWO = False
        if noDWO:
            GAC(unAssignedVars, battle_csp)
        Variable.restoreValues(var,val)
    var.setValue(None)
    # backtrack
    unAssignedVars.append(var)
    return

def make_solution(battle_csp):
    '''
    After a sucesful GAC, creates an nxn board of the resulting solution given all the variables.
    '''
    variables = battle_csp.variables()
    count = 0
    sol = []
    for i in range(battle_csp.size):
        new_row = []
        for j in range(battle_csp.size):
            new_row.append(count)
            count += 1
        sol.append(new_row)
    for var in variables:
        cur_idx = copy.deepcopy(int(var.name()))
        col_num = cur_idx % battle_csp.size
        row_num = cur_idx // battle_csp.size
        sol[row_num][col_num] = var.getValue()
    
    return sol
def count_ships(board, ship_cnsts):
    '''
    ship constraints: [(number of 1x1 ships), (number of 1x2 ships), (number 1x3 ships), (number 1x4 ships)]
    '''
    num_ships = [0,0,0,0]
    size = len(board)
    for i in range(size):
        for j in range(size):
            if board[i][j] == '<':
                ship = count_horizontal_ship_size(board, i, j, count=1)
                if ship == None:
                    return False
                num_ships[ship-1] += 1
                
            elif board[i][j] == '^':
                ship = count_vertical_ship_size(board, i, j, count=1)
                if ship == None:
                    return False
                num_ships[ship-1] += 1
            elif board[i][j] == 'S':
                num_ships[0] += 1
    
    if num_ships == ship_cnsts:
        return True

def count_horizontal_ship_size(board, i, j, count=1):
    '''
    returns size of horizontal ship starting at (i, j)
    '''
    if board[i][j] == '>':
        return count
    elif board[i][j] == '.' or j == len(board) - 1:
        return None #invalid board
    count += 1
    return count_horizontal_ship_size(board, i, j+1, count)

def count_vertical_ship_size(board, i, j, count=1):
    '''
    returns size of horizontal ship starting at (i, j)
    '''
    if board[i][j] == 'v':
        return count
    elif board[i][j] == '.' or i == len(board)-1:
        return None # invalid board
    count += 1
    return count_vertical_ship_size(board, i+1, j, count)

def find_valid_solution(ship_cnsts):
    for sol in solution_list:
        if count_ships(sol, ship_cnsts) == True:
            return sol
    return # no solution found
if __name__ == '__main__':

    board = [ ['0', '0', '0', '0', 'S', '0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '.', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
              ['0', 'S', '0', '0', '0', '0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0'] ]
    row_nums = [1,3,0,4,3,3,2,0,3,1]
    col_nums = [4,3,2,2,1,0,0,4,0,4]
    ship_cnsts = [4,3,2,1]
    varn, varlist = initialize_vars(board)
    #ssprint(varlist)
    constraints = make_conslist(board, varn, row_nums, col_nums)
    battle_csp = CSP('battle_csp', varlist, constraints)
    battle_csp.size = len(board)
    GAC(battle_csp.variables(), battle_csp)
    print(len(solution_list))
    # for lst in solution_list:
    #     if lst == [ ['.', '.', '.', '.', 'S', '.', '.', '.', '.', '.'],
    #                 ['<', 'M', '>', '.', '.', '.', '.', '.', '.', '.'],
    #                 ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
    #                 ['<', '>', '.', '^', '.', '.', '.', '.', '.', '^'],
    #                 ['.', '.', '.', 'v', '.', '.', '.', '^', '.', 'M'],
    #                 ['.', 'S', '.', '.', '.', '.', '.', 'M', '.', 'M'],
    #                 ['.', '.', '.', '.', '.', '.', '.', 'v', '.', 'v'],
    #                 ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
    #                 ['^', '.', 'S', '.', '.', '.', '.', 'S', '.', '.'],
    #                 ['v', '.', '.', '.', '.', '.', '.', '.', '.', '.'] ]:
    #         print('solution is here')
    # for i in range(len(solution_list)):
    #     print(solution_list[i])
    print(find_valid_solution(ship_cnsts))