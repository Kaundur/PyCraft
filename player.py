from pyglet.window import key
import pyglet
import math

import pyclid

import math_helper
import block


class Player:
    def __init__(self, world, gui):
        self.world = world
        self.player_height = 0.0
        self.position = pyclid.Vec3(8, 60, 8)

        self.keys = key.KeyStateHandler()

        self.action_bar_keys = [key._1,
                                key._2,
                                key._3,
                                key._4,
                                key._5]

        # negative rotation is up
        # -90 up, 90 down
        self.rotation = pyclid.Vec2(100, 10)
        self.speed = 1.0
        self.gui = gui
        self.active_item_id = 1
        self.update_active_item(self.active_item_id)

        self.flying = False
        self.on_ground = False

        self.velocity = pyclid.Vec3()

        # TODO - Should be external of player - Need a physics class
        # Doesn't need to match the FPS, FPS just shows whats happened with the physical objects
        self.dt = 1.0/30.0

        self.sight_vector = pyclid.Vec3()
        self.get_sight_vector()

        # Coords in real space
        self.focused_block = None
        self.connecting_block = None

        # Map action bar item to block id
        self.action_bar_item_map = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}

    def update_active_item(self, item_index):
        self.active_item_id = item_index
        self.gui.update_active_item(self.active_item_id)

    def get_sight_vector(self):
        self.sight_vector = math_helper.get_sight_vector(self.rotation)
        self.connecting_block, self.focused_block = math_helper.los_collision(self.world, self.position, self.sight_vector)

    def draw_focused_block(self):
        if self.focused_block:
            # TODO - Temp, to aid with switch to pyclid
            f_block = pyclid.Vec3(self.focused_block[0], self.focused_block[1], self.focused_block[2])
            block.highlight_cube(f_block, 1)

    def handle_action_bar_keys(self, keys):
        # TODO - Store the keys in an array so they can be updated
        if keys[self.action_bar_keys[0]]:
            self.update_active_item(1)
        elif keys[self.action_bar_keys[1]]:
            self.update_active_item(2)
        elif keys[self.action_bar_keys[2]]:
            self.update_active_item(3)
        elif keys[self.action_bar_keys[3]]:
            self.update_active_item(4)
        elif keys[self.action_bar_keys[4]]:
            self.update_active_item(5)

    def handle_keys(self, keys):

        self.handle_action_bar_keys(keys)

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
                self.world.create_block(self.connecting_block, self.action_bar_item_map[self.active_item_id])

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
            self.position.x = new_x
            self.position.z = new_z

    def _do_vertical_update(self):

        # Block is 1 high. Is block also 1 down? accounts for 2.0
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
