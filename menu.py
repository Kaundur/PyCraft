import pyglet
from pyglet.gl import *


import block


# TODO - Rename menu.py to GUI, and GUIController?
class MenuController:
    def __init__(self, game_textures, main):
        self.main = main
        self.game_textures = game_textures
        self.action_bar = ActionBar(self.game_textures)

    def render(self):
        self.action_bar.render()

    def update_active_item(self, active_item):
        self.action_bar.update_active_item(active_item)


class ActionBar:
    def __init__(self, game_textures):
        self.game_textures = game_textures
        self.texture_group = self.game_textures.texture_main
        self.active_item = 1
        self.item_rotate = 0
        self.action_bar_position = [-6.5, -6.0, -8.0]
        self.action_bar_items = []

        self.initialise_action_bar_items()

    def update_active_item(self, active_item):
        if self.active_item != active_item:
            self.active_item = active_item
            # reset the item_rotation for a cleaner animation
            self.item_rotate = 0

    def render(self):
        # Switch off depth test, so our 3D gui appears on top of the game
        glDisable(GL_DEPTH_TEST)

        self.action_bar_item()
        glEnable(GL_DEPTH_TEST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.item_rotate += 1.5

    def initialise_action_bar_items(self):
        # Base voxel for the action bar
        voxel = block.cube_coordinates((0, 0, 0), 1.0)
        for i in range(5):
            v_texture = self.game_textures.get_texture_full(i)
            self.action_bar_items.append(pyglet.graphics.Batch())
            self.action_bar_items[i].add(24, pyglet.gl.GL_QUADS, self.texture_group, ('v3f', voxel), ('t2f', v_texture))

    def action_bar_item(self):
        x = self.action_bar_position[0]
        y = self.action_bar_position[1]
        z = self.action_bar_position[2]

        for i in range(5):
            active = False
            if i+1 == self.active_item:
                active = True

            x += 2
            glLoadIdentity()

            glTranslatef(x, y, z)
            if active:
                glTranslatef(0.5, 0.5, 0.5)
                glRotatef(self.item_rotate, 0.0, 1.0, 0.0)
                glTranslatef(-0.5, -0.5, -0.5)

            self.action_bar_items[i].draw()
