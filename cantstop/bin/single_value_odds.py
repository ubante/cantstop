#!/usr/bin/env python

"""
Q: What are the odds of a single roll of four dice returning a given sum?
A: Same as with two dice times four.
"""
import argparse

from cantstop.lib.all_the_things import SingleValueOdds


def main():
    description = '''
This generates the odds.  You probably will never run this.
'''
    epilog = '''
Examples:
./single_value_odds.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)

    s1 = SingleValueOdds()
    s2 = SingleValueOdds()
    s3 = SingleValueOdds()

    print(s1.of(3))
    print(s2.of(2))
    print(s3.of(13))


if __name__ == "__main__":
    main()
