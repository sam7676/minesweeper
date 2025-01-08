# Returns the next state given a grid

from collections import deque
from imports import UNSEEN_CONST, MINE_CONST, CHANGE_CONST, EMPTY_CONST, print_grid
import warnings


class Solver:

    def __init__(self):
        self.old_grid = None

    def solve(self, grid, repeat_solving=True, use_old_grid=True, total_mines=99):

        self.grid = grid
        self.width = len(grid[0])
        self.height = len(grid)
        self.total_mines = total_mines

        # Check compatability of old grid

        if self.old_grid is not None:
            if self.width != len(self.old_grid[0]) or self.height != len(self.old_grid):
                raise Exception("Grids are different sizes")
                        

        # Find all numbers

        self.number_cells = []

        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] not in (UNSEEN_CONST, MINE_CONST, EMPTY_CONST, CHANGE_CONST):
                    self.number_cells.append((row, col))

                    # Find discrepancies with old grid and output warnings
                    if self.old_grid is not None:
                        if self.grid[row][col] != self.old_grid[row][col] and self.old_grid[row][col] not in (UNSEEN_CONST, MINE_CONST, EMPTY_CONST, CHANGE_CONST):
                            warnings.warn(f"Error: grids differ at ({col}, {row}), holding old value {self.old_grid[row][col]} and new value {self.grid[row][col]}")
                            self.grid[row][col] = self.old_grid[row][col]


                # Setting mines that were lost since the previous round
                if self.old_grid is not None:

                    if self.old_grid[row][col] == MINE_CONST:

                        self.grid[row][col] = MINE_CONST

        # If q is empty, set a click in the middle

        if len(self.number_cells) == 0:

            self.grid[self.height // 2][self.width // 2] = CHANGE_CONST
            return grid

        self.detect_mines()

        self.round_changes = 1

        # Runs multiple rounds of attempting to solve, stopping when no further information frm a round can be given

        while self.round_changes > 0:

            self.round_changes = 0

            self.clear_cells()
            self.check_mines_valid()
            self.trial_mines()

            if not repeat_solving:
                break

        self.check_complete()

        if use_old_grid:
            self.old_grid = self.copy(grid)

        return grid

    def copy(self, grid):
        return [row[:] for row in grid]

    def reset(self):
        self.old_grid = None

    def detect_mines(self):

        # Check all numbers - if there are n unseen non-mines, we declare those as mines

        detect_mine_q = deque(self.number_cells)

        while detect_mine_q:

            y, x = detect_mine_q.popleft()

            num = int(self.grid[y][x])
            
            poss_mines = 0
            use_unseen = False

            unseen = []
            mines = []
            other = []

            for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                if 0 <= y + dy < self.height and 0 <= x + dx < self.width:
                    if self.grid[y + dy][x + dx] in (UNSEEN_CONST, MINE_CONST):
                        poss_mines += 1

                        if self.grid[y + dy][x + dx] == UNSEEN_CONST:
                            use_unseen = True
                            unseen.append((y + dy, x + dx))
                        else:
                            mines.append((y + dy, x + dx))
                    elif self.grid[y + dy][x + dx] != EMPTY_CONST:
                        other.append((y + dy, x + dx))

            if num == poss_mines and use_unseen:
                for y, x in unseen:
                    self.grid[y][x] = MINE_CONST

                for y, x in other:
                    detect_mine_q.append((y, x))

    def clear_cells(self):

        # Clearing cells where mine requirement is satisfied

        for y, x in self.number_cells:

            mines = []
            unseen = []

            num = int(self.grid[y][x])

            for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

                if 0 <= y + dy < self.height and 0 <= x + dx < self.width:
                    if self.grid[y + dy][x + dx] == MINE_CONST:
                        mines.append((y + dy, x + dx))
                    elif self.grid[y + dy][x + dx] == UNSEEN_CONST:
                        unseen.append((y + dy, x + dx))
            
            if len(mines) == num:
                for y, x in unseen:
                    self.grid[y][x] = CHANGE_CONST
                    self.round_changes += 1
        
    def check_mines_valid(self):

        # Checking all mines are valid

        for y, x in self.number_cells:

            # Count surrounding mines

            num_mines = 0

            for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

                if 0 <= y + dy < self.height and 0 <= x + dx < self.width:
                    if self.grid[y + dy][x + dx] == MINE_CONST:

                        num_mines += 1
            
            if num_mines > int(self.grid[y][x]):
                print_grid(self.grid)
                raise Exception(f"The number of mines is invalid for this board. Check position ({y+1}, {x+1}), with anticipated value {self.grid[y][x]}. This error is likely due to the computer vision process reading the board incorrectly.")
            
    def trial_mines(self):
        # Trialling mines on each number

        for y, x in self.number_cells:

            # Gathering unseen
            num = int(self.grid[y][x])
            num_mines = 0
            unseen = []

            for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

                if 0 <= y + dy < self.height and 0 <= x + dx < self.width:
                    if self.grid[y + dy][x + dx] == UNSEEN_CONST:
                        unseen.append((y + dy, x + dx))
                    elif self.grid[y + dy][x + dx] == MINE_CONST:
                        num_mines += 1

            if len(unseen) == 0:
                continue

            # Collecting numbers around unseen
            sensitive_cells = []    

            for a, b in unseen:
                for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):

                    if 0 <= a + dy < self.height and 0 <= b + dx < self.width:
                        if self.grid[a + dy][b + dx] not in (UNSEEN_CONST, MINE_CONST, EMPTY_CONST, CHANGE_CONST):
                            sensitive_cells.append((a + dy, b + dx))
        
            def test_sensitive(y1, x1):
                value = int(self.grid[y1][x1])
                num_mines = 0
                num_unseen = 0
                for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                    if 0 <= y1 + dy < self.height and 0 <= x1 + dx < self.width:
                        if self.grid[y1 + dy][x1 + dx] == MINE_CONST:
                            num_mines += 1

                        elif self.grid[y1 + dy][x1 + dx] == UNSEEN_CONST:
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
                    
                        self.grid[unseen_y][unseen_x] = MINE_CONST

                    else:
                        self.grid[unseen_y][unseen_x] = CHANGE_CONST

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
                self.grid[y][x] = UNSEEN_CONST

            # If only one choice is valid, we set for this specific cell

            for i in range(len(valid)):
                if valid[i][0] ^ valid[i][1]:

                    unseen_y, unseen_x = unseen[i]

                    if valid[i][0]:

                        self.grid[unseen_y][unseen_x] = CHANGE_CONST
                        self.round_changes += 1

                    else:
                        self.grid[unseen_y][unseen_x] = MINE_CONST
                        self.round_changes += 1

    def check_complete(self):

        # Computing number of mines and number of unseen

        unseen = []
        num_mines = 0
        for y in range(self.height):
            for x in range(self.width):

                if self.grid[y][x] == UNSEEN_CONST:
                    unseen.append((y, x))

                elif self.grid[y][x] == MINE_CONST:
                    num_mines += 1

        if num_mines == self.total_mines:
            for a, b in unseen:
                self.grid[a][b] = CHANGE_CONST
        
        elif num_mines + len(unseen) == self.total_mines:
            for a, b in unseen:
                self.grid[a][b] = MINE_CONST

