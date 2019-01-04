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


def walk_recipe(substance):
    if substance.recipe is None:
        return [substance]
    else:
        (base, additive) = substance.recipe
        return [base] + walk_recipe(base) + [additive] + walk_recipe(additive)


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


class Material(object):
    """A material that can be manipulated."""

    def __init__(
        self,
        composition=elements.SUBSTANCE,
        quality=50,
        mass=1,
        recipe=None,
        name=None,
    ):
        self.composition = composition
        self.quality = quality
        self.mass = mass
        self.recipe = recipe
        self._name = name

    @property
    def strength(self):
        return self.composition.norm()

    @property
    def name(self):
        return self._name or 'unnamed'

    def walk_recipe(self):
        return walk_recipe(self)

    def __repr__(self):
        return '<{0} ({1}) | {2} | m={3}, q={4}>'.format(
            type(self).__name__,
            self.name,
            self.composition,
            self.mass,
            round(self.quality, 2),
        )

    def __hash__(self):
        return hash(
            (
                self.__class__,
                self.name,
                tuple(self.composition.components),
                self.quality,
            )
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
