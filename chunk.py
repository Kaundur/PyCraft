import pyglet
from pyglet.gl import *
import pyclid

import block


class Chunk:
    def __init__(self, x, y, z, surface, textures):
        self.blocks = {}
        self.blocks_new = {}
        self.batch_positions = {}
        self.position = pyclid.Vec3(x, y, z)
        self.CHUNK_SIZE = pyclid.Vec3(16, 16, 16)

        self.surface = surface

        # TODO - Can we keep textures outside of the chunk
        self.textures = textures
        self.batch = pyglet.graphics.Batch()

    def generate_chunk_default(self):
        for x in xrange(self.CHUNK_SIZE.x):
            for z in xrange(self.CHUNK_SIZE.z):
                for y in xrange(self.CHUNK_SIZE.y):
                    real_x = x+self.position.x*16
                    real_y = y+self.position.y*16
                    real_z = z+self.position.z*16
                    if (self.position.y*16 + y) <= self.surface[(real_x, real_z)]:
                        # TODO - Real x, y, z to be passed in
                        self.create_block((real_x, real_y, real_z), False)
        self._find_exposed_blocks()

    def _find_exposed_blocks(self):
        for block_position in self.blocks.keys():
            x = block_position[0]
            y = block_position[1]
            z = block_position[2]
            self._create_exposed_face(x, y, z)

    # TODO - Can be shortend
    def _create_exposed_face(self, x, y, z):
        texture_coords = self.textures.get_texture(self.blocks[(x, y, z)].block_id)

        if (x, y+1, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(x, y, z, 0, self.batch, self.textures.texture_main, texture_coords[0])
        if (x, y-1, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(x, y, z, 1, self.batch, self.textures.texture_main, texture_coords[1])

        if (x+1, y, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(x, y, z, 2, self.batch, self.textures.texture_main, texture_coords[2])
        if (x-1, y, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(x, y, z, 3, self.batch, self.textures.texture_main, texture_coords[3])

        if (x, y, z-1) not in self.blocks:
            self.blocks[(x, y, z)].add_face(x, y, z, 4, self.batch, self.textures.texture_main, texture_coords[4])
        if (x, y, z+1) not in self.blocks:
            self.blocks[(x, y, z)].add_face(x, y, z, 5, self.batch, self.textures.texture_main, texture_coords[5])

    def create_block(self, coords, update=True):
        x, y, z = coords[0], coords[1], coords[2]
        if (x, y, z) not in self.blocks:
            # TODO - Needs lazy init
            # Select block id based on the depth from the surface
            if y <= self.surface[(x, z)]-5:
                self.blocks[(x, y, z)] = block.Block(2)
            elif y <= self.surface[(x, z)]-1:
                self.blocks[(x, y, z)] = block.Block(0)
            else:
                self.blocks[(x, y, z)] = block.Block(1)

            # Used to suppress block update when building the chunk
            if update:
                self._update_surrounding_blocks(x, y, z)
                self.create_batch_block(x, y, z)

    # Called to initialise chunk batch
    def create_batch(self):
        for i in self.blocks.keys():
            self.create_batch_block(i[0], i[1], i[2])

    def create_batch_block(self, x, y, z):
        self._create_exposed_face(x, y, z)

    def find_block(self, block_coords):
        local_coords = self._get_block_local_coords(block_coords)
        if local_coords in self.blocks:
            return True
        return False

    def remove_block(self, block_coords):
        local_coords = self._get_block_local_coords(block_coords)
        x, y, z = local_coords[0], local_coords[1], local_coords[2]

        if local_coords in self.blocks:
            # Remove block
            self.blocks[local_coords].clear_batch()
            del self.blocks[local_coords]
            self._update_surrounding_blocks(x, y, z)

    def _update_surrounding_blocks(self, x, y, z):
        self._update_block((x-1, y, z))
        self._update_block((x+1, y, z))
        self._update_block((x, y-1, z))
        self._update_block((x, y+1, z))
        self._update_block((x, y, z-1))
        self._update_block((x, y, z+1))

    def _update_block(self, coord):
        if (coord) in self.blocks:
            self.blocks[coord].clear_batch()
            self.create_batch_block(coord[0], coord[1], coord[2])

    def _clear_block_batch(self, x, y, z):
        # Delete batch faces of current block
        for i in range(6):
            if (x, y, z, i) in self.batch_positions:
                self.batch_positions[(x, y, z, i)].delete()
                del self.batch_positions[(x, y, z, i)]

    def _get_block_local_coords(self, coords):
        block_coords = (coords[0], coords[1], coords[2])
        return block_coords

    def render(self):
        self.batch.draw()
