import pyglet
from pyglet.gl import *
from pyglet.window import key

import renderer
import menu
import world
import player
import textures


FRAMES_PER_SECOND = 30
# Needs to be an integer
# TODO - Whats the divide by 1.0 for?
GAME_TICK = int(FRAMES_PER_SECOND/1.0)


class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # TODO - How does this super work, overrides the init of Window
        super(Game, self).__init__(*args, **kwargs)
        self.tick_counter = 0

        self.textures = textures.Textures()

        self.game_menu = menu.MenuController(self.textures, self)

        self.main_menu = None

        self.render = renderer.Renderer(self)

        self.set_exclusive_mouse()

        self.world = world.World(self.textures)

        self.player = player.Player(self.world, self.game_menu)

        self.world.current_centered_chunk = self.world.find_chunk_coords(self.player.position)
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
        self.player.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifier):
        self.player.on_mouse_press(x, y, button, modifier)

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def do_tick(self):
        self.tick_counter += 1
        if self.tick_counter % GAME_TICK == 0:
            self.world.do_tick()
            self.tick_counter = 0

    def on_draw(self):
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

        self.player.draw_focused_block()

        # For now this just renders the action bar
        self.game_menu.render()

        self.render.set_2d()

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
