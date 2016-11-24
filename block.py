from pyglet.gl import *


class Block:
    def __init__(self, block_id):
        self.block_id = block_id
        self.batch_pos = None
        self.batch_positions = {}

    def add_faces(self, x, y, z, faces, batch, texture, texture_coords):
        # If the batch already exists, we are trying to add new faces to the batch.
        # First remove the previous batch and regenerate
        if self.batch_pos:
            self.remove_block()
        # Render entire block in one pass, if a new face is added, just rerender the entire block
        # Quicker chunk generation
        batch_pos = render_faces(x, y, z, faces, batch, texture, texture_coords)
        if batch_pos:
            self.batch_pos = batch_pos

    def remove_block(self):
        self.clear_batch()

    def clear_batch(self):
        if self.batch_pos:
            self.batch_pos.delete()
            self.batch_pos = None


def highlight_cube(x, y, z, size, extension=0.1):
    # Extension of cube around normal block size
    highlight_frame = cube_coordinates(x, y, z, size, extension)

    # Make rendering wireframe to draw the highlight cube
    # Is this really faster than glLines?
    pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE)
    pyglet.graphics.draw(24, pyglet.gl.GL_QUADS, ('v3f', highlight_frame), ('c3b', [0, 0, 100]*24))
    pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_FILL)


def cube_coordinates(x, y, z, s=1, e=0):
    # s - size
    # e - extension
    s += e

    # Return all vertices of block, groups of 3 coords
    coordinates = [x-e, y+s, z-e,  x-e, y+s, z+s,  x+s, y+s, z+s,  x+s, y+s, z-e,
                      x-e, y-e, z-e,  x+s, y-e, z-e,  x+s, y-e, z+s,  x-e, y-e, z+s,

                      x+s, y+s, z-e,  x+s, y+s, z+s,  x+s, y-e, z+s,  x+s, y-e, z-e,
                      x-e, y+s, z+s,  x-e, y+s, z-e,  x-e, y-e, z-e,  x-e, y-e, z+s,

                      x-e, y+s, z-e,  x+s, y+s, z-e,  x+s, y-e, z-e,  x-e, y-e, z-e,
                      x+s, y+s, z+s,  x-e, y+s, z+s,  x-e, y-e, z+s,  x+s, y-e, z+s]

    return coordinates


def render_faces(x, y, z, faces, batch, texture_group, texture_coords):
    # Size, extension
    s = 1
    e = 0
    s += e

    face_final = []
    texture_final = []
    for face in faces:
        if face == 0:
            face_out = [x - e, y + s, z - e, x - e, y + s, z + s, x + s, y + s, z + s, x + s, y + s, z - e]
        elif face == 1:
            face_out = [x - e, y - e, z - e, x + s, y - e, z - e, x + s, y - e, z + s, x - e, y - e, z + s]
        elif face == 2:
            face_out = [x + s, y + s, z - e, x + s, y + s, z + s, x + s, y - e, z + s, x + s, y - e, z - e]
        elif face == 3:
            face_out = [x - e, y + s, z + s, x - e, y + s, z - e, x - e, y - e, z - e, x - e, y - e, z + s]
        elif face == 4:
            face_out = [x - e, y + s, z - e, x + s, y + s, z - e, x + s, y - e, z - e, x - e, y - e, z - e]
        elif face == 5:
            face_out = [x + s, y + s, z + s, x - e, y + s, z + s, x - e, y - e, z + s, x + s, y - e, z + s]
        else:
            face_out = None
            # Return None if face doesn't exist
        if face_out:
            texture_final.extend(texture_coords[face])
            face_final.extend(face_out)

    # Does this account for an empty array?
    # TODO - Can we just extend the batch here? test for later use with update to faces
    # TODO - See how Vertex list works, maybe there's an extend function
    if face_final:
        batch_pos = batch.add(int(len(face_final)/3), pyglet.gl.GL_QUADS, texture_group, ('v3f', face_final), ('t2f', texture_final))
        return batch_pos

    return None




