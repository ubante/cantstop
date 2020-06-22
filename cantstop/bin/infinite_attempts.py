"""
In the normal game, your turn ends when you bust out.

But here, you play alone, you can't choose, and you never bust out.

This simulation will see if the column lengths indeed correspond to the likelihood
of rolling that value.

The results of different players shows that the approach take here is not reliably
indicative one way or another.  But I'm happy with how easy it was to create
new rules for Game().
"""
import argparse
import logging
import pprint
import sys

from cantstop.lib import odds
from cantstop.lib.all_the_things import Game
from cantstop.lib.bots.bots import OctoRollerBot


class InfiniteGame(Game):
    def run(self):
        player_name = self.players[0].name
        while not self.game_won:
            self.round_ctr += 1
            self.dice.roll()
            logging.debug("Dice roll: {}".format(self.dice.values))
            logging.debug("Roll values: {}".format(self.dice.get_sums()))
            choice = self.dice.get_sums()[0]

            self.board.register_roll_choice(choice, player_name)
            self.board.register_stop_choice(self.players[0])
            winner = self.board.check_for_winner()
            if winner:
                self.game_won = True

            if logging.root.level <= logging.DEBUG:
                self.board.print_status()
            if self.round_ctr >= 100:
                print("Exiting because we have hit turn 100.  Something is wrong.")
                sys.exit()

        return self.round_ctr, self.board.get_won_columns()


def main():
    description = '''
This simulation will see if the column lengths indeed correspond to the likelihood
of rolling that value.
'''
    epilog = '''
Examples:
./infinite_attempts.py
'''
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-i", "--iteration", help="How many times to run?",
                        type=int, default=10000)
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')
    logging.debug("Starting up....")
    print("Running {} infinite games....".format(args.iteration))

    game = None
    record = []
    for i in range(1, args.iteration+1):
        if i % round(args.iteration/10) == 1:
            print("\n===== We have begun iteration #{} =====".format(i))

        # Maybe I could make a reset() method in Game()?
        game = InfiniteGame()
        game.add_player(OctoRollerBot("Woody"))
        turn, winning_columns = game.run()
        record.append([turn, winning_columns])

    # Run some stats for the collected data.  This logic could be put in the
    # above loop to keep memory usage down from the record list.
    winning_columns_tracker = {}
    for ct in odds.get_column_triplets():
        winning_columns_tracker[ct] = 0

    round_sum = 0
    most_frequent_winning_triple = (None, 0)
    least_frequent_winning_triple = (None, args.iteration)
    for r in record:
        round_sum += r[0]

        # It is possible that there are four winning columns.  Ignore this edge case.
        if len(r[1]) > 3:
            continue

        winning_columns_tracker[tuple(r[1])] += 1

    for wc in winning_columns_tracker:
        if wc[1] < least_frequent_winning_triple[1]:
            least_frequent_winning_triple = [wc, winning_columns_tracker[wc]]
        if wc[1] > most_frequent_winning_triple[1]:
            most_frequent_winning_triple = [wc, winning_columns_tracker[wc]]

    pprint.PrettyPrinter().pprint(winning_columns_tracker)
    print("After {} infinite games with {}....".format(args.iteration, game.players[0].__class__.__name__))
    print("The average number of rounds in a game is {:3.3f}".format(round_sum/len(record)))
    print("The most winning triple: {}".format(most_frequent_winning_triple))
    print("The least winning triple: {}".format(least_frequent_winning_triple))


if __name__ == "__main__":
    main()


"""
The below outputs make me think the random() isn't that random.
After 100000 infinite games with CowardBot....
The average number of rounds in a game is 28.7
The most winning triple: ((2, 3, 12), 2349)
The least winning triple: ((3, 6, 10), 1)

After 10000 infinite games with CowardBot....
The average number of rounds in a game is 28.7
The most winning triple: [(2, 3, 4), 114]
The least winning triple: [(3, 5, 7), 1]

After 100000 infinite games with CowardBot....
The average number of rounds in a game is 28.7
The most winning triple: [(2, 3, 4), 1101]
The least winning triple: [(10, 11, 12), 947]

After 100000 infinite games with HexRollerBot....
The average number of rounds in a game is 28.7
The most winning triple: [(2, 3, 4), 1036]
The least winning triple: [(5, 7, 8), 6]

After 100000 infinite games with HexRollerBot....
The average number of rounds in a game is 28.704
The most winning triple: [(2, 3, 4), 1067]
The least winning triple: [(10, 11, 12), 921]

After 100000 infinite games with OctoRollerBot....
The average number of rounds in a game is 28.727
The most winning triple: [(2, 3, 4), 1099]
The least winning triple: [(7, 8, 10), 7]

"""