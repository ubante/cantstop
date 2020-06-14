#!/usr/bin/env python

"""
Collection of stat functions.

Answer questions like:
- Given two sums, which third sum maximizes a hit in the following attempt.
- Given a temp_progress position, should player stop or continue.
"""

import argparse
from collections import defaultdict
from random import randint


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
        self.roll()

    def roll(self):
        for d in self._dice:
            d.roll()


class RollSet(object):
    """
    All the possible ways to sum four dice.
    """
    def __init__(self):
        self.possibilities = defaultdict(int)
        self.poss_ctr = 0
        self.roll_combinations = 6*6*6*6
        for a in range(1, 7):
            for b in range(1, 7):
                for c in range(1, 7):
                    for d in range(1, 7):
                        total = defaultdict(int)
                        total[a+b] = 1
                        total[a+c] = 1
                        total[a+d] = 1
                        total[b+c] = 1
                        total[b+d] = 1
                        total[c+d] = 1
                        for t in total:
                            self.possibilities[t] += 1
                            self.poss_ctr += 1


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

        odds[dice[0].value+dice[1].value] += 1
        odds[dice[0].value+dice[2].value] += 1
        odds[dice[0].value+dice[3].value] += 1
        odds[dice[1].value+dice[2].value] += 1
        odds[dice[1].value+dice[3].value] += 1
        odds[dice[2].value+dice[3].value] += 1

    return odds


def perc(numerator, denominator):
    fraction = numerator/denominator*100
    return "{:3.1f}%".format(fraction)


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

        return hits/possibilities


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
        print("{}, {}, {}".format(total, rs.possibilities[total], perc(rs.possibilities[total], rs.roll_combinations)))


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
