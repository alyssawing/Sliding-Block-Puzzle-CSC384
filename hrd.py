from copy import deepcopy
from heapq import heappush, heappop
import time
import argparse
import sys

#====================================================================================

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
        self.coord_x = coord_x  # for top left corner
        self.coord_y = coord_y  # for top left corner
        self.orientation = orientation

    def __repr__(self): 
        '''Prints out the attributes of a piece for debugging purposes.'''
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)

    def move(self, direction):
        '''Moves a piece and updates its attributes. The direction can be 
        left ('l'), right ('r'), up ('u'), down ('d'). The function will return
        which direction the piece has moved or "Error" if it did not work.''' #TODO
        if direction == 'l':
            self.coord_x = self.coord_x-1
        elif direction == 'r':
            self.coord_x = self.coord_x+1
        elif direction == 'u':
            self.coord_y = self.coord_y-1
        elif direction == 'd':
            self.coord_y = self.coord_y+1
        return 
    
class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5
        self.pieces = pieces

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

        for piece in self.pieces: # converting the board into given form
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':  # horizontal 1x2 piece
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':  # vertical 2x1 piece
                    #print(self.grid)
                    #print(piece.coord_y, piece.coord_x)
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'
                    #sprint('success')
        
        # Create string of grid content to be used in explored set comparison
        self.grid_str = ''
        for row in self.grid:
            self.grid_str += ''.join(row) # format: '11<>11^2^^v2vv22<>..'
    
    def convert_line_to_grid(self, line):
        '''Converts a line of characters into a 2-d grid.'''
        grid = []
        for i in range(self.height):
            grid.append(line[i*self.width:(i+1)*self.width])
        return grid

    def display(self):
        """
        Print out the current board. If f is not None, print to the file f.
        """

        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
        # else:
        #     for i, line in enumerate(self.grid):
        #         print(self.convert_line_to_grid(line), file=f)
                # for ch in line:
                #     print(ch, end='', file=f)
                    # f.write(ch)

    
    def find_spaces(self): 
        '''Return the coordinates of the  empty spaces on the board.''' #TODO
        spaces = [] # to store result
        count = 0 # to keep track of how many spaces found (stop at 2)
        # Iterate through each grid space on the board to find empty tiles:
        while count < 2:
            for i in range(self.height):
                for j in range(self.width):
                    if self.grid[i][j] == '.':
                        spaces.append(i)
                        spaces.append(j)
                        count += 1
        
        return spaces # example format: [4,1,4,2] where [4][1] is a space and 
                      # [4][2] is the location of another space 

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
        self.depth = depth # number of states from intial to goal state (cost: g)
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.

        # Each state keeps track of heuristic and f value - get this from the 
        # helper function heuristic(board) to give h value. f = g + h

