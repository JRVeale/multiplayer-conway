import numpy as np
from enum import Enum

from world import World

# TODO: Bring across other setup modes
# TODO: Saving and loading setups (whether use user input or not)


class Setup:
    """The possible ways in which to setup the world"""
    def __init__(self, world_size, teams, segmented):
        self.world_size = world_size
        self.teams = teams
        self.needs_user_input = False
        self.finished = False
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
    def create(world_size, teams, setup_name=Names.RANDOM, segmented=Segmented.NONE):
        if setup_name == Setup.Names.RANDOM:
            return SetupRandom(world_size, teams, segmented=segmented)
        else:
            raise NotImplementedError()

    def place_cells(self):
        raise NotImplementedError("This class shouldn't be used,"
                                  "it is an abstract base class")


class SetupRandom(Setup):
    def place_cells(self):
        if self.segmented == Setup.Segmented.NONE:
            team_grid = World.make_random_grid(self.world_size, self.teams,
                                               emptiness=4.0)
            return World.world_array_from_team_grid(team_grid)
        else:
            raise NotImplementedError("Not yet implemented, sorry!")


class SetupPlace(Setup):
    def __init__(self, segmented):
        Setup.__init__(self, segmented)
        self.needs_user_input = True

    def place_cells(self):
        raise NotImplementedError("Not yet implemented, sorry!")
