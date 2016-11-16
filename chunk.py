import pyglet
from pyglet.gl import *

import pyclid

import block


CHUNK_SIZE = pyclid.Vec3(16, 16, 16)


class Chunk:
    def __init__(self, x, y, z, textures, world):
        self.blocks = {}
        self.blocks_new = {}
        self.batch_positions = {}
        self.update_list = []
        self.position = pyclid.Vec3(x, y, z)

        self.batch_generated = False

        # TODO - Can we keep textures outside of the chunk
        self.textures = textures
        self.batch = pyglet.graphics.Batch()
        self.world = world

    def generate_chunk_default(self):
        for x in xrange(CHUNK_SIZE.x):
            for z in xrange(CHUNK_SIZE.z):
                for y in xrange(CHUNK_SIZE.y):
                    real_x = x+self.position.x*16
                    real_y = y+self.position.y*16
                    real_z = z+self.position.z*16
                    surface_point = self.world.get_surface(real_x, real_z)
                    if (self.position.y*16 + y) <= surface_point:
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

                local_x = x-self.position.x*16
                local_y = y-self.position.y*16
                local_z = z-self.position.z*16

                # Look at edge cases
                if local_x == 15 or local_x == 0 or local_y == 15 or local_y == 0 or local_z == 15 or local_z == 0:
                    self.check_exposed_face(x, y, z, True)
                else:
                    self.check_exposed_face(x, y, z)
            self.batch_generated = True

    # TODO - Would be quicker on generation to add all faces to an array
    # TODO - and move all to a batch at the end of genreation
    def create_exposed_face(self, x, y, z):
        texture_coords = self.textures.get_texture(self.blocks[(x, y, z)].block_id)

        # TODO - Using world.find_block will be slower than checking if the block is an edge case
        if not self.world.find_block((x, y+1, z)):
            self.blocks[(x, y, z)].add_face(x, y, z, 0, self.batch, self.textures.texture_main, texture_coords[0])
        # Don't render bottom of world y != 0
        # Check y != 0 first, as this is a quicker call than find_block
        if y != 0 and not self.world.find_block((x, y-1, z)):
            self.blocks[(x, y, z)].add_face(x, y, z, 1, self.batch, self.textures.texture_main, texture_coords[1])

        if not self.world.find_block((x+1, y, z)):
            self.blocks[(x, y, z)].add_face(x, y, z, 2, self.batch, self.textures.texture_main, texture_coords[2])
        if not self.world.find_block((x-1, y, z)):
            self.blocks[(x, y, z)].add_face(x, y, z, 3, self.batch, self.textures.texture_main, texture_coords[3])

        if not self.world.find_block((x, y, z-1)):
            self.blocks[(x, y, z)].add_face(x, y, z, 4, self.batch, self.textures.texture_main, texture_coords[4])
        if not self.world.find_block((x, y, z+1)):
            self.blocks[(x, y, z)].add_face(x, y, z, 5, self.batch, self.textures.texture_main, texture_coords[5])

    # TODO - Is very ugly, can this function be reduced
    def check_exposed_face(self, x, y, z, edge=False):
        # Handle the edges of the chunk, difficult to check since new chunk may not exist yet
        if edge:
            if not self.world.find_block((x, y+1, z)):
                self.world.block_generation_queue.put((self, x, y, z))
            elif not self.world.find_block((x, y-1, z)):
                self.world.block_generation_queue.put((self, x, y, z))

            elif not self.world.find_block((x+1, y, z)):
                self.world.block_generation_queue.put((self, x, y, z))
            elif not self.world.find_block((x-1, y, z)):
                self.world.block_generation_queue.put((self, x, y, z))

            elif not self.world.find_block((x, y, z-1)):
                self.world.block_generation_queue.put((self, x, y, z))
            elif not self.world.find_block((x, y, z+1)):
                self.world.block_generation_queue.put((self, x, y, z))
        else:
            if (x, y+1, z) not in self.blocks:
                self.world.block_generation_queue.put((self, x, y, z))
            elif (x, y-1, z) not in self.blocks:
                self.world.block_generation_queue.put((self, x, y, z))

            elif (x+1, y, z) not in self.blocks:
                self.world.block_generation_queue.put((self, x, y, z))
            elif (x-1, y, z) not in self.blocks:
                self.world.block_generation_queue.put((self, x, y, z))

            elif (x, y, z-1) not in self.blocks:
                self.world.block_generation_queue.put((self, x, y, z))
            elif (x, y, z+1) not in self.blocks:
                self.world.block_generation_queue.put((self, x, y, z))

    def create_block(self, coords, block_id, update=True):
        x, y, z = coords[0], coords[1], coords[2]
        if (x, y, z) not in self.blocks:
            # TODO - Need to check if block_id is valid
            self.blocks[(x, y, z)] = block.Block((x, y, z), block_id, self)

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
        local_coords = self._get_block_local_coords(block_coords)
        if local_coords in self.blocks:
            return True
        return False

    def remove_block(self, block_coords):
        if block_coords in self.blocks:
            self.blocks[block_coords].clear_batch()
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
            self.blocks[coord].clear_batch()
            self.create_batch_block(coord[0], coord[1], coord[2])
        else:
            if self.world.find_block(coord):
                self.world.find_chunk(coord).update_block(coord)

    def _clear_block_batch(self, x, y, z):
        # Delete batch faces of current block
        for i in range(6):
            if (x, y, z, i) in self.batch_positions:
                self.batch_positions[(x, y, z, i)].delete()
                del self.batch_positions[(x, y, z, i)]

    def _get_block_local_coords(self, coords):
        block_coords = (coords[0], coords[1], coords[2])
        return block_coords

    def add_to_update_list(self, position, block_object):
        self.update_list.append((position, block_object))

    def render(self):
        self.batch.draw()


def get_chunk_coords(position):
    chunk_x = int(position.x / CHUNK_SIZE.x)
    chunk_y = int(position.y / CHUNK_SIZE.y)
    chunk_z = int(position.z / CHUNK_SIZE.z)
    return pyclid.Vec3(chunk_x, chunk_y, chunk_z)
