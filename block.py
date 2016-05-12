from pyglet.gl import *


class Block:
    # We dont store block position within the object to save on memory
    def __init__(self, position, block_id, chunk_obj):
        # Really dont want to store position in the block if I can help it
        self.block_id = block_id
        # Store batch faces so its easy to delete
        self.batch_positions = {}

        # Dont need to store a reference to the chunk in the block object
        self.update_block_id(position, self.block_id, chunk_obj)

    def update_block_id(self, position, block_id, chunk_obj):
        self.block_id = block_id
        if self.block_id == 1:
            chunk_obj.add_to_update_list(position, self)

    def add_face(self, x, y, z, face, batch, texture, texture_coords):
        batch_pos = render_face(x, y, z, face, batch, texture, texture_coords)
        self.batch_positions[face] = batch_pos

    def clear_batch(self):
        for batch_pos in self.batch_positions.keys():
            self.batch_positions[batch_pos].delete()
            del self.batch_positions[batch_pos]


def highlight_cube(x, y, z, size, extension=0.1):
    # Extension of cube around normal block size
    highlight_voxel = voxel(x, y, z, size, extension)

    # Make rendering wireframe to draw the highlight cube
    # Is this really faster than glLines?
    pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE)
    pyglet.graphics.draw(24, pyglet.gl.GL_QUADS, ('v3f', highlight_voxel), ('c3b', [0, 0, 100]*24))
    pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_FILL)


def voxel(x, y, z, s=1, e=0):
    # s - size
    # e - extension
    s += e

    # Return all vertices of block, groups of 3 coords
    voxel_vertices = [x-e, y+s, z-e,  x-e, y+s, z+s,  x+s, y+s, z+s,  x+s, y+s, z-e,
                      x-e, y-e, z-e,  x+s, y-e, z-e,  x+s, y-e, z+s,  x-e, y-e, z+s,

                      x+s, y+s, z-e,  x+s, y+s, z+s,  x+s, y-e, z+s,  x+s, y-e, z-e,
                      x-e, y+s, z+s,  x-e, y+s, z-e,  x-e, y-e, z-e,  x-e, y-e, z+s,

                      x-e, y+s, z-e,  x+s, y+s, z-e,  x+s, y-e, z-e,  x-e, y-e, z-e,
                      x+s, y+s, z+s,  x-e, y+s, z+s,  x-e, y-e, z+s,  x+s, y-e, z+s]

    return voxel_vertices


def render_face(x, y, z, face, batch, texture_group, texture_coords):
    # Size, extension
    s = 1
    e = 0
    s += e

    # TODO - Store this array somewhere else
    verts = [[x-e, y+s, z-e,  x-e, y+s, z+s,  x+s, y+s, z+s,  x+s, y+s, z-e],
             [x-e, y-e, z-e,  x+s, y-e, z-e,  x+s, y-e, z+s,  x-e, y-e, z+s],

             [x+s, y+s, z-e,  x+s, y+s, z+s,  x+s, y-e, z+s,  x+s, y-e, z-e],
             [x-e, y+s, z+s,  x-e, y+s, z-e,  x-e, y-e, z-e,  x-e, y-e, z+s],

             [x-e, y+s, z-e,  x+s, y+s, z-e,  x+s, y-e, z-e,  x-e, y-e, z-e],
             [x+s, y+s, z+s,  x-e, y+s, z+s,  x-e, y-e, z+s,  x+s, y-e, z+s]]

    batch_pos = batch.add(4, pyglet.gl.GL_QUADS, texture_group, ('v3f', verts[face]), ('t2f', texture_coords))
    return batch_pos



