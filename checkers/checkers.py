import argparse
import copy
import sys
import time

global cache
cache = {}
### TODO:
# speedup code
# implement tiebreak if BOTH players cant move
# evaluation function 

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board):

        self.board = board

        self.width = 8
        self.height = 8

        # Modification: stores who is to move
        self.turn = 'r'

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")

def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']

def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board
################################################################################# IMPLEMENTED FUNCTIONS ################################################################################
def one_move(board, row, col, turn, successors, piece):
    '''
    given one red or black piece, appends all possible onemoves to successors list (i.e. empty space -> one move to get there)
    '''
    # red's turn
    if turn == 'r':
        # up left move
        if row-1 >= 0 and col-1 >= 0 and board[row-1][col-1] == '.':
            new_board = copy.deepcopy(board)
            if row-1 == 0:
                new_board[row-1][col-1] = 'R'
            else:
                new_board[row-1][col-1] = board[row][col]
            new_board[row][col] = '.'
            new_state = State(new_board)
            new_state.turn = 'b'
            string_board = stringify(new_state)
            if cache.get(string_board) == None:
                # add terminal state to cache
                cache[string_board] = (evaluation(new_state), new_state)     
            successors.append((cache.get(string_board)[0], new_state)) 
        # up right move
        if row-1 >= 0 and col+1 <= 7 and board[row-1][col+1] == '.':
            new_board = copy.deepcopy(board)
            if row-1 == 0:
                new_board[row-1][col+1] = 'R'
            else:
                new_board[row-1][col+1] = board[row][col]
            new_board[row][col] = '.'
            new_state = State(new_board)
            new_state.turn = 'b'
            string_board = stringify(new_state)
            if cache.get(string_board) == None:
                # add terminal state to cache
                cache[string_board] = (evaluation(new_state), new_state)     
            successors.append((cache.get(string_board)[0], new_state)) 
        # if king: check down left and down right as well
        if piece == 'R':
            #down left move
            if row+1 <= 7 and col-1 >= 0 and board[row+1][col-1] == '.':
                new_board = copy.deepcopy(board)
                new_board[row+1][col-1] = board[row][col]
                new_board[row][col] = '.'
                new_state = State(new_board)
                new_state.turn = 'b'
                string_board = stringify(new_state)
                if cache.get(string_board) == None:
                    # add terminal state to cache
                    cache[string_board] = (evaluation(new_state), new_state)     
                successors.append((cache.get(string_board)[0], new_state))  
            # down right move
            if row+1 <= 7 and col+1 <= 7 and board[row+1][col+1] == '.':
                new_board = copy.deepcopy(board)
                new_board[row+1][col+1] = board[row][col]
                new_board[row][col] = '.'
                new_state = State(new_board)
                new_state.turn = 'b'
                string_board = stringify(new_state)
                if cache.get(string_board) == None:
                    # add terminal state to cache
                    cache[string_board] = (evaluation(new_state), new_state)     
                successors.append((cache.get(string_board)[0], new_state)) 
    
    # black's Turn
    if turn == 'b':
        # down left move
        if row+1 <= 7 and col-1 >= 0 and board[row+1][col-1] == '.':
            new_board = copy.deepcopy(board)
            if row+1 == 7:
                new_board[row+1][col-1] = 'B'
            else:
                new_board[row+1][col-1] = board[row][col]
            new_board[row][col] = '.'
            new_state = State(new_board)
            new_state.turn = 'r'
            string_board = stringify(new_state)
            if cache.get(string_board) == None:
                # add terminal state to cache
                cache[string_board] = (evaluation(new_state), new_state)     
            successors.append((cache.get(string_board)[0], new_state)) 
        # down right move
        if row+1 <= 7 and col+1 <= 7 and board[row+1][col+1] == '.':
            new_board = copy.deepcopy(board)
            if row+1 == 7:
                new_board[row+1][col+1] = 'B'
            else:
                new_board[row+1][col+1] = board[row][col]
            new_board[row][col] = '.'
            new_state = State(new_board)
            new_state.turn = 'r'

            string_board = stringify(new_state)
            if cache.get(string_board) == None:
                # add terminal state to cache
                cache[string_board] = (evaluation(new_state), new_state)     
            successors.append((cache.get(string_board)[0], new_state)) 
        # if king:
        if piece == 'B':
            # up left move
            if row-1 >= 0 and col-1 >= 0 and board[row-1][col-1] == '.':
                new_board = copy.deepcopy(board)
                new_board[row-1][col-1] = board[row][col]
                new_board[row][col] = '.'
                new_state = State(new_board)
                new_state.turn = 'r'
                string_board = stringify(new_state)
                if cache.get(string_board) == None:
                    # add terminal state to cache
                    cache[string_board] = (evaluation(new_state), new_state)     
                successors.append((cache.get(string_board)[0], new_state)) 
            # up right move
            if row-1 >= 0 and col+1 <= 7 and board[row-1][col+1] == '.':
                new_board = copy.deepcopy(board)
                new_board[row-1][col+1] = board[row][col]
                new_board[row][col] = '.'
                new_state = State(new_board)
                new_state.turn = 'r'
                string_board = stringify(new_state)
                if cache.get(string_board) == None:
                    # add terminal state to cache
                    cache[string_board] = (evaluation(new_state), new_state)     
                successors.append((cache.get(string_board)[0], new_state)) 
    return

