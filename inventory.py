#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


from collections import Counter, Iterable
from cytoolz import memoize


import item


#
# Constants
#


#
# Helpers
#


#
# Classes
#


class Index(object):
    """An index of items."""

    def __init__(self, indexer, items=None):
        self.indexer = memoize(indexer)
        self.index = []
        if items:
            self.populate(items)

    def add(self, obj):
        """Add an obj to the index."""
        raise NotImplementedError()

    def remove(self, obj):
        """Remove an obj from the index."""
        raise NotImplementedError()

    def populate(self, objs):
        """Initially populate the index."""
        for obj in objs:
            self.add(obj)


class CategoricalIndex(Index):
    """An index of items by discrete category."""

    def lookup(self, idx):
        """Return matching objects from the index by ``idx``."""
        return self.index.get(idx, [])

    def add(self, obj):
        """Add an obj to the index."""
        objhash = hash(obj)
        self.index = self.index or {}
        categories = self.indexer(obj)
        if (
            isinstance(categories, Iterable) and
            not isinstance(categories, str)
        ):
            for category in categories:
                self.index[category] = self.index.get(category, []) + [objhash]
        else:
            self.index[categories] = self.index.get(categories, []) + [objhash]

    def remove(self, obj):
        """Remove an obj from the index."""
        self.index = self.index or {}
        idx = self.indexer(obj)
        if idx in self.index:
            self.index.pop(idx)

    def keys(self):
        return list(self.index.keys())


class QuantitativeIndex(Index):
    """An index of items by some quantitative measure."""

    def _position(self, value):
        self.index = self.index or []

        for (i, (found, key)) in enumerate(self.index):
            if found > value:
                return i

        # If none of the entries exceed the current value, the value must be
        # inserted at the END of the list.
        return len(self.index)

    def greater_than(self, value):
        """Return matching objects from the index by ``idx``."""
        return self.index[self._position(value):]

    def less_than(self, value):
        """Return matching objects from the index by ``idx``."""
        return self.index[:self._position(value)]

    def near(self, value, fuzz=1):
        lo = value - fuzz*abs(value)
        hi = value + fuzz*abs(value)
        return self.index[self._position(lo):self._position(hi)]

    def add(self, obj):
        """Add an obj to the index."""
        objhash = hash(obj)
        entry = (self.indexer(obj), objhash)
        if not self.index:
            self.index = [entry]
        # Do not insert duplicates
        elif entry in self.index:
            pass
        else:
            position = self._position(entry[0])
            self.index.insert(position, entry)

    def remove(self, obj):
        """Remove an obj from the index."""
        objhash = hash(obj)
        position = next(
            (
                i for (i, (val, key)) in enumerate(self.index)
                if key == objhash
            ),
            None,
        )
        if position:
            self.index.pop(position)

    def keys(self):
        return [val for (val, key) in self.index]


class Inventory(object):

    def __init__(self, items=None):
        self.item_hashes = {}
        self.item_counts = Counter()
        self.indices = {
            'name': CategoricalIndex(lambda it: it.name),
            'strength': QuantitativeIndex(lambda it: it.strength),
            'element': CategoricalIndex(
                lambda it: [
                    k for (k, v) in it.composition.elemental_dict.items()
                    if v != 0
                ]
            ),
            'type': CategoricalIndex(lambda it: it.__class__),
            'item': CategoricalIndex(lambda it: isinstance(it, item.Item)),
            'quality': QuantitativeIndex(lambda it: it.quality),
        }
        if items is not None:
            self.populate(items)

    def reified(self, index_computation):
        results = index_computation(self)
        return [self.item_hashes[r] for r in results]

    def add(self, it):
        self.item_counts[it] += 1
        self.item_hashes[hash(it)] = it
        for index in self.indices.values():
            index.add(it)

    def remove(self, it):
        if self.item_counts[it] < 1:
            pass
        elif self.item_counts[it] == 1:
            self.item_counts[it] -= 1
            self.item_hashes.pop(hash(it))
            for index in self.indices.values():
                index.remove(it)
        else:
            self.item_counts[it] -= 1

    def populate(self, items):
        for it in items:
            self.add(it)
