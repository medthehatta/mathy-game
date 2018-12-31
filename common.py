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


def average(*lst):
    return sum(lst) / len(lst)
