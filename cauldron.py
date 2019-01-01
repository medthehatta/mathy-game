#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


from cytoolz import merge


import elements
from common import average


#
# Constants
#


QUALITY_THRESH = 5


EXAMPLE_CAULDRON = {
    'strength': 4,
    'element_mastery': {
        'substance': 10,
        'absence': 5,
        'ardor': 3,
        'aegis': 3,
        'speed': 1,
        'stall': 1,
        'heal': 0,
        'wither': 0,
        'quintessence': 0,
        'void': 0,
        'fire': 0,
        'water': 0,
        'air': 0,
        'earth': 0,
        'light': 0,
        'shadow': 0,
    },
    # No status effect (meaning this cauldron works!)
    'status_effect': elements.e(0),
}


def item(x, quality=5, type_='potion'):
    return {'composition': x, 'quality': quality, 'type': type_}


def ash(x, quality):
    return item(x, quality, type_='ash')


EXAMPLE_BASE = item(1 + elements.FIRE)


EXAMPLE_ADDITIVE = item(elements.FIRE)


NOTHING = item(0, quality=0, type_='nothing')
BASE_POTION = item(elements.SUBSTANCE)
BASE_SWORD = item(elements.SUBSTANCE, type_='sword')


#
# Business
#


def mastery_of(cauldron, element):
    return cauldron['element_mastery'][element.lower()]


def strength_exceeded(cauldron, item):
    strength = cauldron['strength']
    if strength <= 0:
        raise ValueError(
            'Cauldron strength must be positive, but found: {}'.format(
                strength,
            ),
        )
    norm = item.norm()
    fields = {
        'item': item,
        'item_strength': norm,
        'cauldron_strength': strength,
        'deficit': norm - strength,
        'strength_fraction': strength / norm,
    }
    if norm > strength:
        return merge(fields, {'strength_exceeded': True})
    else:
        return merge(fields, {'strength_exceeded': False})


def mastery_exceeded(cauldron, item):
    masteries = [
        {
            'item': item,
            'element': el,
            'value': value,
            'mastery': mastery_of(cauldron, el),
            'deficit': value - mastery_of(cauldron, el),
            'mastery_fraction': mastery_of(cauldron, el) / max(value, 1),
            'status_effect': elements.e(**{el: value}),
        }
        for (el, value) in item.stat_dict().items()
    ]
    return [x for x in masteries if x['deficit'] > 0]


def get_quality(cauldron, composition):
    # The average mastery of the elements in the result, weighted by fraction
    return sum(mastery_of(cauldron, el)*composition[el] for el in composition)


def get_composition(result):
    # NOTE: we don't want the "norm" here; we literally want the sum of the
    # component magnitudes so we can see what "fraction" of the composition is
    # made of each component.  If we use norm, the sum of components won't be
    # 1.
    total_output = sum(abs(x) for x in result.components)
    return {
        element: abs(element_amount)/total_output
        for (element, element_amount) in result.stat_dict().items()
    }


def failure_work_result(**kwargs):
    return merge({'item': NOTHING, 'success': False}, kwargs)


def ash_result(result, quality, **kwargs):
    return merge({'item': ash(result, quality), 'success': False}, kwargs)


def detect_failure(cauldron, elements):
    exceeded_mastery = mastery_exceeded(cauldron, elements)
    if exceeded_mastery:
        return failure_work_result(
            exceeded_mastery=exceeded_mastery,
            new_cauldron=merge(
                cauldron,
                {
                    'status_effect': sum(
                        m['status_effect'] for m in exceeded_mastery
                    ),
                }
            ),
        )
    exceeds_strength = strength_exceeded(cauldron, elements)
    if exceeds_strength['strength_exceeded']:
        return failure_work_result(exceeded_strength=exceeds_strength)
    # Otherwise
    return None


def work(cauldron, base, additive, capture_substance=False):
    # TODO: We should check for failure from base and additives as soon as
    # they're added, not once they're "cooked"
    bases = base.get('composition')
    base_quality = base.get('quality')

    failed_base = detect_failure(cauldron, bases)
    if failed_base:
        return failed_base

    additives = additive.get('composition')
    additive_quality = additive.get('quality')

    failed_additives = detect_failure(cauldron, additives)
    if failed_additives:
        return failed_additives

    # Calculate the resulting stats
    result = bases*additives

    failed_result = detect_failure(cauldron, result)
    if failed_result:
        return failed_result

    composition = get_composition(result)
    quality = average(
        base_quality,
        additive_quality,
        get_quality(cauldron, composition),
    )

    # If the thing we made has trash quality, it turns to ash
    if quality < QUALITY_THRESH:
        return ash_result(result, quality)

    # If we made it here, we had mastery over the ingredients and result, so we
    # actually produce something
    new_element_masteries = {
        k: v + composition.get(k.upper(), 0)
        for (k, v) in cauldron['element_mastery'].items()
    }
    if capture_substance:
        substance_produced = result.SUBSTANCE
        result = result - substance_produced*elements.SUBSTANCE
    else:
        substance_produced = 0
        result = result
    return {
        'item': merge(base, {'composition': result, 'quality': quality}),
        'substance_produced': substance_produced*elements.SUBSTANCE,
        'strength': result.norm(),
        'success': True,
        'new_cauldron': merge(
            cauldron,
            {'element_mastery': new_element_masteries},
        ),
    }


def affect_cauldron(cauldron, additive):
    status_effect = cauldron['status_effect']
    additive_composition = additive['composition']

    result = status_effect*additive_composition

    # If we got "close enough", remove the effect
    if result.SUBSTANCE / sum(result.components) > 0.9:
        result = elements.e(0)

    return merge(cauldron, {'status_effect': result})
