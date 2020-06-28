#!/usr/bin/env python

"""
Q: After you have chosen your three columns, what are the odds that you will get a hit
on your next attempt?
A: Between 43.8% and 92.0%.
"""
import argparse

from cantstop.lib.odds import AttemptHitter


def main():
    description = '''
After you have chosen your three columns, what are the odds that you will get a hit
on your next attempt?
'''
    epilog = '''
Examples:
./odds_after_choosing_three.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)

    # current_sums = [2, 3, 4]
    current_sums = [6, 7, 8]
    # current_sums = [2, 3, 12]
    odds = AttemptHitter(current_sums)

    print("If your columns are {}, then your odds of a hit are {}".format(current_sums, odds))


if __name__ == "__main__":
    main()

"""
If your columns are [2, 3, 12], then your odds of a hit are 43.8%
If your columns are [6, 7, 8], then your odds of a hit are 92.0%
"""