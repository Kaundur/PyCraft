import math
import Queue
import thread

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

        self.current_centered_chunk = None

        # Not really a seed, the position of the noise in the 3D dimension
        self.seed = 0
        self.block_generation_queue = Queue.Queue()
        self._loaded_position = Vec3()

        # Chunks around the player to generate
        self.generate_distance = 5
        self.chunks = {}
        self.surface = {}

        self.generation_threads = []

    def generate_world(self, position):
        # Get chunk coordinates (player coordinates divided by chunk size and floored)
        # 5, 20, 40 >>> 5//16, 20//16, 40//16 >>> 0, 1, 2
        # Store the position, so that we have a reference point to generate and render the chunks around
        self._loaded_position = chunk.get_chunk_coords(position)

        for x in range(self._loaded_position.x-self.generate_distance, self._loaded_position.x + self.generate_distance):
            for z in range(self._loaded_position.z-self.generate_distance, self._loaded_position.z +self.generate_distance):
                if (x, 0, z) not in self.chunks:
                    self.generate_surface(x, z)
                    # TODO - What is this doing?
                    max_y_chunk = self._loaded_position.y + self.generate_distance
                    for y in range(max_y_chunk):
                        if (x, y, z) not in self.chunks:
                            self.generate_new_chunk(x, y, z)

        self._generate_chunk_batches(position)

    def _generate_chunk_batches(self, position):
        # Generate the faces of the surface
        for x in range(self._loaded_position.x-self.generate_distance+1, self._loaded_position.x+self.generate_distance-1):
            for z in range(self._loaded_position.z-self.generate_distance+1, self._loaded_position.z+self.generate_distance-1):
                max_y_chunk = self._loaded_position.y + self.generate_distance+1
                for y in range(max_y_chunk):
                    if (x, y, z) in self.chunks:
                        thread.start_new_thread(self.chunks[(x, y, z)].find_exposed_blocks, ())

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

    def generate_new_chunk(self, x, y, z):
        self.chunks[(x, y, z)] = chunk.Chunk(x, y, z, self.textures, self)
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
        found_chunk = self.find_chunk(coords)
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
        block_chunk = self.find_chunk(coords)
        if block_chunk:
            block_found = block_chunk.find_block(coords)
        return block_found

    def find_chunk_coords(self, coords):
        return Vec3(int(math.floor(coords.x/16)), int(math.floor(coords.y/16)), int(math.floor(coords.z/16)))

    def find_chunk(self, coords):
        # Takes in real coords of block, returns the chunk that the block exists in
        chunk_coords = (int(math.floor(coords[0]/16)), int(math.floor(coords[1]/16)), int(math.floor(coords[2]/16)))
        if chunk_coords in self.chunks:
            return self.chunks[chunk_coords]
        return None

    def update_position(self, coords):
        if self.find_chunk_coords(coords) != self.current_centered_chunk:
            self.current_centered_chunk = self.find_chunk_coords(coords)
            self.generate_world(coords)

