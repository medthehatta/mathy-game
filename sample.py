#!/usr/bin/env python
# coding: utf-8


"""Harness."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import math
import random
import pickle
from cytoolz import unique, partition_all, reduce
import fractions
import os


import numpy as np
import matplotlib.pyplot as plt
from plotly.offline import (
    plot as plotly_plot,
    iplot as plotly_iplot,
)
import plotly.graph_objs as go


import material
import elements as el
import cauldron
import inventory
import textui as ui
import octonion


from common import average


my_inventory = inventory.Inventory()
my_cauldron = cauldron.Cauldron()


# TODO
def list_inventory(inventory):
    materials = sorted(
        inventory.item_hashes.values(),
        key=lambda m: (m.__class__, m.quality, m.mass, m.name),
    )
    widest_type = max(len(m.__class__.__name__) for m in materials)
    # WIP...
    for type_ in inventory.indices['type'].keys():
        materials = inventory.reified(sorted(i.indices['type'].lookup(type_)))
        for material in materials:
            amount = inventory.item_counts[material]


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


def trial(raws, exponent, trials=100):
    return [
        reduce(
            lambda acc, x: acc*x,
            [random.choice(raws) for _ in range(exponent)],
        )
        for _ in range(trials)
    ]


def cauldron_can_make(caul, substance):
    return not (
        caul._insufficient_mastery_for(substance) or
        caul._insufficient_strength_for(substance)
    )


def foo():
    caul = cauldron.Cauldron()

    try:
        with open('/tmp/raws', 'rb') as f:
            raws = pickle.load(f)
    except (OSError, EOFError):
        raws = material.all_raw_compositions()
        with open('/tmp/raws', 'wb') as f:
            pickle.dump(raws, f)

    all_pairs = [x*y for x in raws for y in raws]
    craftable = [x for x in all_pairs if cauldron_can_make(caul, x)]
    return (raws, all_pairs, craftable)


def analyze(concoctions):
    complexities = [len([x for x in c.components if x]) for c in concoctions]
    gross_complexities = [
        len([x for x in c.components if x >= 1]) for c in concoctions
    ]
    return {
        'avg_complexity': average(complexities),
        'avg_gross_complexity': average(gross_complexities),
    }


def fraction_of_right(x, y):
    return (math.pi/2) / (math.atan(y/x))


def frac(numerator, denomenator=1):
    return fractions.Fraction(numerator, denomenator)


def iterated_products(generators, n):
    products = generators
    recent = generators
    for _ in range(n, 0, -1):
        products = list(set(x*y for x in recent for y in generators))
        recent = products
    return products


def plot_complex_octs(octs, path='/tmp/foo.png', proj=lambda oc: [oc.R, oc.I], **kwargs):
    x_ys = np.array([proj(oct_) for oct_ in octs])
    plt.scatter(*x_ys.T, **kwargs)
    plt.xlim([-10, 10])
    plt.ylim([-10, 10])
    plt.axes().set_aspect('equal')
    plt.savefig(path)


def plot_complex_octs_from_gens(gens, limit=10, path='/tmp/foo.png'):
    plt.cla()
    plt.title(gens)
    for i in range(limit, 1, -1):
        plot_complex_octs(iterated_products(gens, i))
    plot_complex_octs(iterated_products(gens, 0), path=path, marker="P")


def random_complex_gens(max_=4, num=4):
    return [
        (
            random.choice([1, -1])*frac(random.randint(1, max_), random.randint(1, max_))*octonion.oR +  # noqa
            random.choice([1, -1])*frac(random.randint(1, max_), random.randint(1, max_))*octonion.oI  # noqa
        )
        for _ in range(num)
    ]


def random_quaternion_gens(max_=4, num=4):
    return [
        (
            random.choice([1, -1])*frac(random.randint(1, max_), random.randint(1, max_))*octonion.oI +  # noqa
            random.choice([1, -1])*frac(random.randint(1, max_), random.randint(1, max_))*octonion.oJ +  # noqa
            random.choice([1, -1])*frac(random.randint(1, max_), random.randint(1, max_))*octonion.oK  # noqa
        )
        for _ in range(num)
    ]


def random_nearly_unit_complex_gens(max_=4, num=4):
    return [
        (
            rational_near_unity(max_)*octonion.oR +
            rational_near_unity(max_)*octonion.oI
        )
        for _ in range(num)
    ]


def random_nearly_unit_quaternion_gens(max_=4, num=4):
    return [
        (
            rational_near_unity(max_)*octonion.oR +
            rational_near_unity(max_)*octonion.oI +
            rational_near_unity(max_)*octonion.oJ
        )
        for _ in range(num)
    ]


def rational_near_unity(max_=10):
    denom = random.randint(1, max_)
    sign = random.choice([1, -1])
    diff = random.choice([1, -1])
    return sign*(denom + diff)/(denom)


def proj(projletters):
    pup = projletters.upper()
    def _proj(oc):
        return [
            float(x)
            for x in [getattr(oc, p) for p in pup]
        ]
    return _proj


def plot_quaternion_octs(octs, projection=None, **kwargs):
    projection = projection or (
        lambda oct_: [float(oct_.R), float(oct_.I), float(oct_.J)]
    )
    x_y_zs = np.array([projection(oct_) for oct_ in octs]).T
    return go.Scatter3d(
        x=x_y_zs[0],
        y=x_y_zs[1],
        z=x_y_zs[2],
        mode='markers',
        marker=dict(
            size=10,
            symbol='circle',
            opacity=0.8,
        ),
    )


def plot_generations(generations, projection):
    traces = [
        plot_octs(gen, projection=projection)
        for gen in generations
    ]
    plotly_iplot(go.Figure(data=traces, layout=go.Layout()))


def plot_octs(octs, projection, **kwargs):
    projection_dim = len(projection(octonion.oR))
    if projection_dim == 2:
        return plot_octs_2d(octs, projection, **kwargs)
    elif projection_dim == 3:
        return plot_octs_3d(octs, projection, **kwargs)
    else:
        raise ValueError('Projection must pull out either 2 or 3 components!')


def plot_octs_2d(octs, projection=None, **kwargs):
    projection = projection or proj('ri')
    xys = np.array([projection(oc) for oc in octs]).T
    return go.Scatter(
        x=xys[0],
        y=xys[1],
        mode='markers',
        marker=dict(
            size=10,
            symbol='circle',
        ),
        **kwargs
    )


def plot_octs_3d(octs, projection=None, **kwargs):
    projection = projection or proj('rij')
    xyzs = np.array([projection(oc) for oc in octs]).T
    return go.Scatter3d(
        x=xyzs[0],
        y=xyzs[1],
        z=xyzs[2],
        mode='markers',
        marker=dict(
            size=5,
            symbol='circle',
            opacity=0.8,
        ),
        **kwargs
    )


def plot_quaternion_octs_from_gens(gens, limit=10, path='/tmp/foo.html'):
    traces = []
    for i in range(limit):
        print('Plotting for value i={}'.format(i))
        traces.append(plot_quaternion_octs(iterated_products(gens, i)))
    fig = go.Figure(data=traces, layout=go.Layout())
    plotly_plot(fig, filename=path, auto_open=False)
    return fig


def make_q_plots():
    for i in range(20):
        os.system('rm -f /tmp/foo-{}.html'.format(i))
        plot_quaternion_octs_from_gens(
            (
                random_nearly_unit_quaternion_gens(num=1, max_=10) +
                random_nearly_unit_complex_gens(num=2, max_=10)
            ),
            limit=6,
            path='/tmp/foo-{}.html'.format(i),
        )
