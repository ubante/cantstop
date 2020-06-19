"""
These are the classes for a Can't Stop simulation.

Can't Stop is a game where 2-4 players try to be the first to climb a mountain
via three different paths.  Progress up a path is determined by the roll of
dice.  The most unlikely dice rolls correspond with the shortest paths up the
mountain.

The strategy is to choose the paths that complement each other wrt dice rolls.

Each game contains rounds where each player gets a turn.  Each turn continues
long as that players gets dice rolls that are valid or that player decides to
stop and make their progress permanent.
"""
import logging
import sys

from collections import defaultdict
from random import shuffle

from cantstop.lib.odds import Dice, perc


class Settings(object):
    MIN_COLUMN = 2
    MAX_COLUMN = 12


class Game(object):
    def __init__(self):
        self.board = Board()
        self.players = []
        self.round_ctr = 0
        self.game_won = False
        self.dice = Dice()
        self.winner = None

    def get_roll_choices(self, player):
        """
        Check the board to see which of the rolls are possible choices.  It is
        possible that there are no choices.

        :return:
        """
        free_columns = self.board.get_incomplete_columns()
        roll_values = self.dice.get_sums()
        temp_columns = self.board.temporary_progress.keys()

        # Check that the progress in the temp_columns don't exceed the
        # available space in the free columns.
        for col in temp_columns:
            locked_position = self.board.columns[col].get_position(player.name)
            temp_position = self.board.temporary_progress[col]
            if locked_position + temp_position >= self.board.columns[col].intervals:
                free_columns.remove(col)

        logging.debug("Available: {}".format(free_columns))
        logging.debug("Rolls:     {}".format(roll_values))

        # If there are free markers, then the player can still choose
        # a new column or two new columns.  Otherwise, their rolls
        # have to overlap the columns they have already chosen on this
        # turn.  Or they bust out.
        choices = []
        if self.board.free_markers >= 2:
            for input_tuple in roll_values:
                output_list = []
                for element in input_tuple:
                    if element in free_columns:
                        output_list.append(element)
                if output_list:
                    choices.append(tuple(output_list))
        else:
            flattened_choices = [item for rv in roll_values for item in rv]
            if self.board.free_markers == 1:
                for element in flattened_choices:
                    if element in free_columns:
                        choices.append((element,))
            else:
                for element in flattened_choices:
                    if element in free_columns:
                        if element in temp_columns:
                            choices.append((element,))

        logging.debug("Choices:   {}".format(choices))
        return choices

    def add_player(self, p):
        self.players.append(p)
        self.board.add_player(p)

    def print_status(self):
        self.board.print_status()
        if self.game_won:
            print("The game ended after {} turns.  And the winner is: {}"
                  .format(self.round_ctr, self.winner))
        else:
            print("The game is on turn {}.".format(self.round_ctr))

    def run(self):
        shuffle(self.players)

        while not self.game_won:
            self.round_ctr += 1
            print("\n===== We have begun round #{} =====".format(self.round_ctr))

            for p in self.players:
                print("{}'s turn:".format(p.name))
                attempt_counter = 0

                is_busted = False
                do_play = True
                while not is_busted and do_play:
                    attempt_counter += 1
                    self.dice.roll()
                    roll_choices = self.get_roll_choices(p)

                    if not roll_choices:
                        """
                        The player rolled once to many times.
                        """
                        self.board.reset_progress()
                        logging.debug("Dice roll: {}".format(self.dice.values))
                        logging.debug("Roll values: {}".format(self.dice.get_sums()))
                        p.bust_out()
                        is_busted = True
                        continue

                    state = State(roll_choices, self.board.get_status(), self.round_ctr)
                    choice = p.choose_columns(state)
                    self.board.register_roll_choice(choice, p.name)

                    state = State(roll_choices, self.board.get_status(), self.round_ctr)
                    choice = p.stop_or_continue(state)
                    if choice == 1:
                        do_play = False
                        self.board.register_stop_choice(p)

                        winner = self.board.check_for_winner()
                        if winner:
                            self.game_won = True
                            self.winner = winner

                            # Once there is a winner, return to main.
                            return


