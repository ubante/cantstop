#!/usr/bin/env python

"""
Q: What is the best triple?
A: XXX
"""
import argparse


def main():
    description = '''
At the start of a game, which triple will allow you the most successive rolls?'''
    epilog = '''
Examples:
./triple.py
'''
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)


if __name__ == "__main__":
    main()
