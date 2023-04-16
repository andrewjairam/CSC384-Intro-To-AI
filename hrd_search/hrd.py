from copy import deepcopy
from heapq import heappush, heappop
import time
import argparse
import sys

#====================================================================================

# modelling the big boys
char_goal = '1'
char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation
 
    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]

        MODIFICATION: store the goal piece separately for space: determining the goal piece is an O(n) algorithm where n is the
        number of pieces
        :param goal: the goal piece
        :type pieces: class Piece 
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # MODIFICATION: goal will be found in __construct_grid
        self.goal = Piece(None, None, None, None, None)

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal

                # MODIFICATION: set the goal piece to self.goal
                self.goal = piece
    
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
        

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.


def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    board = Board(pieces)
    
    return board

### HELPERS =========================================================================================================================

def goal_test(state):
    '''
    Takes in a state and returns True if the state is a goal, false if not.
    '''
    for piece in state.board.pieces:
        if piece.is_goal:
            if piece.coord_x == 1 and piece.coord_y == 3:
                return True
    return False

def heuristic_function(state):
    '''
    Takes in a state and return the state's heuristic (manhattan distance of the goal piece from (2,4))
    returns an integer with the heuristic value
    H = abs(2-x) + abs(4-y), where (x,y) are the coordinates of the goal piece
    '''
    for piece in state.board.pieces:
        if piece.is_goal:
            x = piece.coord_x
            y = piece.coord_y
            return abs(1-x) + abs(3-y)

def get_empty_spaces(state):
    '''
    Takes in a state and returns a 1x2 list of the coordinates of the two empty spaces in tuple format. Helper for generate_successors
    '''
    spaces_found = 0
    coords = []

    # i represents y coordinate, j represents x coordinate
    for i in range(5):
        for j in range(4):
            if spaces_found >= 2:
                return coords
            if state.board.grid[i][j] == '.':
                spaces_found += 1
                coords.append((j, i))
    
    return coords # format: [(x1,y1),(x2,y2)]