def takes(board, row, col, turn, successors, piece):
    '''
    input: board
    returns True if a swap happened, False if it didnt
    the recursive_takes() function by default modifies successors without having to return anything
    This function should be executed AFTER the first swap to not dupe states!
    '''
    # swap variables
    isSwap = False # True if a swap happened
    
    # red's turn 
    if turn == 'r':
        # if we can take up-left (take piece @ row-1, col-1)
        if row-2 >= 0 and col-2 >= 0 and (board[row-1][col-1] in ['b', 'B']) and board[row-2][col-2] == '.':
            # new_state = state after taking left
            new_board = copy.deepcopy(board)
            if row-2 == 0:
                new_board[row-2][col-2] = 'R'
            else:
                new_board[row-2][col-2] = piece
            new_board[row][col] = '.'
            new_board[row-1][col-1] = '.'
            # recursive_takes(new_board, row-2, col-2, red'sturn)
            recursive_takes(new_board, row-2, col-2, 'r', successors, piece)
            isSwap = True

        # if we can take up-right (take piece @ row-1, col+1)
        if row-2 >= 0 and col+2 <= 7 and (board[row-1][col+1] in ['b', 'B']) and board[row-2][col+2] == '.':
            # new_state = state after taking right
            new_board = copy.deepcopy(board)
            if row-2 == 0:
                new_board[row-2][col+2] = 'R'
            else:
                new_board[row-2][col+2] = piece
            new_board[row][col] = '.'
            new_board[row-1][col+1] = '.'
            # recursive_takes(new_state, row-2, col+2, red'sturn)
            recursive_takes(new_board, row-2, col+2, 'r', successors, piece)
            isSwap = True

        # account for down moves if the piece is a red king
        if piece == 'R':

            # if we can take down left (take piece @ row+1, col-1)
            if row+2 <= 7 and col-2 >= 0 and (board[row+1][col-1] in ['b', 'B']) and board[row+2][col-2] == '.':
                # new_state = state after taking down-left
                new_board = copy.deepcopy(board)
                new_board[row+2][col-2] = piece
                new_board[row][col] = '.'
                new_board[row+1][col-1] = '.'
                # recursive_takes(new_board, row+2, col-2, red'sturn)
                recursive_takes(new_board, row+2, col-2, 'r', successors, piece)
                isSwap = True

            # if we can take down right (take piece @ row+1, col+1)
            if row+2 <= 7 and col+2 <= 7 and (board[row+1][col+1] in ['b', 'B']) and board[row+2][col+2] == '.':
                # new_state = state after taking down-right
                new_board = copy.deepcopy(board)
                new_board[row+2][col+2] = piece
                new_board[row][col] = '.'
                new_board[row+1][col+1] = '.'
                # recursive_takes(new_board, row+2, col+2, red'sturn)
                recursive_takes(new_board, row+2, col+2, 'r', successors, piece)
                isSwap = True

    # black's turn
    if turn == 'b':
        # if we can take down left (take piece @ row+1, col-1)
        if row+2 <= 7 and col-2 >= 0 and (board[row+1][col-1] in ['r', 'R']) and board[row+2][col-2] == '.':
            # new_state = state after taking down-left
            new_board = copy.deepcopy(board)
            if row+2 == 7:
                new_board[row+2][col-2] = 'B'
            else:
                new_board[row+2][col-2] = piece
            new_board[row][col] = '.'
            new_board[row+1][col-1] = '.'
            # recursive_takes(new_board, row+2, col-2, red'sturn)
            recursive_takes(new_board, row+2, col-2, 'b', successors, piece)
            isSwap = True

        # if we can take down right (take piece @ row+1, col+1)
        if row+2 <= 7 and col+2 <= 7 and (board[row+1][col+1] in ['r', 'R']) and board[row+2][col+2] == '.':
            # new_state = state after taking down-right
            new_board = copy.deepcopy(board)
            if row+2 == 7:
                new_board[row+2][col+2] == 'B'
            else:
                new_board[row+2][col+2] = piece
            new_board[row][col] = '.'
            new_board[row+1][col+1] = '.'
            # recursive_takes(new_board, row+2, col+2, red'sturn)
            recursive_takes(new_board, row+2, col+2, 'b', successors, piece)
            isSwap = True
        
        if piece =='B':
            # if we can take up-left (take piece @ row-1, col-1)
            if row-2 >= 0 and col-2 >= 0 and (board[row-1][col-1] in ['r', 'R']) and board[row-2][col-2] == '.':
                # new_state = state after taking left
                new_board = copy.deepcopy(board)
                new_board[row-2][col-2] = piece
                new_board[row][col] = '.'
                new_board[row-1][col-1] = '.'
                # recursive_takes(new_board, row-2, col-2, red'sturn)
                recursive_takes(new_board, row-2, col-2, 'b', successors, piece)
                isSwap = True

            # if we can take up-right (take piece @ row-1, col+1)
            if row-2 >= 0 and col+2 <= 7 and (board[row-1][col+1] in ['r', 'R']) and board[row-2][col+2] == '.':
                # new_state = state after taking right
                new_board = copy.deepcopy(board)
                new_board[row-2][col+2] = piece
                new_board[row][col] = '.'
                new_board[row-1][col+1] = '.'
                # recursive_takes(new_state, row-2, col+2, red'sturn)
                recursive_takes(new_board, row-2, col+2, 'b', successors, piece)
                isSwap = True

    return isSwap


