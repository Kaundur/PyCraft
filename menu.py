import pyglet
from pyglet.gl import *

import textures
import menu_item
import math_helper
import block
import renderer

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
        self.active_item = 3
        self.item_rotate = 0

        self.initialise_action_bar_items()


    # def action_bar(self):
    #     items = 4
    #     box_size = 50
    #     x = int(self.width/2.0 - box_size*(items/2.0))
    #     y = 10

    def update_active_item(self, active_item):
        self.active_item = active_item

    def render(self):
        self.render_action_bar()

    def render_action_bar(self):
        # Switch off depth test, so our 3D gui items appear ontop of the game
        glDisable(GL_DEPTH_TEST)

        self.action_bar_item()

        glEnable(GL_DEPTH_TEST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.item_rotate += 1.5

    def initialise_action_bar_items(self):
        self.action_bar_items = []
        z = 0.0
        y = 0.0
        x = 0.0
        # Voxel doesnt need a location, just move based on position in action bar.
        # This way we can move the position of an item without recreating the batch
        voxel = block.voxel(x, y, z, 1.0)
        for i in range(5):
            v_texture = self.game_textures.get_texture_full(i)
            self.action_bar_items.append(pyglet.graphics.Batch())
            self.action_bar_items[i].add(24, pyglet.gl.GL_QUADS, self.texture_group, ('v3f', voxel), ('t2f', v_texture))

    def action_bar_item(self):
        z = -8.0
        y = -6.0
        x = -6.5
        for i in range(5):
            active = False

            if i == self.active_item:

                active = True
            x += 2
            glLoadIdentity()

            glTranslatef(x, y, z)
            if active:
                glTranslatef(0.5, 0.5, 0.5)
                glRotatef(self.item_rotate, 0.0, 1.0, 0.0)
                glTranslatef(-0.5, -0.5, -0.5)

            self.action_bar_items[i].draw()



class MainMenu:
    def __init__(self, game):

        self.menu_batch = pyglet.graphics.Batch()

        # Pass game object in so we can render the mouse cursor
        self.game = game

        self.cursor_position = [self.game.width//2, self.game.height//2]

        self.textures = textures.Textures()
        #self.texture_group = texture_group
        self.texture_group = self.textures.texture_main

        self.menu = []
        self.mouse_over = False

        self.menu_items = []
        self.generate_menu_items()

        self.x_rotation = 45
        self.x_rotation = 0
        #self.y_rotation = -160
        self.y_rotation = 30
        self.y_rotation = 0

        self.z = -2.2
        self.y = -0.5
        self.x = -0.5

        voxel = block.voxel(self.x, self.y, self.z, 1)

        i = 1
        v_texture = self.textures.get_texture(i)

        self.menu_batch.add(24, pyglet.gl.GL_QUADS, self.texture_group, ('v3f', voxel), ('t2f', v_texture))
        #self.menu_batch.add(24, pyglet.gl.GL_QUADS, None, ('v3f', voxel))

    def centre_cursor(self):
        self.cursor_position = [self.game.width//2, self.game.height//2]

    def render_menu_items(self):
        for item in self.menu_items:
            item.render(self.cursor_position)

    # TODO - Need graphics for buttons
    def generate_menu_items(self):

        side = (1, 0, 0)
        self.menu_items.append(menu_item.MenuItem(-0.5, -0.40, -1.15, side))  # Text field, settings
        self.menu_items.append(menu_item.MenuItem(-0.5, -0.15, -1.15, side, True))#, self.toggle_full_screen))
        self.menu_items.append(menu_item.MenuItem(-0.5, 0.1, -1.15, side))

        side = (0, 0, 1)
        self.menu_items.append(menu_item.MenuItem(-0.54, -0.40, -2.15, side, True))#, self.start_game))
        self.menu_items.append(menu_item.MenuItem(-0.54, -0.15, -2.15, side, True))#, self.close_menu)) # Continue, should be blank for no game running
        self.menu_items.append(menu_item.MenuItem(-0.54, 0.1, -2.15, side, True))#, self.game.exit_game)) # Exit







    def on_mouse_press(self, x, y, button, modifier):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            for item in self.menu_items:
                item.click()

    def mouse_motion(self, x, y, dx, dy):
        self.cursor_position[0] += dx
        self.cursor_position[1] += dy

        if self.cursor_position[0] > self.game.width:
            self.cursor_position[0] = self.game.width
        elif self.cursor_position[0] < 0:
            self.cursor_position[0] = 0
        else:
            self.x_rotation -= dx*0.05

        if self.cursor_position[1] > self.game.height:
            self.cursor_position[1] = self.game.height
        elif self.cursor_position[1] < 0:
            self.cursor_position[1] = 0
        else:
            self.y_rotation += dy*0.05

        self.x_rotation = math_helper.clip(self.x_rotation, 0, 90)
        #self.y_rotation = math_helper.clip(self.y_rotation, -170, -120)

    def render(self):
        glDisable(GL_DEPTH_TEST)
        glLoadIdentity()

        glTranslatef(self.x+0.5, self.y+0.5, self.z+0.5)
        glRotatef(self.y_rotation, 1.0, 0.0, 0.0)
        glRotatef(self.x_rotation, 0.0, 1.0, 0.0)
        glTranslatef(-(self.x+0.5), -(self.y+0.5), -(self.z+0.5))

        self.menu_batch.draw()
        self.render_menu_items()

        glEnable(GL_DEPTH_TEST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def render_2d(self):
        # TODO - Render background alpha over the game
        renderer.draw_cursor(self.cursor_position)
