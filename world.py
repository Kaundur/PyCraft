import math
import Queue

from noise import pnoise2, snoise2, pnoise3, snoise3
from pyclid import Vec3

import chunk


class World:
    def __init__(self, textures):
        # Load in textures per world
        self.textures = textures
        # chunks around the player to render
        self.render_distance = 2
        self.gravity = -15.0

        # Not really a seed, the position of the noise in the 3D dimension
        self.seed = 0
        self.block_generation_queue = Queue.Queue()
        self._loaded_position = Vec3()

        # Chunks around the player to generate
        self.generate_distance = 5
        self.chunks = {}
        self.surface = {}

    def generate_world(self, position):

        # Position - Current player position
        # Need to convert to chunk position
        # Then generate chunks around the player

        # TODO -  Could all of the blocks just be added to the queue
        chunk_coords = self.find_chunk_coords(position)
        render_rad = 3
        # y is up
        for x in xrange(chunk_coords.x-render_rad, chunk_coords.x+render_rad+1):
            for z in xrange(chunk_coords.z-render_rad, chunk_coords.z+render_rad+1):

                surface, highest_point = self.generate_surface(x, z)

                # Find the highest chunk required for the current x, z chunk coordinates
                max_y_chunk = int(highest_point/16)+1
                for y in range(max_y_chunk):
                    if (x, y, z) not in self.chunks:
                        self.new_chunk(x, y, z, surface)
        #
        # for x in xrange(chunk_coords.x-self.generate_distance, chunk_coords.x+self.generate_distance+1):
        #     for z in xrange(chunk_coords.z-self.generate_distance, chunk_coords.z+self.generate_distance+1):
        #         # Quick test to see if this x, z section has been generated
        #         # Would be nicer to directly test if its below the generate_distance but outside the render distance
        #         # Or even better, just loop over the outside of the render distance
        #         if (x, 0, z) not in self.chunks:
        #
        #             surface, highest_point = self.generate_surface(x, z)
        #
        #             # Find the highest chunk required for the current x, z chunk coordinates
        #             max_y_chunk = int(highest_point/16)+1
        #             for y in range(max_y_chunk):
        #                 if (x, y, z) not in self.chunks:
        #                     self.new_chunk(x, y, z, surface)
        #


    def generate_surface(self, chunk_x, chunk_z):
        octaves = 10
        freq = 16.0 * octaves
        surface = {}

        real_pos_x = chunk_x*16
        real_pos_z = chunk_z*16
        scale = 5

        highest_point = 0
        for local_x, x in enumerate(xrange(real_pos_x, real_pos_x + 16)):
            for z in xrange(real_pos_z, real_pos_z + 16):
                point = int((snoise3(x / freq, z / freq, self.seed, octaves) * 127.0 + 128.0)/scale)
                surface[(x, z)] = point

                if point > highest_point:
                    highest_point = point

        return surface, highest_point

    def _generate_chunks(self, position):
        chunk_coords = self.find_chunk_coords(position)
        if chunk_coords != self._loaded_position:
            self._loaded_position = chunk_coords
            render_rad = 2
            generate_rad = 1
            # TODO - Should generate things within render_rad first
            # TODO - thread generation of things within generate_rad, but outside of render_rad
            # TODO - there should be one generating function

            # Generate chunk if it doesnt exist
            for x in range(chunk_coords.x-generate_rad, chunk_coords.x+generate_rad+1):
                for z in range(chunk_coords.z-generate_rad, chunk_coords.z+generate_rad+1):
                    if (x, 0, z) not in self.chunks:
                        surface, highest_point = self.generate_surface(x, z)
                        # Get max value in surface
                        max_y_chunk = int(highest_point/16)+1
                        for y in range(max_y_chunk):
                            for y in range(chunk_coords.y-render_rad, chunk_coords.y+render_rad+1):
                                if (x, y, z) not in self.chunks:
                                    self.new_chunk(x, y, z, surface)

    def new_chunk(self, x, y, z, surface):
        # TODO - This is bad style
        self.chunks[(x, y, z)] = chunk.Chunk(x, y, z, surface, self.textures, self)

        # This should be threaded - generate_chunk_default is thread safe if _find_exposed_blocks is removed
        self.chunks[(x, y, z)].generate_chunk_default()

        # Find exposed blocks should be called from here
        # With Locking

    def render(self):
        # Load extra blocks from queue
        self.generate_block_faces()

        # Now render batches created
        render_rad = 5
        for x in range(self._loaded_position.x-render_rad, self._loaded_position.x+render_rad+1):
            for z in range(self._loaded_position.z-render_rad, self._loaded_position.z+render_rad+1):
                for y in range(self._loaded_position.y-render_rad, self._loaded_position.y+render_rad+1):
                    if (x, y, z) in self.chunks:
                        self.chunks[(x, y, z)].render()

    def generate_block_faces(self):

        # TODO - Can throttle here
        # This is causing a crash
        queue_size = self.block_generation_queue.qsize()
        if queue_size > 0:
            queue_loop = 500
            if queue_size < 500:
                queue_loop = queue_size
            for i in range(queue_loop):
                # TODO - if May still be required to check the queue still has values, could use a try and except

                chunk_object, x, y, z = self.block_generation_queue.get()
                chunk_object.create_exposed_face(x, y, z)

    def remove_block(self, coords):
        # Find chunk which block is in
        found_chunk = self._find_chunk(coords)
        if found_chunk:
            found_chunk.remove_block(coords)

    def create_block(self, coords):
        chunk_coords = (int(math.floor(coords[0]/16)), int(math.floor(coords[1]/16)), int(math.floor(coords[2]/16)))
        if chunk_coords in self.chunks:
            chunk = self.chunks[chunk_coords]
            # Find block coordinates local to chunk
            block_coords = (coords[0], coords[1], coords[2])
            chunk.create_block(block_coords)

    def find_block(self, coords):
        block_found = False
        block_chunk = self._find_chunk(coords)
        if block_chunk:
            block_found = block_chunk.find_block(coords)
        return block_found

    def find_chunk_coords(self, coords):
        return Vec3(int(math.floor(coords.x/16)), int(math.floor(coords.y/16)), int(math.floor(coords.z/16)))

    def _find_chunk(self, coords):
        # Takes in real coords of block, returns the chunk that the block exists in
        chunk_coords = (int(math.floor(coords[0]/16)), int(math.floor(coords[1]/16)), int(math.floor(coords[2]/16)))
        if chunk_coords in self.chunks:
            return self.chunks[chunk_coords]
        return None

    def update_position(self, coords):
        #pass
        # TODO - This should check if the coords are in a new chunk
        self._generate_chunks(coords)
