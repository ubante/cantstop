#!/usr/bin/env python

"""
Q: After you have your first two sums, which is the best third value?
A: It's non-linear.  Best use a chart.
"""
import argparse


class Player(object):
    """
    Because this was inevitable.
    """
    pass


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
After you have your first two sums, which is the best third value? 
'''
    epilog = '''
Examples:
./third_die_optimizer.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)

    current_sums = [7, 9]
    tvo = TripleValueOdds(current_sums[0], current_sums[1])

    # Loop through all the possible third sums.
    for third_sum in range(2, 13):
        if third_sum in current_sums:
            continue

        odds = tvo.find_odds(third_sum)
        print("Given {}/{}, if you then get a {}, your hit odds in the next roll are {:4.1f}%"
              .format(current_sums[0], current_sums[1], third_sum, odds*100))


if __name__ == "__main__":
    main()

"""
Given 2/12, if you then get a 3, your hit odds in the next roll are 43.8%
Given 2/12, if you then get a 4, your hit odds in the next roll are 55.2%
Given 2/12, if you then get a 5, your hit odds in the next roll are 63.4%
Given 2/12, if you then get a 6, your hit odds in the next roll are 73.8%
Given 2/12, if you then get a 7, your hit odds in the next roll are 78.1%  <---
Given 2/12, if you then get a 8, your hit odds in the next roll are 73.8%
Given 2/12, if you then get a 9, your hit odds in the next roll are 63.4%
Given 2/12, if you then get a 10, your hit odds in the next roll are 55.2%
Given 2/12, if you then get a 11, your hit odds in the next roll are 43.8%

Given 7/9, if you then get a 2, your hit odds in the next roll are 83.6%
Given 7/9, if you then get a 3, your hit odds in the next roll are 84.3%
Given 7/9, if you then get a 4, your hit odds in the next roll are 89.3%
Given 7/9, if you then get a 5, your hit odds in the next roll are 85.3%
Given 7/9, if you then get a 6, your hit odds in the next roll are 91.4%  <---
Given 7/9, if you then get a 8, your hit odds in the next roll are 88.7%
Given 7/9, if you then get a 10, your hit odds in the next roll are 84.8%
Given 7/9, if you then get a 11, your hit odds in the next roll are 78.7%
Given 7/9, if you then get a 12, your hit odds in the next roll are 80.9%

"""