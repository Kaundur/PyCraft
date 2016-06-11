import pyglet
from pyglet.gl import *

import math_helper
import textures
import block

import letters


# TODO - This shouldn't draw anything
class MenuItem:
    def __init__(self, x, y, z, side, active=False, function=None):
        self.x = x
        self.y = y
        self.z = z
        self.side = side
        self.active = active
        self.function = function

    def render(self, cursor_position):

        height = 0.2

        side_offset = 0.1
        height_offset = 0.1

        mouse_over_color = (255, 255, 255)*4
        default_color = (255, 0, 0)*4

        # Need to generalise this, doesnt work for side (1, 0, 0)
        point_1 = self.x+side_offset*self.side[0], self.y+height_offset, self.z+side_offset*self.side[2]

        point_2 = self.x+side_offset*self.side[0], self.y+height_offset+height, self.z+side_offset*self.side[2]
        point_3 = self.x+(1.0-side_offset)*self.side[0], self.y+height_offset+height, self.z+(1.0-side_offset)*self.side[2]
        point_4 = self.x+(1.0-side_offset)*self.side[0], self.y+height_offset, self.z+(1.0-side_offset)*self.side[2]

        poly = [math_helper.get_3d_menu_screen_coords(point_1),
                math_helper.get_3d_menu_screen_coords(point_2),
                math_helper.get_3d_menu_screen_coords(point_3),
                math_helper.get_3d_menu_screen_coords(point_4)]

        # TODO - Add blocks as pixel art for words, attach to menu item frame
        # TODO - Cannot make drawing small enough
        #block.highlight_cube(self.x, self.y, self.z, 0.00001)


        if self.active and math_helper.point_in_poly(cursor_position[0], cursor_position[1], poly):
            self.mouse_over = True
        else:
            self.mouse_over = False

        color = default_color
        if self.mouse_over:
            color = mouse_over_color

        item = self.x+side_offset*self.side[0], self.y+height_offset, self.z+side_offset*self.side[2], \
               self.x+side_offset*self.side[0], self.y+height_offset+height, self.z+side_offset*self.side[2], \
               self.x+(1.0-side_offset)*self.side[0], self.y+height_offset+height, \
               self.z+(1.0-side_offset)*self.side[2], \
               self.x+(1.0-side_offset)*self.side[0], self.y+height_offset, \
               self.z+(1.0-side_offset)*self.side[2]


        #item_texture = textures.menu_items()


        #glEnable(GL_TEXTURE_2D)
        # Stop texture bleed
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        #image = pyglet.image.load('Images/GameMenu.png')
        #texture = image.get_texture()

        #coords = [0, 0, 0, 1, 1, 1, 1, 0]
        #pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v3f', item), ('t2f', coords))
        pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP, ('v3f', item),  ('c3B', color))

        letters.draw_text(self.x, self.y, self.z)


    def click(self):
        if self.mouse_over:
            if self.function:
                self.function()
            print self.x, self.y