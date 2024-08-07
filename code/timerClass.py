from pygame.time import get_ticks

class Timer:
	def __init__(self, duration, func = None, repeat = False):
		self.duration = duration
		self.func = func
		self.start_time = 0
		self.ended_time = 0
		self.active = False
		self.repeat = repeat

	def activate(self):
		self.active = True
		self.start_time = get_ticks()

	def deactivate(self):
		self.active = False
		self.start_time = 0
		self.ended_time = get_ticks()
		if self.repeat:
			self.activate()

	def kill(self):
		self.active = False
		self.start_time = 0
		self.ended_time = get_ticks()
		self.repeat = False

	def update(self):
		current_time = get_ticks()
		if current_time - self.start_time >= self.duration:
			if self.func and self.start_time != 0:
				self.func()
			self.deactivate()