from detect import screenshot_board, process_board_into_memory, output
from solve import Solver
from imports import print_grid
from time import sleep

def run():

    total_changes = 1
    unseen = 1

    solver = Solver()

    while total_changes > 0 and unseen > 0:

        board, left, top, right, bottom = screenshot_board()
        grid = process_board_into_memory(board)

        old_grid = solver.copy(grid)

        solver.solve(grid, repeat_solving=False, use_old_grid=True, total_mines=99)

        print_grid(solver.grid)

        total_changes, unseen = output(solver.grid, old_grid, left, top, right, bottom)

        sleep(max(0.75, total_changes * 0.01 + 0.4))

if __name__ == '__main__':

    run()
