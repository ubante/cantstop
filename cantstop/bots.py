import logging

from cantstop.all_the_things import Player


class NamedPlayer(Player):
    """
    Getting spicey.
    """
    def __init__(self, name):
        super().__init__()
        self.name = name


class CowardBot(NamedPlayer):
    """
    This bot will always choose the first combination and then stop.

    Head to head against SCB, this class wins 1 out of 10 matches.
    """
    def choose_columns(self, state):
        return state.choices[0]

    def stop_or_continue(self, state):
        return 1


class SmartCowardBot(CowardBot):
    """
    This bot will only make one choice but it will look for rolls that it
    already has.

    This class beats CowardBot 90% of the time.  But it looses 99% of the time
    to CB.
    """
    def choose_columns(self, state):
        if logging.root.level <= logging.DEBUG:
            state.display()
        chosen_cols = state.get_current_columns(self.name)

        overlap = {}
        for i, choice_tup in enumerate(state.choices):
            match_ctr = 0
            for choice in choice_tup:
                if choice in chosen_cols:
                    match_ctr += 1
            overlap[i] = match_ctr

        logging.debug("SCB: overlap = {}".format(overlap))
        best_choice_index = max(overlap, key=overlap.get)
        return state.choices[best_choice_index]


class ConservativeBot(NamedPlayer):
    """
    This bot will:
    - stop when there are no free markers
    """
    def choose_columns(self, state):
        state.display()
        chosen_cols = state.get_current_columns(self.name)

        overlap = {}
        for i, choice_tup in enumerate(state.choices):
            match_ctr = 0
            for choice in choice_tup:
                if choice in chosen_cols:
                    match_ctr += 1
            overlap[i] = match_ctr

        # This will prioritize choosing a column if it has already
        # been chosen in the past.  If there's a choice to advance
        # two ranks in a column, then that choise will be taken.
        logging.info("CB: overlap = {}".format(overlap))
        best_choice_index = max(overlap, key=overlap.get)
        return state.choices[best_choice_index]

    def stop_or_continue(self, state):
        temp_progress_columns = state.temp_progress.keys()
        if len(temp_progress_columns) < 3:
            return 0

        return 1


class SmartConservativeBot(ConservativeBot):
    """
    This bot will:
        - will try to delay using all the markers
        - put the first marker close to the middle
        - put the last marker close to the sides
        - will stop if temp_progress wins the game even if there are extra markers
        - not consider column rank
        - not consider opponents
    """


class QuadRollerBot(NamedPlayer):
    """
    This bot will:
        - choose columns it has already chosen
        - roll four times

    Results:
After 1000 iterations, here are the winners:
defaultdict(<class 'int'>, {'QuadRollerBot': 647, 'ConservativeBot': 352, 'SmartCowardBot': 1})
    """
    def __init__(self, name):
        super().__init__(name)
        self.risk_budget = None
        self.sub_turn = None
        self.end_of_turn_cleanup()

    def end_of_turn_cleanup(self):
        self.risk_budget = 4
        self.sub_turn = 0

    def choose_columns(self, state):
        self.sub_turn += 1
        logging.debug("{}'s sub-turn #{}".format(self.name, self.sub_turn))
        return self.choose_already_selected_columns(state)

    def stop_or_continue(self, state):
        if self.risk_budget == 1:
            logging.debug("The Quad Roller has run out of steam - stopping.")
            self.end_of_turn_cleanup()
            return 1

        self.risk_budget -= 1
        return 2

    def bust_out(self):
        super().bust_out()
        self.end_of_turn_cleanup()
