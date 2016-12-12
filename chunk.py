import pyglet
from pyglet.gl import *

import block

CHUNK_SIZE = (16, 16, 16)


class Chunk:
    def __init__(self, x, y, z, textures, world):
        self.blocks = {}
        self.blocks_new = {}
        self.batch_positions = {}
        self.update_list = []
        self.position = [x, y, z]

        self.batch_generated = False

        # TODO - Can we keep textures outside of the chunk
        self.textures = textures
        self.batch = pyglet.graphics.Batch()
        self.world = world

    def generate_chunk_default(self):
        for x in xrange(CHUNK_SIZE[0]):
            for z in xrange(CHUNK_SIZE[2]):
                for y in xrange(CHUNK_SIZE[1]):
                    real_x = x+self.position[0]*CHUNK_SIZE[0]
                    real_y = y+self.position[1]*CHUNK_SIZE[1]
                    real_z = z+self.position[2]*CHUNK_SIZE[2]
                    surface_point = self.world.get_surface(real_x, real_z)
                    if (self.position[1]*CHUNK_SIZE[1] + y) <= surface_point:
                        # Select block id based on distance to surface block
                        block_id = 1
                        if real_y <= surface_point-5:
                            block_id = 2
                        elif real_y <= surface_point-1:
                            block_id = 0
                        self.create_block((real_x, real_y, real_z), block_id, False)

    def find_exposed_blocks(self):
        if not self.batch_generated:
            for block_position in self.blocks.keys():
                x = block_position[0]
                y = block_position[1]
                z = block_position[2]
                # If the block has any exposed faces, add them to the render queue
                if self.check_exposed_face(x, y, z):
                    self.world.block_generation_queue.put((self, x, y, z))
            self.batch_generated = True

    def check_exposed_face(self, x, y, z):
        # Check blocks around the current block, if one face is exposed add it to the generation queue
        # Note - This will always create a hard boundary at each chunk edge, could be optimised
        surrounding_blocks = [(x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1),
                              (x, y, z - 1)]
        for surrounding in surrounding_blocks:
            if surrounding not in self.blocks:
                return True
        return False

    def create_exposed_face(self, x, y, z):
        texture_coords = self.textures.get_texture(self.blocks[(x, y, z)].block_id)
        faces = []

        if not self.world.find_block((x, y+1, z)):
            faces.append(0)
        # Don't render bottom of world y != 0
        # Check y != 0 first, as this is a quicker call than find_block
        if y != 0 and not self.world.find_block((x, y-1, z)):
            faces.append(1)

        if not self.world.find_block((x+1, y, z)):
            faces.append(2)
        if not self.world.find_block((x-1, y, z)):
            faces.append(3)
        if not self.world.find_block((x, y, z-1)):
            faces.append(4)
        if not self.world.find_block((x, y, z+1)):
            faces.append(5)

        if faces:
            self.blocks[(x, y, z)].add_faces(x, y, z, faces, self.batch, self.textures.texture_main, texture_coords)

    def create_block(self, coords, block_id, update=True):
        x, y, z = coords[0], coords[1], coords[2]
        if (x, y, z) not in self.blocks:
            # TODO - Need to check if block_id is valid
            self.blocks[(x, y, z)] = block.Block(block_id)

            # Used to suppress block update when building the chunk
            if update:
                self._update_surrounding_blocks(x, y, z)
                self.create_batch_block(x, y, z)

    # Called to initialise chunk batch
    def create_batch(self):
        for i in self.blocks.keys():
            self.create_batch_block(i[0], i[1], i[2])

    def create_batch_block(self, x, y, z):
        self.create_exposed_face(x, y, z)

    def find_block(self, block_coords):
        if block_coords in self.blocks:
            return True
        return False

    def remove_block(self, block_coords):
        if block_coords in self.blocks:
            self.blocks[block_coords].remove_block()
            del self.blocks[block_coords]
            self._update_surrounding_blocks(block_coords[0], block_coords[1], block_coords[2])

    def _update_surrounding_blocks(self, x, y, z):
        self.update_block((x-1, y, z))
        self.update_block((x+1, y, z))
        self.update_block((x, y-1, z))
        self.update_block((x, y+1, z))
        self.update_block((x, y, z-1))
        self.update_block((x, y, z+1))

    def update_block(self, coord):
        if coord in self.blocks:
            self.create_batch_block(coord[0], coord[1], coord[2])
        else:
            if self.world.find_block(coord):
                self.world.find_chunk(coord).update_block(coord)

    def add_to_update_list(self, position, block_object):
        self.update_list.append((position, block_object))

    def render(self):
        self.batch.draw()


def find_chunk_coords(position):
    chunk_x = int(position[0] / CHUNK_SIZE[0])
    chunk_y = int(position[1] / CHUNK_SIZE[1])
    chunk_z = int(position[2] / CHUNK_SIZE[2])
    return chunk_x, chunk_y, chunk_z
