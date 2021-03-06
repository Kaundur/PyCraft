import pyglet
from pyglet.gl import *
from pyglet.window import key

import renderer
import menu
import world
import chunk
import player
import textures

FRAMES_PER_SECOND = 30


class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)

        # Will need updating if the screen size changes
        self.cursor_coordinates = [int(self.width/2.0), int(self.height/2.0)]

        self.tick_counter = 0

        self.textures = textures.Textures()

        self.game_menu = menu.MenuController(self.textures, self)

        self.render = renderer.Renderer(self)

        self.set_exclusive_mouse()

        self.world = world.World(self.textures)

        self.player = player.Player(self.world, self.game_menu)

        self.world.current_centered_chunk = chunk.find_chunk_coords(self.player.position)
        self.world.generate_world(self.player.position)

        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # If is in menu or in game
        self.game_state = None
        self.in_menu = False

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.exit_game()

    def on_mouse_motion(self, x, y, dx, dy):
        self.player.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifier):
        self.player.on_mouse_press(x, y, button, modifier)

    def on_draw(self):
        self.player.handle_keys(self.keys)
        self.player.update_player()

        self.player.get_sight_vector()

        self.render.on_draw()

        glRotatef(self.player.rotation[1], 1.0, 0.0, 0.0)
        glRotatef(self.player.rotation[0], 0.0, 1.0, 0.0)

        glTranslatef(-self.player.position[0],
                     -self.player.position[1]+self.player.player_height,
                     -self.player.position[2])

        self.world.render()

        self.player.draw_focused_block()

        # For now this just renders the action bar
        self.game_menu.render()

        self.render.set_2d()

        renderer.draw_crosshair(self.cursor_coordinates)

    @staticmethod
    def exit_game():
        pyglet.app.exit()


def main():
    Game(width=800, height=600, caption='PyCraft')
    frame_rate = 1.0/FRAMES_PER_SECOND
    pyglet.clock.schedule_interval(lambda dt: None, frame_rate)
    pyglet.app.run()


if __name__ == '__main__':
    main()
