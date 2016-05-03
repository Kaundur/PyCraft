__author__ = 'Kaundur'

from pyglet.window import key
import pyglet
import math
from pyclid import Vec2, Vec3

import math_helper
import chunk
import block


class Player:
    def __init__(self, world):
        self.world = world
        self.player_height = 0.0
        self.position = Vec3(16, 60, 16)
        # negative rotation is up
        # -90 up, 90 down
        self.rotation = Vec2(100, 10)
        self.speed = 1.0

        self.flying = False
        self.on_ground = False

        self.velocity = Vec3()

        # TODO - Should be external of player
        self.dt = 1.0/30.0

        self.sight_vector = None
        self.get_sight_vector()

        # Coords in real space
        self.focused_block = None
        self.connecting_block = None

    def get_sight_vector(self):
        self.sight_vector = math_helper.get_sight_vector(self)
        prev_block, pos = math_helper.los_collision_short(self.world, self)
        self.focused_block = pos
        self.connecting_block = prev_block

    def draw_focused_block(self):
        if self.focused_block:
            x, y, z = self.focused_block[0], self.focused_block[1], self.focused_block[2]
            block.highlight_cube(x, y, z, 1)

    def handle_keys(self, keys):
        self.move(keys)

        self._do_collision()

        if self.flying:
            if keys[key.LSHIFT]:
                self.position.y -= 1.0
            if keys[key.SPACE]:
                self.position.y += 1.0
        else:
            if self.on_ground:
                if keys[key.SPACE]:
                    self.velocity.y = 0.1

        # TODO - This should only update when the player changes position
        self.world.update_position(self.position)

    def move(self, keys):
        x_move = self.speed*math.sin(math.radians(self.rotation.x))*0.1
        z_move = self.speed*math.cos(math.radians(self.rotation.x))*0.1

        new_vel_x = self.velocity.x
        new_vel_z = self.velocity.z

        new_vel_x *= 0.7
        new_vel_z *= 0.7

        if keys[key.W]:
            new_vel_x += x_move
            new_vel_z -= z_move
        elif keys[key.S]:
            new_vel_x -= x_move
            new_vel_z += z_move
        elif keys[key.A]:
            new_vel_x -= z_move
            new_vel_z -= x_move
        elif keys[key.D]:
            new_vel_x += z_move
            new_vel_z += x_move

        self.velocity.x = new_vel_x
        self.velocity.z = new_vel_z

        self.velocity.x = math_helper.clip(self.velocity.x, -0.3, 0.3)
        self.velocity.z = math_helper.clip(self.velocity.z, -0.3, 0.3)

    def update_player(self):
        # Should be defined in world, dt should come from main (FPS)
        self._do_vertical_update()

    def on_mouse_motion(self, x, y, dx, dy):
        self.rotation.x += dx*0.1
        self.rotation.y -= dy*0.1

        self.rotation.y = math_helper.clip(self.rotation.y, -90.0, 80.0)

    # TODO - This should add a force, not update position. This will stop keys overriding physics
    def on_mouse_press(self, x, y, button, modifier):
        if button == pyglet.window.mouse.LEFT:
            if self.focused_block:
                self.world.remove_block(self.focused_block)
        if button == pyglet.window.mouse.RIGHT:
            if self.connecting_block:
                self.world.create_block(self.connecting_block)

    def _do_collision(self):

        new_x = self.position.x + self.velocity.x
        new_z = self.position.z + self.velocity.z

        feet_position = (int(new_x), int(self.position.y-1.0), int(new_z))
        body_position = (int(new_x), int(self.position.y), int(new_z))
        collision = self.world.find_block(feet_position)
        # Check both bocks around the player
        if not collision:
            collision = self.world.find_block(body_position)

        if not collision:
            #self.velocity.x = new_x
            #self.velocity.z = new_z
            #self.position.x += self.velocity.x
            #self.position.z += self.velocity.z

            self.position.x = new_x
            self.position.z = new_z

            # Check if player has entered a new chunk
            # If so Generate chunks required, sent correct chunks to render

            self._get_current_chunk()

    def _get_current_chunk(self):
        pass

    def _do_vertical_update(self):
        # TODO - Kind of strange, most likely due to the flipping of a world and player_height
        # Block is 1 high,
        feet_position = (int(self.position.x), int(self.position.y-2.0), int(self.position.z))

        on_ground = self.world.find_block(feet_position)
        if on_ground and not self.on_ground:
            self.on_ground = True
            self.velocity.y = 0.0

        if not on_ground:
            self.on_ground = False

        self.position.y += self.velocity.y
        if not self.on_ground:
            # V = u + 0.5 a*t**2
            self.velocity.y += 0.5*self.world.gravity*self.dt**2