class Column(object):
    """
    The column represents a single ladder up the mountain.  The column for dice
    rolls 2 or 12 are shorter because it's less likely you can climb one rank of
    this column when compared to the column for dice rolls 6, 7, or 8.

    At each rank, there is a list of players at that rank.  All players start at
    the zeroth rank of each column.
    """
    def __init__(self, nums, column_number):
        """
        Now that column_number is passed, I should reconsider if we need nums.

        :param nums: The number of ranks in this column.
        :param column_number: The die roll that corresponds to this column, eg
        7 or 12.
        """
        self.intervals = nums
        self.column_number = column_number
        self.positions = []  # This will be a list of list of players at each position.
        self.winner = None
        self.initialize_positions()

    def __repr__(self):
        return self.positions

    def _declare_winner(self, name):
        # If this column is completed by a player, then that player
        # is marked the owner.  All other players are removed.
        self.winner = name
        if logging.root.level <= logging.INFO:
            print("------- {} has won column {} -------".format(name, self.column_number))

        # Remove other players
        self.initialize_positions()
        self.positions[-1] = [self.winner]

    def initialize_positions(self):
        self.positions = []
        for rank in range(0, self.intervals+1):
            # logging.debug("trying {} rank {}".format(self.intervals, rank))
            self.positions.append([])

    def add_player(self, name):
        """
        Since players start at the bottom of the column, that's where
        we'll put them.st
        :return:
        """
        self.positions[0].append(name)

    def is_complete(self):
        if self.positions[-1]:
            return True
        return False

    def is_incomplete(self):
        return not self.is_complete()

    def get_position(self, name):
        position = 0
        for players_at_this_rank in self.positions:
            if name in players_at_this_rank:
                return position
            position += 1

        logging.fatal("Unreachable code.")
        sys.exit(2)

    def advance(self, name, ranks):
        logging.debug("Advancing {} {} positions".format(name, ranks))

        current_position = self.get_position(name)
        future_position = current_position + ranks
        if future_position > self.intervals:
            future_position = self.intervals

        logging.debug("Was {}, now {}".format(current_position, future_position))
        logging.debug(self.__repr__())
        self.positions[current_position].remove(name)
        self.positions[future_position].append(name)
        logging.debug(self.__repr__())

        if self.is_complete():
            self._declare_winner(name)


class Board(object):
    def __init__(self):
        self.players = []
        self.columns = {}
        self.temporary_progress = {}
        self.free_markers = 3
        self.initialize()

    def initialize(self):
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN+1):
            num_positions = Board.get_ranks_by_column(column)
            self.columns[column] = Column(num_positions, column)

    @staticmethod
    def get_ranks_by_column(column):
        # The columns on the extreme right and left has 3
        # positions.  The next column in, has 5 positions.  This
        # continues until the middle column has 13 positions.
        if column <= 7:
            num_positions = column * 2 - 1
        else:
            num_positions = 27 - (column * 2)
        return num_positions

    def reset_progress(self):
        self.temporary_progress = {}
        self.free_markers = 3

    def add_player(self, p):
        self.players.append(p)

        # Begin everyone at zero on each column.
        for position in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN+1):
            self.columns[position].add_player(p.name)

    def get_player_positions(self):
        player_positions = {}
        for p in self.players:
            player_positions[p.name] = [0] * (Settings.MAX_COLUMN - Settings.MIN_COLUMN + 1)

        for c in self.columns:
            for rank, players_at_this_rank in enumerate(self.columns[c].positions):
                for p in players_at_this_rank:
                    player_positions[p][c-2] = rank

        return player_positions

    def get_status(self):
        return self.get_player_positions(), self.temporary_progress

    def get_incomplete_columns(self):
        incomplete_columns = []
        for column in self.columns:
            if self.columns[column].is_incomplete():
                incomplete_columns.append(column)

        return incomplete_columns

    @staticmethod
    def get_status_string(positions, percentage=False):
        """
        This is static so other classes can call this.
        :param percentage:
        :param positions:
        :return:
        """
        # Generate the header rows.
        status = "{:>19}".format("")
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            status += "{:>5}".format(column)
        status += "\n"
        status += "{:>19}".format("")
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            if column < 10:
                status += "{:>5}".format("-")
            else:
                status += "{:>5}".format("--")
        status += "\n"

        # To find columns that have been won, we have to infer the
        # completed columns since we are not given direct access to
        # the Board() object.
        completed_columns = {}
        player_completed_columns = defaultdict(int)
        for player_name in positions:
            for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
                ranks = Board.get_ranks_by_column(column)
                if positions[player_name][column - 2] == ranks:
                    completed_columns[column] = player_name
                    player_completed_columns[player_name] += 1

        # Generate the position matrix.
        for player_name in positions:
            name_score = "{} ({})".format(player_name, player_completed_columns[player_name])
            status += "{:>19}".format(name_score)
            for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
                # Use pipes to mark completed columns won by another player.
                if column in completed_columns and completed_columns[column] != player_name:
                    status += "{:>5}".format('||')
                    continue

                # Use a period instead of a '0' to make the chart
                # more readable.
                if positions[player_name][column - 2]:
                    if percentage:
                        numerator = positions[player_name][column - 2]
                        denominator = Board.get_ranks_by_column(column)
                        status += "{:>5}".format(perc(numerator, denominator, no_decimal=True))
                    else:
                        status += "{:>5}".format(positions[player_name][column - 2])
                    continue

                status += "{:>5}".format('.')
            status += "\n"

        return status

    def print_status(self, percentage=False):
        """
        The board looks like this:

                    2    3    4    5    6    7    8    9   10   11   12
              Me    0    0    0    0    0    0    0    0    0    0    0
            Bot1    0    0    0    0    0    0    0    0    0    0    0

        :return:
        """
        print(Board.get_status_string(self.get_player_positions(), percentage=percentage))

    def bust_player(self):
        self.reset_progress()

    def register_roll_choice(self, choice, name=None):
        if not name:
            name = "Player"
        logging.debug("{} chose: {}".format(name, choice))
        for column in choice:
            if column in self.temporary_progress:
                # We can assume that if a column is temporarily maxed,
                # then the player would not have had a chance to choose
                # it so no need to check for maxed out state here.
                self.temporary_progress[column] += 1
            else:
                self.free_markers -= 1
                self.temporary_progress[column] = 1

    def register_stop_choice(self, player):
        # Commit the temporary progress.
        logging.debug("Player chose to stop")
        for pos in self.temporary_progress:
            self.columns[pos].advance(player.name, self.temporary_progress[pos])

        self.reset_progress()

    def get_won_columns(self):
        won = []
        for col in self.columns:
            if self.columns[col].winner:
                won.append(col)

        return won

    def check_for_winner(self):
        col_winners = defaultdict(int)
        for col in self.columns:
            possible_winner = self.columns[col].winner
            if possible_winner:
                col_winners[possible_winner] += 1
                if col_winners[possible_winner] >= 3:
                    return possible_winner

        return None


