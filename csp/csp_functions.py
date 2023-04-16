from csp import Constraint, Variable, CSP
from constraints import NValuesConstraint
import copy

global solution_list
solution_list = []

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()
    row_cnsts = board.pop(0)
    col_cnsts = board.pop(0)
    ship_nmbrs = board.pop(0)

    return board, row_cnsts, col_cnsts, ship_nmbrs

def make_domain(board, row, col):
    '''
    Takes in a given board and a row/col idx pair, and returns a list of possible values for that square
    - The general domain is ['.', 's', '<', '>', '^', 'v', 'M']: take out values as needed
    - CONSTRAINTS NOT IMPLEMENTED HERE:
        - row constraints: total ship parts in each row matches the number for the row
        - column constraints: total ship parts in each column matches the number for the column
        - ships on the board match the set of ships

    - CONSTRAINTS THAT ARE IMPLEMENTED HERE:
        - ship parts form valid ships
        - ships are surrounded by water

    '''

    N = len(board) # dimension of board = NxN
    fixed = [] #indices w/ fixed value: i.e, piece is put on the board
    free = [] # indices w/ 0 value
    domain = {'.', 'S', '<', '>', '^', 'v', 'M'}
    # record values in a 3x3 vicinity: i.e, when recording x, get 0's from board
    # 0  0  0
    # 0  x  0
    # 0  0  0
    # 1st word = row, 2nd word = col
    top_left = 'NULL'
    top_mid = 'NULL'
    top_right = 'NULL'
    mid_left = 'NULL'
    mid_right = 'NULL'
    bot_left = 'NULL'
    bot_mid = 'NULL'
    bot_right = 'NULL'

    if row == 0:
        top_left = None
        top_mid = None
        top_right = None
    elif row == N-1:
        bot_left = None
        bot_mid = None
        bot_right = None
    if col == 0:
        top_left = None
        mid_left = None
        bot_left = None
    if col == N-1:
        top_right = None
        mid_right = None
        bot_right = None

    if top_left != None:
        top_left = board[row-1][col-1]
    if top_mid != None:
        top_mid = board[row-1][col]
    if top_right != None:
        top_right = board[row-1][col+1]
    if mid_left != None:
        mid_left = board[row][col-1]
    if mid_right != None:
        mid_right = board[row][col+1]
    if bot_left != None:
        bot_left = board[row+1][col-1]
    if bot_mid != None:
        bot_mid= board[row+1][col]
    if bot_right != None:
        bot_right = board[row+1][col+1]

    # making the domains
    # checking corners first: if there is a piece that isnt a zero, wall, or water, return a domain of only water, otherwise: continue as the square can be anything
    for corner in [top_left, top_right, bot_left, bot_right]:
        if corner not in ['0', '.', None]:
            return ['.']
        
    # top middle checks
    if top_mid in ['S', 'v', '<', '>']:
        return ['.']
    # possible values for top_mid: '^', 'M', '.', '0', None
    elif top_mid == '^':
        if bot_mid in ['.', None]:
            return ['v']
        elif bot_mid in ['v', 'M']:
            return ['M']
        elif bot_mid == '0':
            return ['M', 'v']
        else:
            raise Exception('invalid assignment!')
    elif top_mid == 'M':
        if bot_mid in ['.', None]:
            return ['v']
        elif bot_mid == 'v':
            return ['M']
        elif bot_mid == '0':
            return ['M', 'v']
        else:
            raise Exception('invalid assignment!')     
    elif top_mid in ['.', None]:
        domain.discard('v')
    elif top_mid == '0':
        pass
        

    # bot middle checks
    if bot_mid in ['S', '^', '<', '>']:
        return ['.']
    # possible values for bot_mid: 'v', 'M', '.', '0', None
    elif bot_mid == 'v':
        if top_mid in ['.', None]:
            return ['^']
        elif top_mid in ['^', 'M']:
            return ['M']
        elif top_mid == '0':
            return ['M', '^']
        else:
            raise Exception('invalid assignment!')
    elif bot_mid == 'M':
        if top_mid in ['.', None]:
            return ['^']
        elif top_mid == '^':
            return ['M']
        elif top_mid == '0':
            return ['M', '^']
        else:
            raise Exception('invalid assignment!')
    elif bot_mid in ['.', None]:
        domain.discard('^')
    elif bot_mid == '0':
        pass

    # mid left checks
    if mid_left in ['S', '>', '^', 'v']:
        return ['.']
    # possible values for mid_left: '<', 'M', '.', '0', None
    elif mid_left == '<':
        if mid_right in ['.', None]:
            return ['>']
        elif mid_right in ['>', 'M']:
            return ['M']
        elif mid_right == '0':
            return ['M', '>']
        else:
            raise Exception('invalid assignment!')
    elif mid_left == 'M':
        if mid_right in ['.', None]:
            return ['>']
        elif mid_right == '>':
            return ['M']
        elif mid_right == '0':
            return ['M', '>']
        else:
            raise Exception('invalid assignment!')
    elif mid_left in ['.', None]:
        domain.discard('>')
    elif mid_left == '0':
        pass
    
    # mid right checks
    if mid_right in ['S', '<', '^', 'v']:
        return ['.']
    # possible values for mid_right: '>', 'M', '.', '0', None
    elif mid_right == '>':
        if mid_left in ['.', None]:
            return ['<']
        elif mid_left in ['<','M']:
            return ['M']
        elif mid_left == '0':
            return ['M', '<']
        else:
            raise Exception('invalid assignment!')
    elif mid_right == 'M':
        if mid_left in ['.', None]:
            return ['<']
        elif mid_left == '<':
            return ['M']
        elif mid_right == '0':
            return ['M', '<']
        else:
            raise Exception('invalid assignment!')
    elif mid_right in ['.', None]:
        domain.discard('<')
    elif mid_right == '0':
        pass

    return list(domain)

