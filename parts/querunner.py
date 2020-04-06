
from collections import deque
from datetime import datetime
from threading import Thread
from time import sleep


# This is an example of a function to be passed to a QueueRunner
def example(proc_me, params):
	print("I received a %s" % type(proc_me))

class Terminator:
	def __init__(self):
		pass

ARNOLD = Terminator()

class QueueRunner(Thread):

	def __init__(self, function, fparm = None):
		Thread.__init__(self)
		self.function = function
		self.parms = fparm
		self.queue = deque()
		self.last_seen = datetime.now()
		self.current_ob = None

	def push(self, entity):
		self.queue.append(entity)

	def run(self):
		proc_me = None
		while not isinstance(proc_me, Terminator):
			if len(self.queue) == 0:
				sleep(1)
				continue
			proc_me = self.queue.popleft()
			if isinstance(proc_me, Terminator):
				continue
			self.current_ob = proc_me
			self.function(proc_me, self.parms)

	def ping(self):
		self.last_seen = datetime.now()

	def lastseen(self):
		now = datetime.now()
		return (now - self.last_seen).total_seconds()

	def terminate(self):
		self.queue.clear()
		self.queue.append(ARNOLD)


#if __name__ == '__main__':
#	main()
