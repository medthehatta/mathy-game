#!/usr/bin/env python
# coding: utf-8


"""Harness."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


from cytoolz import unique, partition_all, reduce


import elements as el
import cauldron
import inventory
import textui as ui


my_inventory = inventory.Inventory()
my_cauldron = cauldron.Cauldron()


def bar(percent, pips=10):
    full = int(percent/100 * pips)
    bar = '|' + '='*(full - 1) + (']' if full else '') + '.'*(pips - full)
    return ui.block(bar)


def reversed_bar(percent, pips=10):
    full = int(percent/100 * pips)
    bar = '.'*(pips - full) + ('[' if full else '') + '='*(full - 1) + '|'
    return ui.block(bar)


def left_kv(pairs):
    keys = [k for (k, v) in pairs]
    values = [v for (k, v) in pairs]
    return (
        ui.block(*[k.lower() + ' ' for k in keys]) +
        ui.block(*values)
    )


def material_card(material, id_=None, count=None, known=None):
    known = list(
        unique(['substance', 'absence', 'ardor', 'aegis'] + (known or []))
    )

    title = '{} ({})'.format(material.__class__.__name__, material.name)
    title_block = ui.block(title, '-'*len(title))

    id_block = ui.block('id: {:03d}'.format(id_) if id_ else '')
    count_block = ui.block('n: {:03d}'.format(count) if count else '')

    stat_block = left_kv(
        ('quality', material.quality),
        ('mass', material.mass),
    )

    present_elements = [
        (positive, negative)
        for (component, (positive, negative))
        in zip(material.composition.components, el.OPPOSING_ELEMENTS)
        if positive in known or negative in known or component != 0
    ]

    positives = [
        p.upper() if p in known else '??' for (p, n) in present_elements
    ]
    negatives = [
        n.upper() if n in known else '??' for (p, n) in present_elements
    ]

    positives_block = ui.rblock(*positives)
    negatives_block = ui.lblock(*negatives)

    positives_bars = [
        reversed_bar(100*material.composition.get_component(p)/10)
        for (p, n) in present_elements
    ]
    negatives_bars = [
        bar(100*material.composition.get_component(n)//10)
        for (p, n) in present_elements
    ]

    stats_block = (
        positives_block +
        ui.block(*positives_bars) +
        ui.block(*negatives_bars) +
        negatives_block
    )

    header = (
        (title_block / ui.space() / stat_block) +
        ui.space(width=25) +
        (id_block / count_block)
    )

    card_contents = ui.vadjoin(
        (header / ui.space()),
        (stats_block / ui.space()),
        align='center',
    )
    return ui.in_box(card_contents)


def arrayed(items, single_item_display, columns=2, **kwargs):
    rows = partition_all(columns, enumerate(items, 1))
    row_elements = [
        reduce(
            lambda acc, x: acc + x,
            [single_item_display(m, id_=i, **kwargs) for (i, m) in row],
        )
        for row in rows
    ]
    return reduce(lambda acc, x: acc / x, row_elements)
