import numpy as np
from enum import Enum
from astropy import convolution

from world import World

# TODO: Bring across other rulesets


class Rules:
    """The possible sets of rules for evolving the world"""
    class Name(Enum):
        IGNORANCE = 0
        COOPERATION = 1
        VIOLENCE = 2
        WRETCHED_VIOLENCE = 3

    # TODO: Add borders variable to set whether field is square or toroidal

    # factory for inherited rules classes
    @staticmethod
    def create(rules_name=Name.COOPERATION):
        if rules_name == Rules.Name.COOPERATION:
            return RulesCooperation()

    def evolve(self, world_array):
        pass

    @staticmethod
    def get_neighbours_array(world_array):
        # TODO: REFACTOR so take a World object or at least a number of teams
        neighbours_array = np.zeros(world_array.shape, dtype=int)

        kernel = np.ones((3, 3), dtype=int)
        kernel[1][1] = 0

        _, _, teams = world_array.shape
        for t in range(teams):
            neighbours_array[:, :, t] = \
                (8 * convolution.convolve(world_array[:, :, t], kernel,
                                          fill_value=0))
        return neighbours_array


class RulesCooperation(Rules):
    def evolve(self, world_array):
        # TODO: REFACTOR to take a World object (or at least also take a
        #  number of teams, as after some turns a number of teams are likely to
        #  disappear, causing Exceptions when get_neighbouts_array and
        #  world_array_from_team_grid are called.
        # 3d array, showing count of each team neighbouring for each cell
        neighbours_array = self.get_neighbours_array(world_array)

        # 2d array, showing number of neighbours (all teams) for each cell
        total_neighbours_array = np.sum(neighbours_array, axis=2)

        # 2d array, showing which team is the largest neighbour (if equal, the
        # first of the locally biggest teams - this won't matter as only used
        # if there is an actually dominant team
        biggest_neighbour_array\
            = np.where(total_neighbours_array != 0,
                       np.argmax(neighbours_array, axis=2) + 1,
                       0*total_neighbours_array)

        # 2d array, showing how many neighbours are in the dominant
        # neighbouring team
        num_in_biggest_neighbour_array\
            = np.where(biggest_neighbour_array != 0,
                       np.max(neighbours_array, axis=2),
                       0*biggest_neighbour_array)

        # 2d array, showing the reproductively successful team for each cell,
        # if any. Reproductively successful in this ruleset is
        # (total_neighbours == 3 and one of teams' neighbour count >= 2), if
        # none shows zero
        reproducing_team_array = np.where(
            np.logical_and(
                np.equal(total_neighbours_array, 3),
                np.greater_equal(num_in_biggest_neighbour_array, 2)),
            biggest_neighbour_array,
            0*biggest_neighbour_array)

        world_team_grid = World.team_grid_from_world_array(world_array)
        # if under/overpopulated leave/set dead, else leave in current state
        result_team_grid = np.where(
            np.logical_or(np.less(total_neighbours_array, 2),
                          np.greater(total_neighbours_array, 3)),
            0 * world_team_grid,
            world_team_grid)

        # if was previously dead (0) and tot neighbours == 3, become alive
        result_team_grid += np.where(world_team_grid == 0,
                                    reproducing_team_array,
                                    0*world_team_grid)
        result_world_array = World.world_array_from_team_grid(result_team_grid)

        return result_world_array
