import pyglet
from pyglet.graphics import TextureGroup
from pyglet.gl import *


class Textures:
    def __init__(self):
        self.texture_path = 'Images/tex_main.png'
        self.texture_pixel_size_x = 8
        self.texture_pixel_size_y = 8

        # Load in textures
        self.texture_main = TextureGroup(pyglet.image.load(self.texture_path).get_texture())

        self.textures = {}
        self.load_texture_dictionary()

    # This returns the texture coords split by each face
    def get_texture(self, voxel_id):
        return self.textures[voxel_id]

    def load_texture_dictionary(self):
        # Map texture to block id
        self.textures[0] = self._get_texture((0, 1), (0, 1), (0, 1))  # Dirt
        self.textures[1] = self._get_texture((0, 0), (0, 1), (1, 0))  # Grass
        self.textures[2] = self._get_texture((1, 1), (1, 1), (1, 1))  # Stone
        self.textures[3] = self._get_texture((2, 0), (2, 0), (2, 0))  # Bedrock
        self.textures[4] = self._get_texture((2, 1), (2, 1), (2, 1))  # Brick

    # TODO - Should the textures be stored as face and full values?
    def get_texture_full(self, voxel_id):
        face_texture = self.textures[voxel_id]
        voxel_texture = []
        voxel_texture.extend(face_texture[0])
        voxel_texture.extend(face_texture[1])
        voxel_texture.extend(face_texture[2])
        voxel_texture.extend(face_texture[3])
        voxel_texture.extend(face_texture[4])
        voxel_texture.extend(face_texture[5])

        return voxel_texture

    def _get_texture(self, top, bottom, sides):
        texture_coords = []
        texture_coords.append(self.texture_face_coord(top[0], top[1]))
        texture_coords.append(self.texture_face_coord(bottom[0], bottom[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))

        return texture_coords

    def texture_face_coord(self, x, y):
        dx = 1.0/self.texture_pixel_size_x
        dy = 1.0/self.texture_pixel_size_x

        x *= dx
        y *= dy

        # TODO - Is it better to reverse the order of the texture, or should the voxel be reversed ?
        # return x, y, x+dx, y, x+dx, y+dy, x, y+dy
        return x+dx, y+dy, x, y+dy, x, y, x+dx, y