def recursive_takes(board, row, col, turn, successors, piece):
    '''
    input: board
    returns True if a swap happened, False if it didnt
    the recursive_takes() function by default modifies successors without having to return anything
    This function should be executed AFTER the first swap to not dupe states!
    '''
    # swap variables
    isSwap = False # True if a swap happened
    skipThis = False # True if we can double/triple take
    # red's turn 
    if turn == 'r':
        # if we can take up-left (take piece @ row-1, col-1)
        if row-2 >= 0 and col-2 >= 0 and (board[row-1][col-1] in ['b', 'B']) and board[row-2][col-2] == '.':
            # new_state = state after taking left
            new_board = copy.deepcopy(board)
            if row-2 == 0:
                new_board[row-2][col-2] = 'R'
            else:
                new_board[row-2][col-2] = piece
            new_board[row][col] = '.'
            new_board[row-1][col-1] = '.'
            # recursive_takes(new_board, row-2, col-2, red'sturn)
            recursive_takes(new_board, row-2, col-2, 'r', successors, piece)
            isSwap = True

        # if we can take up-right (take piece @ row-1, col+1)
        if row-2 >= 0 and col+2 <= 7 and (board[row-1][col+1] in ['b', 'B']) and board[row-2][col+2] == '.':
            # new_state = state after taking right
            new_board = copy.deepcopy(board)
            if row-2 == 0:
                new_board[row-2][col+2] = 'R'
            else:
                new_board[row-2][col+2] = piece
            new_board[row][col] = '.'
            new_board[row-1][col+1] = '.'
            # recursive_takes(new_state, row-2, col+2, red'sturn)
            recursive_takes(new_board, row-2, col+2, 'r', successors, piece)
            isSwap = True

        # account for down moves if the piece is a red king
        if piece == 'R':

            # if we can take down left (take piece @ row+1, col-1)
            if row+2 <= 7 and col-2 >= 0 and (board[row+1][col-1] in ['b', 'B']) and board[row+2][col-2] == '.':
                # new_state = state after taking down-left
                new_board = copy.deepcopy(board)
                new_board[row+2][col-2] = piece
                new_board[row][col] = '.'
                new_board[row+1][col-1] = '.'
                # recursive_takes(new_board, row+2, col-2, red'sturn)
                recursive_takes(new_board, row+2, col-2, 'r', successors, piece)
                isSwap = True

            # if we can take down right (take piece @ row+1, col+1)
            if row+2 <= 7 and col+2 <= 7 and (board[row+1][col+1] in ['b', 'B']) and board[row+2][col+2] == '.':
                # new_state = state after taking down-right
                new_board = copy.deepcopy(board)
                new_board[row+2][col+2] = piece
                new_board[row][col] = '.'
                new_board[row+1][col+1] = '.'
                # recursive_takes(new_board, row+2, col+2, red'sturn)
                recursive_takes(new_board, row+2, col+2, 'r', successors, piece)
                isSwap = True

    # black's turn
    if turn == 'b':
        # if we can take down left (take piece @ row+1, col-1)
        if row+2 <= 7 and col-2 >= 0 and (board[row+1][col-1] in ['r', 'R']) and board[row+2][col-2] == '.':
            # new_state = state after taking down-left
            new_board = copy.deepcopy(board)
            if row+2 == 7:
                new_board[row+2][col-2] = 'B'
            else:
                new_board[row+2][col-2] = piece
            new_board[row][col] = '.'
            new_board[row+1][col-1] = '.'
            # recursive_takes(new_board, row+2, col-2, red'sturn)
            recursive_takes(new_board, row+2, col-2, 'b', successors, piece)
            isSwap = True

        # if we can take down right (take piece @ row+1, col+1)
        if row+2 <= 7 and col+2 <= 7 and (board[row+1][col+1] in ['r', 'R']) and board[row+2][col+2] == '.':
            # new_state = state after taking down-right
            new_board = copy.deepcopy(board)
            if row+2 == 7:
                new_board[row+2][col+2] = 'B'
            else:
                new_board[row+2][col+2] = piece
            new_board[row][col] = '.'
            new_board[row+1][col+1] = '.'
            # recursive_takes(new_board, row+2, col+2, red'sturn)
            recursive_takes(new_board, row+2, col+2, 'b', successors, piece)
            isSwap = True
        
        if piece =='B':
            # if we can take up-left (take piece @ row-1, col-1)
            if row-2 >= 0 and col-2 >= 0 and (board[row-1][col-1] in ['r', 'R']) and board[row-2][col-2] == '.':
                # new_state = state after taking left
                new_board = copy.deepcopy(board)
                new_board[row-2][col-2] = piece
                new_board[row][col] = '.'
                new_board[row-1][col-1] = '.'
                # recursive_takes(new_board, row-2, col-2, red'sturn)
                recursive_takes(new_board, row-2, col-2, 'b', successors, piece)
                isSwap = True

            # if we can take up-right (take piece @ row-1, col+1)
            if row-2 >= 0 and col+2 <= 7 and (board[row-1][col+1] in ['r', 'R']) and board[row-2][col+2] == '.':
                # new_state = state after taking right
                new_board = copy.deepcopy(board)
                new_board[row-2][col+2] = piece
                new_board[row][col] = '.'
                new_board[row-1][col+1] = '.'
                # recursive_takes(new_state, row-2, col+2, red'sturn)
                recursive_takes(new_board, row-2, col+2, 'b', successors, piece)
                isSwap = True

    # if isSwap == False, we append the state: this is a terminal position
    if not isSwap:
        # if a swap was made, and no more takes can be made
        # make a state with board, set it to other player's turn
        state = State(board)
        if turn == 'r':
            state.turn = 'b'
        elif turn == 'b':
            state.turn == 'r'
        # caching
        string_board = stringify(state)
        if cache.get(string_board) == None:
            # add terminal state to cache
            cache[string_board] = (evaluation(state), state)        
        successors.append((cache.get(string_board)[0], state)) 
    return isSwap


