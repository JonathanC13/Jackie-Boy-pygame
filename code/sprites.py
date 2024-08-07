from math import sin, cos, radians, atan2, degrees

from settings import *


class Sprite(pygame.sprite.Sprite):
	def __init__(self, pos, surf = pygame.Surface((TILE_SIZE,TILE_SIZE)), groups = None, type = None, z = Z_LAYERS["main"], damage = 1, can_damage = False):
		
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_frect(topleft = pos)
		self.mask = pygame.mask.from_surface(self.image)

		self.old_rect = self.rect.copy()
		self.type = type
		self.z = z

		self.damage = damage
		self.can_damage = can_damage

	def get_damage(self):
		return self.damage

	def get_can_damage(self):
		return self.can_damage
	
	def get_type(self):
		return self.type

class AnimatedSprite(Sprite):
	def __init__(self, pos, frames, groups, type = None, z = Z_LAYERS["main"], animation_speed = ANIMATION_SPEED, damage = 1, can_damage = False):

		self.frames, self.frame_index = frames, 0
		self.len_frames = len(frames)
		super().__init__(pos, self.frames[self.frame_index], groups, type, z, damage, can_damage)

		self.animation_speed = animation_speed
		
	def set_frames(self, frames):
		self.frame_index = 0
		self.frames = frames
		self.len_frames = len(frames)

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt/FPS_TARGET
		if (self.frame_index >= self.len_frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]
		self.mask = pygame.mask.from_surface(self.image)

	def update(self, dt, event_list):
		self.animate(dt)

class Item(AnimatedSprite):
	def __init__(self, item_type, pos, frames, groups, data, player_obj = None):
		super().__init__(pos, frames, groups, item_type)
		self.rect.center = pos
		self.item_type = item_type
		self.data = data
		self.player_obj = player_obj

	def get_item_type(self):
		return self.item_type

	def activate(self):
		if self.item_type == "kibble":
			self.data.kibble = self.data.kibble + 1
		elif (self.item_type == "denta"):
			self.data.denta = self.data.denta + 1

		#self.data.print_data()

	def update(self, dt, event_list = None):
		if self.player_obj is not None:
			# move toward player
			start = pygame.math.Vector2(self.rect.center)
			end = pygame.math.Vector2(self.player_obj.hitbox_rect.center)
			if (end - start) != (0, 0):
				velocity = (end - start).normalize() * 5
			else:
				velocity = pygame.math.Vector2(0, 0)

			self.rect.center += velocity * dt

		self.animate(dt)

class ParticleEffectSprite(AnimatedSprite):
	def __init__(self, pos, frames, groups):
		super().__init__(pos, frames, groups)
		self.rect.center = pos
		self.z = Z_LAYERS["fg"]

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt/FPS_TARGET
		
		if self.frame_index < len(self.frames):
			self.image = self.frames[int(self.frame_index)]
		else:
			self.kill()

class MovingSprite(AnimatedSprite):
	def __init__(self, frames, start_pos, end_pos, path_plane, start_end = False, speed = 0, full_collision = True, flip = False, groups = None, type = None, z = Z_LAYERS["main"]):

		super().__init__(start_pos, frames, groups, type, z)
		
		self.start_pos = start_pos
		self.end_pos = end_pos

		# movement
		self.moving = True
		self.flip = flip
		self.start_end = start_end
		self.speed = speed
		self.full_collision = full_collision
		self.path_plane = path_plane


		if (self.path_plane == "x"):
			if (not start_end):
				self.direction = vector(1, 0)
				self.rect.midleft = start_pos
			else:
				self.direction = vector(-1, 0)
				self.rect.midright = end_pos
		else:
			if (not start_end):
				self.direction = vector(0, 1)
				self.rect.midtop = start_pos
			else:
				self.direction = vector(0, -1)
				self.rect.midbottom = end_pos

		self.reverse = {'x': False, 'y': False}

	def check_border(self):
		if (self.path_plane == "x"):
			if (self.rect.right >= self.end_pos[0] and self.direction.x == 1):
				self.direction.x = -1
				self.rect.right = self.end_pos[0]
			elif (self.rect.left <= self.start_pos[0] and self.direction.x == -1):
				self.direction.x = 1
				self.rect.left = self.start_pos[0]
			self.reverse['x'] = True if self.direction.x < 0 else False
		else:
			if (self.rect.bottom >= self.end_pos[1] and self.direction.y == 1):
				self.direction.y = -1
				self.rect.bottom = self.end_pos[1]
			elif (self.rect.top <= self.start_pos[1] and self.direction.y == -1):
				self.direction.y = 1
				self.rect.top = self.start_pos[1]
			self.reverse['y'] = True if self.direction.y > 0 else False

	def update(self, dt, event_list):
		self.old_rect = self.rect.copy()
		self.rect.center += self.direction * self.speed * dt
		self.check_border()

		self.animate(dt)
		if (self.flip):
			self.image = pygame.transform.flip(self.image, self.reverse['x'], self.reverse['y'])

