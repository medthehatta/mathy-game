#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import octonion
import json
from cytoolz import merge, keymap, valmap


#
# Constants
#


OPPOSING_ELEMENTS = [
    # positive, negative,      # octonion component
    # --------- -------------- # ------------------
    ('substance', 'absence'),  # 1
    ('ardor', 'aegis'),        # i
    ('speed', 'stall'),        # j
    ('flourish', 'wither'),    # k
    ('quintessence', 'void'),  # l
    ('fire', 'water'),         # il
    ('air', 'earth'),          # ij
    ('light', 'shadow'),       # ik
]


#
# Helpers
#


def coefficient_type(x):
    return round(float(x), 3)


def octonion_to_elemental_dict(octo):
    octonion_component_relations = zip(octo.components, OPPOSING_ELEMENTS)
    mappings = [
        {positive: x if x >= 0 else 0, negative: -x if x < 0 else 0}
        for (x, (positive, negative)) in octonion_component_relations
    ]
    mapping = merge(*mappings)
    return valmap(coefficient_type, keymap(lambda x: x.upper(), mapping))


def elemental_dict_to_octonion(elemental_dict):
    components = [
        (
            elemental_dict.get(positive.upper(), 0) -
            elemental_dict.get(negative.upper(), 0)
        )
        for (positive, negative) in OPPOSING_ELEMENTS
    ]
    return octonion.Octonion(*components)


#
# Class
#


class ElementalOctonion(octonion.Octonion):

    def __init__(self, R=0, I=0, J=0, K=0, L=0, IL=0, JL=0, KL=0, **kwargs):  # noqa
        input_octonion = octonion_to_elemental_dict(
            octonion.Octonion(R, I, J, K, L, IL, JL, KL),
        )
        # The elemental dict with all kwargs, including nonsensical crap
        raw_elemental_dict = merge(
            input_octonion,
            keymap(lambda x: x.upper(), kwargs),
        )
        # Instantiate this as an octonion with the appropriate components
        octo = elemental_dict_to_octonion(raw_elemental_dict)
        super().__init__(*octo.components)
        # Recreate the elemental dict, respecting only legit elements (throwing
        # out the nonsensical crap from kwargs)
        self.elemental_dict = octonion_to_elemental_dict(octo)

    def project(self, element):
        return self.elemental_dict.get(element.upper(), 0)

    def __getattr__(self, attr):
        if attr.upper() in self.elemental_dict:
            return self.project(attr.upper())
        else:
            raise AttributeError(
                "'{}' object has no attribute '{}'".format(
                    type(self).__name__,
                    attr,
                ),
            )

    def __repr__(self):
        component_strings = [
            (
                '{}'.format(element) if component == 1 else
                '-{}'.format(element) if component == -1 else
                '{} {}'.format(component, element)
            )
            for (element, component) in self.elemental_dict.items()
            if component != 0
        ]
        return ' + '.join(component_strings)

    def __str__(self):
        stats = self.elemental_dict()
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
