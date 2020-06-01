import sys
from collections import defaultdict
from random import randint, shuffle


class Game(object):
    def __init__(self):
        self.board = Board()
        self.players = []
        self.round_ctr = 0
        self.game_won = False
        self.dice = []
        self.initialize()

    def initialize(self):
        for i in range(1, 5):
            self.dice.append(Die())

    def roll_dice(self):
        for d in self.dice:
            d.roll()

    def get_choices(self):
        # For now, assume all values are possible.
        # return (1, 2), 6, 8
        return self.get_roll_values()

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
            print("The game ended after {} turns.  And the winner is:XXX".format(self.round_ctr))
        else:
            print("The game is on turn {}.".format(self.round_ctr))

    def start(self):
        shuffle(self.players)

        while not self.game_won:
            if self.round_ctr >= 2:
                print("We have played too many rounds - exiting.")
                break
            self.round_ctr += 1

            print("We have begun round #{}:".format(self.round_ctr))

            for p in self.players:
                print("{}'s turn:".format(p.name))
                self.roll_dice()
                # TODO: check if dice allows for a move.

                state = State(self.get_choices(), self.board.get_status())

                # if type(p) == HumanPlayer:
                #     print("This is a dude.")

                choice = p.choose_columns(state)




class Board(object):
    def __init__(self):
        self.players = []
        self.columns = {}
        self.player_positions = {}
        self.initialize()

    def initialize(self):
        for column in range(2, 12+1):
            num_positions = column*2-1
            self.columns[column] = {"intervals": num_positions}

            # Each column has a list of positions.  The outer columns
            # have less positions.  Each position has a list players at
            # that position.
            for position in range(0, column*2-1+1):
                self.columns[column][position] = []

    def add_player(self, p):
        self.players.append(p)

        # Begin everyone at zero on each column.
        for column in range(2, 12+1):
            self.columns[column][0].append(p.name)

        # This list could be derived from self.columns but is recorded
        # for readability.
        self.player_positions[p.name] = [0] * (12 - 2 + 1)

    def get_status(self):
        # Alternatively, this could return player_positions.
        return self.player_positions

    def print_status(self):
        """
        The board looks like this:

                    2    3    4    5    6    7    8    9   10   11   12
              Me    0    0    0    0    0    0    0    0    0    0    0
            Bot1    0    0    0    0    0    0    0    0    0    0    0

        :return:
        """
        print("{:>16}".format(""), end="")
        for column in range(2, 13):
            print("{:>5}".format(column), end="")
        print()
        for p in self.players:
            print("{:>16}".format(p.name), end="")
            for column in range(2, 13):
                print("{:>5}".format(self.player_positions[p.name][column-2]), end="")
            print()
        print()


class State(object):
    """
    Dunno about this.

    The players are presented with the game state when the player has a chance
    to act.  The state is composed of the game board and the available column
    choices.
    """
    def __init__(self, choices, board_status):
        self.choices = choices
        self.board_status = board_status

    def display(self):
        # This block is redundant with Board.print_status().  Dunno.
        print("{:>16}".format(""), end="")
        for column in range(2, 13):
            print("{:>5}".format(column), end="")
        print()
        for name in self.board_status:
            print("{:>16}".format(name), end="")
            for column in range(2, 13):
                print("{:>5}".format(self.board_status[name][column - 2]), end="")
            print()

        print("Your choices are:")
        for ctr, choice in enumerate(self.choices, start=1):
            print("{}: {}".format(ctr, choice))


class Player(object):
    """
    Because this was inevitable.
    """
    def __init__(self):
        self.name = "NoName"  # TODO use a index suffix here.

    def choose_columns(self, state):
        """Abstract"""
        pass

    def stop_or_play(self, state):
        """Abstract"""
        pass


class HumanPlayer(Player):
    def choose_columns(self, state):
        state.display()
        user_input = input("Enter: ")
        return user_input

    def stop_or_play(self, state):
        pass


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