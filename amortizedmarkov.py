

class ExitState:
	def __init__(self, target, distribution):
		# Number of cases that will take this path
		self.distribution = distribution
		# normalized probability of taking this path
		self.probability = 0
		self.target = target

	def pass_downstream(self, value):
		portion = value * self.probability
		self.target.store_pending(portion)
		return portion

# This class uses IC information to populate state-change percentages
class SubgroupRates:
	def __init__(self, icd, pop_dist):
		self.pop_dist = pop_dist
		self.isolate = 1 - icd['hosp_rate']
		self.h_crit = icd['hosp_rate'] * icd['crit_rate']
		self.h_noncrit = icd['hosp_rate'] - self.h_crit
		self.icu_deathrate = icd['fatality'] / self.h_crit
		self.icu_recovery_rate = 1 - self.icu_deathrate

# This class uses IC information to populate state-change percentages
class SubgroupRates:
	def __init__(self, icd, pop_dist):
		self.pop_dist = pop_dist
		self.isolate = 1 - icd['hosp_rate']
		self.h_icu_all     = icd['hosp_rate'] * icd['crit_rate']
		self.h_noncrit     = icd['hosp_rate'] - self.h_icu_all
		self.h_icu         = self.h_icu_all * 0.25
		self.h_icu_vent    = self.h_icu_all * 0.75
		self.icu_deathrate = icd['fatality'] / self.h_icu_all
		print(f"deathrate: {self.icu_deathrate}")
		self.icu_recovery_rate = 1 - self.icu_deathrate

class BedPool:
	def __init__(self, name, size):
		self.name = name
		self.size = size
		self.available = size

	def request(self, count):
		if count > self.available:
			retval = self.available
		else:
			retval = count
		self.available -= retval
		return retval

	def restock(self, count):
		if count + self.available > self.size:
			raise ValueError("Trying to restock bed pool {self.name} to {count} + {self.available} > {self.size} beds")
		self.available += count


class ProbState:
	def __init__(self, period, count=0, name=None):
		self.name = name
		self.period = period
		self.count = count
		self.exit_states = []
		self.domain = [count]
		self.pending = 0
		self.bedpool = None
		self.overflowstate = None


	def set_capacity(self, bedpool, overflowstate):
		self.bedpool = bedpool
		self.overflowstate = overflowstate

	def add_exit_state(self, probability, state):
		self.exit_states.append(ExitState(probability, state))

	def normalize_states_over_period(self):
		total = 0.0
		for state in self.exit_states:
			total += state.distribution
		for state in self.exit_states:
			state.probability = state.distribution / (total * self.period)

	def get_state_redist(self, count_in=None):
		if count_in == None:
			count_in = self.count
		count_out = []
		for outstate in self.exit_states:
			count_out.append(outstate.probability * count_in)
		return count_out

	def pass_downstream(self):
		for state in self.exit_states:
			self.pending -= state.pass_downstream(self.count)

	def store_pending(self, value):
		if self.bedpool != None and (self.count + self.pending) > self.capacity:
			available = self.bedpool.request(value)
			if available < value:
				overflow = value - available
				self.overflowstate.store_pending(overflow)
			pass_along = (self.count + self.pending) > self.capacity
			self.pending -= pass_along
			self.overflowstate.store_pending(pass_along)

		self.pending += value


	def apply_pending(self):
		self.count += self.pending
		self.pending = 0
		self.domain.append(self.count)

	def reset(self, count=0):
		self.count = count
		self.domain = [count]

	def extend(self, values):
		self.domain.pop()
		self.domain.extend(values)
		self.count = self.domain[-1]

	def adjust(self, value):
		self.count += value
		self.domain.append(self.count)
