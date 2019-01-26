#!/usr/bin/env python
# coding: utf-8


"""Harness."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import numpy as np
from plotly.offline import (
    plot as plotly_plot,
    iplot as plotly_iplot,
)
import plotly.graph_objs as go


import octonion


def proj(projletters):
    pup = projletters.upper()

    def _proj(oc):
        return [
            float(x)
            for x in [getattr(oc, p) for p in pup]
        ]
    return _proj


def plot_generations(generations, projection, **kwargs):
    traces = [
        plot_octs(gen, projection=projection, **kwargs)
        for gen in generations
    ]
    square_layout = go.Layout(yaxis=dict(scaleanchor='x'))
    plotly_iplot(go.Figure(data=traces, layout=square_layout))


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
