import pyglet
from pyglet.gl import *
from pyglet.window import key

import renderer
import menu
import world
import player
import textures


FRAMES_PER_SECOND = 30


class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # TODO - How does this super work, overrides the init of Window
        super(Game, self).__init__(*args, **kwargs)

        self.textures = textures.Textures()

        #self.main_menu = menu.MainMenu(self)
        self.main_menu = None

        self.render = renderer.Renderer(self)

        self.set_exclusive_mouse()

        self.world = world.World(self.textures)


        self.player = player.Player(self.world)
        self.world.generate_world(self.player.position)


        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # If is in menu or in game
        self.game_state = None
        self.in_menu = False

    def toggle_menu(self):
        self.in_menu = not self.in_menu

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.toggle_menu()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        #if self.in_menu:
        #    self.main_menu.mouse_motion(x, y, dx, dy)
        #else:
        self.player.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifier):
        #if self.in_menu:
        #    self.main_menu.on_mouse_press(x, y, button, modifier)

        #else:
        self.player.on_mouse_press(x, y, button, modifier)

    def on_mouse_release(self, x, y, button, modifiers):
        pass
        #if self.in_menu:
        #    self.main_menu.on_mouse_release(x, y, button, modifiers)

    def on_draw(self):


        # Maybe render is a bad idea
        # Could just use to set up opengl


        self.player.handle_keys(self.keys)
        self.player.update_player()

        self.player.get_sight_vector()

        self.render.on_draw()

        glRotatef(self.player.rotation.y, 1.0, 0.0, 0.0)
        glRotatef(self.player.rotation.x, 0.0, 1.0, 0.0)

        glTranslatef(-self.player.position.x,
                     -self.player.position.y+self.player.player_height,
                     -self.player.position.z)

        self.world.render()

        #if self.in_menu:
        #    self.main_menu.render()

        self.player.draw_focused_block()

        self.render.set_2d()

        #if self.in_menu:
        #    self.main_menu.render_2d()
        #else:
        renderer.draw_cursor([self.width/2.0, self.height/2.0])

    def exit_game(self):
        pyglet.app.exit()


def main():
    Game(width=800, height=600, caption='PyCraft')
    frame_rate = 1.0/FRAMES_PER_SECOND
    pyglet.clock.schedule_interval(lambda dt: None, frame_rate)
    pyglet.app.run()


if __name__ == '__main__':
    main()
