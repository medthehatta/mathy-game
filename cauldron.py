#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import elements
import item
from common import average


#
# Constants
#


# If your cauldron has mastery of an element at the MASTERY_COMPETENCE level,
# concoctions containing only that element will have a base quality of 50%.
MASTERY_COMPETENCE = 10


# If the concoction quality is below MAX_ASH_QUALITY, it will yield Ash instead
# of a usable item.
MAX_ASH_QUALITY = 30


# Cauldrons are not directly vulnerable to SUBSTANCE.  Instead, they get a
# negative SUBSTANCE effect (rendering the cauldron unusable until fixed) if
# the total STRENGTH of the concoction exceeds the cauldron strength.
DEFAULT_CAULDRON_STRENGTH = 10


DEFAULT_MASTERIES = {
    elements.SUBSTANCE: 10,
    elements.ABSENCE: 1,
    elements.ARDOR: 5,
    elements.AEGIS: 5,
    elements.SPEED: 2,
    elements.STALL: 2,
    elements.FLOURISH: 0,
    elements.WITHER: 0,
    elements.QUINTESSENCE: 0,
    elements.VOID: 0,
    elements.FIRE: 0,
    elements.WATER: 0,
    elements.AIR: 0,
    elements.EARTH: 0,
    elements.LIGHT: 0,
    elements.SHADOW: 0,
}


#
# Helpers
#


def sigmoid_percent(x, fifty_pct=1):
    x_norm = x/fifty_pct
    fraction = x_norm / (1 + abs(x_norm))
    return 100*fraction


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
        if concoction.norm() > self.strength:
            self.effect = concoction.strength*elements.SUBSTANCE
            return True
        else:
            return False

    def _insufficient_mastery_for(self, concoction):
        concoction_mastery = {
            element: (
                self.masteries[element] - concoction.get_component(element)
            )
            for element in self.masteries
            # Cauldrons are not vulnerable to SUBSTANCE by itself, but rather
            # to the total strength of the concoction.  So we skip
            # SUBSTANCE-specific vulnerability.
            if element is not elements.SUBSTANCE
        }
        if any(component < 0 for component in concoction_mastery.values()):
            mastery_deficit = sum(
                (-deficit)*element
                for (element, deficit) in concoction_mastery.items()
                if deficit < 0
            )
            self.effect = mastery_deficit
            return True
        else:
            return False

    def _mastery_against(self, concoction):
        # want the "magnitude" of our masteries parallel to the concoction
        # (weighted by the relative magnitudes of the concoction's components)
        #
        # I.E., want:
        #
        #    (masteries) . (unit vector parallel to concoction)
        #    (masteries) . (concoction / concoction.norm())
        #
        normalized_concoction = concoction / concoction.norm()
        return sum(
            self.masteries[k]*normalized_concoction.get_component(k)
            for k in self.masteries
        )

    def _update_masteries(self, concoction):
        total_concoction = sum(abs(x) for x in concoction.components)
        normalized = concoction / total_concoction
        self.masteries = {
            k: self.masteries[k] + normalized.get_component(k)
            for k in self.masteries
        }

    def concoct(self, base, additive):
        if isinstance(base, (item.Nothing, item.Ash)):
            raise TypeError('Cannot concoct with Nothing or Ash')
        if isinstance(additive, (item.Nothing, item.Ash)):
            raise TypeError('Cannot concoct with Nothing or Ash')

        if self._insufficient_strength_for(additive.composition):
            return item.Nothing()

        if self._insufficient_mastery_for(additive.composition):
            return item.Nothing()

        result_composition = base.composition*additive.composition

        if self._insufficient_strength_for(result_composition):
            return item.Nothing()

        if self._insufficient_mastery_for(result_composition):
            return item.Nothing()

        result_mastery = sigmoid_percent(
            self._mastery_against(result_composition),
            fifty_pct=MASTERY_COMPETENCE,
        )
        quality = average(
            base.quality,
            additive.quality,
            # Double the weight of the result in computing the quality
            result_mastery,
            result_mastery,
        )

        # If the thing we made has trash quality, it turns to ash and does not
        # contribute to our masteries.
        if quality < MAX_ASH_QUALITY:
            return item.Ash(result_composition, quality)

        # If we made it here, we had mastery over the ingredients and result,
        # so we actually (1) produce something of value, and (2) improve our
        # masteries of the elements in the result
        result = base.__class__(
            result_composition,
            quality,
            recipe=[base, additive],
        )
        self._update_masteries(result_composition)

        return result

    def fix(self, agent):
        result = self.composition*agent.composition

        # If we got "close enough", remove the effect
        if result.SUBSTANCE / sum(abs(x) for x in result.components) > 0.9:
            self.effect = elements.NOTHING
            return True
        else:
            return False
