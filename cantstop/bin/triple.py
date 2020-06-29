#!/usr/bin/env python

"""
Q: What is the best triple?
A: XXX
"""
import argparse

from cantstop.lib.odds import AttemptHitter


def main():
    description = '''
At the start of a game, when all columns are available, which triple allows you the 
# most successive rolls?'''
    epilog = '''
Examples:
./triple.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)

    x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
    var = {k: v for k, v in sorted(x.items(), key=lambda item: item[1])}

    results = {}
    column_ctr = 0
    for a in range(2, 11):
        for b in range(a+1, 12):
            for c in range(b+1, 13):
                column_ctr += 1
                columns_chosen = [a, b, c]
                results[tuple(columns_chosen)] = AttemptHitter(columns_chosen).next_attempt_odds

    print("There are {} possible column combinations.".format(column_ctr))

    # Find the top ten results.
    ordered = sorted(results, key=results.get, reverse=True)
    print("\nThe best starting columns:")
    for i in ordered[0:9]:
        print("{}: {:3.1f}%".format(i, results[i]))

    # Find the bottom ten results.
    ordered = sorted(results, key=results.get)
    print("\nThe worset starting columns:")
    for i in ordered[0:9]:
        print("{}: {:3.1f}%".format(i, results[i]))


if __name__ == "__main__":
    main()


"""
There are 165 possible column combinations.

The best starting columns:
(6, 7, 8): 92.0%
(5, 7, 8): 91.4%
(6, 7, 9): 91.4%
(4, 6, 8): 91.1%
(6, 8, 10): 91.1%
(4, 7, 8): 90.3%
(6, 7, 10): 90.3%
(5, 6, 8): 89.5%
(6, 8, 9): 89.5%

The worst starting columns:
(2, 3, 12): 43.8%
(2, 11, 12): 43.8%
(2, 3, 4): 52.2%
(10, 11, 12): 52.2%
(2, 3, 11): 52.5%
(3, 11, 12): 52.5%
(2, 4, 12): 55.2%
(2, 10, 12): 55.2%
(2, 10, 11): 57.9%
"""