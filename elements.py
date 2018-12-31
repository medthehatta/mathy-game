#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import octonion
import json
from fractions import Fraction


#
# Constants
#


# (see "Constants (1)" and "Constants (2)" near bottom)


#
# Helpers
#


def flatten(lst):
    return sum(lst, [])


def merge(dict1, dict2):
    all_keys = set.union(set(dict1.keys()), set(dict2.keys()))
    return {k: dict2.get(k, dict1.get(k)) for k in all_keys}


class Opposites(object):

    def __init__(self, positive_name, negative_name):
        self.positive = positive_name.upper()
        self.negative = negative_name.upper()
        self.allowed_keys = {self.positive, self.negative}

    def value_to_tuple(self, x):
        return (
            (x, 0) if x > 0 else
            (0, -x) if x < 0 else
            (0, 0)
        )

    def value_to_labeled(self, x):
        (positive, negative) = self.value_to_tuple(x)
        return {self.positive: positive, self.negative: negative}

    def from_positive_negative(self, positive=0, negative=0):
        # We can't tolerate accepting a negative "negative" value.
        # Double-negative?  Gimme a break, man.
        if negative < 0:
            raise ValueError('Negative value is itself negative!')

        # Handle the weird "convenience" case next: they passed both positive
        # AND negative.  Perform the subtraction and come to a total.
        elif positive and negative:
            return positive - negative

        # Only positive (or they're both zero)
        elif not negative:
            return positive

        # The only other possibility is we're given a (strictly positive) value
        # for the "negative" field.
        else:
            return -negative

    def from_tuple(self, tup):
        (positive, negative) = tup
        return self.from_positive_negative(positive, negative)

    def from_labeled(self, dic):
        fixed_dict = {k.upper(): v for (k, v) in dic.items()}
        positive = fixed_dict.get(self.positive, 0)
        negative = fixed_dict.get(self.negative, 0)
        return self.from_positive_negative(positive, negative)

    def positive_only(self, val):
        (positive, negative) = self.value_to_tuple(val)
        return positive

    def negative_only(self, val):
        (positive, negative) = self.value_to_tuple(val)
        return negative


#
# Constants (1)
#


SUBSTANCE_DUO = Opposites('SUBSTANCE', 'ABSENCE')
ABSENCE_DUO = SUBSTANCE_DUO
ARDOR_DUO = Opposites('ARDOR', 'AEGIS')
AEGIS_DUO = ARDOR_DUO
SPEED_DUO = Opposites('SPEED', 'STALL')
STALL_DIO = SPEED_DUO
HEAL_DUO = Opposites('HEAL', 'WITHER')
WITHER_DUO = HEAL_DUO
QUINTESSENCE_DUO = Opposites('QUINTESSENCE', 'VOID')
VOID_DUO = QUINTESSENCE_DUO
FIRE_DUO = Opposites('FIRE', 'WATER')
WATER_DUO = FIRE_DUO
AIR_DUO = Opposites('AIR', 'EARTH')
EARTH_DUO = AIR_DUO
LIGHT_DUO = Opposites('LIGHT', 'SHADOW')
SHADOW_DUO = LIGHT_DUO


DUOS = [
    SUBSTANCE_DUO,
    ARDOR_DUO,
    SPEED_DUO,
    HEAL_DUO,
    QUINTESSENCE_DUO,
    AIR_DUO,
    FIRE_DUO,
    LIGHT_DUO,
]


#
# Class
#


