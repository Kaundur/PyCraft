__author__ = 'Kaundur'
import pyglet
from pyglet.gl import *


def letter_dict(letter):
    letters_dict = {
        'A': [0.0, 0.0, 0, 0.25, 1.0, 0, 0.5, 0.0, 0, 0.375, 0.5, 0, 0.125, 0.5, 0],
        'D': [0.0, 1.0, 0, 0.25, 1.0, 0, 0.5, 0.5, 0, 0.25, 0.0, 0, 0.0, 0.0, 0, 0.0, 1.0, 0],
        'E': [0.5, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.5, 0, 0.3, 0.5, 0, 0.0, 0.5, 0, 0.0, 1.0, 0.0, 0.5, 1.0, 0.0],

        'R': [0.0, 0.0, 0, 0.0, 1.0, 0, 0.35, 1.0, 0, 0.35, 0.5, 0, 0.0, 0.5, 0, 0.35, 0.0, 0],
        'S': [0.5, 1.0, 0, 0.0, 1.0, 0, 0.0, 0.5, 0, 0.5, 0.5, 0, 0.5, 0, 0, 0.0, 0, 0],
        'T': [0.0, 1.0, 0, 0.5, 1.0, 0, 0.25, 1.0, 0, 0.25, 0.0, 0],
        'L': [0.0, 1.0, 0, 0.0, 0.0, 0, 0.5, 0.0, 0],
        'N': [0.0, 0.0, 0, 0.0, 1.0, 0, 0.5, 0.0, 0, 0.5, 1.0, 0],
        'O': [0.0, 0.0, 0, 0.0, 1.0, 0, 0.5, 1.0, 0, 0.5, 0.0, 0, 0.0, 0.0, 0],
        'W': [0.0, 1.0, 0.0, 0.1875, 0.0, 0, 0.375, 1.0, 0, 0.5625, 0.0, 0, 0.75, 1.0, 0],

    }

    if letter in letters_dict:
        return letters_dict[letter]
    else:
        return None

# Do this in inkscape as line? extract coords afterwards?
def surface_letters(letter):

    letters_dict = {

        'L': [[0.0, 0.0, 0.0, 1.0, 0.125, 1.0, 0.125, 0.125, 0.5, 0.125, 0.5, 0.0]],
        #'N': [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, ]

        'E': [[0.0, 0.0, 0.0, 1.0, 0.5, 1.0, 0.5, 0.875, 0.125, 0.875, 0.125, 0.5625, 0.3, 0.5625, 0.3, 0.4375, 0.125, 0.4375, 0.125, 0.125, 0.5, 0.125, 0.5, 0.0]],
        'N': [[0.0, 0.0, 0.0, 1.0, 0.125, 1.0, 0.375, 0.125, 0.375, 1.0, 0.5, 1.0, 0.5, 0.0, 0.375, 0.0, 0.125, 0.75, 0.125, 0.0]],
        'O': [[0.0, 0.0, 0.0, 1.0, 0.75, 1.0, 0.75, 0.0], [0.25, 0.25, 0.25, 0.75, 0.5, 0.75, 0.5, 0.25]],

        'R': [[0.0, 0.0, 0.0, 1.0,
               0.4, 1.0, 0.4, 0.5,
               0.15, 0.5, 0.5, 0.0,
               0.45, 0.0, 0.1, 0.45,
               0.1, 0.0
        ]],

        'W': [[0.0, 1.0,
               0.0625, 1.0,
               0.1875, 0.125,

               0.34375, 1.0,
               0.40625, 1.0,
               0.5625, 0.125,

               0.6875, 1.0,
               0.75, 1.0,
               0.59385, 0.0,
               0.53125, 0.0,

               0.375, 0.75,
               0.21875, 0.0,
               0.15625, 0.0,
              ]]
    }

    if letter in letters_dict:
        return letters_dict[letter]
    else:
        return None

def draw_text(x, y, z):
    space = 0.0


    test = [9, 21, 6, 20, 4, 17, 3, 12, 3, 9, 4, 4, 6, 1, 9, 0, 11, 0, 14, 1, 16, 4, 17, 9, 17, 12, 16, 17, 14, 20, 11, 21
            -1, -1, 0, 0, 0, 20]

    scale = 0.005
    for i in range(0, len(test)):
        test[i] = test[i]*scale




    # Add third dimension
    final_array = []
    for i in range(0, len(test)-1, 2):
        final_array.append(test[i])
        final_array.append(test[i+1])
        final_array.append(0)

    #vec_size = int((len()/2)*3)
    vec_size = len(final_array)

    # Position letters
    for i in range(0, vec_size-1, 3):
        final_array[i] += x
        final_array[i+1] += y + 1.0
        final_array[i+2] += z



    poly_size = int(len(final_array)/3)
    pyglet.graphics.draw(poly_size, pyglet.gl.GL_LINE_LOOP, ('v3f', final_array))


    return

    test_new = surface_letters('L')



    #
    # # TODO - Could do this as a poly, now that we are closing the shape
    # test = []
    # for short_array in test_new:
    #     group_len = int(len(short_array)/3.0)
    #     for i in range(0, group_len-1):
    #         j = i*3
    #
    #         test.append(short_array[j])
    #         test.append(short_array[j+1])
    #         test.append(short_array[j+2])
    #         test.append(short_array[j+3])
    #         test.append(short_array[j+4])
    #         test.append(short_array[j+5])


    for test in test_new:

        # Scale letters
        scale = 0.1
        for i in range(0, len(test)):
            test[i] = test[i]*scale


        # Add third dimension
        final_array = []
        for i in range(0, len(test)-1, 2):
            final_array.append(test[i])
            final_array.append(test[i+1])
            final_array.append(0)

        #vec_size = int((len()/2)*3)
        vec_size = len(final_array)

        # Position letters
        for i in range(0, vec_size-1, 3):
            final_array[i] += x
            final_array[i+1] += y + 1.0
            final_array[i+2] += z



        poly_size = int(len(final_array)/3)
        pyglet.graphics.draw(poly_size, pyglet.gl.GL_LINE_LOOP, ('v3f', final_array))
        #pyglet.graphics.draw(poly_size, pyglet.gl.GL_LINES, ('v3f', test))


    # space = 0.0
    # for lett in 'NEW WORLD':
    #     letter_vector = letter_dict(lett)
    #     if letter_vector:
    #         render(letter_dict(lett), x+space, y, z)
    #     space += 0.1


def render(test, x, y, z):
    scale = 0.1
    for i in range(0, len(test)):
        test[i] = test[i]*scale



    for i in range(0, len(test), 3):
        test[i] += x
        test[i+1] += y + 1.0
        test[i+2] += z


    poly_size = int(len(test)/3)
    #pyglet.graphics.draw(poly_size, pyglet.gl.GL_LINE_LOOP, ('v3f', test),  ('c3B', color))
    pyglet.graphics.draw(poly_size, pyglet.gl.GL_LINE_STRIP, ('v3f', test))
