# CSC384_Sliding_Block_Puzzle 

## Hua Rong Dao

This is a sliding block puzzle consisting of one 2x2 piece, five 2x1 pieces, and four 1x1 pieces.
The 2x1 pieces may be either horizontal or vertical, as there are numerous starting configuraations for the board.
The board consists of a 5x4 grid, meaning that there are two 1x1 spaces on the board. 
The goal of the game is to move the 2x2 piece to the bottom of the board (the "exit"). 
See more information here: https://chinesepuzzles.org/huarong-pass-sliding-block-puzzle/ 

## The Challenge

Our goal was to implement A* and DFS with multi-path pruning to obtain the solution to each initial state, and A* would 
always obtain the optimal solution (i.e. the least number of moves to reach the goal state).
An input text file containing the initial board state is in the following format: 

                  ^11^
                  v11v
                  ^<>^
                  v22v
                  2..2

where the 1's represent a part of the goal piece, the <> and ^v arrows represent either a horizontal or vertical
2x1 piece, the 2's represent single pieces, and the . represents a space.

This board is an example starting configuration; this is the most classic configuration of Hua Rong Dao.

The pieces can be moved so long as they are not rotated and there are no other pieces in the way. Upon running either
A* or DFS, the step-by-step solutions to the goal state will be written into the output file.
* hrd.py is the python file to run, containing all of the A* and DFS algorithms and helper functions.
* test_hrd.txt is a sample input file containing the initial (given) state of the board. 
* astar_sol.txt contains the step-by-step optimal solution to the goal state.
* dfs_sol.txt contains the dfs solution to the goal state, which is not guaranteed to be optimal.

### Notes
This was a project for CSC384, Introduction to Artifical Intelligence (Winter 2023).