class ElementalOctonion(octonion.Octonion):

    def __init__(self, R=0, I=0, J=0, K=0, L=0, IL=0, JL=0, KL=0, **kwargs):  # noqa
        input_dict = merge(
            {
                'SUBSTANCE': Fraction(R),
                'ARDOR': Fraction(I),
                'SPEED': Fraction(J),
                'HEAL': Fraction(K),
                'QUINTESSENCE': Fraction(L),
                'AIR': Fraction(IL),
                'FIRE': Fraction(JL),
                'LIGHT': Fraction(KL),
            },
            kwargs,
        )
        self.substance = SUBSTANCE_DUO.from_labeled(input_dict)
        self.ardor_aegis = ARDOR_DUO.from_labeled(input_dict)
        self.speed_stall = SPEED_DUO.from_labeled(input_dict)
        self.heal_wither = HEAL_DUO.from_labeled(input_dict)
        self.quintessence = QUINTESSENCE_DUO.from_labeled(input_dict)
        self.air_earth = AIR_DUO.from_labeled(input_dict)
        self.fire_water = FIRE_DUO.from_labeled(input_dict)
        self.light_shadow = LIGHT_DUO.from_labeled(input_dict)
        self.stats = flatten(
            [[duo.positive, duo.negative] for duo in DUOS]
        )
        super().__init__(
            R=self.substance,
            I=self.ardor_aegis,  # noqa
            J=self.speed_stall,
            K=self.heal_wither,
            L=self.quintessence,
            IL=self.air_earth,
            JL=self.fire_water,
            KL=self.light_shadow,
        )

    @property
    def SUBSTANCE(self):
        return SUBSTANCE_DUO.positive_only(self.substance)

    @property
    def ABSENCE(self):
        return SUBSTANCE_DUO.negative_only(self.substance)

    @property
    def ARDOR(self):
        return ARDOR_DUO.positive_only(self.ardor_aegis)

    @property
    def AEGIS(self):
        return ARDOR_DUO.negative_only(self.ardor_aegis)

    @property
    def SPEED(self):
        return SPEED_DUO.positive_only(self.speed_stall)

    @property
    def STALL(self):
        return SPEED_DUO.negative_only(self.speed_stall)

    @property
    def HEAL(self):
        return HEAL_DUO.positive_only(self.heal_wither)

    @property
    def WITHER(self):
        return HEAL_DUO.negative_only(self.heal_wither)

    @property
    def QUINTESSENCE(self):
        return QUINTESSENCE_DUO.positive_only(self.quintessence)

    @property
    def VOID(self):
        return QUINTESSENCE_DUO.negative_only(self.quintessence)

    @property
    def FIRE(self):
        return FIRE_DUO.positive_only(self.fire_water)

    @property
    def WATER(self):
        return FIRE_DUO.negative_only(self.fire_water)

    @property
    def AIR(self):
        return AIR_DUO.positive_only(self.air_earth)

    @property
    def EARTH(self):
        return AIR_DUO.negative_only(self.air_earth)

    @property
    def LIGHT(self):
        return LIGHT_DUO.positive_only(self.light_shadow)

    @property
    def SHADOW(self):
        return LIGHT_DUO.negative_only(self.light_shadow)

    def stat_dict(self):
        return {k: getattr(self, k) for k in self.stats}

    def __str__(self):
        stats = self.stat_dict()
        return json.dumps({k: str(v) for (k, v) in stats.items() if v})


def e(*args, **kwargs):
    return ElementalOctonion(*args, **kwargs)


#
# Constants (2)
#


# Reals...
SUBSTANCE = e(SUBSTANCE=1)
ABSENCE = e(ABSENCE=1)

# ... extend to complex numbers...
ARDOR = e(ARDOR=1)
AEGIS = e(AEGIS=1)

# ... extend to quaternions...
SPEED = e(SPEED=1)
STALL = e(STALL=1)

HEAL = e(HEAL=1)
WITHER = e(WITHER=1)

# ... extend to octonions...
QUINTESSENCE = e(QUINTESSENCE=1)
VOID = e(VOID=1)

FIRE = e(FIRE=1)
WATER = e(WATER=1)

AIR = e(AIR=1)
EARTH = e(EARTH=1)

LIGHT = e(LIGHT=1)
SHADOW = e(SHADOW=1)
