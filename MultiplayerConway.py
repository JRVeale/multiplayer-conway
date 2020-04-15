import numpy as np
from enum import Enum
from time import sleep, monotonic
import pygame

from world import World, Cursor
from setup import *
from rules import *
from settings import *
from rendering import Screen

# TODO: Stop game if finished
# TODO: Scoring system


class Game:
    class State(Enum):
        SETUP = 0
        PLAYING = 1
        END = 2

    def __init__(self, settings):
        self.world = None
        self.graphics = []
        self.state = Game.State.SETUP
        self.settings = None
        self.screen = Screen(settings.res)
        self.change_settings(settings)
        self.cursor = Cursor()

    def change_settings(self, settings):
        self.settings = settings
        self.screen.change_res(settings.res)

    def update(self):
        # game logic here (setup, running, end, etc)
        if self.state == Game.State.SETUP:
            self.cursor.set_team(1, self.world.team_colours)
            self.cursor.show()

            if self.world.setup.needs_user_input:
                # run through the substates of events to do this setup
                raise NotImplementedError()
            else:
                # no user input, just set it up!
                self.world.set(self.world.setup.place_cells())
                self.world.setup.finished = True

            if self.world.setup.finished:
                # move to PLAYING stage, and reset setup.finished
                print("Finished setup")
                self.state = Game.State.PLAYING
                self.world.setup.finished = False
                self.cursor.hide()
                self.render()
                sleep(2.0)  # pause with view of startup
                print("Starting game")

        elif self.state == Game.State.PLAYING:
            time_since_last = monotonic()\
                              * 1000 - self.world.last_world_update_millis
            if time_since_last >= self.settings.game_tick_wait:
                self.world.update(self.settings.game_tick_wait)

            #TODO: Stop the game! (Could do with a world age attribute...)

        elif self.state == Game.State.END:
            pass

    def get_inputs(self):
        self.cursor.update(pygame.mouse.get_pos(), self.screen.scaling)
        for event in pygame.event.get():
            # must clear events for mouse to update
            # deal with mouse presses and stuff here
            pass

    def render(self):
        self.world.render(self.screen)
        self.cursor.render(self.screen)

        for g in self.graphics:
            g.render()
            # TODO: Try this, and see if passing by reference when adding item
            #  to graphics list

        self.screen.flip()


if __name__ == "__main__":
    res = 1000, 1000
    game_tick_wait = 1000.0 * 1.0 / 10.0
    settings = Settings(res, game_tick_wait)
    game = Game(settings)
    rules = Rules.create(Rules.Name.COOPERATION)
    world_size = (20, 20)
    teams = 4
    setup = Setup.create(world_size, teams,
                         Setup.Names.RANDOM, Setup.Segmented.NONE)
    game.world = World(setup, rules)
    game.screen.update_scaling(game.world)

    while True:
        game.update()
        game.get_inputs()
        game.render()

