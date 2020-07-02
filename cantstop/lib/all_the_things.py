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

from cantstop.lib.odds import Dice, perc, HitPredictor
from cantstop.lib.settings import Settings


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
        not_free_columns = self.board.get_complete_columns()
        roll_values = self.dice.get_sums()
        temp_columns = self.board.temporary_progress.keys()

        # Check that the progress in the temp_columns don't exceed the
        # available space in the free columns.
        for col in temp_columns:
            locked_position = self.board.columns[col].get_position(player.name)
            temp_position = self.board.temporary_progress[col]
            if locked_position + temp_position >= self.board.columns[col].ranks:
                free_columns.remove(col)

        logging.debug("Available: {}".format(free_columns))
        logging.debug("Not available: {}".format(not_free_columns))
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

    def print_summary(self):
        """
        This could be called once there's a winner to display stats.
        :return:
        """
        if not self.game_won:
            print("The game has not yet been won.")
            return

        self.board.print_status()
        print("The game ended after {} turns.  And the winner is: {}"
              .format(self.round_ctr, self.winner))
        #TODO Would be nice to see the P2 and R28 scores here.


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
        self.column_number = column_number
        self.ranks = Column.get_ranks_by_column(self.column_number)
        self.positions = []  # This will be a list of list of players at each position.
        self.winner = None
        self.initialize_positions()

    def __repr__(self):
        return self.positions

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
        for rank in range(0, self.ranks+1):
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
        if future_position > self.ranks:
            future_position = self.ranks

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
        for column in Settings.COLUMN_RANGE:
            num_positions = Column.get_ranks_by_column(column)
            self.columns[column] = Column(num_positions, column)

    def reset_progress(self):
        self.temporary_progress = {}
        self.free_markers = 3

    def add_player(self, p):
        self.players.append(p)

        # Begin everyone at zero on each column.
        for position in Settings.COLUMN_RANGE:
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

    def get_complete_columns(self):
        ic = self.get_incomplete_columns()
        return list(set(Settings.COLUMN_RANGE).difference(set(ic)))

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
        for column in Settings.COLUMN_RANGE:
            status += "{:>5}".format(column)
        status += "\n"
        status += "{:>19}".format("")
        for column in Settings.COLUMN_RANGE:
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
            for column in Settings.COLUMN_RANGE:
                ranks = Column.get_ranks_by_column(column)
                if positions[player_name][column - 2] == ranks:
                    completed_columns[column] = player_name
                    player_completed_columns[player_name] += 1

        # Generate the position matrix.
        for player_name in positions:
            name_score = "{} ({})".format(player_name, player_completed_columns[player_name])
            status += "{:>19}".format(name_score)
            for column in Settings.COLUMN_RANGE:
                # Use pipes to mark completed columns won by another player.
                if column in completed_columns and completed_columns[column] != player_name:
                    status += "{:>5}".format('||')
                    continue

                # Use a period instead of a '0' to make the chart
                # more readable.
                if positions[player_name][column - 2]:
                    if percentage:
                        numerator = positions[player_name][column - 2]
                        denominator = Column.get_ranks_by_column(column)
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
        self.player_positions = board_status[0]  # dict: name->list of current_rank_by_column
        self.temp_progress = board_status[1]  # dict: column_num->temp_rank_by_that_column
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

    def get_free_marker_count(self):
        return 3 - len(self.temp_progress)

    @staticmethod
    def weight_column(col):
        """
        This is part of the rule 28 scoring.
        :param col:
        :return:
        """
        if col <= 7:
            return 8 - col
        else:
            return col - 6

    def get_players_percentage_squared_score(self):
        """
        Return a dict of each player's scores.  Use this to find your relative
        weakness or strength.

        :return: defaultdict name -> int
        """
        scores = defaultdict(int)
        for name in self.player_positions:
            for i, rank_count in enumerate(self.player_positions[name]):
                col = i + 2

                # This might exist elsewhere.
                scores[name] += (rank_count / Column.get_ranks_by_column(col)) ** 2 * 100
        return scores

    def get_players_rule28_score(self):
        """
        Return a dict of each player's scores.  Use this to find your relative
        weakness or strength.

        :return: defaultdict name -> int
        """
        scores = defaultdict(int)
        for name in self.player_positions:
            for i, rank_count in enumerate(self.player_positions[name]):
                col = i + 2
                # print("{} has {} ranks of col {} = {}"
                #       .format(name, rank_count, col, rank_count * self.weight_column(col)))
                scores[name] += rank_count * self.weight_column(col)
        return scores

    def rule28(self):
        """
        From https://www.aaai.org/ocs/index.php/FLAIRS/2009/paper/download/123/338

        This method will naively weigh all ranks equally, whether it is the first
        or last.  Also disregard the number of free markers.
        :return:
        """
        score_by_col = {}
        for col in Settings.COLUMN_RANGE:
            score_by_col[col] = State.weight_column(col)

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

    def p2(self, name):
        """
        This is a naive way to score the existing progress.  "p2" is percentage squared.
        Each column's percentage progress is squared then summed to make this score
        :return:
        """
        p2_score = 0
        for i, rank in enumerate(self.player_positions[name]):
            col_number = i + 2
            player_rank_in_this_column = self.player_positions[name][i]
            num_ranks_in_col = Column.get_ranks_by_column(col_number)
            p = player_rank_in_this_column / num_ranks_in_col
            p2 = p * p
            p2_score += p2

        return p2_score

    def p2_temp_progress(self, name):
        """
        The incremental p2 score contributed by temp_progress only.

        :return:
        """
        return self.p2_combined(name) - self.p2(name)

    def p2_combined(self, name):
        """
        This includes the temporary progress in the P2 score
        :param name:
        :return:
        """
        p2_score = 0
        for i, rank in enumerate(self.player_positions[name]):
            col_number = i + 2
            initial_rank_in_this_column = self.player_positions[name][i]
            temp_rank_in_this_column = 0
            if col_number in self.temp_progress:
                temp_rank_in_this_column = self.temp_progress[col_number]
            num_ranks_in_col = Column.get_ranks_by_column(col_number)
            p = (initial_rank_in_this_column + temp_rank_in_this_column) / num_ranks_in_col
            p2 = p * p
            p2_score += p2

        return p2_score


