#!/usr/bin/env python

"""
This will take all the bots and find the best performer.

This will be done with a double elimination done in 2-4 player games.
"""
import argparse
import logging
import sys


class Tournament(object):
    def __init__(self):
        self.game_history = []
        self.scoreboard = None

    def begin(self):
        # Find the players

        # Build the brackets

        # Run the first round

        # Run the next rounds

        # Report the results
        pass


def main():
    description = '''
This will take all the bots and find the best performer.
'''
    epilog = '''
Examples:
./arena.py
'''
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-i", "--iteration", help="How many times to run?",
                        type=int, default=10000)
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')
    logging.debug("Starting up....")

    t = Tournament()
    t.begin()


if __name__ == "__main__":
    main()

