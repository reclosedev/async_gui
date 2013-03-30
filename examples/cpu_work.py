#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
if sys.version_info[0] == 3:
    xrange = range

import math


PRIMES = [
    112272535095293,
    112582705942171,
    1063310852888943,
    112272535095293,
    234576030762038,
    115280095190773,
    314924391886526,
    115797848077099,
    1099726899285419,
    108127518666465,
]


def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in xrange(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True
