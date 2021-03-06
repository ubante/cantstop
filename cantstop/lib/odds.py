#!/usr/bin/env python

"""
Collection of stat functions.

Answer questions like:
- Given two sums, which third sum maximizes a hit in the following attempt.
- Given a temp_progress position, should player stop or continue.

This should not import any other module in /lib.
"""

import argparse
import logging
from collections import defaultdict
from random import randint

from cantstop.lib.settings import Settings


class Die(object):
    """
    This might be overkill.
    """

    def __init__(self):
        self.value = None
        self.roll()

    def roll(self):
        self.value = randint(1, 6)


class Dice(object):
    """
    A set of dice.
    """

    def __init__(self):
        self._dice = []
        self.count = 4
        for i in range(0, self.count):
            self._dice.append(Die())
        self.values = []
        self.roll()

    def roll(self):
        self.values = []
        for d in self._dice:
            d.roll()
            self.values.append(d.value)

    def get_sums(self):
        """
        This returns three tuples where each value has the sum of two distinct
        pairs of dice.

        :return: eg [(5, 10), (6, 9), (7, 8)]
        """
        pair_of_sums1 = tuple(sorted([self._dice[0].value + self._dice[1].value,
                                      self._dice[2].value + self._dice[3].value]))
        pair_of_sums2 = tuple(sorted([self._dice[0].value + self._dice[2].value,
                                      self._dice[1].value + self._dice[3].value]))
        pair_of_sums3 = tuple(sorted([self._dice[0].value + self._dice[3].value,
                                      self._dice[1].value + self._dice[2].value]))

        # It's possible that there are duplicate tuples.  For example,
        # the dice rolls are 1, 2, 2, 5].  This results in these possible
        # pairs: [(3, 7), (4, 6), (3, 7)].  So unique the list.
        return list({pair_of_sums1, pair_of_sums2, pair_of_sums3})


