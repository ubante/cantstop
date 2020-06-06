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
from random import randint, shuffle


class Settings(object):
    MIN_COLUMN = 2
    MAX_COLUMN = 12


class Game(object):
    def __init__(self):
        self.board = Board()
        self.players = []
        self.round_ctr = 0
        self.game_won = False
        self.dice = []
        self.winner = None
        self.initialize()

    def initialize(self):
        for i in range(1, 5):
            self.dice.append(Die())

    def roll_dice(self):
        for d in self.dice:
            d.roll()

    def get_roll_choices(self):
        """
        Check the board to see which of the rolls are possible choices.  It is
        possible that there are no choices.

        :return:
        """
        free_columns = self.board.get_incomplete_columns()
        roll_values = self.get_roll_values()
        temp_columns = self.board.temporary_progress.keys()

        logging.debug("Available: {}".format(free_columns))
        logging.debug("Rolls:     {}".format(roll_values))

        # If there are free markers, then the player can still choose
        # a new column or two new columns.  Otherwise, their rolls
        # have to overlap the columns they have already chosen on this
        # turn.  Or they bust out.
        # TODO this is allowing user to choose a column that is full
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

    def get_dice_values(self):
        return [die.value for die in self.dice]

    def get_roll_values(self):
        pair_of_sums1 = tuple(sorted([self.dice[0].value + self.dice[1].value,
                                      self.dice[2].value + self.dice[3].value]))
        pair_of_sums2 = tuple(sorted([self.dice[0].value + self.dice[2].value,
                                      self.dice[1].value + self.dice[3].value]))
        pair_of_sums3 = tuple(sorted([self.dice[0].value + self.dice[3].value,
                                      self.dice[1].value + self.dice[2].value]))

        # It's possible that there are duplicate tuples.  For example,
        # the dice rolls are 1, 2, 2, 5].  This results in these possible
        # pairs: [(3, 7), (4, 6), (3, 7)].  So unique the list.
        return list({pair_of_sums1, pair_of_sums2, pair_of_sums3})

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
            # Even with cowards, games are won before 50 rounds.
            if self.round_ctr >= 50:
                print("We have played too many rounds - exiting.")
                break
            self.round_ctr += 1

            print("We have begun round #{}:".format(self.round_ctr))

            for p in self.players:
                print("{}'s turn:".format(p.name))

                is_busted = False
                do_play = True
                while not is_busted and do_play:
                    self.roll_dice()
                    roll_choices = self.get_roll_choices()

                    if not roll_choices:
                        """
                        The player rolled once to many times.
                        """
                        self.board.reset_progress()
                        print("Dice roll: {}".format(self.get_dice_values()))
                        print("Roll values: {}".format(self.get_roll_values()))
                        p.bust_out()
                        is_busted = True
                        continue

                    state = State(roll_choices, self.board.get_status(), self.round_ctr)
                    choice = p.choose_columns(state)

                    # Right now, the bots don't know how to choose.  So skip them.
                    if not choice:
                        logging.debug("Skipping turn of {}".format(p.name))
                        p.bust_out()
                        is_busted = True
                        self.board.bust_player(p)
                        continue

                    self.board.register_roll_choice(choice)

                    # Do I need to send the state for this?
                    state = State(roll_choices, self.board.get_status(), self.round_ctr)
                    choice = p.stop_or_continue(state)
                    if choice == 1:
                        do_play = False
                        self.board.register_stop_choice(p)

                    winner = self.board.check_for_winner()
                    if winner:
                        self.game_won = True
                        self.winner = winner