class State(object):
    """
    The players are presented with the game state when the player has a chance
    to act.  The state is composed of the game board and the available column
    choices.
    """
    def __init__(self, choices, board_status, turn):
        self.choices = choices
        self.player_positions, self.temp_progress = board_status  # Weird to use a tuple here.
        self.turn = turn

    def display(self, percentage=False):
        print(Board.get_status_string(self.player_positions, percentage=percentage))

    def print_choices(self):
        print("Turn #{}, your choices are:".format(self.turn))
        for ctr, choice in enumerate(self.choices, start=1):
            print("{}: {}".format(ctr, choice))

    def get_current_columns(self, name):
        my_position = self.player_positions[name]
        logging.debug("Position = {}".format(my_position))
        chosen_cols = []
        for col_num, value in enumerate(my_position, start=2):
            if value:
                chosen_cols.append(col_num)
        logging.debug("Chosen_cols = {}".format(chosen_cols))

        return chosen_cols

    @staticmethod
    def weight_column(col):
        if col <= 7:
            return 8 - col
        else:
            return col - 6

    def rule28(self):
        """
        From https://www.aaai.org/ocs/index.php/FLAIRS/2009/paper/download/123/338

        This method will naively weigh all ranks equally, whether it is the first
        or last.  Also disregard the number of free markers.
        :return:
        """
        score_by_col = {}
        for col in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN+1):
            if col <= 7:
                score_by_col[col] = 8 - col
            else:
                score_by_col[col] = col - 6

        score28 = 0
        product = 1
        for col in self.temp_progress:
            score28 += score_by_col[col] * (self.temp_progress[col] + 1)
            product *= col

        # Check for oddness.
        if product > 1 and (product % 2) == 1:
            score28 += 2

        # Check for evenness.
        if (product % 8) == 0:
            score28 -= 2

        return score28


class Player(object):
    """
    Superduperclass

    These are the things a bot could do:
        - try to delay using all the markers
        - put the first marker close to the middle
        - put the last marker close to the sides
        - will stop if temp_progress wins the game even if there are extra markers
        - deprioritize columns almost won by opponent
        - score opponents to decide how aggressive to play
    """
    index = 0  # To make the generic name unique.

    def __init__(self):
        """
        I really don't want the base class to require a name.
        """
        self.name = "NoName{}".format(Player.index)
        Player.index += 1

    def choose_columns(self, state):
        print("Default player, {}, is passing on choosing columns.".format(self.name))

    def stop_or_continue(self, state):
        """
        1 = Stop
        2 = Play

        :param state:
        :return:
        """
        return 1

    def bust_out(self):
        print("Player {} has busted out.".format(self.name))