class Orbit(AnimatedSprite):
	def __init__(self, pos, frames, radius, speed, start_angle, end_angle, clockwise = True, groups = None, type = None,z = Z_LAYERS['main'], direction_changes = -1, rotate = False, image_orientation = IMAGE_RIGHT, damage = 1, can_damage = False, **kwargs):
		# note: Clockwise if want an end angle > 360. Do not offset, put the added degrees. I.e. 370, not 10
		#	Counter Clockwise, if starting angle > end angle and start angle >= 0. use base 360. I.e. 370, not 10
		self.center = pos
		self.radius = radius
		self.speed = speed
		self.start_angle = start_angle
		self.end_angle = end_angle
		self.clockwise = clockwise	# starting orbit direction
		self.angle = self.start_angle
		self.direction = 1 if clockwise else -1	# current orbit direction 
		self.full_circle = True if self.end_angle == -1 else False
		self.rotate = rotate
		self.image_orientation = image_orientation
		self.direction_changes = direction_changes
		self.direction_changes_completed = 0

		# trigonometry
		# sin(deg) = op/hyp
		y = self.center[1] + sin(radians(self.angle)) * self.radius
		# cos(deg) = adj/hyp
		x = self.center[0] + cos(radians(self.angle)) * self.radius

		super().__init__(pos = (x,y), frames = frames, groups = groups, type = type, z = z, damage = damage, can_damage = can_damage, **kwargs)

	def get_damage(self):
		return self.damage

	def get_can_damage(self):
		return self.can_damage

	def rotate_image(self, image_orientation):
		direction = pygame.math.Vector2(math.cos(radians(self.angle)), math.sin(radians(self.angle))).normalize()
		angle = degrees(atan2(direction.x, direction.y)) - image_orientation		#atan2(y, x). y = x and x = y and then - image_orientation (this also requires user to start the image in the correct position relative to the center of the object orbiting) for correct angle of rotation

		if (direction.x > 0 or (image_orientation in [IMAGE_UP, IMAGE_DOWN])):
			self.image = pygame.transform.rotozoom(self.image, angle, 1).convert_alpha()	# must apply rotozoom to the original image (surface). Since inherit from class AnimatedSprite, the self.image is refreshed with the image load
		else:
			self.image = pygame.transform.rotozoom(self.image, abs(angle), 1).convert_alpha()
			self.image = pygame.transform.flip(self.image, False, True)
		
		self.rect = self.image.get_frect(center = self.center + direction * self.radius)
		#pygame.draw.rect(pygame.display.get_surface(), "red", self.rect)

	def orbit_to_angle(self, start_angle, end_angle, speed, clockwise, direction_changes):
		# one time call per orbit to new destination

		start_angle = 360 + start_angle if (start_angle < 0) else start_angle
		end_angle = 360 + end_angle if (end_angle < 0) else end_angle

		self.start_angle = self.angle = start_angle
		self.end_angle = end_angle
		self.speed = speed
		self.direction_changes = direction_changes
		self.direction_changes_completed = 0

		#curr = pygame.math.Vector2(math.cos(radians(self.angle)), math.sin(radians(self.angle))).normalize()
		#new = pygame.math.Vector2(math.cos(radians(self.end_angle)), math.sin(radians(self.end_angle))).normalize()

		self.clockwise = clockwise
		self.direction = 1 if clockwise else -1

		if (self.clockwise and end_angle < self.angle):
			self.end_angle = 360 + end_angle
			if (self.end_angle >= 360 and self.angle % 360 <= self.end_angle % 360):
				self.angle = self.angle % 360
				self.end_angle = self.end_angle % 360	
		elif (not self.clockwise and self.start_angle < end_angle):
			self.start_angle = self.angle = 360 + self.angle

		#print('====')
		#print(self.start_angle)
		#print(self.end_angle)

	def set_radius(self, radius):
		self.radius = radius

	def set_angle(self, angle):
		new_end_angle = 360 - abs(angle) if (angle < 0) else angle
		#print(new_end_angle)
		#self.move_to_angle(detected = self.owner.player_proximity["detected"], end_angle = new_end_angle, speed = 5, direction = 0, direction_changes = 1)
		self.start_angle = self.end_angle = self.angle = new_end_angle
		#print(self.angle)

	def point_image(self, source, location):
		source = pygame.math.Vector2(source)
		location = pygame.math.Vector2(location)
		angle = degrees(atan2(location.y - source.y, location.x - source.x))
		self.set_angle(angle)
		
	def update_angle(self, dt):
		# if (self.detected):
		# 	if (self.clockwise):
				
		# 		if (self.angle < self.end_angle):
		# 			self.angle += self.direction * self.speed * dt

		# 		if (self.end_angle >= 360 and self.angle % 360 <= self.end_angle % 360):
		# 			self.angle = self.angle % 360
		# 			self.end_angle = self.end_angle % 360	

		# 		if (self.angle >= self.end_angle):
		# 			self.angle = self.end_angle
		# 			#print("=========================")
		# 			self.detected = False
		# 	else:
		# 		if (self.angle > self.end_angle):
		# 			self.angle += self.direction * self.speed * dt

		# 		if (self.angle <= self.end_angle):
		# 			self.angle = self.end_angle
		# 			#print("=========================")
		# 			self.detected = False

			#print(self.start_angle, ", ", self.end_angle, ", ", self.angle)
		if (self.direction_changes == -1 or self.direction_changes_completed < self.direction_changes):		
			self.angle += self.direction * self.speed * dt

			if (not self.full_circle):
				if (self.clockwise):
					if ((self.angle >= self.end_angle) or (self.angle < self.start_angle)):
						self.direction = self.direction * -1
						self.direction_changes_completed = self.direction_changes_completed + 1 if self.direction_changes > 0 else self.direction_changes_completed
				else:
					if ((self.angle <= self.end_angle) or (self.angle > self.start_angle)):
						self.direction = self.direction * -1
						self.direction_changes_completed = self.direction_changes_completed + 1 if self.direction_changes > 0 else self.direction_changes_completed

		y = self.center[1] + sin(radians(self.angle)) * self.radius
		x = self.center[0] + cos(radians(self.angle)) * self.radius
		self.rect.center = (x,y)


	def update(self, dt, event_list):
		self.update_angle(dt)

		self.animate(dt)

		if (self.direction > 0):
			self.image = pygame.transform.flip(self.image, True, False)

		if (self.rotate):
			self.rotate_image(self.image_orientation)
			
class Cloud(Sprite):
	def __init__(self, pos, frames, groups, type = 'cloud', z = Z_LAYERS["clouds"], speed = 0.25):
		super().__init__(pos, frames, groups, type, z)

		self.cloud_direction = -1
		self.cloud_speed = speed

		self.rect.bottomleft = pos

	def update(self, dt, event_list = None):
		self.rect.x += self.cloud_direction * self.cloud_speed * dt
		if (self.rect.right <= 0):
			self.kill()