def read_from_file(filename):
    """
    Load initial board from a given file. Read in a puzzle

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

##############################################################################
################  HELPER FUNCTIONS: ##########################################
##############################################################################

def is_goal(board):
    '''Goal Test: Return True iff the board state is a goal state'''
    if board.grid[3][1]=='1' and board.grid[3][2]=='1' and board.grid[4][1]=='1' \
    and board.grid[4][2]=='1':
        return True   # we are at a goal state; the 2x2 piece is by the exit
    return False  # we are not at a goal state yet

def heuristic(board):  
    '''Heuristic function: takes in a board state and return the state's 
    heuristic (h) value. This will use the Manhattan distance heuristic for 
    the 2x2 piece.'''
    for piece in board.pieces: 
        if piece.is_goal: # only looking at the 2x2 goal tile
            # the goal coordinates for the top left corner of 2x2 tile are [3][1] = [y][x]
            return (abs(3 - piece.coord_y)+abs(1-piece.coord_x)) # Manhattan distance

def find_goal_coords(y,x,board):
    '''Given an x and y coordinate of a part of the 2x2 goal piece, find the
    coordinates of the top left corner of the 2x2 goal piece.'''
    c = '1'
    # Corner cases:
    if x == 0 and y == 0: # top left corner
        x_coord = x # this is the top left corner of the 2x2 piece
        y_coord = y
    elif x == 0 and y == 4: # bottom left corner
        x_coord = x
        y_coord = y-1
    elif x == 0 and y == 0: # top right corner
        x_coord = x-1
        y_coord = y
    elif x == 3 and y == 4: # bottom right corner
        x_coord = x-1
        y_coord = y-1

    # Edge cases (only looking left & up so ignore right & bottom edge):
    elif x == 0: # left edge
        if board.grid[y-1][x] == c:
            y_coord = y-1   
        else:
            y_coord = y
        x_coord = x
    elif y == 0: # top edge
        if board.grid[y][x-1] == c:
            x_coord = x-1
        else:
            x_coord = x
        y_coord = y
    
    else:   # General case in the middle of the board:
        # Find the leftmost coordinate (x_coord)
        if board.grid[y][x-1] == c:
            x_coord = x-1
            y_coord = y
        else:
            x_coord = x
        # Find the topmost coordinate (y_coord)
        if board.grid[y-1][x] == c:
            y_coord = y-1   
        else:
            y_coord = y

    return [y_coord, x_coord]

def id_neighbour(y,x,board): 
    '''Given an x & y coord of a part of a piece, find the coordinates of the 
    top left corner of the piece. Return piece'''
    res = [] # ATM, store the actual top left coords here of the piece: [y,x]

    if board.grid[y][x] == '1': # goal piece
        res = find_goal_coords(y,x,board)
        # print(y,x)
        # print("if1")
        # print("res: ", res)
    elif board.grid[y][x] == '<' or board.grid[y][x] == '^' or \
    board.grid[y][x] == '2': # h left piece, v top piece, or 1x1 piece 
        res.append(y)
        res.append(x)
        # print("if2")
    elif board.grid[y][x] == '>': # h right piece
        res.append(y)
        res.append(x-1)
        # print("if3")
    elif board.grid[y][x] == 'v': # v bottom piece
        res.append(y-1)
        res.append(x)
        # print("if4")
    else: # must be the space
        return None, None # return a piece that doesn't exist

    for i in range(len(board.pieces)):
        if board.pieces[i].coord_y == res[0] and board.pieces[i].coord_x == res[1]:
            # return the piece object and its index in list of pieces:
            return board.pieces[i], i #  format: (piece, i)

def find_neighbours(y, x, res,board): #TODO: test
    '''Given the x & y coords of one space, find a list of the neighbours (piece 
    objects) and what direction they will try to move in towards the space.'''

     # list of pieces to try to move: [('d', piece, i), ('d', piece, i)...]
    # TODO: can i even call move with the 'd' and the piece itself as parameters?

    if (y==0):   # top edge: can only look below, and neighbour tries to go up
        piece, index = id_neighbour(1,x,board)
        res.append(('u', piece, index))
    if (y==4): # bottom edge: can only look above, and neighbour tries to go down
        piece, index = id_neighbour(3,x,board)
        res.append(('d', piece, index))
    if y != 0 and y != 4: # middle y case
        piece1, index1 = id_neighbour(y-1,x,board)
        res.append(('d', piece1, index1))
        piece2, index2 = id_neighbour(y+1,x,board)
        res.append(('u', piece2, index2))
    if (x==0): # left edge: can only look right, and neighbour tries to go left
        piece, index = id_neighbour(y,1,board)
        res.append(('l', piece, index))
    if (x==3): # right edge: can only look left, and neighbour tries to go right
        piece, index = id_neighbour(y,2,board)
        res.append(('r', piece, index))
    if x != 0 and x != 3: # middle x case
        piece1, index1 = id_neighbour(y,x-1,board)
        res.append(('r', piece1, index1))
        piece2, index2 = id_neighbour(y,x+1,board)
        res.append(('l', piece2, index2))
        
    return res # format: [('d', piece, i), ('d', piece, i)...]. [('d', None, i)] if space

def is_valid_move(direction, piece, board):
    '''Checks if a move for a certain piece is valid (if there are spaces 
    in the correct positions. Return True if it works, and False otherwise.
    N.B. Edge cases are not needed here becausse this will only be called 
    if there is a space in the direction where we want to move.'''

    if piece is None:   # two spaces next to each other
        return False
    elif piece.is_single:   # 1x1 piece
        return True # always valid moving into a space
    elif piece.is_goal: # 2x2 goal piece
        if direction == 'l':
            if board.grid[piece.coord_y][piece.coord_x-1] == '.' and \
            board.grid[piece.coord_y+1][piece.coord_x-1] == '.':
                return True
            else:
                return False
        elif direction == 'r':
            if board.grid[piece.coord_y][piece.coord_x+2] == '.' and \
                board.grid[piece.coord_y+1][piece.coord_x+2] == '.':
                return True
            else:
                return False
        elif direction == 'u':
            if board.grid[piece.coord_y-1][piece.coord_x] == '.' and \
                board.grid[piece.coord_y-1][piece.coord_x+1] == '.':
                return True
            else:
                return False
        elif direction == 'd':
            if board.grid[piece.coord_y+2][piece.coord_x] == '.' and \
                board.grid[piece.coord_y+2][piece.coord_x+1] == '.':
                return True
            else:
                return False
    elif piece.orientation == 'h': # horizontal 1x2 piece
        if direction == 'l' or direction == 'r': # always established there's a space where we want to try
            return True
        elif direction == 'u':
            if board.grid[piece.coord_y-1][piece.coord_x] == '.' and \
                board.grid[piece.coord_y-1][piece.coord_x+1] == '.':
                return True
            else:
                return False
        elif direction == 'd':
            if board.grid[piece.coord_y+1][piece.coord_x] == '.' and \
                board.grid[piece.coord_y+1][piece.coord_x+1] == '.':
                return True
            else:
                return False
    elif piece.orientation == 'v': # vertical 2x1 piece
        if direction == 'u' or direction == 'd':
            return True
        elif direction == 'l':
            if board.grid[piece.coord_y][piece.coord_x-1] == '.' and \
                board.grid[piece.coord_y+1][piece.coord_x-1] == '.':
                return True
            else:
                return False
        elif direction == 'r':
            if board.grid[piece.coord_y][piece.coord_x+1] == '.' and \
                board.grid[piece.coord_y+1][piece.coord_x+1] == '.':
                return True
            else:
                return False

    pass

def generate_successors(state, successors): #TODO: test
    '''Take a state and return a list of its successor states'''
    board = state.board
    spaces = board.find_spaces() # format: [y,x,y,x]
    # print(spaces)
    space1 = [spaces[0], spaces[1]]
    space2 = [spaces[2], spaces[3]]
    # successors = [] # to store final successor boards
    res = [] # list of possible moves 
    res = find_neighbours(space1[0], space1[1],res, board) # format: [('d', piece), ('d', piece)...]. [('d', None)] if space
    try_moves = find_neighbours(space2[0], space2[1],res,board)
    #print(try_moves)
    try_moves = set(try_moves) # remove duplicate move attempts
    try_moves = list(try_moves) # convert back to list
    # print(board.grid)
    # print('moves to try',try_moves)
    for attempt in try_moves:   # format: ('d', piece, i) for each attempt
        if is_valid_move(attempt[0], attempt[1], board):
            # print("valid move: ", attempt[0], attempt[1])
            new_piece = deepcopy(attempt[1])   # duplicate the piece to move
            new_piece.move(attempt[0])  # move the new piece in given direction (change its coordinates)
            new_board = deepcopy(board.pieces)  # create new list of board pieces (duplicate)
            new_board[attempt[2]] = new_piece # change the moved piece in the new board list
            new_board = Board(new_board) # create new board with piece changes
            # print("valid  move on new board:")
            # new_board.display()

            # Create new state:
            # State parameters: board, f, depth, parent=None
            new_state = State(new_board, (state.depth+1+heuristic(new_board)), \
               state.depth+1, parent=state)
            successors.append(new_state)

            #TODO: how do i use the self.id in State for breaking ties?
    return successors

def get_solution(initial_state, goal_state):    #TODO: test
    '''Given a goal state, backtrack through the parent state references until
    initial state. Return sequence of states from the initial to the goal.'''
    solution = [] # list of states to lead to given goal state
    solution.append(goal_state)
    p = goal_state.parent
    while p != initial_state:
        solution.insert(0, p)
        p = p.parent
    solution.insert(0,initial_state)
    return solution

def dfs(initial_state): #TODO
    '''Given an initial state, return the first solution (goal_state) found
    using the DFS with pruning algorithm.'''
    frontier = [initial_state]
    explored = set() 
    while frontier:
        curr = frontier.pop() # take out last state in frontier (stack)
        if curr.board.grid_str not in explored:
            # print("I'm exploring the current boards")
            # curr.board.display()
            #print()
            explored.add(curr.board.grid_str)
            if is_goal(curr.board):
                # print("GOAL FOUND!")
                return curr
            frontier = generate_successors(curr, frontier)
    return None

def astar(initial_state): #TODO
    '''Given an initial state, return the first solution (goal_state) found
    using the A* with pruning algorithm.'''
    # frontier is a heapq (priority q with lowest f value and its state at top)
    # frontier format: [(f, state), (f, state)...]
    frontier = [(initial_state.f, initial_state.id, initial_state)] 
    explored = set()
    while frontier:
        curr_f, curr_id, curr = heappop(frontier)    # take out state with smallest f value
        if curr.board.grid_str not in explored:
            explored.add(curr.board.grid_str)
            if is_goal(curr.board):
                # print("number of moves: ", curr.depth)
                return curr
            for successor in generate_successors(curr, []):
                heappush(frontier, (successor.f, successor.id, successor))
    return 

def convert_to_str(state):
    '''Given a state, return a string representation of the board with proper
    formatting (5x4).'''
    res = ""    # string of board to return

    for i in range(len(state.board.grid_str)):
        res += state.board.grid_str[i]
        if (i+1) % 4 == 0:
            res += "\n"
    
    res += "\n"     # add newline at end of board

    return res
        

def write_solution(solution, outputfile): #TODO
    '''Given a list of states that lead from the initial state to the solved 
    goal state, write the solution steps to the output file.'''

    res = ""

    file = open(outputfile, "w")
    for state in solution:  # solution is a list of states
        res += convert_to_str(state)
        # file.write(state.board.display)
    file.write(res)
    file.close()

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
    board = read_from_file(args.inputfile)
    # print("initial state: ")
    # board.display()
    initial_state = State(board,heuristic(board),0)
    # print()
    time1 = time.time()
    if args.algo == 'astar':
        final_goal_state = astar(initial_state)
        time2 = time.time()
    elif args.algo == 'dfs':
        final_goal_state = dfs(initial_state)
        time2 = time.time()
    solution = get_solution(initial_state, final_goal_state)
    # print("elapsed time: ", time2-time1)
    # print("number of moves: ", final_goal_state.depth)
    write_solution(solution, args.outputfile)

##################### DFS TESTING #####################
    # time1 = time.time()
    # print("STARTING DFS: ")
    # goaal = dfs(initial_state)
    # time2 = time.time()
    # print("dfs solution: ")
    # goaal.board.display()
    # print()
    # print("elapsed time: ", time2-time1)
    # # print("solution path: ")
    # # for step in get_solution(initial_state, goaal):
    # #     step.board.display()
    #     # print()

    # print("heuristic: ", heuristic(goaal.board))

##################### A* TESTING #####################
    # time1 = time.time()
    # print("STARTING A*: ")
    # goaal = astar(initial_state)
    # time2 = time.time()
    # print("a* solution: ")
    # goaal.board.display()
    # print()
    # print("elapsed time: ", time2-time1)
    # # print("solution path: ")
    # # for step in get_solution(initial_state, goaal):
    # #     step.board.display()
    # #     print()
    
    # print("heuristic: ", heuristic(goaal.board))





