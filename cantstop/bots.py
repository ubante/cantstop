import logging

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

    This class beats CowardBot 90% of the time.
    """
    def choose_columns(self, state):
        state.display()

        my_position = state.player_positions[self.name]
        # logging.debug("SCB: position = {}".format(my_position))
        chosen_cols = []
        for col_num, value in enumerate(my_position, start=2):
            if value:
                chosen_cols.append(col_num)
        # logging.debug("SCB: chosen_cols = {}".format(chosen_cols))

        overlap = {}
        for i, choice_tup in enumerate(state.choices):
            match_ctr = 0
            for choice in choice_tup:
                if choice in chosen_cols:
                    match_ctr += 1
            overlap[i] = match_ctr

        # logging.debug("SCB: overlap = {}".format(overlap))
        best_choice_index = max(overlap, key=overlap.get)
        return state.choices[best_choice_index]


class ConservativeBot(Player):
    """
    This bot will:
    - stop when there are no free markers
    - will try to delay using all the markers
    - put the first marker close to the middle
    - put the last marker close to the sides
    - not consider column rank
    - not consider opponents
    """