class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def print_temp_progress(self, state):
        existing_progress = state.player_positions[self.name]  # List
        combined_progress = []
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            if column in state.temp_progress:
                total = state.temp_progress[column] + existing_progress[column - 2]
            else:
                total = existing_progress[column - 2]
            combined_progress.append(total)

        # Header line
        status = "{:>19}".format("Temp Progress")
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            status += "{:>5}".format(column)
        status += "\n"
        status += "{:>19}".format("")
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            if column < 10:
                status += "{:>5}".format("-")
            else:
                status += "{:>5}".format("--")
        status += "\n"

        # Infer pipes
        # TODO Not sure this is working
        completed_columns = {}
        player_completed_columns = defaultdict(int)
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            ranks = Board.get_ranks_by_column(column)
            if existing_progress[column - 2] == ranks:
                completed_columns[column] = self.name
                player_completed_columns[self.name] += 1

        # Print out two rows.  The first is the temp progress.
        percentage = True  # Let's see which looks better.
        status += "{:>19}".format("")
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            # Use pipes to mark completed columns won by another player.
            if column in completed_columns and completed_columns[column] != self.name:
                status += "{:>5}".format('||')
                continue

            # Use a period instead of a '0' to make the chart
            # more readable.
            if column in state.temp_progress:
                status += "  +{:>2}".format(state.temp_progress[column])
                continue

            status += "{:>5}".format('.')
        status += "\n"

        # And the second is the combined.
        status += "{:>19}".format("")
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            # Use pipes to mark completed columns won by another player.
            if column in completed_columns and completed_columns[column] != self.name:
                status += "{:>5}".format('||')
                continue

            # Use a period instead of a '0' to make the chart
            # more readable.
            if combined_progress[column - 2]:
                if percentage:
                    numerator = combined_progress[column - 2]
                    denominator = Board.get_ranks_by_column(column)
                    status += "{:>5}".format(perc(numerator, denominator, no_decimal=True))
                else:
                    status += "{:>5}".format(combined_progress[column - 2])
                continue

            status += "{:>5}".format('.')
        status += "\n"
        print(status)

    def choose_columns(self, state):
        state.display(percentage=True)
        logging.debug("TempProgress: {}".format(state.temp_progress))
        self.print_temp_progress(state)
        print("Current Rule28 score: {}".format(state.rule28()))
        print("{} free markers".format(3-len(state.temp_progress)))
        state.print_choices()

        user_input = None
        while True:
            try:
                user_input = int(input("Enter: "))
            except ValueError:
                print("Try again.")
                continue

            if user_input not in range(1, len(state.choices)+1):
                print("Try again.")
                continue

            break

        return state.choices[user_input-1]

    def stop_or_continue(self, state):
        self.print_temp_progress(state)
        print("Current Rule28 score: {}".format(state.rule28()))
        print("1: Stop\n2: Continue")
        user_input = input("Enter: ")
        return int(user_input)

    @staticmethod
    def enter(max_value):
        user_input = None
        while True:
            try:
                user_input = int(input("Enter: "))
            except ValueError:
                print("Try again.")
                continue

            if user_input not in range(1, max_value):
                print("Try again.")
                continue

            break

        return user_input


class SingleValueOdds(object):
    """
    Singleton to help performance a little.
    https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    """
    class __SingleValueOdds(object):
        def __init__(self):
            self.sum_count = defaultdict(int)
            self.odds = {}
            self.find_odds()

        def find_odds(self):
            """
            This results in the same odds as a pair of dice x 4 since four dice
            creates four sets of pairs.
            :return:
            """
            ctr = 0
            for d1 in range(1, 7):
                for d2 in range(1, 7):
                    for d3 in range(1, 7):
                        for d4 in range(1, 7):
                            ctr += 1
                            self.sum_count[d1 + d2] += 1
                            self.sum_count[d1 + d3] += 1
                            self.sum_count[d1 + d4] += 1
                            self.sum_count[d2 + d4] += 1

            for roll in self.sum_count:
                self.odds[roll] = self.sum_count[roll] / ctr

    instance = None

    def __init__(self):
        if not SingleValueOdds.instance:
            SingleValueOdds.instance = SingleValueOdds.__SingleValueOdds()

    def of(self, roll):
        if roll in self.instance.odds:
            return self.instance.odds[roll]
        else:
            print("The roll of {} is impossible with two 6-sided dice.".format(roll))
            return 0
