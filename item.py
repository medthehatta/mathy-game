#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import random


import elements
from material import Material, Nothing, Ash, random_concoction


#
# Constants
#


#
# Helpers
#


def random_item():
    invalid_item_types = [Nothing, Ash]
    valid_item_types = [
        cls for cls in Item.__subclasses__()
        if cls not in invalid_item_types
    ]
    klass = random.choice(valid_item_types)

    composition = elements.NOTHING
    while composition == elements.NOTHING:
        composition = random_concoction()

    quality = random.randint(50, 99)
    return klass(composition, quality)


def random_items(n=20):
    result = [random_item() for _ in range(n)]
    for (i, item) in enumerate(result):
        print('{0:02}  {1}'.format(i, item))
    return result


#
# Classes
#


class Item(Material):
    """A material that can be used in some way (other than crafting)."""

    def element_activity(self, element):
        # int() is used to round down the component
        # If the component magnitude is less than 1, it is inert
        return int(self.composition.get_component(element))

    def strength_augmented_by(self, element):
        return (1 + self.element_activity(element))*self.strength


class Weapon(Item):
    """An item which inflicts damage."""

    @property
    def damage(self):
        return self.strength_augmented_by('ardor')

    def range(self):
        # Range '1' is melee distance
        return 1


class Melee(Weapon):
    """An item which inflicts damage at close range."""


class Ranged(Weapon):
    """An item which inflicts damage at range."""

    @property
    def range(self):
        # int() is used to round down the component
        # If the component magnitude is less than 1, it is inert
        return 2 + int(self.composition.get_component('air'))


class Armor(Item):
    """An item which inhibits damage."""

    @property
    def defense(self):
        return self.strength_augmented_by('aegis')


class Elixir(Item):
    """An item which is consumed by the user to enact various effects."""
