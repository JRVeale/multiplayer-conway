# Start by making a standard game of life with a random start

# Add teams (colours) and additional rules for their interaction

# Add setup phase where players take turns to place a single starting cell in
# their zone

# Different game modes (placing dot-by-dot, place set 'pieces', etc

# colourblind mode (shapes/patterns instead of colours)

# general TODOs:
'''
Set screen size by worldsize, rather than vice-versa (ideally make unlinked)
'''

from time import sleep
from random import randint
import pygame

pygame.init()
width = 600
height = 600
screen = pygame.display.set_mode((width, height), 0, 24)    # 24-bit screen


def evolve_cell(alive, neighbours):
    return neighbours == 3 or (alive and neighbours == 2)


def count_neighbours(grid, position):
    x, y = position
    neighbour_cells = [(x - 1, y - 1), (x - 1, y + 0), (x - 1, y + 1),
                       (x + 0, y - 1),                 (x + 0, y + 1),
                       (x + 1, y - 1), (x + 1, y + 0), (x + 1, y + 1)]
    count = 0
    for x,y in neighbour_cells:
        if x >= 0 and y >= 0:
            try:
                count += grid[x][y]
            except:
                pass
    return count


def make_empty_grid(x, y):
    return make_grid(x, y, mode="empty")


def make_random_grid(x, y, teams):
    return make_grid(x, y, mode="rand", teams=teams)


def make_grid(x, y, mode="empty", teams=1):
    if mode == "rand":
        def filling():
            return randint(0, teams)
    else:
        def filling():
            return 0
    grid = []
    for r in range(x):
        row = []
        for c in range(y):
            row.append(filling())
        grid.append(row)
    return grid


def evolve(grid):
    x = len(grid)
    y = len(grid[0])
    new_grid = make_empty_grid(x, y)
    for r in range(x):
        for c in range(y):
            cell = grid[r][c]
            neighbours = count_neighbours(grid, (r, c))
            new_grid[r][c] = 1 if evolve_cell(cell, neighbours) else 0
    return new_grid


BLACK = (0, 0, 0)


def draw_block(x, y, size, alive_colour):
    block_size = 10
    x *= block_size
    y *= block_size
    # centre_point = (int(x + (block_size / 2)), int(y + (block_size / 2)))
    # pygame.draw.circle(screen, alive_colour, centre_point, int(block_size/2), 0)
    rect = pygame.Rect(x, y, block_size-2, block_size-2)
    pygame.draw.rect(screen, alive_colour, rect)


def play_game():

    # setup
    cell_number = 0
    alive_colour = pygame.Color(255, 255, 255)
    block_size = 10
    xlen = int(width / block_size)
    ylen = int(height / block_size)
    rounds = 200

    # generate random start
    world = make_random_grid(xlen, ylen, teams=1)

    # for each round
    for i in range(rounds):
        # render current round
        for x in range(xlen):
            for y in range(ylen):
                alive = world[x][y]
                cell_number += 1
                cell_colour = alive_colour if alive else BLACK
                draw_block(x, y, block_size, cell_colour)
        pygame.display.flip()

        # calc next round
        world = evolve(world)
        cell_number = 0

        # wait for next round
        sleep(0.01)

    sleep(5)


def main():
    play_game()


if __name__ == '__main__':
    main()