class Column(object):
    """
    The column represents a single ladder up the mountain.  The column for dice
    rolls 2 or 12 are shorter because it's less likely you can climb one rank of
    this column when compared to the column for dice rolls 6, 7, or 8.

    At each rank, there is a list of players at that rank.  All players start at
    the zeroth rank of each column.
    """
    def __init__(self, nums):
        self.intervals = nums
        self.positions = []  # This will be a list of list of players at each position.
        self.winner = None
        self.initialize()

    def __repr__(self):
        return self.positions

    def _declare_winner(self, name):
        # If this column is completed by a player, then that player
        # is marked the owner.  All other players are removed.
        self.winner = name
        print("------- {} has won this column -------".format(name))
        # logging.debug("{} has won this column".format(name))
        # TODO remove other players

    def initialize(self):
        for rank in range(0, self.intervals+1):
            # logging.debug("trying {} rank {}".format(self.intervals, rank))
            self.positions.append([])

    def add_player(self, name):
        """
        Since players start at the bottom of the column, that's where
        we'll put them.
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
            # The columns on the extreme right and left has 3
            # positions.  The next column in, has 5 positions.  This
            # continues until the middle column has 13 positions.
            if column <= 7:
                num_positions = column*2-1
            else:
                num_positions = 27 - (column*2)
            self.columns[column] = Column(num_positions)

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
        # Alternatively, this could return self.columns.
        return self.get_player_positions(), self.temporary_progress

    def get_incomplete_columns(self):
        # TODO include the temporary_progress columns in here.
        #   otherwise, I'm not sure what would happen.
        incomplete_columns = []
        for column in self.columns:
            if self.columns[column].is_incomplete():
                incomplete_columns.append(column)

        return incomplete_columns

    @staticmethod
    def get_status_string(positions):
        """
        This is static so other classes can call this.
        :param positions:
        :return:
        """
        status = "{:>16}".format("")
        for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
            status += "{:>5}".format(column)
        status += "\n"
        for p in positions:
            status += "{:>16}".format(p)
            for column in range(Settings.MIN_COLUMN, Settings.MAX_COLUMN + 1):
                # Use a period instead of a '0' to make the chart
                # more readable.
                if positions[p][column - 2]:
                    status += "{:>5}".format(positions[p][column - 2])
                else:
                    status += "{:>5}".format('.')
            status += "\n"

        return status

    def print_status(self):
        """
        The board looks like this:

                    2    3    4    5    6    7    8    9   10   11   12
              Me    0    0    0    0    0    0    0    0    0    0    0
            Bot1    0    0    0    0    0    0    0    0    0    0    0

        :return:
        """
        print(Board.get_status_string(self.get_player_positions()))

    def bust_player(self, player):
        self.reset_progress()

    def register_roll_choice(self, choice):
        print("Player chose: {}".format(choice))
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
        print("Player chose to stop")
        for pos in self.temporary_progress:
            self.columns[pos].advance(player.name, self.temporary_progress[pos])

        self.reset_progress()

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
        self.player_positions, self.temp_progress = board_status
        self.turn = turn

    def display(self):
        print(Board.get_status_string(self.player_positions))

    def print_choices(self):
        print("Turn #{}, your choices are:".format(self.turn))
        for ctr, choice in enumerate(self.choices, start=1):
            print("{}: {}".format(ctr, choice))


class Player(object):
    """
    Superduperclass
    """
    index = 0

    def __init__(self):
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

    def choose_columns(self, state):
        state.display()
        logging.debug("TempProgress: {}".format(state.temp_progress))
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


class TripleValueOdds(object):
    """
    Start with two sums, what are the odds of rolling a match with a given third sum?
    """
    def __init__(self, sum1, sum2):
        self.sums = [sum1, sum2]

    def find_odds(self, sum3):
        three_sums = [self.sums[0], self.sums[1], sum3]

        possibilities = 0
        hits = 0
        for d1 in range(1, 7):
            for d2 in range(1, 7):
                for d3 in range(1, 7):
                    for d4 in range(1, 7):
                        possibilities += 1
                        if d1 + d2 in three_sums:
                            hits += 1
                            continue
                        if d1 + d3 in three_sums:
                            hits += 1
                            continue
                        if d1 + d4 in three_sums:
                            hits += 1
                            continue
                        if d2 + d3 in three_sums:
                            hits += 1
                            continue
                        if d2 + d4 in three_sums:
                            hits += 1
                            continue
                        if d3 + d4 in three_sums:
                            hits += 1
                            continue

        return hits/possibilities


class Die(object):
    """
    This might be overkill.
    """
    def __init__(self):
        self.value = None
        self.roll()

    def roll(self):
        self.value = randint(1, 6)


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
