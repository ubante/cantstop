#!/usr/bin/env python

"""
This will take all the bots and find the best performer.

Here's the final score:
   RunningScoringBot won 26 games
  ChoosingScoringBot won 25 games
       QuadRollerBot won 23 games
     ConservativeBot won 21 games
          ScoringBot won 19 games
        HexRollerBot won 17 games
      SeptaRollerBot won 15 games
       DecaRollerBot won 8 games
       OctoRollerBot won 7 games
      SmartCowardBot won 3 games
           CowardBot won 1 games

Here's the final score:
  ChoosingScoringBot won 26 games
       QuadRollerBot won 22 games
        HexRollerBot won 22 games
     ConservativeBot won 21 games
   RunningScoringBot won 21 games
          ScoringBot won 19 games
       OctoRollerBot won 13 games
      SeptaRollerBot won 11 games
       DecaRollerBot won 6 games
      SmartCowardBot won 3 games
           CowardBot won 1 games

"""
import argparse
import sys
from collections import defaultdict

from cantstop.lib.all_the_things import Game
from cantstop.lib.bots.bots import *


class Tournament(object):
    def __init__(self):
        self.game_history = []
        self.scoreboard = None
        self.game_indices = []  # list of tuples of ints
        self.results = {}
        self.all_players = []

    def plan(self):
        # Find the players - eventually, this should not be explicit.
        self.all_players = [CowardBot, SmartCowardBot, ConservativeBot, ScoringBot, ChoosingScoringBot,
                            RunningScoringBot, QuadRollerBot, HexRollerBot, SeptaRollerBot, OctoRollerBot,
                            DecaRollerBot]

        # Make a game with each combination of three players.
        pcount = len(self.all_players)
        for a in range(0, pcount-2):
            for b in range(a+1, pcount-1):
                for c in range(b+1, pcount):
                    self.game_indices.append((a, b, c))
        print("Will play {} games with {} players.".format(len(self.game_indices), pcount))

    def play_game(self, players):
        # print("Playing a game with {}, {}, and {}".format(players[0].name, players[1].name, players[2].name))
        game = Game()
        for player in players:
            game.add_player(player)

        game.run()
        print("Winner is {}".format(game.winner))
        self.results[tuple(players)] = game.winner  # this is a str of the winning player's name

    def run(self):
        for game_index in self.game_indices:
            players = []  # instances of bots
            for g_ctr, i in enumerate(game_index):
                player_class = self.all_players[i]
                players.append(player_class(player_class.__name__))

            self.play_game(players)

    def report(self):
        win_record = defaultdict(int)
        for r in self.results:
            game_players = "{}, {}, {}".format(r[0].name, r[1].name, r[2].name)
            print("{:>55} ---> {}".format(game_players, self.results[r], ))
            win_record[self.results[r]] += 1

        print("\nHere's the final score:")
        for name in sorted(win_record.items(), key=lambda x: x[1], reverse=True):
            print("{:>20} won {} games".format(name[0], win_record[name[0]]))


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
    t.plan()
    t.run()
    t.report()


if __name__ == "__main__":
    main()

