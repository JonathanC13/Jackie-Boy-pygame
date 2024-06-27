from settings import *

class Sprite(pygame.sprite.Sprite):

	def __init__(self, pos, surf = pygame.Surface((TILE_SIZE,TILE_SIZE)), groups = None, type = None, z = Z_LAYERS["main"]):
		
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_frect(topleft = pos)

		self.old_rect = self.rect.copy()
		self.type = type
		self.z = z

class AnimatedSprite(Sprite):

	def __init__(self, pos, frames, groups, type = None, z = Z_LAYERS["main"], animation_speed = ANIMATION_SPEED):

		self.frames, self.frame_index = frames, 0
		self.len_frames = len(frames)
		super().__init__(pos, self.frames[self.frame_index], groups, type, z)

		self.animation_speed = animation_speed

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt/FPS_TARGET
		if (self.frame_index > self.len_frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self, dt, event_list):
		#self.animate(dt)
		pass

class MovingSprite(Sprite):

	def __init__(self, start_pos, end_pos, path_plane, start_end = False, speed = 0, full_collision = True, groups = None, flip = False, type = None, z = Z_LAYERS["main"]):

		surf = pygame.Surface((100, 25))
		super().__init__(start_pos, surf, groups, type, z)
		if (not full_collision):
			self.image.fill("green")
		else:
			self.image.fill("white")
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

		if (self.flip):
			self.image = pygame.transform.flip(self.image, self.reverse['x'], self.reverse['y'])