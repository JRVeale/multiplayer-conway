# NEXT
# Add zoned player place_cell start - requires knowing where each player's zone
# is, and we haven't kept that info from the segment generator - mi
#
# Add place saved setpieces - probably worth rewriting with numpy array's and
# convolution instead of


# TODOs:
#
# Keep count of each teams total, at each timestep (can then come up with an
# overall score by average points, time in dominance, etc)
#
# Let players pick colours
#
# Make more performant
#
# OOPify - REALLY do it, fiddling with features is fun, but it's a lot smoother
# if done properly.
# Also use pygame properly (not just for rendering. Separate render loop from
# game logic loop (as if you were doing this properly in a real language)
# ACTUALLY, consider doing this in Unity rather, it'd be fun?
# Use enums instead of strings for modes
#
# Able to save a seed and rerun
#
# Stop the run early if reached end (grid == new_grid)
#
# Set max update rate (photosensitive epilepsy!)
# colourblind mode (shapes/patterns instead of colours)
#
# Why do I always forget about numpy arrays?!

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
                if neighbours[key] > 3 and key != 0:
                    # Too crowded for any team to reproduce
                    return 0

            for key in neighbours:
                if neighbours[key] == 3 and key != 0:
                    # Can reproduce unless competition
                    for other_team in neighbours:
                        if neighbours[other_team] == 3:
                            if other_team != key and other_team != 0:
                                return 0
                    return key
            # not enough neighbours of any individual team
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


def make_random_grid(x, y, teams, emptiness, first_team=1):
    return make_grid(x, y,
                     mode="rand",
                     teams=teams,
                     emptiness=emptiness,
                     first_team=first_team)


def size_segment_grid(x, y, teams):
    # start with an approximation, will either be correct, or be above the
    # largest square number that is too small
    xt = floor(4 * x / (teams + 4))
    yt = floor(4 * y / (teams + 4))

    x_segments = floor(x/xt)
    y_segments = floor(y/yt)
    total_segments = 2 * (x_segments + y_segments) - 4

    # add extra segments (making segments more square where possible)
    # until enough segments for teams
    while total_segments < teams:
        # if not enough segments, divide the larger edge further
        if xt > yt:
            x_segments += 1
        else:
            y_segments += 1
        total_segments = 2 * (x_segments + y_segments) - 4

    # recalculate xt, yt to create this number of segments
    xt = floor(x / x_segments)
    yt = floor(y / y_segments)

    return xt, yt


def arrange_around_edge(grid, list_of_items):
    x_segs = len(grid)
    y_segs = len(grid[0])

    if len(list_of_items) > 2 * (x_segs + y_segs) - 4:
        raise Exception("list_of_items too long for grid")

    mode = "inc_y"
    x = 0
    y = 0

    for i in list_of_items:
        # place item
        grid[x][y] = i

        # see if mode needs changing
        if mode == "inc_y" and y >= y_segs - 1:
            mode = "inc_x"
        elif mode == "inc_x" and x >= x_segs - 1:
            mode = "dec_y"
        elif mode == "dec_y" and y <= 0:
            mode = "dec_x"

        # move to next position
        if mode == "inc_y":
            y += 1
        elif mode == "inc_x":
            x += 1
        elif mode == "dec_y":
            y -= 1
        elif mode == "dec_x":
            x -= 1
        else:
            raise Exception("broken arrange_around_edge")

    return grid


def replace_list_subset(list, subset, index):
    ix, iy = index
    if ix < 0 or iy < 0:
        raise Exception("index out of bounds")
    if ix + len(subset) > len(list) or iy + len(subset[0]) > len(list[0]):
        raise Exception("subset too large for list and index")
    for r in range(len(subset)):
        for c in range(len(subset[0])):
            list[r+ix][c+iy] = subset[r][c]
    return list


def arrange_segments(x, y, mini_grids, teams):
    xt = len(mini_grids[0])
    yt = len(mini_grids[0][0])
    x_segments = floor(x / xt)
    y_segments = floor(y / yt)
    total_segments = 2 * (x_segments + y_segments) - 4

    segments_around_edge = []  # segments in clockwise order around edge

    if total_segments != teams:
        # there are some empty segments that need inserting into mini_grids
        # insert the empty segments equally around the edges
        empty_segments = total_segments - teams
        empty_segment_spacing = floor(total_segments/empty_segments)
        current_team = 0
        for s in range(1, total_segments + 1):
            if s % (empty_segment_spacing+1) == 0 or current_team >= teams:
                # multiple of empty_segment_spacing, place empty segment
                segments_around_edge.append(make_empty_grid(xt, yt))
            else:
                segments_around_edge.append(mini_grids[current_team])
                current_team += 1
    else:
        segments_around_edge = mini_grids

    # make empty grid of grids
    grid_of_segments = []
    for r in range(x_segments):
        row = []
        for c in range(y_segments):
            row.append(make_empty_grid(xt, yt))
        grid_of_segments.append(row)

    # arrange segments on empty grid of grids
    grid_of_segments = arrange_around_edge(grid_of_segments,
                                           segments_around_edge)

    # arrange grid of segments evenly on actual world (with borders around
    # each segment if needed
    world = make_empty_grid(x, y)

    x_gap = floor((x - (xt * x_segments)) / (xt * x_segments - 1))
    y_gap = floor((y - (yt * y_segments)) / (yt * y_segments - 1))

    for r in range(len(grid_of_segments)):
        for c in range(len(grid_of_segments[0])):
            world = replace_list_subset(world, grid_of_segments[r][c],
                                        (r * (xt + x_gap), c * (yt + y_gap)))

    return world