def make_state(parent, direction, piece_idx):
    '''
    takes in an original state, the INDEX of the piece, and direction to move the piece and makes a new state
    '''
    # make a copy of the board OTHERWISE THE PARENT BOARD WILL CHANGE TOO
    new_state = State(deepcopy(parent.board), 0, 0, parent)

    piece = new_state.board.pieces[piece_idx]
    # the og coords of the piece
    x = piece.coord_x
    y = piece.coord_y

    if direction == 'u':
        piece.coord_y -= 1

        if piece.is_single:
            new_state.board.grid[y][x], new_state.board.grid[y-1][x] = new_state.board.grid[y-1][x], new_state.board.grid[y][x]
        elif piece.is_goal:
            new_state.board.grid[y+1][x], new_state.board.grid[y-1][x] = new_state.board.grid[y-1][x], new_state.board.grid[y+1][x]
            new_state.board.grid[y+1][x+1], new_state.board.grid[y-1][x+1] = new_state.board.grid[y-1][x+1], new_state.board.grid[y+1][x+1]
        else:
            if piece.orientation == 'h':
                new_state.board.grid[y][x], new_state.board.grid[y-1][x] = new_state.board.grid[y-1][x], new_state.board.grid[y][x]
                new_state.board.grid[y][x+1], new_state.board.grid[y-1][x+1] = new_state.board.grid[y-1][x+1], new_state.board.grid[y][x+1]
            elif piece.orientation == 'v':
                new_state.board.grid[y][x], new_state.board.grid[y-1][x] = new_state.board.grid[y-1][x], new_state.board.grid[y][x]
                new_state.board.grid[y+1][x], new_state.board.grid[y][x] = new_state.board.grid[y][x], new_state.board.grid[y+1][x]

    elif direction == 'd':
        piece.coord_y += 1

        if piece.is_single:
            new_state.board.grid[y][x], new_state.board.grid[y+1][x] = new_state.board.grid[y+1][x], new_state.board.grid[y][x]
        elif piece.is_goal:
            new_state.board.grid[y][x], new_state.board.grid[y+2][x] = new_state.board.grid[y+2][x], new_state.board.grid[y][x]
            new_state.board.grid[y][x+1], new_state.board.grid[y+2][x+1] = new_state.board.grid[y+2][x+1], new_state.board.grid[y][x+1]
        else:
            if piece.orientation == 'h':
                new_state.board.grid[y][x], new_state.board.grid[y+1][x] = new_state.board.grid[y+1][x], new_state.board.grid[y][x]
                new_state.board.grid[y][x+1], new_state.board.grid[y+1][x+1] = new_state.board.grid[y+1][x+1], new_state.board.grid[y][x+1]
            elif piece.orientation == 'v':
                new_state.board.grid[y+1][x], new_state.board.grid[y+2][x] = new_state.board.grid[y+2][x], new_state.board.grid[y+1][x]
                new_state.board.grid[y+1][x], new_state.board.grid[y][x] = new_state.board.grid[y][x], new_state.board.grid[y+1][x]

    elif direction == 'l':
        piece.coord_x -= 1

        if piece.is_single:
            new_state.board.grid[y][x], new_state.board.grid[y][x-1] = new_state.board.grid[y][x-1], new_state.board.grid[y][x]
        elif piece.is_goal:
            new_state.board.grid[y][x+1], new_state.board.grid[y][x-1] = new_state.board.grid[y][x-1], new_state.board.grid[y][x+1]
            new_state.board.grid[y+1][x+1], new_state.board.grid[y+1][x-1] = new_state.board.grid[y+1][x-1], new_state.board.grid[y+1][x+1]
        else:
            if piece.orientation == 'h':
                new_state.board.grid[y][x], new_state.board.grid[y][x-1] = new_state.board.grid[y][x-1], new_state.board.grid[y][x]
                new_state.board.grid[y][x+1], new_state.board.grid[y][x] = new_state.board.grid[y][x], new_state.board.grid[y][x+1]
            elif piece.orientation == 'v':
                new_state.board.grid[y][x], new_state.board.grid[y][x-1] = new_state.board.grid[y][x-1], new_state.board.grid[y][x]
                new_state.board.grid[y+1][x], new_state.board.grid[y+1][x-1] = new_state.board.grid[y+1][x-1], new_state.board.grid[y+1][x]

    elif direction == 'r':
        piece.coord_x += 1

        if piece.is_single:
            new_state.board.grid[y][x], new_state.board.grid[y][x+1] = new_state.board.grid[y][x+1], new_state.board.grid[y][x]
        elif piece.is_goal:
            new_state.board.grid[y][x], new_state.board.grid[y][x+2] = new_state.board.grid[y][x+2], new_state.board.grid[y][x]
            new_state.board.grid[y+1][x], new_state.board.grid[y+1][x+2] = new_state.board.grid[y+1][x+2], new_state.board.grid[y+1][x]
        else:
            if piece.orientation == 'h':
                new_state.board.grid[y][x+2], new_state.board.grid[y][x+1] = new_state.board.grid[y][x+1], new_state.board.grid[y][x+2]
                new_state.board.grid[y][x+1], new_state.board.grid[y][x] = new_state.board.grid[y][x], new_state.board.grid[y][x+1]
            elif piece.orientation == 'v':
                new_state.board.grid[y][x], new_state.board.grid[y][x+1] = new_state.board.grid[y][x+1], new_state.board.grid[y][x]
                new_state.board.grid[y+1][x], new_state.board.grid[y+1][x+1] = new_state.board.grid[y+1][x+1], new_state.board.grid[y+1][x]

    # new_state.parent = parent
    new_state.depth = parent.depth + 1
    new_state.f = new_state.depth + heuristic_function(new_state)

    return new_state


def generate_successors(state):
    '''
    Takes in a state and returns a list of successor states
    '''
    state_list = []
    # algorithm: 
        # get_empty_spaces to get the empty space coordinates
        # iterate through pieces and check if any can move to the empty space
    empty_coords = get_empty_spaces(state)
    piece_idx = 0
    for piece in state.board.pieces:
        x, y = piece.coord_x, piece.coord_y
        if piece.is_goal:
            if empty_coords == [(x, y-1), (x+1, y-1)]:
                # move up
                state_list.append(make_state(state, 'u', piece_idx))
            if empty_coords == [(x-1, y), (x-1, y+1)]:
                #move left
                state_list.append(make_state(state, 'l', piece_idx))
            if empty_coords == [(x, y+2), (x+1, y+2)]:
                #move down
                state_list.append(make_state(state, 'd', piece_idx))
            if empty_coords == [(x+2, y), (x+2, y+1)]:
                #move right
                state_list.append(make_state(state, 'r', piece_idx))
        elif piece.is_single:
            for empty in empty_coords:
                if empty == (x+1, y):
                    #move right
                    state_list.append(make_state(state, 'r', piece_idx))
                if empty == (x-1, y):
                    #move left
                    state_list.append(make_state(state, 'l', piece_idx))
                if empty == (x, y-1):
                    #move up
                    state_list.append(make_state(state, 'u', piece_idx))
                if empty == (x, y+1):
                    #move down
                    state_list.append(make_state(state, 'd', piece_idx))                   
        else:
            if piece.orientation == 'v':
                if empty_coords == [(x-1, y), (x-1, y+1)]:
                    # move left
                    state_list.append(make_state(state, 'l', piece_idx))
                if empty_coords == [(x+1, y), (x+1, y+1)]:
                    # move right
                    state_list.append(make_state(state, 'r', piece_idx))
                for empty in empty_coords:
                    if empty == (x, y-1):
                        # move up
                        state_list.append(make_state(state, 'u', piece_idx))
                    if empty == (x, y+2):
                        # move down
                        state_list.append(make_state(state, 'd', piece_idx))

            elif piece.orientation == 'h':
                if empty_coords == [(x, y-1), (x+1, y-1)]:
                    # move up
                    state_list.append(make_state(state, 'u', piece_idx))
                if empty_coords == [(x, y+1), (x+1, y+1)]:
                    # move down
                    state_list.append(make_state(state, 'd', piece_idx))
                for empty in empty_coords:
                    if empty == (x-1, y):
                        # move left
                        state_list.append(make_state(state, 'l', piece_idx))
                    if empty == (x+2, y):
                        # move right
                        state_list.append(make_state(state, 'r', piece_idx))
        piece_idx += 1

    return state_list

