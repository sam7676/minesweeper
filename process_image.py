from detect import process_board_into_memory, process
from imports import print_grid

from PIL import Image

board = Image.open('board.png')
grid = process_board_into_memory(board)
grid = process(grid)
print_grid(grid)