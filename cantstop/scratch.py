#!/usr/bin/env python
import logging
import sys
from cantstop.lib.odds import Triplet, RollSet

logging.basicConfig(level=logging.DEBUG,
                    stream=sys.stdout,
                    format='%(levelname)s - %(message)s')
t1 = Triplet(2, 3, 12)
print("\n{} has a {} chance to hit in the next roll attempt.\n".format(t1, t1.compute_hit(percent_format=True)))

t1 = Triplet(6, 7, 8)
print("\n{} has a {} chance to hit in the next roll attempt.\n".format(t1, t1.compute_hit(percent_format=True)))

t1 = Triplet(6, 7, 8)
t1.values = (2, 3, 4, 5, 6, 8, 9, 10, 11, 12)
print("\n{} has a {} chance to hit in the next roll attempt.\n".format(t1, t1.compute_hit(percent_format=True)))

rs = RollSet()
print(rs.possibilities)

"""
odds to hit by each of the three column values
DEBUG - 0.8680555555555556 0.7669753086419753 0.8680555555555556

TRIP[2|3|12] has a 42.2% chance to hit in the next roll attempt.

DEBUG - {} odds to hit by each of the three column values
DEBUG - 0.4390432098765432 0.3564814814814815 0.4390432098765432

TRIP[6|7|8] has a 93.1% chance to hit in the next roll attempt.
"""


