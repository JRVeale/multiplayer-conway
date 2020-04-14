from pygame import Color


class Colours:
    def __init__(self, teams):
        self.teams = {
            0: Color(0, 0, 0),  # Go Team Dead!
            1: Color(255, 255, 255),  # White
            2: Color(255, 0, 0),  # Red
            3: Color(0, 255, 0),  # Green
            4: Color(0, 0, 255),  # Blue
            5: Color(255, 0, 255),  # Pink
            6: Color(255, 255, 0),  # Yellow
            7: Color(0, 255, 255),  # Cyan
            8: Color(255, 123, 0),  # Orange
            9: Color(123, 0, 255),  # Purple

        }

        for t in range(teams + 1):
            if t not in self.teams:
                prev_cycle_colour = self.teams[t - 8]
                self.teams[t] = self.shift_colour(prev_cycle_colour,
                                                  sat_multiplier=0.6)

    def get_team_colour(self, team):
        return self.teams[team]

    @staticmethod
    def shift_colour(colour,
                     hue_multiplier=1.0, sat_multiplier=1.0,
                     val_multiplier=1.0,
                     alpha_multiplier=1.0, ):
        new_colour = Color(0, 0, 0)
        new_colour.hsva = tuple([
            colour.hsva[0] * hue_multiplier,
            colour.hsva[1] * sat_multiplier,
            colour.hsva[2] * val_multiplier,
            colour.hsva[3] * alpha_multiplier
        ])
        return new_colour
