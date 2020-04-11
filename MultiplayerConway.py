# NEXT
# Add setup phase where players take turns to place a single starting cell in
# their zone / a few cells at a time / set shapes of cells at a time

# TODOs:
#
# Keep count of each teams total, at each timestep (can then come up with an
# overall score by average points, time in dominance, etc)
#
# Let players pick colours
#
# Make more performant
#
# OOPify
# Use enums instead of strings for modes
#
# Able to save a seed and rerun
#
# Stop the run early if reached end (grid == new_grid)
#
# Set max update rate (photosensitive epilepsy!)
# colourblind mode (shapes/patterns instead of colours)


from time import sleep
from random import randint
import pygame
from math import floor


def evolve_cell(team, neighbours, ruleset):
    if ruleset == "cooperation":
        total_population = 8 - neighbours[0]
        if team != 0:
            if total_population < 2 or total_population > 3:
                # Under/overpopulation -> I diagnose you with dead!
                return 0
            else:
                # Survival -> remain in team
                return team
        else:
            # Reproduction?
            # lots of options for how to do this...
            if total_population == 3:
                for key in neighbours:
                    if key != 0 and neighbours[key] >= 2:
                        # three total neighbours, with a team in the majority
                        return key
                return 0
            else:
                return 0

    elif ruleset == "ignorance":
        # works poorly on a random start
        # but might lead to clean ends on a designed start

        try:
            teammates = neighbours[team]
        except:
            teammates = 0

        if team != 0:
            if teammates < 2 or teammates > 3:
                # Under/overpopulation -> Dead!
                return 0
            else:
                # Survival -> Remain
                return team
        else:
            # Reproduction?
            for key in neighbours:
                if neighbours[key] > 3:
                    # Too crowded for any team to reproduce
                    return 0

            for key in neighbours:
                if neighbours[key] == 3:
                    # Can reproduce unless competition
                    for other_team in neighbours:
                        if neighbours[other_team] == 3:
                            if other_team != key and other_team != 0:
                                return 0
                    return key
                else:
                    # Not enough to reproduce
                    return 0

    elif ruleset == "wretched_violence":
        majority = team
        neighbours.setdefault(majority, 0)
        stalemate = False
        for other_team in neighbours:
            if majority == 0 and neighbours[other_team] > 2:
                majority = other_team
            elif neighbours[other_team] > neighbours[majority]:
                if other_team != 0:
                    majority = other_team
                    stalemate = False
            elif neighbours[other_team] == neighbours[majority]:
                if other_team != 0:
                    stalemate = True
        if stalemate:
            return team
        else:
            return majority

    elif ruleset == "violence":
        if team != 0 and neighbours.setdefault(team, 0) > 3:
            return 0
        else:
            majority = team
            neighbours.setdefault(majority, 0)
            for other_team in neighbours:
                if majority == 0 and neighbours[other_team] > 0:
                    majority = other_team
                elif neighbours[other_team] > neighbours[majority]:
                    if other_team != 0 or majority == 0:
                        majority = other_team
            return majority

    else:
        raise Exception("Unrecognised ruleset!")


def count_neighbours(grid, position):
    x, y = position
    neighbour_cells = [(x - 1, y - 1), (x - 1, y + 0), (x - 1, y + 1),
                       (x + 0, y - 1),                 (x + 0, y + 1),
                       (x + 1, y - 1), (x + 1, y + 0), (x + 1, y + 1)]

    team_counts = {0: 0}
    for x, y in neighbour_cells:
        if x < 0 or y < 0:
            team_counts[0] += 1
        elif x >= 0 and y >= 0:
            try:
                if grid[x][y] not in team_counts:
                    team_counts[grid[x][y]] = 0
                team_counts[grid[x][y]] += 1
            except:
                team_counts[0] += 1
    return team_counts


def make_empty_grid(x, y):
    return make_grid(x, y, mode="empty")


