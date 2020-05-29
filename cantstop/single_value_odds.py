#!/usr/bin/env python

"""
Q: What are the odds of a single roll of four dice returning a given sum?
A: Same as with two dice times four.
"""
import argparse
from collections import defaultdict


class SingleValueOdds(object):
    """
    Singleton to help performance a little.
    https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    """
    class __SingleValueOdds(object):
        def __init__(self):
            self.sum_count = defaultdict(int)
            self.odds = {}
            self.find_odds()

        def find_odds(self):
            """
            This results in the same odds as a pair of dice x 4 since four dice
            creates four sets of pairs.
            :return:
            """
            ctr = 0
            for d1 in range(1, 7):
                for d2 in range(1, 7):
                    for d3 in range(1, 7):
                        for d4 in range(1, 7):
                            ctr += 1
                            self.sum_count[d1 + d2] += 1
                            self.sum_count[d1 + d3] += 1
                            self.sum_count[d1 + d4] += 1
                            self.sum_count[d2 + d4] += 1

            for roll in self.sum_count:
                self.odds[roll] = self.sum_count[roll] / ctr

    instance = None

    def __init__(self):
        if not SingleValueOdds.instance:
            SingleValueOdds.instance = SingleValueOdds.__SingleValueOdds()

    def of(self, roll):
        if roll in self.instance.odds:
            return self.instance.odds[roll]
        else:
            print("The roll of {} is impossible with two 6-sided dice.".format(roll))
            return 0


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

    print(s1.of(5))
    print(s2.of(2))
    print(s3.of(13))


if __name__ == "__main__":
    main()
