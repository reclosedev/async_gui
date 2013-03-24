#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math


PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419,
    ]


def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in xrange(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True