def make_random_grid(x, y, teams, emptiness=1.0):
    return make_grid(x, y, mode="rand", teams=teams, emptiness=emptiness)


def make_grid(x, y, mode="empty", teams=1, emptiness=1.0):
    if mode == "rand":
        def filling():
            # the below ensures there is a reasonable amount of dead space,
            # no matter how many teams there are.
            lower_bound = (1-(teams * emptiness))
            return max(0, randint(lower_bound, teams))
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


def evolve(grid, ruleset):
    x = len(grid)
    y = len(grid[0])
    new_grid = make_empty_grid(x, y)
    for r in range(x):
        for c in range(y):
            team = grid[r][c]
            neighbours = count_neighbours(grid, (r, c))
            new_grid[r][c] = evolve_cell(team, neighbours, ruleset)
    return new_grid


def draw_block(screen, x, y, size, alive_colour):
    block_size = floor(size*0.8)
    x *= int(size)
    y *= int(size)
    rect = pygame.Rect(x, y, block_size, block_size)
    pygame.draw.rect(screen, alive_colour, rect)


def shift_colour(colour,
                 hue_multiplier=1.0, sat_multiplier=1.0, val_multiplier=1.0,
                 alpha_multiplier=1.0,):
    new_colour = pygame.Color(0, 0, 0)
    new_colour.hsva = tuple([
        colour.hsva[0]*hue_multiplier,
        colour.hsva[1]*sat_multiplier,
        colour.hsva[2]*val_multiplier,
        colour.hsva[3]*alpha_multiplier
    ])
    return new_colour


def generate_team_colours(teams):
    team_colours = {
        0: pygame.Color(0, 0, 0),       # Go Team Dead!
        1: pygame.Color(255, 255, 255), # White
        2: pygame.Color(255, 0, 0),     # Red
        3: pygame.Color(0, 255, 0),     # Green
        4: pygame.Color(0, 0, 255),     # Blue
        5: pygame.Color(255, 0, 255),   # Pink
        6: pygame.Color(255, 255, 0),   # Yellow
        7: pygame.Color(0, 255, 255),   # Cyan
        8: pygame.Color(255, 123, 0),   # Orange
        9: pygame.Color(123, 0, 255),   # Purple

    }

    for t in range(teams+1):
        if t not in team_colours:
            prev_cycle_colour = team_colours[t-8]
            team_colours[t] = shift_colour(prev_cycle_colour,
                                           sat_multiplier=0.6)
    return team_colours


def render(screen, xlen, ylen, world, team_colours, block_size):
    for x in range(xlen):
        for y in range(ylen):
            team = world[x][y]
            cell_colour = team_colours[team]
            draw_block(screen, x, y, block_size, cell_colour)
    pygame.display.flip()


def play_game(screen_size=(600, 600),
              field_size=(60, 60), rounds=200, teams=4, emptiness=4,
              ruleset="cooperation",
              rounds_per_second=5, ):

    # setup
    pygame.init()
    width, height = screen_size
    screen = pygame.display.set_mode((width, height), 0, 24)  # 24-bit screen

    xlen, ylen = field_size
    block_size = min((width / xlen), (height / ylen))

    team_colours = generate_team_colours(teams)

    # generate and show random start
    world = make_random_grid(xlen, ylen, teams=teams, emptiness=emptiness)
    render(screen, xlen, ylen, world, team_colours, block_size)
    sleep(1)

    # for each round
    for i in range(rounds):
        # render current round
        render(screen, xlen, ylen, world, team_colours, block_size)

        # calc next round
        world = evolve(world, ruleset)
        cell_number = 0

        # wait for next round
        sleep(1 / rounds_per_second)

    # view results for a while
    sleep(2)


def main():

    play_game(ruleset="cooperation", emptiness=4, teams=4,
              rounds_per_second=20, rounds=50,
              screen_size=(1200, 800), field_size=(100, 90))


if __name__ == '__main__':
    main()
