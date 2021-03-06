from pyglet.gl import *


class Renderer:
    def __init__(self, game):
        self.game = game
        self.init_opengl()
        self.full_screen = False
        self.game.set_location(500, 50)

    def on_draw(self):
        self.game.clear()
        self.set_3d()

    def init_opengl(self):
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_CULL_FACE)

        # Stop texture bleed
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def set_3d(self):
        width, height = self.game.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Angle, ratio, near, far
        # Angle was 65.0
        gluPerspective(90.0, width / float(height), 0.1, 120.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Stop texture bleed - TODO - Does this need to be called every frame?
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def set_2d(self):
        width, height = self.game.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


def draw_crosshair(coords):
    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', [coords[0], coords[1]]))

    # Draw extra points around centre
    c_width = 10
    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', [coords[0],         coords[1]-c_width]))
    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', [coords[0],         coords[1]+c_width]))
    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', [coords[0]-c_width, coords[1]]))
    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2i', [coords[0]+c_width, coords[1]]))
