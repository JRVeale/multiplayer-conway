import numpy as np
from enum import Enum

from world import World
from math import floor

# TODO: Bring across other setup modes
# TODO: Saving and loading setups (whether use user input or not)


class Setup:
    """The possible ways in which to setup the world"""
    def __init__(self, world_size, teams, segmented):
        self.world_size = world_size
        self.teams = teams
        self.needs_user_input = False
        self.segmented = segmented

    class Names(Enum):
        RANDOM = 0
        PLACE_CELLS = 1

    class Segmented(Enum):
        NONE = 0
        EDGES = 1
        EDGES_NO_CORNERS = 2

    # factory for inherited setup classes
    @staticmethod
    def create(world_size, teams, setup_name=Names.RANDOM,
               segmented=Segmented.NONE,
               num_cells_each=None,):
        if setup_name == Setup.Names.RANDOM:
            return SetupRandom(world_size, teams, segmented=segmented)
        elif setup_name == Setup.Names.PLACE_CELLS:
            return SetupPlace(world_size, teams, segmented=segmented,
                              num_cells_each=num_cells_each)
        else:
            raise NotImplementedError()

    def place_cells(self):
        raise NotImplementedError("This class shouldn't be used,"
                                  "it is an abstract base class")

    def setup_complete(self):
        raise NotImplementedError("This class shouldn't be used,"
                                  "it is an abstract base class")


class SetupRandom(Setup):
    def place_cells(self):
        if self.segmented == Setup.Segmented.NONE:
            team_grid = World.make_random_grid(self.world_size, self.teams,
                                               emptiness=4.0)
            return World.world_array_from_team_grid(team_grid)

        elif self.segmented == Setup.Segmented.EDGES:
            raise NotImplementedError("Not yet implemented, sorry!")
        else:
            raise NotImplementedError("Not yet implemented, sorry!")

    def setup_complete(self):
        return True


class SetupPlace(Setup):
    def __init__(self, world_size, teams, segmented, num_cells_each):
        Setup.__init__(self, world_size, teams, segmented)
        self.needs_user_input = True
        x, y = world_size
        if num_cells_each is None:
            self.num_cells_each = floor(0.2*x*y/teams)
        elif num_cells_each*teams > x*y:
            raise ValueError("The world isn't big enough for this many cells!")
        else:
            self.num_cells_each = num_cells_each
        self.placing_rounds_complete = 0

    def place_cells(self, world_array, team, cursor_pos):
        if self.segmented == Setup.Segmented.NONE:
            # use cursor_pos and team to add a live cell to world map
            new_world_array = World.change_cell_team(world_array,
                                                     cursor_pos,
                                                     team)
            if team == self.teams:
                self.placing_rounds_complete += 1
            return new_world_array
        else:
            raise NotImplementedError("Not yet implemented, sorry!")

    def setup_complete(self):
        return self.placing_rounds_complete >= self.num_cells_each
