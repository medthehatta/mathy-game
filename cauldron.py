#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


from cytoolz import merge


import elements
import item
from common import average


#
# Constants
#


DEFAULT_CAULDRON_STRENGTH = 10


DEFAULT_MASTERIES = elements.e(
    SUBSTANCE=10,
    ABSENCE=1,
    ARDOR=3,
    AEGIS=3,
    SPEED=2,
    STALL=2,
    FLOURISH=0,
    WITHER=0,
    QUINTESSENCE=0,
    VOID=0,
    FIRE=0,
    WATER=0,
    AIR=0,
    EARTH=0,
    LIGHT=0,
    SHADOW=0,
)


#
# Classes
#


class Cauldron(object):

    def __init__(
        self,
        strength=DEFAULT_CAULDRON_STRENGTH,
        masteries=DEFAULT_MASTERIES,
        effect=elements.NOTHING,
    ):
        self.strength = strength
        self.masteries = masteries
        self.effect = effect

    def _insufficient_strength_for(self, concoction):
        if concoction.strength > self.strength:
            self.effect = concoction.strength*elements.SUBSTANCE
            return True
        else:
            return False

    def _insufficient_mastery_for(self, concoction):
        concoction_mastery = self.masteries - concoction
        if any(component < 0 for component in concoction_mastery.components):
            # The effect is gonna come from all the non-substance components
            self.effect = concoction - concoction.R
            return True
        else:
            return False

    def _mastery_against(self, concoction):
        return (self.mastery*concoction.inverse()).norm()

    def craft(self, base, additive):
        if self._insufficient_strength_for(additive):
            return item.Nothing()

        if self._insufficient_mastery_for(additive):
            return item.Nothing()

        result_composition = base.composition*additive.composition

        if self._insufficient_strength_for(result_composition):
            return item.Nothing()

        if self._insufficient_mastery_for(result_composition):
            return item.Nothing()

        result_mastery = self._mastery_against(result_composition)
        quality = average(
            base.quality,
            additive.quality,
            # Double the weight of the result in computing the quality
            result_mastery,
            result_mastery,
        )

        # If the thing we made has trash quality, it turns to ash and does not
        # contribute to our masteries.
        if quality < 40:
            return item.Ash(result_composition, quality)

        # If we made it here, we had mastery over the ingredients and result,
        # so we actually (1) produce something of value, and (2) improve our
        # masteries of the elements in the result
        result = base.__class__(result_composition, quality)
        self.masteries += result_composition/result_composition.norm()

        return result


#
# Business
#


def affect_cauldron(cauldron, additive):
    status_effect = cauldron['status_effect']
    additive_composition = additive['composition']

    result = status_effect*additive_composition

    # If we got "close enough", remove the effect
    if result.SUBSTANCE / sum(result.components) > 0.9:
        result = elements.e(0)

    return merge(cauldron, {'status_effect': result})
