import pyglet
from pyglet.gl import *
import pyclid

import block


class Chunk:
    def __init__(self, x, y, z, surface, textures, world):
        self.blocks = {}
        self.blocks_new = {}
        self.batch_positions = {}
        self.update_list = []
        self.position = pyclid.Vec3(x, y, z)
        self.CHUNK_SIZE = pyclid.Vec3(16, 16, 16)

        self.surface = surface

        # TODO - Can we keep textures outside of the chunk
        self.textures = textures
        self.batch = pyglet.graphics.Batch()
        self.world = world

    def generate_chunk_default(self):
        for x in xrange(self.CHUNK_SIZE.x):
            for z in xrange(self.CHUNK_SIZE.z):
                for y in xrange(self.CHUNK_SIZE.y):
                    real_x = x+self.position.x*16
                    real_y = y+self.position.y*16
                    real_z = z+self.position.z*16
                    if (self.position.y*16 + y) <= self.surface[(real_x, real_z)]:
                        self.create_block((real_x, real_y, real_z), False)

        #self.find_exposed_blocks()

    def find_exposed_blocks(self):
        for block_position in self.blocks.keys():
            x = block_position[0]
            y = block_position[1]
            z = block_position[2]
            # Put block location and chunk into the queue
            # TODO - This queue can greatly be reduced by checking if the faces are exposed
            # TODO - However, will require a rethink, as blocks may be updated while in the queue
            # TODO - May be already handled by the immediate block update
            #self.world.block_generation_queue.put((self, x, y, z))
            local_x = x-self.position.x*16
            local_y = y-self.position.y*16
            local_z = z-self.position.z*16


            # Look at edge cases

            # How can we apply this if the nearby batch hasnt been created yet?
            # 3 distances , render, generate_batch, generate_world,
            # when inside generate_world just generate the blocks
            # when inside generate_batch, data will be available to generate with edge cases

            if local_x == 15 or local_x == 0 or local_y == 15 or local_y == 0 or local_z == 15 or local_z == 0:
                self.check_exposed_face(x, y, z)
            else:
                self.check_exposed_face(x, y, z)

    # TODO - Do we still need to check entire block????, rewrite functions to add block to batch then recheck every face
    def create_exposed_face(self, x, y, z):
        texture_coords = self.textures.get_texture(self.blocks[(x, y, z)].block_id)

        # TODO - Must be a better way of doing this

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

    def check_exposed_face(self, x, y, z):
        #texture_coords = self.textures.get_texture(self.blocks[(x, y, z)].block_id)

        if (x, y+1, z) not in self.blocks:
            self.world.block_generation_queue.put((self, x, y, z))
            #self.blocks[(x, y, z)].add_face(x, y, z, 0, self.batch, self.textures.texture_main, texture_coords[0])
        elif (x, y-1, z) not in self.blocks:
            self.world.block_generation_queue.put((self, x, y, z))
            #self.blocks[(x, y, z)].add_face(x, y, z, 1, self.batch, self.textures.texture_main, texture_coords[1])

        elif (x+1, y, z) not in self.blocks:
            self.world.block_generation_queue.put((self, x, y, z))
            #self.blocks[(x, y, z)].add_face(x, y, z, 2, self.batch, self.textures.texture_main, texture_coords[2])
        elif (x-1, y, z) not in self.blocks:
            self.world.block_generation_queue.put((self, x, y, z))
            #self.blocks[(x, y, z)].add_face(x, y, z, 3, self.batch, self.textures.texture_main, texture_coords[3])

        elif (x, y, z-1) not in self.blocks:
            self.world.block_generation_queue.put((self, x, y, z))
            #self.blocks[(x, y, z)].add_face(x, y, z, 4, self.batch, self.textures.texture_main, texture_coords[4])
        elif (x, y, z+1) not in self.blocks:
            self.world.block_generation_queue.put((self, x, y, z))
            #self.blocks[(x, y, z)].add_face(x, y, z, 5, self.batch, self.textures.texture_main, texture_coords[5])


    # TODO - Can be shortend
    def create_exposed_face_old(self, x, y, z):
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
                self.blocks[(x, y, z)] = block.Block(2, self)
            elif y <= self.surface[(x, z)]-1:
                self.blocks[(x, y, z)] = block.Block(0, self)
            else:
                self.blocks[(x, y, z)] = block.Block(1, self)

            # Used to suppress block update when building the chunk
            if update:
                self._update_surrounding_blocks(x, y, z)
                self.create_batch_block(x, y, z)

    # Called to initialise chunk batch
    def create_batch(self):
        for i in self.blocks.keys():
            self.create_batch_block(i[0], i[1], i[2])

    def create_batch_block(self, x, y, z):
        # TODO - This is broke, need to redo the create face function
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
        self._update_block((x-1, y, z))
        self._update_block((x+1, y, z))
        self._update_block((x, y-1, z))
        self._update_block((x, y+1, z))
        self._update_block((x, y, z-1))
        self._update_block((x, y, z+1))

    def _update_block(self, coord):
        if (coord) in self.blocks:
            # TODO - May not to clear here, if we are just adding a face
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

    def add_to_update_list(self, block_object):
        self.update_list.append(block_object)

    def update_block_new(self):
        if len(self.update_list) > 0:
            pass
            # Call world? so we can update surrounding blocks across chunks

    def render(self):
        self.batch.draw()
