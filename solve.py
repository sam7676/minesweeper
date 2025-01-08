# Returns the next state given a grid

from collections import deque
from imports import UNSEEN_CONST, MINE_CONST, CHANGE_CONST, EMPTY_CONST, print_grid
import warnings


def process(grid, old_grid=None, total_mines = 99):

    width = len(grid[0])
    height = len(grid)

    # Check compatability of old grid

    if old_grid is not None:
        if width != len(old_grid[0]) or height != len(old_grid):
            raise Exception("Grids are different sizes")
                    

    # Find all numbers

    number_cells = []

    for row in range(height):
        for col in range(width):
            if grid[row][col] not in (UNSEEN_CONST, MINE_CONST, EMPTY_CONST, CHANGE_CONST):
                number_cells.append((row, col))

                # Find discrepancies with old grid and output warnings
                if old_grid is not None:
                    if grid[row][col] != old_grid[row][col] and old_grid[row][col] not in (UNSEEN_CONST, MINE_CONST, EMPTY_CONST, CHANGE_CONST):
                        warnings.warn(f"Error: grids differ at ({col}, {row}), holding old value {old_grid[row][col]} and new value {grid[row][col]}")
                        grid[row][col] = old_grid[row][col]


            # Setting mines that were lost since the previous round
            if old_grid is not None:

                if old_grid[row][col] == MINE_CONST:

                    grid[row][col] = MINE_CONST


    detect_mine_q = deque(number_cells)

    # If q is empty, set a click in the middle

    if len(detect_mine_q) == 0:

        grid[height // 2][width // 2] = CHANGE_CONST
        return grid

    # Check all numbers - if there are n unseen non-mines, we declare those as mines

    while detect_mine_q:

        y, x = detect_mine_q.popleft()

        num = int(grid[y][x])
        
        poss_mines = 0
        use_unseen = False

        unseen = []
        mines = []
        other = []

        for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            if 0 <= y + dy < height and 0 <= x + dx < width:
                if grid[y + dy][x + dx] in (UNSEEN_CONST, MINE_CONST):
                    poss_mines += 1

                    if grid[y + dy][x + dx] == UNSEEN_CONST:
                        use_unseen = True
                        unseen.append((y + dy, x + dx))
                    else:
                        mines.append((y + dy, x + dx))
                elif grid[y + dy][x + dx] != EMPTY_CONST:
                    other.append((y + dy, x + dx))

        if num == poss_mines and use_unseen:
            for y, x in unseen:
                grid[y][x] = MINE_CONST

            for y, x in other:
                detect_mine_q.append((y, x))

    # Clearing cells where mine requirement is satisfied
    for y, x in number_cells:

        mines = []
        unseen = []

        num = int(grid[y][x])

        for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

            if 0 <= y + dy < height and 0 <= x + dx < width:
                if grid[y + dy][x + dx] == MINE_CONST:
                    mines.append((y + dy, x + dx))
                elif grid[y + dy][x + dx] == UNSEEN_CONST:
                    unseen.append((y + dy, x + dx))
        
        if len(mines) == num:
            for y, x in unseen:
                grid[y][x] = CHANGE_CONST

    # Checking all mines are valid

    for y, x in number_cells:

        # Count surrounding mines

        num_mines = 0

        for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

            if 0 <= y + dy < height and 0 <= x + dx < width:
                if grid[y + dy][x + dx] == MINE_CONST:

                    num_mines += 1
        
        if num_mines > int(grid[y][x]):
            print_grid(grid)
            raise Exception(f"The number of mines is invalid for this board. Check position ({y+1}, {x+1}), with anticipated value {grid[y][x]}. This error is likely due to the computer vision process reading the board incorrectly.")
        

    # Trialling mines on each number

    for y, x in number_cells:

        # Gathering unseen
        num = int(grid[y][x])
        num_mines = 0
        unseen = []

        for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

            if 0 <= y + dy < height and 0 <= x + dx < width:
                if grid[y + dy][x + dx] == UNSEEN_CONST:
                    unseen.append((y + dy, x + dx))
                elif grid[y + dy][x + dx] == MINE_CONST:
                    num_mines += 1

        if len(unseen) == 0:
            continue

        # Collecting numbers around unseen
        sensitive_cells = []    

        for a, b in unseen:
            for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

                if 0 <= a + dy < height and 0 <= b + dx < width:
                    if grid[a + dy][b + dx] not in (UNSEEN_CONST, MINE_CONST, EMPTY_CONST, CHANGE_CONST):
                        sensitive_cells.append((a + dy, b + dx))
    
        def test_sensitive(y1, x1):
            value = int(grid[y1][x1])
            num_mines = 0
            num_unseen = 0
            for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                if 0 <= y1 + dy < height and 0 <= x1 + dx < width:
                    if grid[y1 + dy][x1 + dx] == MINE_CONST:
                        num_mines += 1

                    elif grid[y1 + dy][x1 + dx] == UNSEEN_CONST:
                        num_unseen += 1

            return num_mines <= value <= num_mines + num_unseen


        # Creating array to examine validities
        valid = [[False, False] for _ in range(len(unseen))]

        # Modelling the unseen mines
        for i in range(2**len(unseen)):
            bin_arr = list(map(int, bin(i)[2:].zfill(len(unseen))))

            for j in range(len(unseen)):

                unseen_y, unseen_x = unseen[j]

                if bin_arr[j]:
                
                    grid[unseen_y][unseen_x] = MINE_CONST

                else:
                    grid[unseen_y][unseen_x] = CHANGE_CONST

            valid_model = True

            for a, b in sensitive_cells:
                if not test_sensitive(a, b):
                    valid_model = False
                    break

            if valid_model:

                for j, value in enumerate(bin_arr):
                    valid[j][int(value)] = True

        # Resetting all of unseen
        for y, x in unseen:
            grid[y][x] = UNSEEN_CONST

        # If only one choice is valid, we set for this specific cell

        for i in range(len(valid)):
            if valid[i][0] ^ valid[i][1]:

                unseen_y, unseen_x = unseen[i]

                if valid[i][0]:

                    grid[unseen_y][unseen_x] = CHANGE_CONST

                else:
                    grid[unseen_y][unseen_x] = MINE_CONST

    # Computing number of mines and number of unseen

    unseen = []
    num_mines = 0
    for y in range(height):
        for x in range(width):

            if grid[y][x] == UNSEEN_CONST:
                unseen.append((y, x))

            elif grid[y][x] == MINE_CONST:
                num_mines += 1


    if num_mines == total_mines:
        for a, b in unseen:
            grid[a][b] = CHANGE_CONST
    
    elif num_mines + len(unseen) == total_mines:
        for a, b in unseen:
            grid[a][b] = MINE_CONST

        

    return grid