def generate_successors(state):
    '''
    returns a list of successor states. 
    Inputs: turn: player who is currently moving: either red or black
    board: the current board

    for a piece at board[row][col], a piece can move:
    for red: regular can move to board[row-1][col-1], or board[row-1][col+1]
        red king: board[row-1][col-1], board[row-1][col+1], board[row+1][col-1], or board[row+1][col+1]

    Successors only stores swaps if there is a swap, and otherwise, stores all possible moves. to do this, make two frontiers and return whichever one applies
    Stores states as a tuple (eval, state) where eval is the evaluation 
    '''
    board = state.board
    isSwap = False # toggles if the frontier is only swaps or blank moves
    successors_swap = []
    successors_noswap = []

    # iterate through the board
    for row in range(len(board)):
        for col in range(len(board[row])):
            # Red's turn 
            if state.turn == 'r':
                if board[row][col] in ['r', 'R']:
                    # check if taking is possible (also adds taking moves to successors)
                    if takes(board, row, col, 'r', successors_swap, board[row][col]) == True:
                        isSwap = True
                    if isSwap == False: # check for empty guys only: no swaps available from this position
                        one_move(board, row, col, 'r', successors_noswap, board[row][col])

            # Black's turn
            elif state.turn == 'b':
                if board[row][col] in ['b', 'B']:
                    # check if taking is possible (also adds taking moves to successors)
                    if takes(board, row, col, 'b', successors_swap, board[row][col]) == True:
                        isSwap = True
                    if isSwap == False: # check for empty guys only: no swaps available from this position
                        one_move(board, row, col, 'b', successors_noswap, board[row][col])
    if isSwap == True:
        return successors_swap
    elif isSwap == False:
        return successors_noswap

