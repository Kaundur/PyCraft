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