def make_segmented_grid(x, y, teams, emptiness):
    mini_grids = []
    xt, yt = size_segment_grid(x, y, teams)
    for t in range(teams):
        mini_grids.append(make_random_grid(xt, yt, 1, emptiness,
                                           first_team=t + 1))
    return arrange_segments(x, y, mini_grids, teams)


def make_grid(x, y, mode="empty", teams=1, emptiness=1.0, first_team=1):
    if mode == "rand":
        def filling():
            # the below ensures there is a reasonable amount of dead space,
            # no matter how many teams there are.
            lower_bound = (1-(teams * emptiness))
            result = max(0, randint(lower_bound, teams))
            if result != 0:
                result += (first_team - 1)
            return result
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


def draw_outline(screen, pos, size, world_size, colour, thickness = 1):
    xlen, ylen = size
    x_size = xlen * world_size
    y_size = ylen * world_size
    x, y = pos
    rect = pygame.Rect(x, y, int(x_size), int(y_size))

    pygame.draw.rect(screen, colour, rect, thickness)


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


def screen_pos_to_world_pos(screen_pos, world, size):
    x_pos, y_pos = screen_pos
    x_size = len(world) * size
    y_size = len(world[0]) * size
    if x_pos < 0 or x_pos >= x_size or y_pos < 0 or y_pos >= y_size:
        # screen_pos is outside of field
        return -1, -1
    else:
        return floor(x_pos/size), floor(y_pos/size)


def render(screen, xlen, ylen, world, team_colours, block_size,
           outline, cursor):
    for x in range(xlen):
        for y in range(ylen):
            team = world[x][y]
            cell_colour = team_colours[team]
            draw_block(screen, x, y, block_size, cell_colour)
    outline_draw, outline_colour, outline_pos, outline_size = outline
    if outline_draw:
        draw_outline(screen, outline_pos, outline_size, block_size, outline_colour)
    cursor_draw, cursor_colour, cursor_pos = cursor
    if cursor_draw:
        cursor_x, cursor_y = cursor_pos
        draw_block(screen, cursor_x, cursor_y, block_size, cursor_colour)
    pygame.display.flip()


def play_game(screen_size=(600, 600),
              field_size=(60, 60), rounds=200, teams=4, emptiness=4,
              ruleset="cooperation", setup="random",
              placing_turns=0, cells_per_placing_turn=1,
              rounds_per_second=5, ):

    # setup
    pygame.init()
    width, height = screen_size
    screen = pygame.display.set_mode((width, height), 0, 24)  # 24-bit screen

    xlen, ylen = field_size
    block_size = min((width / xlen), (height / ylen))

    team_colours = generate_team_colours(teams)

    outline = (False, pygame.Color(0,0,0), (-1, -1), (-1, -1))
    cursor = (False, pygame.Color(0,0,0), (-1, -1))

    # generate and show random start
    if setup == "random":
        world = make_random_grid(xlen, ylen, teams=teams, emptiness=emptiness)
    elif setup == "segmented":
        world = make_segmented_grid(xlen, ylen, teams=teams,
                                    emptiness=emptiness)
    elif setup == "place_cells" or "segmented_place_cells":
        if placing_turns < 1:
            raise Exception("too few turns")
        if cells_per_placing_turn < 1:
            raise Exception("too few cells_per_turn")

        # start with empty world, and let players click to add a cell
        world = make_empty_grid(xlen, ylen)

        for turn in range(placing_turns):
            for t in range(1, teams + 1):
                for turn_cell in range(cells_per_placing_turn):
                    # show outline to show whose turn it is
                    outline = (True, team_colours[t], (0,0), (xlen, ylen))
                    render(screen, xlen, ylen, world, team_colours, block_size,
                           outline, cursor)
                    # wait for input
                    input_received = False
                    while not input_received:
                        screen_pos = pygame.mouse.get_pos()
                        world_pos = screen_pos_to_world_pos(screen_pos,
                                                            world,
                                                            block_size)
                        cursor = (True,
                                  shift_colour(team_colours[t],
                                               alpha_multiplier=.4),
                                  world_pos)
                        render(screen, xlen, ylen, world, team_colours, block_size,
                               outline, cursor)
                        events = pygame.event.get()
                        for e in events:
                            if e.type == pygame.MOUSEBUTTONUP:
                                # mouse clicked
                                world_x, world_y = world_pos
                                if world_x != -1 or world_y != -1:
                                    if world[world_x][world_y] == 0:
                                        input_received = True
                                        world[world_x][world_y] = t


    else:
        raise Exception("Unrecognised setup")
    render(screen, xlen, ylen, world, team_colours, block_size, outline, cursor)
    sleep(1)

    # for each round
    for i in range(rounds):
        # render current round
        render(screen, xlen, ylen, world, team_colours, block_size, outline, cursor)

        # calc next round
        world = evolve(world, ruleset)
        cell_number = 0

        # wait for next round
        sleep(1 / rounds_per_second)

    # view results for a while
    sleep(2)


def main():

    play_game(ruleset="cooperation", setup="place_cells", emptiness=4, teams=2,
              rounds_per_second=60, rounds=600,
              placing_turns=10, cells_per_placing_turn=2,
              screen_size=(1200, 800), field_size=(50, 40))


if __name__ == '__main__':
    main()