def print_successors(successors):
    for i in range(len(successors)):
        print(successors[i].board)

def compute_utility(state):
    board = state.board
    reds = 0
    red_kings = 0
    blacks = 0
    black_kings = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == 'r':
                reds += 1
            elif board[row][col] == 'R':
                red_kings += 1
            elif board[row][col] == 'b':
                blacks += 1
            elif board[row][col] == 'B':
                black_kings += 1

# def cannot_move(state, row, col, piece):
#     '''
#     takes in a state and a (row, col) index pair of a piece and returns True if the piece has no legal moves
#     To be used in evaluation: if no piece can move during a player's turn, return a win for the other player
#     '''
def is_safe(state, row, col):
    '''
    Returns True if a piece is safe from capture
    - isSafe only checks for single captures
    '''

    isSafe = True
    canMove = None
    isForking = None
    # king position ratings

    # forward rating for normie pieces only: want to know how close they are from becoming kings
    forwardRating = None
    middleRating = None

    piece = state.board[row][col]
    if row == 0 or row == 7 or col == 0 or col == 7:
        isSafe = True
        return isSafe
    # piece is not at the edge of the board 
    if piece in ['r', 'R']:
        if state.board[row-1][col-1] in ['b', 'B'] and state.board[row+1][col+1] == '.':
            isSafe = False
        if state.board[row-1][col+1] in ['b', 'B'] and state.board[row+1][col-1] == '.':
            isSafe = False
        # back takes
        if state.board[row+1][col-1] == 'B' and state.board[row-1][col+1] == '.':
            isSafe = False
        if state.board[row+1][col+1] == 'B' and state.board[row-1][col-1] == '.':
            isSafe = False
        
    elif piece in ['b', 'B']:
        if state.board[row+1][col-1] in ['r', 'R'] and state.board[row-1][col+1] == '.':
            isSafe = False
        if state.board[row+1][col+1] in ['r', 'R'] and state.board[row-1][col-1] == '.':
            isSafe = False
        # back takes
        if state.board[row-1][col-1] == 'R' and state.board[row+1][col+1] == '.':
            isSafe = False
        if state.board[row-1][col+1] == 'R' and state.board[row+1][col-1] == '.':
            isSafe = False
    
    return isSafe