class Triplet(object):
    """
    This represents the three columns of temporary progress.

    Not sure about this.
    """

    def __init__(self, a=0, b=0, c=0):
        if a not in [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:  # lol
            raise ValueError("'a' value of '{}' is not zero and not in [2, 12]".format(a))
        if b not in [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:  # lol
            raise ValueError("'b' value of '{}' is not zero and not in [2, 12]".format(b))
        if c not in [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:  # lol
            raise ValueError("'c' value of '{}' is not zero and not in [2, 12]".format(c))

        self.values = sorted([a, b, c])
        self.rs = RollSet()

    def __repr__(self):
        return "TRIP[{}|{}|{}]".format(self.values[0], self.values[1], self.values[2])

    def compute_hit(self, percent_format=False):
        """
        Find the odds of the next attempt producing a hit.
        :return: 1.0 is 100%
        """
        # This method only makes sense if all three markers are spent.
        if not self.values[0] * self.values[1] * self.values[2]:
            if percent_format:
                return "100%"
            else:
                return 1.0

        individual_odds = []
        for value in self.values:
            odd = 1 - (self.rs.possibilities[value] / self.rs.roll_combinations_length)
            individual_odds.append(odd)
        logging.debug("Individual odds:")
        logging.debug(individual_odds)
        not_hitting_odds = 1
        for io in individual_odds:
            not_hitting_odds *= io
        odds = 1 - not_hitting_odds

        # # To simplify the math, compute the odds of not hitting.
        # odds1 = 1 - (self.rs.possibilities[self.values[0]] / self.rs.roll_combinations_length)
        # odds2 = 1 - (self.rs.possibilities[self.values[1]] / self.rs.roll_combinations_length)
        # odds3 = 1 - (self.rs.possibilities[self.values[2]] / self.rs.roll_combinations_length)
        # logging.debug("{} odds to hit by each of the three column values")
        # logging.debug("{} {} {}".format(odds1, odds2, odds3))
        # odds = 1 - (odds1 * odds2 * odds3)

        if percent_format:
            return "{:3.1f}%".format(100 * odds)
        else:
            return odds


class RollSet(object):
    """
    All the possible ways to sum four dice.
    """

    def __init__(self):
        self.possibilities = defaultdict(int)
        self.possibilities_ctr = 0
        # List of unsorted tuples, eg (1, 1, 5, 6).
        self.roll_combinations = []
        self.roll_combinations_length = 6 * 6 * 6 * 6
        self.roll_sorted_combinations = []
        # List of unsorted tuples, eg (2, 6, 7, 6, 7, 11)
        self.sum_combinations = []
        self.compute_combinations()

    def reset(self):
        self.roll_combinations = []
        self.possibilities = defaultdict(int)
        self.possibilities_ctr = 0
        self.sum_combinations = []
        self.roll_sorted_combinations = []

    def compute_combinations(self):
        self.reset()
        for a in range(1, 7):
            for b in range(1, 7):
                for c in range(1, 7):
                    for d in range(1, 7):
                        self.roll_combinations.append((a, b, c, d))
                        total = defaultdict(int)
                        total[a + b] = 1
                        total[a + c] = 1
                        total[a + d] = 1
                        total[b + c] = 1
                        total[b + d] = 1
                        total[c + d] = 1
                        for t in total:
                            self.possibilities[t] += 1
                            self.possibilities_ctr += 1

                        self.sum_combinations.append((a + b, a + c, a + d, b + c, b + d, c + d))

        for a in range(1, 7):
            for b in range(a, 7):
                for c in range(b, 7):
                    for d in range(c, 7):
                        self.roll_sorted_combinations.append((a, b, c, d))

    def compute_limited_combinations(self, available_columns=Settings.COLUMN_RANGE):
        """
        Keep this separate from compute_combinations() until it's clear what is needed.

        Compute the combinations when a one or more columns have been won, ie are
        unavailable.

        :return:
        """
        self.reset()
        for a in range(1, 7):
            for b in range(1, 7):
                for c in range(1, 7):
                    for d in range(1, 7):
                        self.roll_combinations.append((a, b, c, d))
                        total = defaultdict(int)
                        total[a + b] = 1
                        total[a + c] = 1
                        total[a + d] = 1
                        total[b + c] = 1
                        total[b + d] = 1
                        total[c + d] = 1
                        for t in total:
                            self.possibilities[t] += 1
                            self.possibilities_ctr += 1

                        good_pairs = []
                        for pair_sum in [a + b, a + c, a + d, b + c, b + d, c + d]:
                            if pair_sum in available_columns:
                                good_pairs.append(pair_sum)

                        self.sum_combinations.append(tuple(good_pairs))
        print("There are {} combinations of pair-sums.".format(len(self.sum_combinations)))

        for a in range(1, 7):
            for b in range(a, 7):
                for c in range(b, 7):
                    for d in range(c, 7):
                        self.roll_sorted_combinations.append((a, b, c, d))


class ScoreRule28(object):
    """
    This is a heuristic described in https://www.aaai.org/ocs/index.php/FLAIRS/2009/paper/download/123/338
    """

    @staticmethod
    def score(columns):
        """
        Accept a dict of column ranks and sum the score of each column.  See link.

        :param columns: dict of column_number->rank_achieved
        :return: int
        """
        score = 0
        for c in columns:
            multiplier = abs(7 - c) + 1
            score += multiplier * columns[c]

        return score


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

        return hits / possibilities


class HitPredictor(object):
    """
    Accept a triplet of pair-sums and return the percentage odds that the next attempt
    will hit.
    """
    def __init__(self):
        self.rollset = RollSet()
        self.available_cols = Settings.COLUMN_RANGE

    def update_columns(self, available_columns):
        """
        Use this to make predictions on a board where some columns have already been won.

        :param available_columns:
        :return:
        """
        self.available_cols = available_columns
        self.rollset.compute_limited_combinations(self.available_cols)

    def compute_next_attempt_odds(self, trips):
        hit_ctr = 0
        miss_ctr = 0
        tripset = set(trips)
        for roll in self.rollset.sum_combinations:
            if tripset.intersection(set(roll)):
                hit_ctr += 1
                # print("{} hits".format(roll))
            else:
                miss_ctr += 1
                # print("{} misses".format(roll))

        # print("length = {}".format(len(self.rollset.sum_combinations)))
        # print("hit_ctr = {}".format(hit_ctr))
        # print("miss_ctr = {}".format(miss_ctr))

        next_attempt_odds = 100 * hit_ctr / len(self.rollset.sum_combinations)
        return next_attempt_odds


def roll_the_dice(iterations):
    odds = {}
    dice = [Die(), Die(), Die(), Die()]

    for i in range(0, iterations):
        for d in dice:
            d.roll()

        pair_of_sums_1 = tuple(sorted([dice[0].value + dice[1].value, dice[2].value + dice[3].value]))
        pair_of_sums_2 = tuple(sorted([dice[0].value + dice[2].value, dice[1].value + dice[3].value]))
        pair_of_sums_3 = tuple(sorted([dice[0].value + dice[3].value, dice[1].value + dice[2].value]))
        for t in pair_of_sums_1, pair_of_sums_2, pair_of_sums_3:
            if t in odds:
                odds[t] += 1
            else:
                odds[t] = 1

    return odds


def roll_the_dice_2(iterations):
    odds = {}
    for i in range(2, 13):
        odds[i] = 0
    dice = [Die(), Die(), Die(), Die()]

    for i in range(0, iterations):
        for d in dice:
            d.roll()

        odds[dice[0].value + dice[1].value] += 1
        odds[dice[0].value + dice[2].value] += 1
        odds[dice[0].value + dice[3].value] += 1
        odds[dice[1].value + dice[2].value] += 1
        odds[dice[1].value + dice[3].value] += 1
        odds[dice[2].value + dice[3].value] += 1

    return odds


def perc(numerator, denominator, no_decimal=False):
    fraction = numerator / denominator * 100
    if no_decimal:
        return "{:3.0f}%".format(fraction)
    return "{:3.1f}%".format(fraction)


def get_column_triplets():
    """
    This returns the different combinations of three distinct columns.
    :return:
    """
    triplets = []
    for a in range(2, 13):
        for b in range(a + 1, 13):
            for c in range(b + 1, 13):
                triplets.append((a, b, c))
    return triplets


def main():
    description = '''
Just go.
'''
    epilog = '''
Examples:
./odds.py
'''
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("--iterations", help="How exact do you want to be?",
                        type=int, default=10000)
    args = parser.parse_args()

    # First method
    print("\nThe odds of each tuple:")
    odds = roll_the_dice(args.iterations)
    for o in sorted(odds):
        print("{}, {}, {}".format(o[0], o[1], perc(odds[o], args.iterations)))

    print("Another way to see this is to count the elements of the tuples:")
    elements = defaultdict(int)
    roll_ctr = 0
    for (a, b) in odds:
        elements[a] += odds[(a, b)]
        elements[b] += odds[(a, b)]
        roll_ctr += odds[(a, b)]
    for total in sorted(elements):
        print("{}, {}, {}".format(total, elements[total], perc(elements[total], args.iterations)))

    # Second method.
    print("\nThe odds of hitting each sum of two dice:")
    odds = roll_the_dice_2(args.iterations)
    for o in odds:
        print("{:>2}, {}, {}".format(o, odds[o], perc(odds[o], args.iterations)))

    # Third method
    print("\nThis is theoretical and not empirical.")
    print("This counts four bullets as rolling 2 exactly once.")
    print("The odds rolling four dice and getting at this sum:")
    rs = RollSet()
    for total in sorted(rs.possibilities):
        print("{}, {}, {}".format(total, rs.possibilities[total],
                                  perc(rs.possibilities[total], rs.roll_combinations_length)))


if __name__ == "__main__":
    main()

'''
The odds of hitting seven is, as expected, the greatest odds.
 2: 98
 3: 215
 4: 316
 5: 429
 6: 550
 7: 714
 8: 493
 9: 443
10: 352
11: 248
12: 142

For tuples, {7, 8} is the most common pair of sums.  For bubble chart, see: 
https://docs.google.com/spreadsheets/d/10vniw_8VG3R96euRF-vUJ17uv91_qgZbmwOQ8oqAAmE/edit#gid=71164707

For any turn, the likelihood of hitting this value:
#	Likelihood
2	13.19%
3	23.30%
4	35.57%
5	44.75%
6	56.10%
7	64.35%
8	56.10%
9	44.75%
10	35.57%
11	23.30%
12	13.19%
'''
