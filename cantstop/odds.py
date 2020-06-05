#!/usr/bin/env python

"""
Which starting three should I be happy with?
"""

import argparse

from cantstop.all_the_things import Die


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

        pair_of_sum1 = tuple(sorted([dice[0].value + dice[1].value, dice[2].value + dice[3].value]))
        pair_of_sum2 = tuple(sorted([dice[0].value + dice[2].value, dice[1].value + dice[3].value]))
        pair_of_sum3 = tuple(sorted([dice[0].value + dice[3].value, dice[1].value + dice[2].value]))
        for t in pair_of_sum1, pair_of_sum2, pair_of_sum3:
            if t in odds:
                odds[t] += 1
            else:
                odds[t] = 1

        # a_list = sorted([dice[0].value + dice[1].value,
        #                  dice[0].value + dice[2].value,
        #                  dice[0].value + dice[3].value,
        #                  dice[1].value + dice[3].value])
        # t = tuple(a_list)
        # if t in odds:
        #     odds[t] += 1
        # else:
        #     odds[t] = 1

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
    parser.add_argument("--iterations", help="How exact do you want to be?", type=int, default=1000)
    args = parser.parse_args()

    print("\nThe odds of each tuple:")
    odds = roll_tuple(args.iterations)
    for o in sorted(odds):
        print("{}, {}, {}".format(o[0], o[1], odds[o]))
        # print("{}: {}".format(o, odds[o]))

    print("The odds of hitting each sum of two dice:")
    odds = roll(args.iterations)
    for o in odds:
        # print("{:>2}, {}".format(o, odds[o]))
        print("{:>2}: {}".format(o, odds[o]))


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
'''