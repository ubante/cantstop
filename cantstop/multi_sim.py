#!/usr/bin/env python

"""
Run different bots many times to see who is best.
"""
import argparse
import logging
import sys
from collections import defaultdict

from cantstop.all_the_things import Game
from cantstop.bots import CowardBot, SmartCowardBot, ConservativeBot, SmartConservativeBot


def set_logger(verbose_level):
    """
    Initialize the logger.  The verbose_level should be in [0, 1, 2].
    This won't return anything but will reconfigure the root logger.
    :param logfile_name:
    :param verbose_level:
    :return:
    """
    if verbose_level >= 2:
        logging_level = logging.DEBUG
    elif verbose_level == 1:
        logging_level = logging.INFO
    else:
        logging_level = logging.ERROR

    logging.basicConfig(level=logging_level,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')


def main():
    description = '''
Run different bots many times to see who is best.
'''
    epilog = '''
Examples:
./multi_sim.py
./multi_sim.py -i 10
./multi_sim.py -i 5 -vv
'''
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog)
    parser.add_argument("-i", "--iteration", help="How many times to run?", type=int, default=1000)
    parser.add_argument("-v", "--verbose", help="Print info/debug", action="count", default=1)
    args = parser.parse_args()
    set_logger(args.verbose)

    logging.debug("Starting up....")

    chicken_dinner = defaultdict(int)
    for i in range(0, args.iteration):

        game = Game()
        # players = [CowardBot, SmartCowardBot]
        players = [SmartCowardBot, ConservativeBot, SmartConservativeBot]
        for player in players:
            name = player.__name__
            game.add_player(player(name))

        game.run()
        print("Winner is {}".format(game.winner))
        chicken_dinner[game.winner] += 1

    print("After {} iterations, here are the winners:".format(args.iteration))
    print(chicken_dinner)


if __name__ == "__main__":
    main()
