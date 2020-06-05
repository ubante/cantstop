from cantstop.all_the_things import Player


class CowardBot(Player):
    """
    This bot will always choose the first combination and then stop.
    """
    def __init__(self, name):
        super().__init__()
        self.name = name

    def choose_columns(self, state):
        return state.choices[0]

    def stop_or_continue(self, state):
        return 1


class SmartCowardBot(CowardBot):
    """
    This bot will only make one choice but it will look for rolls that it
    already has.
    """
    def choose_columns(self, state):

        return state.choices[0]
