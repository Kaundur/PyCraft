from pyglet.window import key
import pyglet
import math

import math_helper
import block


class Player:
    def __init__(self, world, gui):
        self.world = world
        self.player_height = 0.0
        self.position = [8, 60, 8]

        self.keys = key.KeyStateHandler()

        self.action_bar_keys = [key._1,
                                key._2,
                                key._3,
                                key._4,
                                key._5]

        self.drag = 0.7
        self.max_velocity = 0.3

        # negative rotation is up
        # -90 up, 90 down
        self.rotation = [100, 10]

        self.rotation_speed = 0.1

        self.max_rotation_up = -90
        self.max_rotation_down = 80

        self.gui = gui
        self.active_item_id = 1
        self.update_active_item(self.active_item_id)

        self.on_ground = False

        self.velocity = [0, 0, 0]

        # Should be independent of FPS
        self.dt = 1.0/30.0

        self.sight_vector = None
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
            block.highlight_cube(self.focused_block, 1)

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

        if self.on_ground:
            if keys[key.SPACE]:
                self.velocity[1] = 0.1

        self.world.update_position(self.position)

    def on_mouse_motion(self, x, y, dx, dy):
        self.rotation[0] += dx*self.rotation_speed
        self.rotation[1] -= dy*self.rotation_speed

        # Clip the rotation so that the camera doesn't go beyond the players natural movement,
        # 0deg is forward, up is negative, down is positive
        self.rotation[1] = math_helper.clip(self.rotation[1], self.max_rotation_up, self.max_rotation_down)

    def on_mouse_press(self, x, y, button, modifier):
        # Destroy block
        if button == pyglet.window.mouse.LEFT:
            if self.focused_block:
                self.world.remove_block(self.focused_block)
                # TODO - Using a tuple here, need to update other functions to accept pyclid
                # All world generation needs to be updated to accept it
                # TODO - I dont think pyclid is the correct way to go, will we be able to hash it for the chunk key?
                # I think itll work well for the player, but not for the blocks
                #self.world.remove_block((self.focused_block.x, self.focused_block.y, self.focused_block.z))
        # Create block
        if button == pyglet.window.mouse.RIGHT:
            if self.connecting_block:
                self.world.create_block(self.connecting_block, self.action_bar_item_map[self.active_item_id])

    def move(self, keys):
        # TODO - Can we combine some functions here, so that all the velocity is handled together
        # Get directional components
        x_move = math.sin(math.radians(self.rotation[0]))
        # Do I need to calculate this, they'll be 90deg out of phase
        z_move = math.cos(math.radians(self.rotation[0]))

        updated_velocity_x = self.velocity[0]*self.drag
        updated_velocity_z = self.velocity[2]*self.drag

        if keys[key.W]:
            updated_velocity_x += x_move
            updated_velocity_z -= z_move
        elif keys[key.S]:
            updated_velocity_x -= x_move
            updated_velocity_z += z_move
        elif keys[key.A]:
            updated_velocity_x -= z_move
            updated_velocity_z -= x_move
        elif keys[key.D]:
            updated_velocity_x += z_move
            updated_velocity_z += x_move

        self.velocity[0] = updated_velocity_x
        self.velocity[2] = updated_velocity_z

        # Find the maximum velocity for each component
        velocity_mag = math.sqrt(self.velocity[0]*self.velocity[0] + self.velocity[2]*self.velocity[2])
        # Cap velocity to the maximum velocity
        if velocity_mag > self.max_velocity:
            self.velocity[0] /= velocity_mag
            self.velocity[2] /= velocity_mag
            self.velocity[0] *= self.max_velocity
            self.velocity[2] *= self.max_velocity

    def update_player(self):
        # Block is 1 high. Is block also 1 down? accounts for 2.0
        feet_position = (int(self.position[0]), int(self.position[1]-2.0), int(self.position[2]))

        on_ground = self.world.find_block(feet_position)
        if on_ground and not self.on_ground:
            self.on_ground = True
            self.velocity[1] = 0.0

        if not on_ground:
            self.on_ground = False

        self.position[1] += self.velocity[1]
        if not self.on_ground:
            # V = u + 0.5 a*t**2
            self.velocity[1] += 0.5*self.world.gravity*self.dt**2

    def _do_collision(self):
        new_x = self.position[0] + self.velocity[0]
        new_z = self.position[2] + self.velocity[2]

        feet_position = (int(new_x), int(self.position[1]-1.0), int(new_z))
        body_position = (int(new_x), int(self.position[1]), int(new_z))
        collision = self.world.find_block(feet_position)
        # Check both bocks around the player
        if not collision:
            collision = self.world.find_block(body_position)

        if not collision:
            self.position[0] = new_x
            self.position[2] = new_z
