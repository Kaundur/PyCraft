import math
import Queue

from noise import pnoise2, snoise2, pnoise3, snoise3
from pyclid import Vec3

import chunk

# TODO - Issue with boarder around lowest blocks


class World:
    def __init__(self, textures):
        # Load in textures per world
        self.textures = textures
        # chunks around the player to render
        self.render_distance = 2
        self.gravity = -15.0

        self.current_centered_chunk = None

        # Not really a seed, the position of the noise in the 3D dimension
        self.seed = 0
        self.block_generation_queue = Queue.Queue()
        self._loaded_position = Vec3()

        # Chunks around the player to generate
        self.generate_distance = 5
        self.chunks = {}
        self.surface = {}


    def generate_world(self, position):
        chunk_x = int(position.x/16)
        chunk_y = int(position.y/16)
        chunk_z = int(position.z/16)
        self._loaded_position = Vec3(chunk_x, chunk_y, chunk_z)
        for x in range(chunk_x-self.generate_distance, chunk_x+self.generate_distance):
            for z in range(chunk_z-self.generate_distance, chunk_z+self.generate_distance):
                if (x, 0, z) not in self.chunks:
                    self.generate_surface(x, z)
                    max_y_chunk = chunk_y +self.generate_distance
                    for y in range(max_y_chunk):
                        if (x, y, z) not in self.chunks:
                            self.new_chunk(x, y, z)

        self._generate_chunk_batches(position)

    def _generate_chunk_batches(self, position):
        # Generate the faces of the surface
        chunk_x = int(position.x/16)
        chunk_y = int(position.y/16)
        chunk_z = int(position.z/16)

        for x in range(chunk_x-self.generate_distance+1, chunk_x+self.generate_distance-1):
            for z in range(chunk_z-self.generate_distance+1, chunk_z+self.generate_distance-1):
                max_y_chunk = chunk_y + self.generate_distance+1
                for y in range(max_y_chunk):
                    if (x, y, z) in self.chunks:
                        self.chunks[(x, y, z)].find_exposed_blocks()

    def generate_surface(self, chunk_x, chunk_z):
        real_pos_x = chunk_x*16
        real_pos_z = chunk_z*16

        if (real_pos_x, real_pos_z) not in self.surface:
            octaves = 10
            freq = 16.0 * octaves
            scale = 5

            for x in xrange(real_pos_x, real_pos_x + 16):
                for z in xrange(real_pos_z, real_pos_z + 16):
                    point = int((snoise3(x / freq, z / freq, self.seed, octaves) * 127.0 + 128.0)/scale)
                    self.surface[(x, z)] = point

    def get_surface(self, x, z):
        return self.surface[(x, z)]

    def new_chunk(self, x, y, z):
        # TODO - This is bad style
        self.chunks[(x, y, z)] = chunk.Chunk(x, y, z, self.textures, self)
        # This should be threaded - generate_chunk_default is thread safe if _find_exposed_blocks is removed
        self.chunks[(x, y, z)].generate_chunk_default()

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
        # TODO - Can use if not self.block_generation_queue.empty()

        blocks_per_frame = 500
        queue_size = self.block_generation_queue.qsize()
        if queue_size > 0:
            print queue_size
            queue_loop = blocks_per_frame
            if queue_size < blocks_per_frame:
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

    def create_block(self, coords, block_id):
        chunk_coords = (int(math.floor(coords[0]/16)), int(math.floor(coords[1]/16)), int(math.floor(coords[2]/16)))
        if chunk_coords in self.chunks:
            chunk = self.chunks[chunk_coords]
            # Find block coordinates local to chunk
            block_coords = (coords[0], coords[1], coords[2])
            chunk.create_block(block_coords, block_id)

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
        # TODO - This should check if the coords are in a new chunk

        if self.find_chunk_coords(coords) != self.current_centered_chunk:
            self.current_centered_chunk = self.find_chunk_coords(coords)
            self.generate_world(coords)
