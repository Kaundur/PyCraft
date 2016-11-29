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


# Step along sight vector until a block collisions occurs,
# return the block as well as the position connected to the block
def los_collision(world, position, sight_vector):
    if sight_vector:
        sight_position = position
        # step size to increase accuracy of collision
        step_size = 0.1
        # Max length of the block search, in block units
        max_range = 10

        # Find vector step for sight vector
        step_vector = sight_vector*step_size

        search_iterations = max_range / step_size
        previous_block = None
        for _ in xrange(search_iterations):
            # Calculate what chunk the sight vector is inside
            cx = math.floor(sight_position.x/16)
            cy = math.floor(sight_position.y/16)
            cz = math.floor(sight_position.z/16)

            # Calculate what block coord the sight vector is inside
            block_key = (math.floor(sight_position.x),
                         math.floor(sight_position.y),
                         math.floor(sight_position.z))

            # Does the chunk exist
            if (cx, cy, cz) in world.chunks:
                chunk = world.chunks[cx, cy, cz]
                # Check that the sight vector has moved to a new block, and the block exists
                if block_key != previous_block and block_key in chunk.blocks and chunk.blocks[block_key] is not None:
                    # Return the previous block position and the position of the block collided with the sight vector
                    return previous_block, (math.floor(sight_position.x),
                                            math.floor(sight_position.y),
                                            math.floor(sight_position.z))

                # If a collision hasn't occurred, Set the previous block position as the current position
                previous_block = (math.floor(sight_position.x),
                                  math.floor(sight_position.y),
                                  math.floor(sight_position.z))
                sight_position += step_vector

        # Return None values when no blocks are found within the maximum range
        return None, None
