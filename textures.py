import pyglet
from pyglet.graphics import TextureGroup
from pyglet.gl import *


class Textures:
    def __init__(self):
        self.texture_path = 'Images/tex_main.png'
        self.menu_texture_path = 'Images/GameMenu.png'
        self.texture_image_size_x = 8
        self.texture_image_size_y = 8

        # Load in textures
        self.texture_main = TextureGroup(pyglet.image.load(self.texture_path).get_texture())
        self.menu_textures = TextureGroup(pyglet.image.load(self.texture_path).get_texture())



        self.textures = {}
        self.load_texture_dictionary()

    def get_texture(self, voxel_id):
        return self.textures[voxel_id]

    def load_texture_dictionary(self):
        # Map texture to block id
        self.textures[0] = self._get_texture((0, 1), (0, 1), (0, 1))  # Dirt
        self.textures[1] = self._get_texture((0, 0), (0, 1), (1, 0))  # Grass
        self.textures[2] = self._get_texture((1, 1), (1, 1), (1, 1))  # Stone
        self.textures[3] = self._get_texture((2, 0), (2, 0), (2, 0))  # Bedrock
        self.textures[4] = self._get_texture((2, 1), (2, 1), (2, 1))  # Brick

    def _get_texture(self, top, bottom, sides):
        texture_coords = []

        texture_coords.append(self.texture_face_coord(top[0], top[1]))
        texture_coords.append(self.texture_face_coord(bottom[0], bottom[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))
        texture_coords.append(self.texture_face_coord(sides[0], sides[1]))


        # This is the whole block, only require the face
        # texture_coords.extend(self.texture_face_coord(top[0], top[1]))
        # texture_coords.extend(self.texture_face_coord(bottom[0], bottom[1]))
        #
        # texture_coords.extend(self.texture_face_coord(sides[0], sides[1]))
        # texture_coords.extend(self.texture_face_coord(sides[0], sides[1]))
        # texture_coords.extend(self.texture_face_coord(sides[0], sides[1]))
        # texture_coords.extend(self.texture_face_coord(sides[0], sides[1]))

        return texture_coords

    def texture_face_coord(self, x, y):
        dx = 1.0/self.texture_image_size_x
        dy = 1.0/self.texture_image_size_x

        x *= dx
        y *= dy

        # TODO - Is it better to reverse the order of the texture, or should the voxel be reversed ?
        # return x, y, x+dx, y, x+dx, y+dy, x, y+dy
        return x+dx, y+dy, x, y+dy, x, y, x+dx, y

# TODO - REMOVE Menu_items graphics
def menu_items():

    texture_path = 'Images/GameMenu.png'

    #texture_main = TextureGroup(pyglet.image.load(texture_path).get_texture())

    texture_main = None

    return texture_main