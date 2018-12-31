#!/usr/bin/env python
# coding: utf-8


"""Some common functionality."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


#
# Business
#


def flatten(lst):
    return sum(lst, [])


def merge(dict1, dict2):
    all_keys = set.union(set(dict1.keys()), set(dict2.keys()))
    return {k: dict2.get(k, dict1.get(k)) for k in all_keys}


def average(*lst):
    return sum(lst) / len(lst)
