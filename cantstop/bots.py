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


class SafeBot(Player):
    """
    This bot prefers columns in the middle of the mountain and will
    stop when there are no more markers.
    """
    pass
