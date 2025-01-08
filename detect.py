# Program used to detect a grid using screen capture

import pyautogui as pg

from imports import UNSEEN_CONST, MINE_CONST, CHANGE_CONST, EMPTY_CONST

distance_threshold = 25


def screenshot_board():

    # Take screenshot

    ss = pg.screenshot()

    # We start using knowledge of grid co-ordinates, can use ML model here to get grid co-ordinates
    # Hard mode

    left, top, right, bottom = (510, 240, 1410, 990)

    ss = ss.crop((left, top, right, bottom))
    
    return ss, left, top, right, bottom

def process_board_into_memory(board):

    def hex_to_tuple(hex_code):
        return tuple(int(hex_code[i:i+2], 16) for i in (1, 3, 5))

    square_size = 37.5

    unchecked_colors = (hex_to_tuple('#AAD751'), hex_to_tuple('#A2D149'))
    checked_colors = (hex_to_tuple('#E5C29F'), hex_to_tuple('#D7B899'))


    colors = [  [(49, 127, 204), 1], 
                [(191, 178, 139), 2], 
                [(215, 81, 73), 3], 
                [(205, 157, 160), 4], 
                [(255, 142, 0), 5], 
                [(4, 152, 167), 6], 
                [(66, 66, 66), 7]]

    board_width = int(board.width // square_size)
    board_height = int(board.height // square_size)

    grid = [['?' for _ in range(board_width)] for _ in range(board_height)]

    # Finds the most likely value for working with unseen and empty

    def compute_min_dist(pixel, color_set):
        min_dist = 10**5
        for color in color_set:

            dist = sum(abs(color[i] - pixel[i]) for i in range(3))

            if dist < min_dist:
                min_dist = dist
        
        return min_dist

    # Detect cell
    for row in range(board_height):
        for col in range(board_width):

            # Find middle of cell

            x = int(col * square_size + square_size // 2)
            y = int(row * square_size + square_size // 2)

            x_outer = int(col * square_size + (square_size * 3 // 4))
            y_outer = int(row * square_size + (square_size * 3 // 4))

            center_pixel = board.getpixel((x, y))
            outer_pixel = board.getpixel((x_outer, y_outer))
            up_pixel = board.getpixel((x, y - 2))
            down_pixel = board.getpixel((x, y + 2))
            left_pixel = board.getpixel((x - 2, y))
            right_pixel = board.getpixel((x + 2, y))
            up_left_pixel = board.getpixel((x - 2, y - 2))
            up_right_pixel = board.getpixel((x + 2, y - 2))
            down_left_pixel = board.getpixel((x - 2, y + 2))
            down_right_pixel = board.getpixel((x + 2, y + 2))

            unseen_valid = True
            for px in (center_pixel, outer_pixel, up_pixel, down_pixel, left_pixel, right_pixel, up_left_pixel, up_right_pixel, down_left_pixel, down_right_pixel):
                if compute_min_dist(px, unchecked_colors) > distance_threshold:
                    unseen_valid = False

            if unseen_valid:
                grid[row][col] = UNSEEN_CONST

            checked_valid = True
            for px in (center_pixel, outer_pixel, up_pixel, down_pixel, left_pixel, right_pixel, up_left_pixel, up_right_pixel, down_left_pixel, down_right_pixel):
                if compute_min_dist(px, checked_colors) > distance_threshold:
                    checked_valid = False

            if checked_valid:
                grid[row][col] = EMPTY_CONST

            if not unseen_valid and not checked_valid:

                # Use nearest neighbour to detect digit

                pixels = (center_pixel, up_pixel, down_pixel, left_pixel, right_pixel, up_left_pixel, up_right_pixel, down_left_pixel, down_right_pixel)
                
                min_distance = 10**5
                digit = -1
                for color_px, num in colors:

                    all_distance = [sum([abs(color_px[i] - px[i]) for i in range(3)]) for px in pixels]

                    distance = sum(sorted(all_distance)[:2])
                    
                    if distance < min_distance:
                        min_distance = distance
                        digit = num

                grid[row][col] = str(digit)

    return grid



def output(grid, old_grid, left, top, right, bottom):

    width = len(grid[0])
    height = len(grid)

    total_changes = 0
    total_unseen = 0

    for row in range(height):
        for col in range(width):
            if grid[row][col] == CHANGE_CONST:
                pg.click(left + col * 37.5 + 18.5, top + row * 37.5 + 18.5)
            
            elif grid[row][col] == UNSEEN_CONST:
                total_unseen += 1

            if old_grid is None:
                total_changes = 1
            elif grid[row][col] != old_grid[row][col]:
                    total_changes += 1

    return total_changes, total_unseen

