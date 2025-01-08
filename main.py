from detect import screenshot_board, process_board_into_memory, output
from solve import process
from imports import print_grid
from time import sleep

def run():

    total_changes = 1
    unseen = 1

    old_grid = None

    while total_changes > 0 and unseen > 0:

        board, left, top, right, bottom = screenshot_board()
        grid = process_board_into_memory(board)
        grid = process(grid, old_grid=old_grid)
        print_grid(grid)
        total_changes, unseen = output(grid, old_grid, left, top, right, bottom)

        old_grid = grid
        sleep(max(0.75, total_changes * 0.015 + 0.3))

if __name__ == '__main__':

    run()