def row_constraint(board, domain, row, col, cnst):
    '''
    takes in a coordinate pair of a variable, its domain, and the row constraint and checks if any more ship PARTS can be placed on the row.
    '''
    part_count = 0
    for c in range(len(board)):
        if board[row][c] not in ['.', '0']:
            part_count += 1
            if part_count == cnst:
                return ['.'] # no more ships can be placed: domain is now only water
    # if ship assignments arent done, return the unchanged domain
    return domain 

def row_constraint(board, domain, row, col, cnst):
    '''
    takes in a coordinate pair of a variable, its domain, and the row constraint and checks if any more ship PARTS can be placed on the row.
    '''
    part_count = 0
    for r in range(len(board)):
        if board[r][col] not in ['.', '0']:
            part_count += 1
            if part_count == cnst:
                return ['.'] # no more ships can be placed: domain is now only water
    # if ship assignments arent done, return the unchanged domain
    return domain
#########################################################################################################################################################################
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
                elif i == size-1: # row size
                    potentialDomain.discard('^')
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
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i+1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # botmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[(i+1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '<'], ['.', '>'], ['^', 'v'], ['M', 'v'], ['^', 'M'], ['M', 'M'], ['S', '.'], ['v', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # midright
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[i*size+j+1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '<'], ['.', '^'], ['.', 'v'], ['<', '>'], ['M', '>'], ['<', 'M'], ['M', 'M'], ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
            elif i == 0 and j == size-1:
                # botleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i+1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # botmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[(i+1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '<'], ['.', '>'], ['^', 'v'], ['M', 'v'], ['^', 'M'], ['M', 'M'], ['S', '.'], ['v', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # midleft
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[i*size+j-1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '>'], ['.', '^'], ['.', 'v'], ['>', '<'], ['M', '<'], ['>', 'M'], ['M', 'M'], ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
            elif i == size-1 and j == 0:
                # topright: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i-1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # topmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[(i-1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['.', '>'], ['v', '^'], ['M', '^'], ['v', 'M'], ['M', 'M'], ['S', '.'], ['^', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # midright
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[i*size+j+1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '<'], ['.', '^'], ['.', 'v'], ['<', '>'], ['M', '>'], ['<', 'M'], ['M', 'M'], ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
            elif i == size-1 and j == size-1:
                # topleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i-1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # topmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[(i-1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['.', '>'], ['v', '^'], ['M', '^'], ['v', 'M'], ['M', 'M'], ['S', '.'], ['^', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # midleft
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[i*size+j-1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '>'], ['.', '^'], ['.', 'v'], ['>', '<'], ['M', '<'], ['>', 'M'], ['M', 'M'], ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
            
            # top row of the board checks that arent corners

            elif i == 0 and j not in [0,size-1]:
                # botleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i+1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # botright: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i+1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # midleft
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[i*size+j-1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '>'], ['.', '^'], ['.', 'v'], ['>', '<'], ['M', '<'], ['>', 'M'], ['M', 'M'], ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
                # midright
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[i*size+j+1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '<'], ['.', '^'], ['.', 'v'], ['<', '>'], ['M', '>'], ['<', 'M'], ['M', 'M'], ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
                # botmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[(i+1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '<'], ['.', '>'], ['^', 'v'], ['M', 'v'], ['^', 'M'], ['M', 'M'], ['S', '.'], ['v', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
            
            ### bot row of the board checks that arent corners

            elif i == size-1 and j not in [0,size-1]:
                # topleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i-1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # topright: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i-1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # midleft
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[i*size+j-1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '>'], ['.', '^'], ['.', 'v'], ['>', '<'], ['M', '<'], ['>', 'M'], ['M', 'M'], ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
                # midright
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[i*size+j+1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '<'], ['.', '^'], ['.', 'v'], ['<', '>'], ['M', '>'], ['<', 'M'], ['M', 'M'], ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
                # topmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[(i-1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['.', '>'], ['v', '^'], ['M', '^'], ['v', 'M'], ['M', 'M'], ['S', '.'], ['^', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])

            ### left col of the board checks that arent corners

            elif i not in [0,size-1] and j == 0:
                # topright: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i-1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # botright: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i+1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # topmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[(i-1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['.', '>'], ['v', '^'], ['M', '^'], ['v', 'M'], ['M', 'M'], ['S', '.'], ['^', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # botmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[(i+1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '<'], ['.', '>'], ['^', 'v'], ['M', 'v'], ['^', 'M'], ['M', 'M'], ['S', '.'], ['v', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # midright
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[i*size+j+1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '<'], ['.', '^'], ['.', 'v'], ['<', '>'], ['M', '>'], ['<', 'M'], ['M', 'M'], ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
            
            ### right col of the board checks that arent corners

            elif i not in [0, size-1] and j == size-1:
                # topleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i-1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # botleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i+1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # topmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[(i-1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['.', '>'], ['v', '^'], ['M', '^'], ['v', 'M'], ['M', 'M'], ['S', '.'], ['^', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # botmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[(i+1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '<'], ['.', '>'], ['^', 'v'], ['M', 'v'], ['^', 'M'], ['M', 'M'], ['S', '.'], ['v', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # midleft
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[i*size+j-1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '>'], ['.', '^'], ['.', 'v'], ['>', '<'], ['M', '<'], ['>', 'M'], ['M', 'M'], ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
            
            ### else: no restrictions, add arc formed with this square and all 8 surrounding squares, done with table constraints
            
            else:
                # topleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i-1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # topright: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i-1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # botleft: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j-1), [varn[str(i*size+j)], varn[(i+1)*size+j-1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # botright: corner
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j+1), [varn[str(i*size+j)], varn[(i+1)*size+j+1]], [['.', '.'],  ['S', '.'], ['<', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'], ['.', 'S'],['.', '<'], ['.', '>'], ['.', '^'], ['.', 'v'], ['.', 'M']])
                # topmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i-1)+' col'+str(j), [varn[str(i*size+j)], varn[(i-1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', 'v'], ['.', '<'], ['.', '>'], ['v', '^'], ['M', '^'], ['v', 'M'], ['M', 'M'], ['S', '.'], ['^', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # botmid
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i+1)+' col'+str(j), [varn[str(i*size+j)], varn[(i+1)*size+j]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '^'], ['.', '<'], ['.', '>'], ['^', 'v'], ['M', 'v'], ['^', 'M'], ['M', 'M'], ['S', '.'], ['v', '.'], ['<', '.'], ['>', '.'], ['M', '.'] ])
                # midleft
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j-1), [varn[str(i*size+j)], varn[i*size+j-1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '>'], ['.', '^'], ['.', 'v'], ['>', '<'], ['M', '<'], ['>', 'M'], ['M', 'M'], ['S', '.'], ['<', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
                # midright
                conslist.append('row'+str(i)+' col'+str(j)+' vs row'+str(i)+' col'+str(j+1), [varn[str(i*size+j)], varn[i*size+j+1]], [ ['.', '.'], ['.', '.'], ['.', 'S'], ['.', '<'], ['.', '^'], ['.', 'v'], ['<', '>'], ['M', '>'], ['<', 'M'], ['M', 'M'], ['S', '.'], ['>', '.'], ['^', '.'], ['v', '.'], ['M', '.'] ])
        
        ##### row and col constraints
        conslist.append(NValuesConstraint('row'+str(i), rowi, ['M', '<', '>', '^', 'v', 'S']), row_nums[i], row_nums[i])
        conslist.append(NValuesConstraint('col'+str(i), coli, ['M', '<', '>', '^', 'v', 'S']), col_nums[i], col_nums[i])
    
    return conslist

### AC3 == GAC algorithms, following pseudocode
def GacEnforce(cnstrs, assignedvar, assignedval, battle_csp):
    '''
    cnstrs is a list of constraints not known GAC: establish GAC on them and on all affected constraints
    Type(cnstrs) = List, Type(cnstr) = Constraint
    '''
    while not cnstrs.empty():
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
    if unAssignedVars.empty():
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
        row_numb = 0
        while cur_idx > battle_csp.size:
            row_numb += 1
            cur_idx -= row_numb*battle_csp.size
        sol[row_numb][cur_idx] = var.getValue()
    
    return sol
if __name__ == '__main__':
    board = [ ['0', '.', '.', '.', '0'],
              ['.', '.', '0', '.', '0'],
              ['0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0'],
              ['0', '0', '0', '0', '0']]
    row_nums = []
    col_nums = []
    varlist, varn = initialize_vars(board)
    constraints = make_conslist(board, varn, row_nums, col_nums)
    battle_csp = CSP('battle_csp', varlist, constraints)
    battle_csp.size = len(board)
