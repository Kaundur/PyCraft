import math
from pyglet.gl import *
import ctypes

import pyclid


# Bound a value to a min/max value
def clip(value, min_value, max_value):
    if value > max_value:
        value = max_value
    elif value < min_value:
        value = min_value
    return value


def get_sight_vector(rotation):
    # TODO - Rewrite notes, y has be made negative
    # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
    # is 1 when looking ahead parallel to the ground and 0 when looking
    # straight up or down.
    m = math.cos(math.radians(-rotation.y))
    # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
    # looking straight up.
    dy = math.sin(math.radians(-rotation.y))
    dx = math.cos(math.radians(rotation.x - 90)) * m
    dz = math.sin(math.radians(rotation.x - 90)) * m

    return pyclid.Vec3(dx, dy, dz)


def los_collision(world, position, sight_vector):
    # TODO - This should accept the sight vector and position, not the player
    if sight_vector:
        sight_position = position
        # step size to increase accuracy of collision
        step_size = 0.1
        max_range = 10

        step_vector = sight_vector*step_size

        m = 100
        previous_block = None
        for _ in xrange(max_range * m):
            cx = int(math.floor(sight_position.x/16))
            cy = int(math.floor(sight_position.y/16))
            cz = int(math.floor(sight_position.z/16))

            block_key = (int(math.floor(sight_position.x)),
                           int(math.floor(sight_position.y)+1)-1,
                           int(math.floor(sight_position.z)))
            try:
                chunk = world.chunks[cx, cy, cz]
                if block_key != previous_block and block_key in chunk.blocks and chunk.blocks[block_key] is not None:
                    return previous_block, (int(math.floor(sight_position.x)),
                                            int(math.floor(sight_position.y)),
                                            int(math.floor(sight_position.z)))

                previous_block = (int(math.floor(sight_position.x)),
                                            int(math.floor(sight_position.y)),
                                            int(math.floor(sight_position.z)))
                sight_position += step_vector
            except:
                # TODO - Add error here
                pass

        return None, None


# Return true if point (x, y) is within a polygon (Array poly)
# Note, this is fairly complex, can this be reduced
def point_in_poly(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def get_3d_menu_screen_coords(point):
        vm = (GLfloat * 16)()
        pm = (GLfloat * 16)()
        vp = (GLint * 4)()

        glGetFloatv(GL_MODELVIEW_MATRIX, vm)
        glGetFloatv(GL_PROJECTION_MATRIX, pm)
        glGetIntegerv(GL_VIEWPORT, vp)


        # https://code.google.com/p/geoffrey/source/browse/trunk/selection.py?r=1&spec=svn6
        fouriv = ctypes.c_int * 4
        sixteendv = ctypes.c_double * 16
        viewport = fouriv() # Where The Viewport Values Will Be Stored
        glGetIntegerv(GL_VIEWPORT, viewport) # Retrieves The Viewport Values (X, Y, Width, Height)
        modelview = sixteendv() # Where The 16 Doubles Of The Modelview Matrix Are To Be Stored
        glGetDoublev(GL_MODELVIEW_MATRIX, modelview) # Retrieve The Modelview Matrix
        projection = sixteendv() # Where The 16 Doubles Of The Projection Matrix Are To Be Stored
        glGetDoublev(GL_PROJECTION_MATRIX, projection) # Retrieve The Projection Matrix

        x_ctype = ctypes.c_double()
        y_ctype = ctypes.c_double()
        # z_ctype = ctypes.c_double()
        return x_ctype.value, y_ctype.value


def is_within_rect(m, a, b, c, d):
    # if sum of areas mab, mbc, mcd, mda == sum of area abcd
    # Then within the rect
    # Only use 2d coords here, as we are only interested in the on screen coords

    total_area = area_triangle(m, a, b) + area_triangle(m, b, c) + area_triangle(m, c, d) + area_triangle(m, d, a)
    rect_area = area_rect(a, b, c, d)

    if total_area > rect_area:
        return False
    else:
        return True


def area_triangle(a, b, c):
    # https://en.wikipedia.org/wiki/Shoelace_formula
    return 0.5*(a[0]*b[1] + b[0]*c[1] + c[0]*a[1] - a[0]*c[1] - c[0]*b[1] - b[0]*a[1])


def area_rect(a, b, c, d):
    # shoelace_formula - calculating from points, can be used on non 90deg angles
    return 0.5*(a[0]*b[1] + b[0]*c[1] + c[0]*d[1] + d[0]*a[1] - a[1]*b[0] - b[1]*c[0] - c[1]*d[0] - d[1]*a[0])
