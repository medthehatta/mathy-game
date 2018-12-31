#!/usr/bin/env python
# coding: utf-8


"""Octonion math."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


import math
from functools import reduce


#
# Constants
#


R = 0  # R is an alias for "the scalar part"; i.e., the part parallel to 1
I = 1  # noqa
J = 2
K = 3
L = 4
IL = 5
JL = 6
KL = 7


# (more constants after further definitions under "More Constants")


#
# Helpers
#


def o(*args, **kwargs):
    """Create an octonion with the given components."""
    return Octonion(*args, **kwargs)


def printable(x):
    """Create a printable string representation of an octonion."""
    basis_vector_names = ['', 'I', 'J', 'K', 'L', 'IL', 'JL', 'KL']
    if all(component == 0 for component in x):
        return '0'

    component_strings = [
        (
            '1' if component == 1 and basis_vector == '' else
            '-1' if component == -1 and basis_vector == '' else
            '{}'.format(basis_vector) if component == 1 else
            '-{}'.format(basis_vector) if component == -1 else
            '{}{}'.format(component, basis_vector)
        )
        for (component, basis_vector) in zip(x, basis_vector_names)
        if component != 0
    ]
    return ' + '.join(component_strings)


def mksym(x, y):
    """Make a function that takes i,j and return xi*yj + xj*yi."""
    def _sym(i, j):
        return x[i]*y[j] + x[j]*y[i]
    return _sym


def mkalt(x, y):
    """Make a function that takes i,j and return xi*yj - xj*yi."""
    def _alt(i, j):
        return x[i]*y[j] - x[j]*y[i]
    return _alt


def componentwise(binary_op, x_components, y_components):
    """Perform binary_op componentwise to x and y."""
    return [
        binary_op(x_component, y_component)
        for (x_component, y_component) in zip(x_components, y_components)
    ]


#
# Octonionic math
#


def real_part(x):
    """Return the real part of x."""
    return x[R]


def imaginary_part(x):
    """Return the imaginary part of x."""
    return x[R:]


def conjugate(x):
    """Return the octonionic conjugate of x."""
    return [real_part(x)] + [-x_component for x_component in imaginary_part(x)]


def norm_squared(x):
    """Return the norm squared of x."""
    xc = conjugate(x)
    x_xc = octoprod(x, xc)
    return real_part(x_xc)


def norm(x):
    """Return the norm of x."""
    return math.sqrt(norm_squared(x))


#
# Octonionic product
#


def octoprod(x, y):
    """Compute the octionic product between octonions x and y."""
    sym = mksym(x, y)
    alt = mkalt(x, y)

    # basis products parallel to 1
    z1 = x[R]*y[R] - sum(x[i]*y[i] for i in [I, J, K, L, IL, JL, KL])

    # basis products parallel to I
    zi = sum([sym(R, I), alt(L, IL), alt(KL, JL), alt(J, K)])

    # basis products parallel to J
    zj = sum([sym(R, J), alt(L, JL), alt(IL, KL), alt(K, I)])

    # basis products parallel to K
    zk = sum([sym(R, K), alt(L, KL), alt(JL, IL), alt(I, J)])

    # basis products parallel to L
    zl = sum([sym(R, L), alt(IL, I), alt(JL, J), alt(KL, K)])

    # basis products parallel to IL
    zil = sum([sym(R, IL), alt(I, L), alt(KL, J), alt(K, JL)])

    # basis products parallel to JL
    zjl = sum([sym(R, JL), alt(J, L), alt(IL, K), alt(I, KL)])

    # basis products parallel to KL
    zkl = sum([sym(R, KL), alt(K, L), alt(JL, I), alt(J, IL)])

    return [z1, zi, zj, zk, zl, zil, zjl, zkl]


def octoprod_from_left(*xs):
    """
    Perform multiple octonionic products in a row, from left-to-right.

    The order matters (it is explicitly left-to-right) because octonion
    multiplication is NOT associative.
    """
    if len(xs) == 0:
        raise ValueError('Need to provide octonions to multiply')
    else:
        return reduce(octoprod, xs[1:], xs[0])


#
# Class
#


class Octonion(object):

    def __init__(self, R=0, I=0, J=0, K=0, L=0, IL=0, JL=0, KL=0):  # noqa
        self.components = [R, I, J, K, L, IL, JL, KL]

    def __getitem__(self, index):
        return self.components[index]

    @property
    def R(self):
        return self.components[R]

    @property
    def I(self):  # noqa
        return self.components[I]

    @property
    def J(self):
        return self.components[J]

    @property
    def K(self):
        return self.components[K]

    @property
    def L(self):
        return self.components[L]

    @property
    def IL(self):
        return self.components[IL]

    @property
    def JL(self):
        return self.components[JL]

    @property
    def KL(self):
        return self.components[KL]

    def conj(self):
        other_components = [-x for x in self.components[1:]]
        return type(self)(self.components[R], *other_components)

    def norm_squared(self):
        return (self*self.conj()).R

    def norm(self):
        return math.sqrt(self.norm_squared())

    def __add__(self, other):
        if isinstance(other, Octonion):
            components = componentwise(
                lambda x, y: x + y,
                self.components,
                other.components,
            )
            return type(self)(*components)
        else:
            return self + type(self)(R=other)

    def __sub__(self, other):
        if isinstance(other, Octonion):
            return self + -1*other
        else:
            return self + -1*type(self)(R=other)

    def __mul__(self, other):
        if isinstance(other, Octonion):
            components = octoprod(self.components, other.components)
        else:
            components = [other*component for component in self.components]
        return type(self)(*components)

    def __rmul__(self, scalar):
        return self*scalar

    def __radd__(self, scalar):
        return self + type(self)(R=scalar)

    def __rsub__(self, scalar):
        return type(self)(R=scalar) - self

    def __repr__(self):
        return printable(self.components)

    def __neg__(self):
        return -1*self


#
# More constants
#


oR = o(R=1)
oI = o(I=1)  # noqa
oJ = o(J=1)
oK = o(K=1)
oL = o(L=1)
oIL = o(IL=1)
oJL = o(JL=1)
oKL = o(KL=1)
