#!/usr/bin/env python

"""
Interactive game.
"""
import argparse
import logging
import sys

from cantstop.lib.all_the_things import HumanPlayer, Game
from cantstop.lib.bots.bots import *


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
    logging.basicConfig(level=logging.DEBUG,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')
    logging.debug("Starting up....")

    game = Game()
    game.add_player(HumanPlayer("Cond"))
    game.add_player(ScoringBot("ScoringBot"))
    game.add_player(RunningScoringBot("RSB"))
    game.run()

    game.print_conclusion()


if __name__ == "__main__":
    main()
