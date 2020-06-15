"""
In the normal game, your turn ends when you bust out.

But here, you play alone, you can't choose, and you never bust out.

This simulation will see if the column lengths indeed correspond to the likelihood
of rolling that value.
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
    # This is just to generate the usage.
    argparse.ArgumentParser(description=description, epilog=epilog)
    logging.basicConfig(level=logging.DEBUG,
                        stream=sys.stdout,
                        format='%(levelname)s - %(message)s')
    logging.debug("Starting up....")


if __name__ == "__main__":
    main()