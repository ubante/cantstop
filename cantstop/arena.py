#!/usr/bin/env python

"""
This will take all the bots and find the best performer.

This will be done with a double elimination done in 2-4 player games.
"""
import argparse
import logging
import sys


def main():
    description = '''
This simulation will see if the column lengths indeed correspond to the likelihood
of rolling that value.
'''
    epilog = '''
Examples:
./infinite_attempts.py
'''
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-i", "--iteration", help="How many times to run?",
                        type=int, default=10000)
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')
    logging.debug("Starting up....")


if __name__ == "__main__":
    main()

