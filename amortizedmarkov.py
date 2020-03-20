class ExitState:
	def __init__(self, target, distribution):
		# Number of cases that will take this path
		self.distribution = distribution
		# normalized probability of taking this path
		self.probability = 0
		self.target = target


class ProbState:
	def __init__(self, period, count=0):
		self.period = period
		self.count = count
		self.exit_states = []
		self.domain = [count]

	def add_exit_state(self, probability, state):
		self.exit_states.append(ExitState(probability, state))

	def normalize_states_over_period(self):
		total = 0.0
		for state in self.exit_states:
			total += state.distribution
		for state in self.exit_states:
			state.probability = state.distribution / (total * self.period)

	def get_state_redist(self, count_in):
		count_out = []
		for outstate in self.exit_states:
			count_out.append(outstate.probability * count_in)
		return count_out

	def reset(self, count=0):
		self.count = count
		self.domain = [count]

	def extend(self, values):
		self.domain.pop()
		self.domain.extend(values)
		self.count = self.domain[-1]
