"""
In the normal game, your turn ends when you bust out.

But here, you play alone, you can't choose, and you never bust out.

This simulation will see if the column lengths indeed correspond to the likelihood
of rolling that value.
"""
import argparse
import logging
import sys

from cantstop.lib.all_the_things import Game, Column, Board
from cantstop.lib.bots import NamedPlayer
from cantstop.lib.odds import Dice


class InfiniteGame(Game):
    def __init__(self):
        super().__init__()
        self.player_name = "Infinity"
        self.player = NamedPlayer(self.player_name)
        self.add_player(self.player)
        self.dice = Dice()  # This should be changed in superclass too.

    def run(self):
        while not self.game_won:
            self.round_ctr += 1
            print("\n===== We have begun round #{} =====".format(self.round_ctr))

            self.dice.roll()
            logging.debug("Dice roll: {}".format(self.get_dice_values()))
            logging.debug("Roll values: {}".format(self.get_roll_values()))
            # Later we can be smarter about placing the markers.
            choice = None
            for preferred_value in [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12]:
                if preferred_value in self.dice.values:
                    choice = (preferred_value, )
                    break

            self.board.register_roll_choice(choice, self.player_name)
            self.board.register_stop_choice(self.player)
            winner = self.board.check_for_winner()
            if winner:
                self.game_won = True

            self.board.print_status()
            if self.round_ctr >= 10:
                sys.exit()


def main():
    description = '''
This simulation will see if the column lengths indeed correspond to the likelihood
of rolling that value.
'''
    epilog = '''
Examples:
./infinite_attempts.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)
    logging.basicConfig(level=logging.DEBUG,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')
    logging.debug("Starting up....")

    game = InfiniteGame()
    game.run()


if __name__ == "__main__":
    main()
