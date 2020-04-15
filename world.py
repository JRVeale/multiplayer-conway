import numpy as np
from math import floor
from colours import Colours
from time import monotonic
from rendering import Screen
import pygame

class World:
    """The world upon which the Game of Life occurs"""
    # instance variables

    def __init__(self, setup, rules):
        self.array = None
        self.setup = None
        self.rules = None
        self.reset(setup=setup, rules=rules)
        self.team_colours = Colours(setup.teams)

        self.set_last_evolution_millis()

    def update(self, game_tick_wait):
        if self.enough_time_since_last_evolution(game_tick_wait):
            self.evolve()
            self.set_last_evolution_millis()


    def time_since_last_evolution(self):
        return monotonic() * 1000 - self.last_world_update_millis

    def enough_time_since_last_evolution(self, game_tick_wait):
        return self.time_since_last_evolution() >= game_tick_wait

    def set_last_evolution_millis(self):
        self.last_world_update_millis = monotonic() * 1000

    def evolve(self):
        self.array = self.rules.evolve(self.array)

    def render(self, screen):
        # TODO: there will be a more efficient way to do this
        team_grid = self.team_grid_from_world_array(self.array)
        for x in range(len(team_grid)):
            for y in range(len(team_grid[0])):
                screen.draw_block((x, y), self.get_team_colour(team_grid[x][y]))

    def reset(self, setup=None, world_size=None, teams=None, rules=None):
        if setup is not None:
            self.setup = setup
            world_x, world_y = setup.world_size
            # self.array = np.zeros((world_x, world_y, setup.teams))
            self.create_empty_world_array(setup.world_size, setup.teams)
        elif world_size == -1 and teams == -1:
            self.array.fill(0)
        else:
            self.create_empty_world_array(world_size, teams)

        if rules is not None:
            self.rules = rules
        else:
            # Leave the rules as they are
            pass

    def create_empty_world_array(self, world_size, teams):
        world_x, world_y = world_size
        self.array = np.zeros((world_x, world_y, teams))

    def set(self, new_array):
        self.array = new_array

    def get_team_colour(self, team):
        return self.team_colours.get_team_colour(team)

    @staticmethod
    def make_random_grid(size, teams, emptiness=1.0, first_team=1):
        emptiness_lower_bound = 1 - floor(teams * emptiness)
        options = np.arange(emptiness_lower_bound, teams + 1)
        options[options < 0] = 0
        options += (first_team - 1)
        return np.random.choice(options, size=size)

    @staticmethod
    def make_empty_grid(size):
        return np.zeros(size)

    @staticmethod
    def world_array_from_team_grid(team_grid):
        # TODO: REFACTOR so take a World object or at least a number of teams
        teams = np.amax(team_grid)
        x, y = team_grid.shape
        world_array = np.zeros((x, y, teams), dtype=int)
        # fill world_array from team_grid
        for t in range(teams):
            world_array[:, :, t] = np.where(team_grid == t + 1,
                                            team_grid / (t + 1), 0*team_grid)
        return world_array

    @staticmethod
    def team_grid_from_world_array(world_array):
        x = len(world_array)
        y = len(world_array[0])
        teams = len(world_array[0][0])
        team_grid = np.zeros((x, y), dtype=int)
        for t in range(teams):
            team_grid += (world_array[:,:,t] * (t+1))
        return team_grid


class Cursor:
    def __init__(self, style=0):
        self.pos = None
        self.colour = None
        self.active = False
        self.style = style

    def update(self, screen_pos, scaling):
        if self.active:
            x, y = screen_pos
            print("mouse_pos: ")
            print((x, y))
            x = floor(x / scaling)
            y = floor(y / scaling)
            print((x, y))
            self.pos = (x, y)

    def set_team(self, team, colours):
        self.colour = colours.shift_colour(colours.get_team_colour(team),
                                           alpha_multiplier=0.4)

    def hide(self):
        self.active = False

    def show(self):
        self.active = True

    def render(self, screen):
        if self.pos is not None and self.colour is not None and self.active:
            if self.style == 1:
                screen.draw_outline(self.pos, (1.0, 1.0), self.colour,
                                    thickness=4)
            else:
                screen.draw_block(self.pos, self.colour)

