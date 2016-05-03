import pyglet
from pyglet.gl import *
from noise import pnoise2, snoise2
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
                    if (self.position.y*16 + y) <= self.surface[x][z]:
                        self.create_block((x, y, z), False)
        self._find_exposed_blocks()

    def _find_exposed_blocks(self):
        for block_position in self.blocks.keys():
            x = block_position[0]
            y = block_position[1]
            z = block_position[2]

            # Could pass b coords into the batch creation, will increase speed of batch loop
            world_x = x+self.position.x*self.CHUNK_SIZE.x
            world_y = y+self.position.y*self.CHUNK_SIZE.y
            world_z = z+self.position.z*self.CHUNK_SIZE.z

            self._check_exposed_face_new(x, y, z, world_x, world_y, world_z)

    def _check_exposed_face_new(self, x, y, z, world_x, world_y, world_z):
        texture_coords = self.textures.get_texture(self.blocks[(x, y, z)].block_id)

        if (x, y+1, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(world_x, world_y, world_z, 0, self.batch, self.textures.texture_main, texture_coords[0])
        if (x, y-1, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(world_x, world_y, world_z, 1, self.batch, self.textures.texture_main, texture_coords[1])

        if (x+1, y, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(world_x, world_y, world_z, 2, self.batch, self.textures.texture_main, texture_coords[2])
        if (x-1, y, z) not in self.blocks:
            self.blocks[(x, y, z)].add_face(world_x, world_y, world_z, 3, self.batch, self.textures.texture_main, texture_coords[3])

        if (x, y, z-1) not in self.blocks:
            self.blocks[(x, y, z)].add_face(world_x, world_y, world_z, 4, self.batch, self.textures.texture_main, texture_coords[4])
        if (x, y, z+1) not in self.blocks:
            self.blocks[(x, y, z)].add_face(world_x, world_y, world_z, 5, self.batch, self.textures.texture_main, texture_coords[5])

    def create_block(self, coords, update=True):
        x, y, z = coords[0], coords[1], coords[2]
        if (x, y, z) not in self.blocks:
            # TODO - Needs lazy init
            if (self.position.y*16 + y) <= self.surface[x][z]-5:
                self.blocks[(x, y, z)] = block.Block(2)
            elif (self.position.y*16 + y) <= self.surface[x][z]-1:
                self.blocks[(x, y, z)] = block.Block(0)
            else:
                self.blocks[(x, y, z)] = block.Block(1)

            if update:
                self._update_surrounding_blocks(x, y, z)
                self.create_batch_block(x, y, z)

    # Called to initialise chunk batch
    def create_batch(self):
        for i in self.blocks.keys():
            self.create_batch_block(i[0], i[1], i[2])

    def create_batch_block(self, x, y, z):
        b_x = x+self.position.x*self.CHUNK_SIZE.x
        b_y = y+self.position.y*self.CHUNK_SIZE.y
        b_z = z+self.position.z*self.CHUNK_SIZE.z
        self._check_exposed_face_new(x, y, z, b_x, b_y, b_z)

    def _create_block_face(self, x, y, z, b_x, b_y, b_z, face):
        block_id = self.blocks[(x, y, z)]
        texture_coords = self.textures.get_texture(block_id)
        batch_pos = block.render_face(b_x, b_y, b_z, face, self.batch, self.textures.texture_main, texture_coords[face])
        self.batch_positions[(x, y, z, face)] = batch_pos

    # # TODO - Pass through Block ID
    # def _check_exposed_face(self, x, y, z, b_x, b_y, b_z):
    #     if (x, y+1, z) not in self.blocks:
    #         self._create_block_face(x, y, z, b_x, b_y, b_z, 0)
    #     # Check bottom
    #     if (x, y-1, z) not in self.blocks:
    #         self._create_block_face(x, y, z, b_x, b_y, b_z, 1)
    #
    #     if (x+1, y, z) not in self.blocks:
    #         self._create_block_face(x, y, z, b_x, b_y, b_z, 2)
    #     if (x-1, y, z) not in self.blocks:
    #         self._create_block_face(x, y, z, b_x, b_y, b_z, 3)
    #
    #     if (x, y, z-1) not in self.blocks:
    #         self._create_block_face(x, y, z, b_x, b_y, b_z, 4)
    #     if (x, y, z+1) not in self.blocks:
    #         self._create_block_face(x, y, z, b_x, b_y, b_z, 5)
    #

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
        if (x-1, y, z) in self.blocks:
            self.blocks[(x-1, y, z)].clear_batch()
            #self._clear_block_batch(x-1, y, z)
            self.create_batch_block(x-1, y, z)
        if (x+1, y, z) in self.blocks:
            self.blocks[(x+1, y, z)].clear_batch()
            #self._clear_block_batch(x+1, y, z)
            self.create_batch_block(x+1, y, z)

        if (x, y-1, z) in self.blocks:
            self.blocks[(x, y-1, z)].clear_batch()
            #self._clear_block_batch(x, y-1, z)
            self.create_batch_block(x, y-1, z)
        if (x, y+1, z) in self.blocks:
            self.blocks[(x, y+1, z)].clear_batch()
            #self._clear_block_batch(x, y+1, z)
            self.create_batch_block(x, y+1, z)

        if (x, y, z-1) in self.blocks:
            self.blocks[(x, y, z-1)].clear_batch()
            #self._clear_block_batch(x, y, z-1)
            self.create_batch_block(x, y, z-1)
        if (x, y, z+1) in self.blocks:
            self.blocks[(x, y, z+1)].clear_batch()
            #self._clear_block_batch(x, y, z+1)
            self.create_batch_block(x, y, z+1)

    def _clear_block_batch(self, x, y, z):
        # Delete batch faces of current block
        for i in range(6):
            if (x, y, z, i) in self.batch_positions:
                self.batch_positions[(x, y, z, i)].delete()
                del self.batch_positions[(x, y, z, i)]

    def _get_block_local_coords(self, coords):
        block_coords = (coords[0]-self.position.x*16, coords[1]-self.position.y*16, coords[2]-self.position.z*16)
        return block_coords

    def render(self):
        self.batch.draw()
