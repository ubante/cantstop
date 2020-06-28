#!/usr/bin/env python

"""
Q: After you have your first two sums, which is the best third value?
A: It's non-linear.  Best use a chart.
"""
import argparse

from cantstop.lib.odds import TripleValueOdds


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

    current_sums = [5, 7]
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
If 7 and something less than 7, choose 8.
If 7 and something greater than 7, choose 6.
If 3/5, choose 8.
If 9/11, choose 6.
If both are less than 7, choose 8.
If both are greater than 7, choose 6.
Otherwise, choose 7.

Given 9/11, if you then get a 2, your hit odds in the next roll are 63.7%
Given 9/11, if you then get a 3, your hit odds in the next roll are 71.0%
Given 9/11, if you then get a 4, your hit odds in the next roll are 75.8%
Given 9/11, if you then get a 5, your hit odds in the next roll are 77.6%
Given 9/11, if you then get a 6, your hit odds in the next roll are 80.8%  <--- 6
Given 9/11, if you then get a 7, your hit odds in the next roll are 78.7%
Given 9/11, if you then get a 8, your hit odds in the next roll are 77.1%
Given 9/11, if you then get a 10, your hit odds in the next roll are 66.9%
Given 9/11, if you then get a 12, your hit odds in the next roll are 58.4%

Given 5/6, if you then get a 2, your hit odds in the next roll are 77.0%
Given 5/6, if you then get a 3, your hit odds in the next roll are 77.1%
Given 5/6, if you then get a 4, your hit odds in the next roll are 79.6%
Given 5/6, if you then get a 7, your hit odds in the next roll are 88.7%
Given 5/6, if you then get a 8, your hit odds in the next roll are 89.5%  <--- 8
Given 5/6, if you then get a 9, your hit odds in the next roll are 86.7%
Given 5/6, if you then get a 10, your hit odds in the next roll are 86.3%
Given 5/6, if you then get a 11, your hit odds in the next roll are 83.6%
Given 5/6, if you then get a 12, your hit odds in the next roll are 82.3%

Given 4/7, if you then get a 2, your hit odds in the next roll are 80.7%
Given 4/7, if you then get a 3, your hit odds in the next roll are 79.1%
Given 4/7, if you then get a 5, your hit odds in the next roll are 84.8%
Given 4/7, if you then get a 6, your hit odds in the next roll are 88.6%
Given 4/7, if you then get a 8, your hit odds in the next roll are 90.3%  <--- 8
Given 4/7, if you then get a 9, your hit odds in the next roll are 89.3%
Given 4/7, if you then get a 10, your hit odds in the next roll are 87.7%
Given 4/7, if you then get a 11, your hit odds in the next roll are 83.6%
Given 4/7, if you then get a 12, your hit odds in the next roll are 83.3%

Given 2/12, if you then get a 3, your hit odds in the next roll are 43.8%
Given 2/12, if you then get a 4, your hit odds in the next roll are 55.2%
Given 2/12, if you then get a 5, your hit odds in the next roll are 63.4%
Given 2/12, if you then get a 6, your hit odds in the next roll are 73.8%
Given 2/12, if you then get a 7, your hit odds in the next roll are 78.1%  <--- 7
Given 2/12, if you then get a 8, your hit odds in the next roll are 73.8%
Given 2/12, if you then get a 9, your hit odds in the next roll are 63.4%
Given 2/12, if you then get a 10, your hit odds in the next roll are 55.2%
Given 2/12, if you then get a 11, your hit odds in the next roll are 43.8%

Given 7/9, if you then get a 2, your hit odds in the next roll are 83.6%
Given 7/9, if you then get a 3, your hit odds in the next roll are 84.3%
Given 7/9, if you then get a 4, your hit odds in the next roll are 89.3%
Given 7/9, if you then get a 5, your hit odds in the next roll are 85.3%
Given 7/9, if you then get a 6, your hit odds in the next roll are 91.4%  <--- 6
Given 7/9, if you then get a 8, your hit odds in the next roll are 88.7%
Given 7/9, if you then get a 10, your hit odds in the next roll are 84.8%
Given 7/9, if you then get a 11, your hit odds in the next roll are 78.7%
Given 7/9, if you then get a 12, your hit odds in the next roll are 80.9%

Given 7/8, if you then get a 2, your hit odds in the next roll are 89.0%
Given 7/8, if you then get a 3, your hit odds in the next roll are 89.3%
Given 7/8, if you then get a 4, your hit odds in the next roll are 90.3%
Given 7/8, if you then get a 5, your hit odds in the next roll are 91.4%
Given 7/8, if you then get a 6, your hit odds in the next roll are 92.0%  <--- 6
Given 7/8, if you then get a 9, your hit odds in the next roll are 88.7%
Given 7/8, if you then get a 10, your hit odds in the next roll are 88.6%
Given 7/8, if you then get a 11, your hit odds in the next roll are 86.5%
Given 7/8, if you then get a 12, your hit odds in the next roll are 86.4%

Given 3/5, if you then get a 2, your hit odds in the next roll are 58.4%
Given 3/5, if you then get a 4, your hit odds in the next roll are 66.9%
Given 3/5, if you then get a 6, your hit odds in the next roll are 77.1%
Given 3/5, if you then get a 7, your hit odds in the next roll are 78.7%
Given 3/5, if you then get a 8, your hit odds in the next roll are 80.8%  <--- 8
Given 3/5, if you then get a 9, your hit odds in the next roll are 77.6%
Given 3/5, if you then get a 10, your hit odds in the next roll are 75.8%
Given 3/5, if you then get a 11, your hit odds in the next roll are 71.0%
Given 3/5, if you then get a 12, your hit odds in the next roll are 63.7%

"""