class Player(object):
    """
    Superduperclass

    TODO: These are the things a bot could do:
        - put the first marker close to the middle
        - put the last marker close to the sides
        - will stop if temp_progress wins the game even if there are extra markers
        - deprioritize columns almost won by opponent
        - score opponents to decide how aggressive to play
        - switch from an early game scoring system to late game scoring system
    """
    index = 0  # To make the generic name unique.

    def __init__(self):
        """
        I really don't want the base class to require a name.
        """
        self.name = "NoName{}".format(Player.index)
        self.state = None
        self.rating = 0  # not sure about this
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
        self.state = None

    def print_temp_progress_table(self):
        existing_progress = self.state.player_positions[self.name]  # List
        combined_progress = []
        for column in Settings.COLUMN_RANGE:
            if column in self.state.temp_progress:
                total = self.state.temp_progress[column] + existing_progress[column - 2]
            else:
                total = existing_progress[column - 2]
            combined_progress.append(total)

        # Header line
        status = "{:>19}".format("Temp Progress")
        for column in Settings.COLUMN_RANGE:
            status += "{:>5}".format(column)
        status += "\n"
        status += "{:>19}".format("")
        for column in Settings.COLUMN_RANGE:
            if column < 10:
                status += "{:>5}".format("-")
            else:
                status += "{:>5}".format("--")
        status += "\n"

        # Infer pipes.  Considering using Column()s in State().
        completed_columns = {}
        for column in Settings.COLUMN_RANGE:
            max_rank = Column.get_ranks_by_column(column)
            for name in self.state.player_positions:
                if self.state.player_positions[name][column-2] == max_rank:
                    completed_columns[column] = name
                    continue

        # Print out two rows.  The first is the temp progress.
        percentage = True  # Let's see which looks better.
        status += "{:>19}".format("")
        for column in Settings.COLUMN_RANGE:
            # Use pipes to mark completed columns won by another player.
            if column in completed_columns and completed_columns[column] != self.name:
                status += "{:>5}".format('||')
                continue

            # Use a period instead of a '0' to make the chart
            # more readable.
            if column in self.state.temp_progress:
                status += "  +{:>2}".format(self.state.temp_progress[column])
                continue

            status += "{:>5}".format('.')
        status += "\n"

        # And the second is the combined.
        status += "{:>19}".format("")
        for column in Settings.COLUMN_RANGE:
            # Use pipes to mark completed columns won by another player.
            if column in completed_columns and completed_columns[column] != self.name:
                status += "{:>5}".format('||')
                continue

            # Use a period instead of a '0' to make the chart
            # more readable.
            if combined_progress[column - 2]:
                if percentage:
                    numerator = combined_progress[column - 2]
                    denominator = Column.get_ranks_by_column(column)
                    status += "{:>5}".format(perc(numerator, denominator, no_decimal=True))
                else:
                    status += "{:>5}".format(combined_progress[column - 2])
                continue

            status += "{:>5}".format('.')
        status += "\n"
        print(status)

    def print_marker_count(self):
        marker_count = 3 - len(self.state.temp_progress)
        if marker_count == 1:
            print("1 free marker")
        elif marker_count == 3:
            print("--->>> 3 free markers")
        elif marker_count == 2:
            print("2 free markers")
        else:
            hp = HitPredictor()
            odd_to_hit_next_attempt = hp.compute_next_attempt_odds(self.state.temp_progress.keys())
            print("{} free markers - odds to hit on next attempt: {:3.1f}%"
                  .format(marker_count, odd_to_hit_next_attempt))
            print("I need to balance the risk of hitting against what I've gained so far.")

    def print_competition(self):
        opp_r28 = self.state.get_players_rule28_score()
        print("Current Rule28 scores:")
        for name in sorted(opp_r28.keys()):
            print("{:>19}: {:3}".format(name, opp_r28[name]))

        # TODO this does not add up
        opp_p2 = self.state.get_players_percentage_squared_score()
        print("Current P2 scores:")
        for name in sorted(opp_p2.keys()):
            print("{:>19}: {:4.0f}".format(name, opp_p2[name]))
        print()

    def print_info_block(self):
        self.print_marker_count()
        print("TempProgress: {}".format(self.state.temp_progress))
        print("Current Rule28 score: {}".format(self.state.rule28()))
        print("{:1.2f}: Initial P2 score".format(self.state.p2(self.name)))
        print("{:1.2f}: TempProgress P2 score".format(self.state.p2_temp_progress(self.name)))
        print("{:1.2f}: Combined P2 score".format(self.state.p2_combined(self.name)))

    def compute_inc_rule28_score(self, choice_tuple):
        # TODO incremental Rule28
        return 11

    def compute_p2_score(self, choice_tuple):
        """
        There are three possible inputs.
            (1) Two different values
            (2) Two identical values
            (3) Single value

        :param choice_tuple:
        :return:
        """
        # For case (2), we need some special logic otherwise the
        # returned value will be slightly lower.
        is_same = False
        if len(choice_tuple) == 2 and choice_tuple[0] == choice_tuple[1]:
            is_same = True
            choice_tuple = (choice_tuple[0],)

        possible_total = 0
        for ct in choice_tuple:
            tp_row_rank = 0
            if ct in self.state.temp_progress:
                tp_row_rank = self.state.temp_progress[ct]
            initial_plus_temp_progress = self.state.player_positions[self.name][ct-2] \
                + tp_row_rank
            if is_same:
                possible_progress = initial_plus_temp_progress + 2
            else:
                possible_progress = initial_plus_temp_progress + 1
            num_ranks_in_col = Column.get_ranks_by_column(ct)
            possible_total += (possible_progress / num_ranks_in_col) ** 2 \
                - (initial_plus_temp_progress / num_ranks_in_col) ** 2

        return possible_total

    def compute_k_score(self, choice_tuple):
        """
        This will improve on P2 by giving weight to completing a column.  And for
        winning the game.

        :param choice_tuple:
        :return:
        """
        # TODO figure this out and add caller to L784
        return 0.0

    def print_choices(self):
        """
        This replaces State.print_choices().
        :return:
        """
        print("Turn #{}, your choices are:\n".format(self.state.turn))
        print("          Inc28 IncP2K IncK")
        print("             -- ------ --")
        for ctr, choice in enumerate(self.state.choices, start=1):
            if len(choice) == 1:
                print("{:2}: ({:2}, {:2}) {:2} {:1.0f}"
                      .format(ctr, choice[0], "", self.compute_inc_rule28_score(choice),
                              1000*self.compute_p2_score(choice)))
            else:
                print("{:2}: ({:2}, {:2}) {:2} {:1.0f}"
                      .format(ctr, choice[0], choice[1], self.compute_inc_rule28_score(choice),
                              1000*self.compute_p2_score(choice)))

    def choose_columns(self, state):
        self.state = state
        self.state.display(percentage=True)
        self.state.display(percentage=False)
        self.print_temp_progress_table()
        self.print_competition()
        self.print_info_block()
        self.print_choices()

        user_input = None
        while True:
            try:
                user_input = int(input("Enter choice: "))
            except ValueError:
                print("Try again.")
                continue

            if user_input not in range(1, len(self.state.choices)+1):
                print("Try again.")
                continue

            break

        return self.state.choices[user_input-1]

    def stop_or_continue(self, state):
        self.state = state
        self.print_temp_progress_table()
        self.print_info_block()

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

    # def bust_out(self):
    #     print("==========================================================================")
    #     for i in range(0,10):
    #         print("========= BUSTED =========================================================")
    #     print("==========================================================================")


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
