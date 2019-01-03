#!/usr/bin/env python
# coding: utf-8


"""Harness."""


from __future__ import (
    print_function, division, absolute_import, unicode_literals,
)


#
# Business
#


def vlen(string):
    string = str(string)
    return len(string.split('\n'))


def hlen(string):
    string = str(string)
    return max(len(row) for row in string.split('\n'))


def pad_top(string, length, pad='\n'):
    string = str(string)
    deficit = length - vlen(string)
    full_pad = pad + ' '*hlen(string)
    return full_pad*deficit + string


def pad_bottom(string, length, pad='\n'):
    string = str(string)
    deficit = length - vlen(string)
    full_pad = pad + ' '*hlen(string)
    return string + full_pad*deficit


def pad_vcenter(string, length, pad='\n'):
    string = str(string)
    deficit = length - vlen(string)
    full_pad = pad + ' '*hlen(string)
    return full_pad*deficit//2 + string + full_pad*(deficit - deficit//2)


def pad_right(string, length=None, pad=' '):
    string = str(string)
    length = length or hlen(string)
    rows = [row + pad*(length - len(row)) for row in string.split('\n')]
    return '\n'.join(rows)


def pad_left(string, length=None, pad=' '):
    string = str(string)
    length = length or hlen(string)
    rows = [pad*(length - len(row)) + row for row in string.split('\n')]
    return '\n'.join(rows)


def pad_center(string, length=None, pad=' '):
    string = str(string)
    length = length or hlen(string)
    rows = [
        (
            pad*((length - len(row))//2) +
            row +
            pad*((length - len(row)) - ((length - len(row))//2))
        )
        for row in string.split('\n')
    ]
    return '\n'.join(rows)


def hadjoin(block1, block2, hsep=' ', vsep='\n', align='top'):
    height1 = vlen(block1)
    height2 = vlen(block2)
    height = max(height1, height2)

    width1 = hlen(block1)

    block1_padded = pad_bottom(pad_right(block1, width1), height)
    block2_padded = (
        pad_bottom(block2, height) if align == 'top' else
        pad_top(block2, height) if align == 'bottom' else
        pad_vcenter(block2, height)
    )

    rows = [
        b1_row + hsep + b2_row
        for (b1_row, b2_row)
        in zip(block1_padded.split('\n'), block2_padded.split('\n'))
    ]

    return '\n'.join(rows)


def vadjoin(block1, block2, hsep=' ', vsep='\n', align='left'):
    width1 = hlen(block1)
    width2 = hlen(block2)
    width = max(width1, width2)

    block1_padded = pad_right(block1, width)
    block2_padded = (
        pad_right(block2, width) if align == 'left' else
        pad_left(block2, width) if align == 'right' else
        pad_center(block2, width)
    )

    return block1_padded + vsep + block2_padded


def in_box(s):
    s = str(s)
    width = hlen(s)
    height = vlen(s)
    top_bottom = block('+-' + '-'*width + '-+')
    left_right = block('|\n'*(height-1) + '|')
    res = top_bottom / (left_right + block(s) + left_right) / top_bottom
    return res


#
# Classes
#


class TextBlock(object):

    def __init__(self, text):
        if isinstance(text, TextBlock):
            text = text.text
        self.text = text
        self.height = vlen(text)
        self.width = hlen(text)

    def __add__(self, other):
        return TextBlock(hadjoin(self.text, other.text))

    def __truediv__(self, other):
        return TextBlock(vadjoin(self.text, other.text))

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text


def block(*text):
    return TextBlock('\n'.join(map(str, text)))


def rblock(*text):
    return block(pad_left('\n'.join(map(str, text))))


def lblock(*text):
    return block(pad_right('\n'.join(map(str, text))))


def cblock(*text):
    return block(pad_center('\n'.join(map(str, text))))


def fill(filling, width=1, height=1):
    return block('\n'.join([filling*width]*height))


def space(width=1, height=1):
    return block('\n'.join([' '*width]*height))
