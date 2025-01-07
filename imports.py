MINE_CONST = '*'
UNSEEN_CONST = '-'
EMPTY_CONST = ' '
CHANGE_CONST = 'c'

def print_grid(grid):
    print('\n'*3)
    for y in grid:
        print(''.join(y))
    print('\n'*3)