#!/usr/bin/env python3
"""Draws an SVG barometer dial in kPa.

   400 x 400 image, with circle centre at (200, 200)
"""

__RCS__ = '$Id$'
__version__ = '$Revision:$'
__initialdate__ = 'January 2019'
__author__ = 'Darren Paul Griffith <http://madphilosopher.ca/>'


import math


def degrees(pressure):
    '''Returns the degree of the dial pointer for a given pressure in kPa. 
    
    pressure:   [  95 kPa, 107 kPa]
    degrees:    [-240 deg,  60 deg]

    The output is rounded so that 104.6 kPa returns as 0.0 exactly.
    '''

    return round((pressure - 95.0) * 25.0 - 240.0, 4)


def partialCircle(cx, cy, r, start, end):
    '''Calculates an arc of a circle, given the start and end in degrees.
    
    Adapted from: https://github.com/derhuerst/svg-partial-circle/blob/master/index.js
                  Copyright (c) 2017, Jannis Redmann
    '''

    # convert start and end to radians
    start = math.radians(start)
    end   = math.radians(end)

    length = end - start
    assert (length != 0), "start and end must be distinct values."

    fromX = r * math.cos(start) + cx
    fromY = r * math.sin(start) + cy
    toX   = r * math.cos(end) + cx
    toY   = r * math.sin(end) + cy
    
    if abs(length) <= math.pi:
        large = 0
    else:
        large = 1

    if length < 0:
        sweep = 0
    else:
        sweep = 1

    return '<path d="%s %s %s %s %s %s %s %s %s %s %s" />' % ('M', fromX, fromY, 'A', r, r, 0, large, sweep, toX, toY)


def write_svg(path="barometer.svg", p_ref=None, p_ind=None):
    '''Writes the SVG file with two optional needles.

       p_ref: reference needle (past) pressure in kPa
       p_ind: indicator needle (current) pressure in kPa

    '''

    FONT_KPA   = 'Anaktoria'    # font of 'kPA label
    FONT_SCALE = 'Anaktoria'    # font of numbered scale
    COLOUR_REF = '#88f'         # reference needle colour
    COLOUR_IND = 'red'          # indicator needle colour
    BORDER     = False          # draw outside border around image

    CENTRE = 200                # centre of circle at (200, 200)

    # svg header
    out = '''<?xml version="1.0" standalone="no"?>
    <svg 
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:cc="http://creativecommons.org/ns#"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:svg="http://www.w3.org/2000/svg"
        xmlns="http://www.w3.org/2000/svg"
        version="1.1"
        height="400"
        width="400">\n\n'''

    # outer and inner scale circles
    out = out + '<g stroke="black" stroke-width="1.5" fill="none">\n'
    out = out + partialCircle(CENTRE, CENTRE, CENTRE-20, -240, 60) + '\n'
    out = out + partialCircle(CENTRE, CENTRE, CENTRE-30, -240, 60) + '\n'
    out = out + '</g>\n\n'

    # scale tick marks every 0.1 kPa
    out = out + '<g stroke="black" stroke-width="1.0" fill="none">\n'
    for mbar in range(950, 1071):
        out = out + '<path stroke="#000"  d="M369.5 200 l11 0" transform="rotate(  %f 200 200)" />\n' % degrees(mbar/10.0)
    out = out + '</g>\n\n'

    # longer tick marks every 0.5 kPa, between the numbered labels
    out = out + '<g stroke="black" stroke-width="1.0" fill="none">\n'
    for mbar in range(955, 1075, 10):
        out = out + '<path stroke="#000"  d="M369.5 200 l22 0" transform="rotate(  %f 200 200)" />\n' % degrees(mbar/10.0)
    out = out + '</g>\n\n'

    # thicker tick marks for 95, 96, 97, ..., 107 kPa
    out = out + '<g stroke="black" stroke-width="2.5" fill="none">\n'
    for mbar in range(950, 1080, 10):
        out = out + '<path stroke="#000"  d="M369.5 200 l11 0" transform="rotate(  %f 200 200)" />\n' % degrees(mbar/10.0)
    out = out + '</g>\n\n'

    # line for pressure reference needle
    if p_ref:
        out = out + '<!-- coloured needle for reference (past) pressure -->\n'
        out = out + '<g stroke-width="1.5" >\n'
        out = out + '<path stroke="%s" d="M160 200 L368 200" transform="rotate(  %f 200 200)" />\n' % (COLOUR_REF, degrees(p_ref))
        out = out + '</g>\n\n'

    # line for pressure indicator needle (with arrowhead)
    if p_ind:
        out = out + '<!-- red needle with arrowhead for indicator (current) pressure -->\n'
        out = out + '<g stroke="%s" stroke-width="1.5" fill="%s">\n' % (COLOUR_IND, COLOUR_IND)
        out = out + '<path d="M160 200 L368 200" transform="rotate(  %f 200 200)" />\n' % degrees(p_ind)
        out = out + '<path d="M330 203 L330 197 L368 200 Z" transform="rotate(  %f 200 200)" />\n' % degrees(p_ind)
        out = out + '</g>\n\n'

    # kPa label
    out = out + '<text id="TextElement" x="200" y="380" style="font-family:%s; text-anchor:middle; font-weight:bold" font-size="18">kPa</text>\n\n' % FONT_KPA

    # scale labels for 96, 97, 98, ..., 106 kPa
    for mbar in range(960, 1070, 10):
        rotation = degrees(mbar/10.0) + 90.0
        label = int(round(mbar/10.0))
        out = out + '<text id="TextElement" x="200" y="15" style="font-family:%s; text-anchor:middle; font-weight:normal" font-size="14" transform="rotate( %f 200 200)">%d</text>\n' % (FONT_SCALE, rotation, label)

    # centre dot
    out = out + '\n<circle cx="200" cy="200" r="5" stroke="black" stroke-width="1" fill="black" />\n\n'

    # outside square border
    if BORDER:
        out = out + '<path stroke="#000"  d="M0 0 L0 400 L400 400 L400 0 Z" fill="none" />\n'


    # svg footer
    out = out + '</svg>\n'


    # write the svg file
    f = open(path, "w")
    f.write(out)
    f.close()


if __name__ == '__main__':

    # with needles
    write_svg("barometer.svg", p_ref=97.35, p_ind=100.20)

    # no needles
    #write_svg("barometer_blank.svg")

