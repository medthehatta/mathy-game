#!/usr/bin/env python
# coding: utf-8


"""Elemental stuff modeled as octonions."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import elements
from common import merge, average


#
# Constants
#


EXAMPLE_CAULDRON = {
    'toughness': 5,
    'element_mastery': {
        'substance': 10,
        'absence': 5,
        'ardor': 3,
        'aegis': 3,
        'speed': 3,
        'stall': 3,
        'heal': 3,
        'wither': 3,
        'quintessence': 3,
        'void': 3,
        'fire': 3,
        'water': 3,
        'air': 3,
        'earth': 3,
        'light': 3,
        'shadow': 3,
    },
}


EXAMPLE_BASE = {
    'elements': 1 + elements.FIRE,
    'quality': 5,
    'type': 'potion',
}


def additive(x):
    return {'elements': x, 'quality': 5}


EXAMPLE_ADDITIVE = additive(elements.FIRE)


#
# Business
#


def mastery_of(cauldron, element):
    return cauldron['element_mastery'][element.lower()]


def toughness_exceeded(cauldron, item):
    toughness = cauldron['toughness']
    if toughness <= 0:
        raise ValueError(
            'Cauldron toughness must be positive, but found: {}'.format(
                toughness,
            ),
        )
    norm = item.norm()
    if norm > toughness:
        return {
            'item': item,
            'toughness_exceeded': True,
            'magnitude': norm,
            'toughness': toughness,
            'deficit': norm - toughness,
            'toughness_fraction': norm / toughness,
        }
    else:
        return {
            'item': item,
            'toughness_exceeded': False,
            'magnitude': norm,
            'toughness': toughness,
            'deficit': norm - toughness,
            'toughness_fraction': norm / toughness,
        }


def mastery_exceeded(cauldron, item):
    masteries = [
        {
            'item': item,
            'element': el,
            'value': value,
            'mastery': mastery_of(cauldron, el),
            'deficit': value - mastery_of(cauldron, el),
            'mastery_fraction': value / max(mastery_of(cauldron, el), 1),
        }
        for (el, value) in item.stat_dict().items()
    ]
    return [x for x in masteries if x['deficit'] > 0]


def _quality(cauldron, composition):
    # The average mastery of the elements in the result, weighted by fraction
    res = sum(
        mastery_of(cauldron, el)*composition[el]
        for el in composition
    )
    return res


def _composition(result):
    # The "composition" of the mixture
    total_output = sum(abs(x) for x in result.components)
    result_dict = result.stat_dict()
    return {
        el: abs(result_dict[el])/total_output
        for el in result_dict
    }


def work(cauldron, base, additive, capture_substance=False):
    bases = base.get('elements')
    base_quality = base.get('quality')
    exceeded_base_mastery = mastery_exceeded(cauldron, bases)
    if exceeded_base_mastery:
        return {
            'item': merge(base, {'elements': elements.e(0)}),
            'quality': 0,
            'success': False,
            'exceeded_mastery': exceeded_base_mastery,
        }
    base_exceeds_toughness = toughness_exceeded(cauldron, bases)
    if base_exceeds_toughness['toughness_exceeded']:
        return {
            'item': merge(base, {'elements': elements.e(0)}),
            'quality': 0,
            'success': False,
            'exceeded_toughness': base_exceeds_toughness,
        }

    additives = additive.get('elements')
    additive_quality = additive.get('quality')
    exceeded_additive_mastery = mastery_exceeded(cauldron, additives)
    if exceeded_additive_mastery:
        return {
            'item': merge(base, {'elements': elements.e(0)}),
            'quality': 0,
            'success': False,
            'exceeded_mastery': exceeded_additive_mastery,
        }
    additive_exceeds_toughness = toughness_exceeded(cauldron, additives)
    if additive_exceeds_toughness['toughness_exceeded']:
        return {
            'item': merge(additive, {'elements': elements.e(0)}),
            'quality': 0,
            'success': False,
            'exceeded_toughness': additive_exceeds_toughness,
        }

    # Calculate the resulting stats
    result = bases*additives

    exceeded_result_mastery = mastery_exceeded(cauldron, result)
    if exceeded_result_mastery:
        return {
            'item': merge(base, {'elements': elements.e(0)}),
            'quality': 0,
            'success': False,
            'exceeded_mastery': exceeded_result_mastery,
        }
    result_exceeds_toughness = toughness_exceeded(cauldron, result)
    if result_exceeds_toughness['toughness_exceeded']:
        return {
            'item': merge(result, {'elements': elements.e(0)}),
            'quality': 0,
            'success': False,
            'exceeded_toughness': result_exceeds_toughness,
        }

    # If we made it here, we had mastery over the ingredients and result, so we
    # actually produce something
    composition = _composition(result)
    mastery_increases = {k: v for (k, v) in composition.items() if v}
    if capture_substance:
        substance_produced = result.SUBSTANCE
        result = result - substance_produced*elements.SUBSTANCE
    else:
        substance_produced = 0
        result = result
    return {
        'item': merge(base, {'elements': result}),
        'substance_produced': substance_produced,
        'magnitude': result.norm(),
        'quality': average(
            base_quality,
            additive_quality,
            _quality(cauldron, composition),
        ),
        'success': True,
        'mastery_increases': mastery_increases,
        'new_cauldron': merge(
            cauldron,
            {
                'element_mastery': {
                    k: v + mastery_increases.get(k.upper(), 0)
                    for (k, v) in cauldron['element_mastery'].items()
                },
            },
        ),
    }


def work_multiple(cauldron, base, additives, **kwargs):
    results = {
        'initial_cauldron': cauldron,
        'base': base,
        'additives': additives,
        'outcomes': [],
    }
    for additive in additives:
        found = work(cauldron, base, additive, **kwargs)
        results['outcomes'].append(found)
        if found['success'] is False:
            return results
        base = found['item']
        cauldron = found['new_cauldron']

    # When done with the additives, return results
    return results
