#!/usr/bin/env python

"""
Interactive game.
"""
import argparse
import logging
import sys

from cantstop.all_the_things import HumanPlayer, Game
from cantstop.bots import CowardBot, SmartCowardBot, ConservativeBot, SmartConservativeBot


def add_players():
    pass


def main():
    description = '''
Play a solo game.
'''
    epilog = '''
Examples:
./simulation_runner.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')
    logging.debug("Starting up....")

    game = Game()
    game.add_player(CowardBot("Cow"))
    game.add_player(SmartCowardBot("Dog"))
    game.add_player(ConservativeBot("Emu"))
    game.add_player(SmartConservativeBot("Fox"))
    game.run()

    game.print_status()


def test():
    game = Game()
    you = HumanPlayer("Me")
    game.add_player(you)

    game.roll_dice()
    print("Dice rolls: {}".format(game.get_dice_values()))
    print("Pairs:      {}".format(game.get_roll_values()))
    print()
    game.print_status()


if __name__ == "__main__":
    main()
    # test()
