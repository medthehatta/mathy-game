#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import random


import elements


#
# Constants
#


#
# Helpers
#


def random_concoction():
    # Available elements
    available_elements = [
        elements.SUBSTANCE,
        elements.SUBSTANCE,
        elements.SUBSTANCE,
        elements.SUBSTANCE,
        elements.SUBSTANCE,
        elements.ARDOR,
        elements.SPEED,
        elements.FLOURISH,
        elements.QUINTESSENCE,
        elements.FIRE,
        elements.AIR,
        elements.LIGHT,
    ]
    coefficients = [
        -2, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2,
    ]
    composition_components = [random.choice(coefficients) for _ in range(3)]
    composition_elements = [
        random.choice(available_elements) for _ in range(3)
    ]
    composition = sum(
        (c*e for (c, e) in zip(composition_components, composition_elements)),
        elements.NOTHING,
    )
    return composition


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

    quality = random.randint(50, 100)
    return klass(composition, quality)


def random_items(n=20):
    result = [random_item() for _ in range(n)]
    for (i, item) in enumerate(result):
        print('{0:02}  {1}'.format(i, item))
    return result


#
# Classes
#


class Material(object):
    """A material that can be manipulated."""

    def __init__(
        self,
        composition=elements.SUBSTANCE,
        quality=50,
        recipe=None,
        name=None,
    ):
        self.composition = composition
        self.quality = quality
        self.recipe = recipe
        self.name = name or 'unnamed'

    @property
    def strength(self):
        return self.composition.norm()

    def __repr__(self):
        return '<{} ({}) | {} | q={}>'.format(
            type(self).__name__,
            self.name,
            self.composition,
            self.quality,
        )


class Nothing(Material):
    """The null material."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.composition = elements.NOTHING
        self.quality = 0


class Ash(Material):
    """A material with such outrageously low quality it no longer functions."""


class Item(Material):
    """A material that can be used in some way (other than crafting)."""


class Sword(Item):
    """An item which inflicts damage at close range."""


class Bomb(Item):
    """An item which inflicts damage at long range."""


class Shield(Item):
    """An item which inhibits damage."""


class Elixir(Item):
    """An item which is consumed by the user to enact various effects."""