# UNUSED?
def get_solution(goal):
    '''
    Given a goal state, backtrack through the parent state references until the initial state. 
    Return a sequence of states from the initial state to the goal state.
    '''
    cur_state = goal
    solution = ''
    temp = ''
    Stop = False
    while not Stop:
        for line in cur_state.board.grid:
            for letter in line:
                temp += letter
            temp += '\n'  
        solution = temp + '\n' + solution
        temp = ''
        if cur_state.parent == None:
            # print the final guy
            # for line in cur_state.board.grid:
            #     for letter in line:
            #         temp += letter
            #     temp += '\n'  
            # solution = temp + '\n' + solution
            #print(solution)
            Stop = True

        cur_state = cur_state.parent
        #solution += '\n'
    return solution

### SEARCH FUNCTIONS ===================================================================================================================

def dfs(board):
    '''
    Takes an initial state (board) and returns the first solution found by DFS
    '''
    # make the initial state
    state_init = State(board, 0, 0, None)
    state_init.f = heuristic_function(state_init)
    frontier = [state_init]

    string = ''
    # max counter = 100000: break if we exceed 100 000 steps
    max_count = 0
    # pruning
    visited = set()

    while len(frontier) > 0:
        cur_state = frontier.pop()

        # break out and get out if we are at the goal state
        if goal_test(cur_state):
            break
        
        # for line in cur_state.board.grid:
        #     for letter in line:
        #         string += letter
        #     string += '\n'

        # pruning
        stringified = ''
        for line in cur_state.board.grid:
            for letter in line:
                stringified += letter
        if stringified in visited:
            continue
        visited.add(stringified)
        
        #string += '\n'

        for state in generate_successors(cur_state):
            frontier.append(state)

    # write the solution to the output
    
    solution = get_solution(cur_state)
    output = open(args.outputfile, 'w') ## MODIFIED FOR TEST: args.outputfile
    output.write(solution)
    output.close()
    return

        

def astar(board):
    '''
    A* search: Takes in an initial state and returns the optimal solution found by A* search
    '''
    # push tuple (priority, state) onto heap
    # make the initial state
    state_init = State(board, 0, 0, None)
    state_init.f = heuristic_function(state_init)
    frontier = [state_init]

    string = ''
    # max counter = 100000: break if we exceed 100 000 steps
    max_count = 0

    # initialize the heap
    h = []
    heappush(h, (state_init.f, state_init.id, state_init))

    # pruning
    visited = set()

    while len(h) > 0:

        cur_state = heappop(h)[2]

        # break out and get out if we are at the goal state
        if goal_test(cur_state):
            break
        
        # for line in cur_state.board.grid:
        #     for letter in line:
        #         string += letter
        #     string += '\n'

        # pruning
        stringified = ''
        for line in cur_state.board.grid:
            for letter in line:
                stringified += letter
        if stringified in visited:
            continue
        visited.add(stringified)
        
        #string += '\n'

        for state in generate_successors(cur_state):
            heappush(h, (state.f, state.id, state))

    solution = get_solution(cur_state)
    output = open(args.outputfile, 'w') ## MODIFIED FOR TEST: args.outputfile
    output.write(solution)
    output.close()
    return 0




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board = read_from_file(args.inputfile) ## MODIFIED FOR TEST: args.inputfile
    
    dfs(board)

    starttime = time.time()
    astar(board)
    print(time.time() - starttime)


