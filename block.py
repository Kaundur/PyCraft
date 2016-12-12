from pyglet.gl import *


class Block:
    def __init__(self, block_id):
        # Block is initialised on creation, graphics is not.
        # This allows for physics to take place even if the block cannot be seen
        self.block_id = block_id
        self._batch_pos = None

    def add_faces(self, x, y, z, faces, batch, texture, texture_coords):
        # If the batch already exists, we are trying to add new faces to the batch.
        # First remove the previous batch and regenerate
        if self._batch_pos:
            self.remove_block()
        # Render entire block in one pass, if a new face is added, just rerender the entire block
        # Quicker chunk generation
        batch_pos = render_faces(x, y, z, faces, batch, texture, texture_coords)
        if batch_pos:
            self._batch_pos = batch_pos

    def remove_block(self):
        self.clear_batch()

    def clear_batch(self):
        if self._batch_pos:
            self._batch_pos.delete()
            self._batch_pos = None


# Draw a wireframe cube, used as a visual aid to show the player what block they are looking at
def highlight_cube(coords, size, extension=0.1):
    # Extension of cube around normal block size
  
    highlight_frame = cube_coordinates(coords, size, extension)

    # render wireframe cube
    pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE)
    pyglet.graphics.draw(24, pyglet.gl.GL_QUADS, ('v3f', highlight_frame), ('c3b', [0, 0, 100]*24))
    pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_FILL)


def cube_coordinates(coords, s=1, e=0):
    # s - size
    # e - extension

    x = coords[0]
    y = coords[1]
    z = coords[2]
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

    # Build list of coordinates and textures for the faces passed in
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

    # if we have built a list of faces to render, all all to the batch
    # return a reference to the position in the batch so that it can easily be deleted
    if face_final:
        batch_pos = batch.add(int(len(face_final)/3), pyglet.gl.GL_QUADS, texture_group, ('v3f', face_final), ('t2f', texture_final))
        return batch_pos
    return None
