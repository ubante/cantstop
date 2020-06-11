#!/usr/bin/env python

"""
Which starting three should I be happy with?
"""

import argparse
from collections import defaultdict

from cantstop.all_the_things import Die


class RollSet(object):
    def __init__(self):
        self.possibilities = defaultdict(int)
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


def roll(iterations):
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


def roll_tuple(iterations):
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
    odds = roll_tuple(args.iterations)
    for o in sorted(odds):
        print("{}, {}, {}".format(o[0], o[1], odds[o]))

    print("Another way to see this is to count the elements of the tuples:")
    elements = defaultdict(int)
    for (a, b) in odds:
        elements[a] += odds[(a, b)]
        elements[b] += odds[(a, b)]
    for total in sorted(elements):
        print("{}, {}".format(total, elements[total]))

    # Second method.
    print("\nThe odds of hitting each sum of two dice:")
    odds = roll(args.iterations)
    for o in odds:
        print("{:>2}, {}".format(o, odds[o]))

    # Third method
    print("\nThis is theoretical and not empirical.")
    print("This counts four bullets as rolling 2 exactly once.")
    print("The odds rolling four dice and getting at this sum:")
    rs = RollSet()
    for total in sorted(rs.possibilities):
        print("{}, {}".format(total, rs.possibilities[total]))


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