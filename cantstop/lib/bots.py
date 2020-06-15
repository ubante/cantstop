import logging

from cantstop.lib.all_the_things import Player


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


class ScoringBot(NamedPlayer):
    """
    This bot will:
    - score the temp_progress gains against the possible chance of busting out
    """
    def __init__(self, name):
        super().__init__(name)
        self.state = None  # This may need to go to Player()

    def score_columns(self, col_list):
        pass

    def choose_columns(self, state):
        self.state = state

    def stop_or_continue(self, state):
        self.state = state


class RollerBot(NamedPlayer):
    """
    This bot will:
        - choose columns it has already chosen
        - roll X times

    Results: HexRB is the best.
After 10000 iterations, here are the winners:
defaultdict(<class 'int'>, {'QuadRollerBot': 2311, 'OctoRollerBot': 2657, 'DecaRollerBot': 2079, 'HexRollerBot': 2953})

    It's a valid argument to say that subclasses could be composed.  But I want
    the class name to be different in multi_sim.
    """
    def __init__(self, name, budget):
        super().__init__(name)
        self.fixed_budget = budget
        self.risk_budget = None
        self.sub_turn = None
        self.end_of_turn_cleanup()

    def end_of_turn_cleanup(self):
        self.risk_budget = self.fixed_budget
        self.sub_turn = 0

    def choose_columns(self, state):
        self.sub_turn += 1
        logging.debug("{}'s sub-turn #{}".format(self.name, self.sub_turn))
        return self.choose_already_selected_columns(state)

    def stop_or_continue(self, state):
        if self.risk_budget == 1:
            logging.debug("{} has run out of steam - stopping.".format(self.name))
            self.end_of_turn_cleanup()
            return 1

        self.risk_budget -= 1
        return 2

    def bust_out(self):
        super().bust_out()
        self.end_of_turn_cleanup()


class QuadRollerBot(RollerBot):
    def __init__(self, name):
        super().__init__(name, 4)


class HexRollerBot(RollerBot):
    def __init__(self, name):
        super().__init__(name, 6)


class SeptaRollerBot(RollerBot):
    def __init__(self, name):
        super().__init__(name, 7)


class OctoRollerBot(RollerBot):
    def __init__(self, name):
        super().__init__(name, 8)


class DecaRollerBot(RollerBot):
    def __init__(self, name):
        super().__init__(name, 10)