def can_move(state, row, col):
    '''
    Returns true if the piece can move
    '''
    board = state.board
    piece = state.board[row][col]
    if piece == 'r':
        # emptyspaces
        if row-1 >= 0 and col-1 >= 0 and board[row-1][col-1] == '.':
            return True
        if row-1 >= 0 and col+1 <= 7 and board[row-1][col+1] == '.':
            return True
        # takes
        if row-2 >= 0 and col-2 >= 0 and (board[row-1][col-1] in ['b', 'B']) and board[row-2][col-2] == '.':
            return True
        if row-2 >= 0 and col+2 <= 7 and (board[row-1][col+1] in ['b', 'B']) and board[row-2][col+2] == '.':
            return True        
    elif piece == 'R':
        # emptyspaces
        if row-1 >= 0 and col-1 >= 0 and board[row-1][col-1] == '.':
            return True
        if row-1 >= 0 and col+1 <= 7 and board[row-1][col+1] == '.':
            return True
        if row+1 <= 7 and col-1 >= 0 and board[row+1][col-1] == '.':
            return True
        if row+1 <= 7 and col+1 <= 7 and board[row+1][col+1] == '.':
            return True
        #takes
        if row-2 >= 0 and col-2 >= 0 and (board[row-1][col-1] in ['b', 'B']) and board[row-2][col-2] == '.':
            return True
        if row-2 >= 0 and col+2 <= 7 and (board[row-1][col+1] in ['b', 'B']) and board[row-2][col+2] == '.':
            return True    
        if row+2 <= 7 and col-2 >= 0 and (board[row+1][col-1] in ['b', 'B']) and board[row+2][col-2] == '.':
            return True 
        if row+2 <= 7 and col+2 <= 7 and (board[row+1][col+1] in ['b', 'B']) and board[row+2][col+2] == '.':
            return True 
    elif piece == 'b':
        #emptyspaces
        if row+1 <= 7 and col-1 >= 0 and board[row+1][col-1] == '.':
            return True
        if row+1 <= 7 and col+1 <= 7 and board[row+1][col+1] == '.':
            return True
        #takes
        if row+2 <= 7 and col-2 >= 0 and (board[row+1][col-1] in ['r', 'R']) and board[row+2][col-2] == '.':
            return True
        if row+2 <= 7 and col+2 <= 7 and (board[row+1][col+1] in ['r', 'R']) and board[row+2][col+2] == '.':
            return True
    elif piece == 'B':
        #emptyspaces
        if row+1 <= 7 and col-1 >= 0 and board[row+1][col-1] == '.':
            return True
        if row+1 <= 7 and col+1 <= 7 and board[row+1][col+1] == '.':
            return True
        if row-1 >= 0 and col-1 >= 0 and board[row-1][col-1] == '.':
            return True
        if row-1 >= 0 and col+1 <= 7 and board[row-1][col+1] == '.':
            return True
        #takes
        if row+2 <= 7 and col-2 >= 0 and (board[row+1][col-1] in ['r', 'R']) and board[row+2][col-2] == '.':
            return True
        if row+2 <= 7 and col+2 <= 7 and (board[row+1][col+1] in ['r', 'R']) and board[row+2][col+2] == '.':
            return True
        if row-2 >= 0 and col-2 >= 0 and (board[row-1][col-1] in ['r', 'R']) and board[row-2][col-2] == '.':
            return True
        if row-2 >= 0 and col+2 <= 7 and (board[row-1][col+1] in ['r', 'R']) and board[row-2][col+2] == '.':
            return True
        
    # no moves
    return False
