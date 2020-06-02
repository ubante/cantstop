#!/usr/bin/env python

"""
Interactive game.
"""
import argparse

from cantstop.all_the_things import HumanPlayer, Board, Game
from cantstop.bots import SimpleBot


def main():
    description = '''
Play a solo game.
'''
    epilog = '''
Examples:
./human_player.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)

    you = HumanPlayer()
    you.name = "Me"
    game = Game()
    game.add_player(you)
    bot1 = SimpleBot()
    bot1.name = "Bot1"
    game.add_player(bot1)
    game.add_player(SimpleBot())
    game.start()

    game.print_status()


def test():
    game = Game()
    you = HumanPlayer()
    you.name = "Me"
    game.add_player(you)

    game.roll_dice()
    print("Dice rolls: {}".format(game.get_dice_values()))
    print("Pairs:      {}".format(game.get_roll_values()))
    print()
    game.print_status()


if __name__ == "__main__":
    main()
    # test()