def compute_middle_utility(row,col,middleRating):
    # euclidean dist from the centre (3.5, 3.5)
    dist = 1/(((3.5-row)**2 + (3.5-col)**2)**(1/2)) # maxed at row in [3,4], col in [3,4]: dist = sqrt(2), min @ corners = sqrt(1/5)
    return dist*middleRating
    

def evaluation(state):
    '''
    Gets the utility of a state
    - infinite utility for won endgame
    - negative infinite utility for lost endgame
    - 5000 for kings
    - 3000 for regular pieces
    - (142.75 x how far you are up) for forward rating (regulars only)
        - 1000 max rating at row just before king row
    - (-250) for # of regular pieces unsafe
    - (-750) for an unsafe king
    - max of 250 for middle rating
    - +350 for king row defense
    '''
    # utility values
    red_utility = 0
    black_utility = 0

    ############################################### parameters to tweak/change! ###############################################
    kingAdvantage = 5000
    regAdvantage = 3000
    forwardRating = 142.75 # times row number of how far you are up: range = [0,7]
    regUnsafe = -250
    kingUnsafe = -750
    middleRating = 250/(2**(1/2)) # maxes out at numerator
    kingRowDefense = 350

    board = state.board
    reds = 0
    red_kings = 0
    blacks = 0
    black_kings = 0
    no_blacks = True
    no_reds = True

    red_can_move = False
    black_can_move = False
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == 'r':
                reds += 1
                no_reds = False
                if red_can_move == False:
                    red_can_move = can_move(state, row, col)
                
                if row == 0 and col in [2, 4, 6]:
                    red_utility += kingRowDefense
                red_utility += forwardRating*(8-row)
                red_utility += compute_middle_utility(row,col,middleRating)
                if is_safe(state,row,col) != True:
                    red_utility += regUnsafe
        
            elif board[row][col] == 'R':
                red_kings += 1
                no_reds = False
                if red_can_move == False:
                    red_can_move = can_move(state, row, col)        
                red_utility += compute_middle_utility(row,col,middleRating)
                if is_safe(state,row,col) != True:
                    red_utility += kingUnsafe

            elif board[row][col] == 'b':
                blacks += 1
                no_blacks = False
                if black_can_move == False:
                    black_can_move = can_move(state, row, col)
                black_utility += compute_middle_utility(row,col,middleRating)               
                if row == 7 and col in [1,3,5]:
                    black_utility += forwardRating*row
                if is_safe(state,row,col) != True:
                    black_utility += regUnsafe
                black_utility += forwardRating*row

            elif board[row][col] == 'B':
                black_kings += 1
                no_blacks = False
                if black_can_move == False:
                    black_can_move = can_move(state, row, col)
                
                if is_safe(state,row,col) != True:
                    black_utility += kingUnsafe
                black_utility += compute_middle_utility(row,col,middleRating)
    
    if no_reds == True:
        return float('-inf')
    elif no_blacks == True:
        return float('inf')
    # if current player can't move, return as win for other player
    if red_can_move == False and state.turn == 'r':
        return float('-inf') # black wins
    elif black_can_move == False and state.turn == 'b':
        return float('inf') # red wins

    red_utility += kingAdvantage*red_kings + regAdvantage*reds
    black_utility += kingAdvantage*black_kings + regAdvantage*blacks   
    return red_utility - black_utility

def stringify(state):
    '''
    returns a string version of state.board
    '''
    stringified = ''
    for line in state.board:
        for letter in line:
            stringified += letter
        stringified += '\n'
    return stringified

############### Alpha Beta Pruning ########################
def a_b_search_max(state):
    v, action = max_value(state, float('-inf'), float('inf'), 0)
    #  return the action in ACTIONS (state) with value v   // ???? 
    return action # type state

def a_b_search_min(state):
    v, action = min_value(state, float('-inf'), float('inf'), 0)
    #  return the action in ACTIONS (state) with value v   // ???? 
    return action # type state

def max_value(state, a, b, depth):
    '''
    returns a utility value
    Note for max and min: caching should only be done at terminal states
    '''

    if is_terminal(state, depth):
        # cache
        string_board = stringify(state)
        if cache.get(string_board) != None:
            return cache.get(string_board)[0], cache.get(string_board)[1]
        # add terminal state to cache
        cache[string_board] = (evaluation(state), state)
        return cache.get(string_board)
    
    # # State caching
    # string_board = stringify(state)
    # if cache_max.get(string_board) != None:
    #     return cache_max.get(string_board)[0], cache_max.get(string_board[1])
    
    v = float('-inf')
    best_action = None
    # move ordering: max orders successors in descending order of utility
    successors = sorted(generate_successors(state), reverse=True, key=lambda k: k[0])

    for succ in successors: # succ is type (state)
        # v = max(v, min_value(action, a, b, depth+1))s
        temp_v = min_value(succ[1], a, b, depth+1)[0]
        if temp_v >= v:
            v = temp_v
            best_action = succ[1]  
        if v >= b:
            return v, best_action
        a = max(a, v)
    
    # # this state not in the cache yet: add it
    # cache_max[string_board] = (v, best_action)
    return v, best_action


def min_value(state, a, b, depth):
    '''
    returns a utility value
    '''

    if is_terminal(state, depth):
        # cache
        string_board = stringify(state)
        if cache.get(string_board) != None:
            return cache.get(string_board)[0], cache.get(string_board)[1]
        # add terminal state to cache
        cache[string_board] = (evaluation(state), state)
        return cache.get(string_board)
    
    # # State caching
    # string_board = stringify(state)
    # if cache_min.get(string_board) != None:
    #     return cache_min.get(string_board)[0], cache_min.get(string_board)[1]
    
    v = float('inf')
    best_action = None
    # move ordering: min orders successors in ascending order of utility
    successors = sorted(generate_successors(state), key=lambda k: k[0])
    for succ in successors: # action is type (eval, state)
        # v = min(v, max_value(action, a, b, depth+1))
        temp_v = max_value(succ[1], a, b, depth+1)[0]
        if temp_v <= v:
            v = temp_v
            best_action = succ[1]
        if v <= a:
            return v, best_action
        b = min(b, v)

    # # this state not in the cache yet: add it
    # cache_min[string_board] = (v, best_action)
    return v, best_action

def is_terminal(state, depth):
    '''
    Returns True if we are at a terminal state: either a won endgame or we have reached the depth limit
    '''
    if depth == 10 or evaluation(state) == float('inf') or evaluation(state) == float('-inf'):
        return True
    return False

def solve(state):
    solution = ''
    temp_state = state
    #print(temp_state)
    while evaluation(temp_state) != float('inf') and evaluation(temp_state) != float('-inf'):
        if temp_state.turn == 'r':
            next_state = a_b_search_max(temp_state)
        elif temp_state.turn == 'b':
            next_state = a_b_search_min(temp_state)
        #print(stringify(temp_state))
        solution += stringify(temp_state) + '\n'
        temp_state = next_state
    # add the last state to solution
    solution += stringify(temp_state)
    #print(stringify(temp_state))
    # write the solution to output file
    output = open(args.outputfile, 'w') ## MODIFIED FOR TEST: args.outputfile
    output.write(solution)
    output.close()
    return solution

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()

    initial_board = read_from_file(args.inputfile)
    state = State(initial_board)
    turn = 'r'
    state.turn = 'r'
    ctr = 0

    sys.stdout = open(args.outputfile, 'w')

    sys.stdout = sys.__stdout__

    solve(state)
    
    #NOTE: TO RUN FILE:
    #    python3 checkers.py --inputfile <input file> --outputfile <output file>
