

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
	def __init__(self, icd):
		self.isolate = 1 - icd['hosp_rate']
		self.h_crit = icd['hosp_rate'] * icd['crit_rate']
		self.h_noncrit = icd['hosp_rate'] - self.h_crit
		self.icu_deathrate = icd['fatality'] / self.h_crit
		self.icu_recovery_rate = 1 - self.icu_deathrate


class AgeGroup:
	def __init__(self, subgroupstats, name=None):

		self.name = name
		self.stats = subgroupstats
		# Variables to store state changes

		# Probability states
		if self.name != None:
			self.isolated = ProbState(14,  name=f"{self.name}: isolated")
		else:
			self.isolated = ProbState(14)
		self.h_noncrit = ProbState(8)
		self.h_crit = ProbState(6)
		self.h_icu = ProbState(10)
		self.recovered = ProbState(1000)
		self.deceased = ProbState(1000)

		self.isolated.add_exit_state(self.recovered, 1)
		self.isolated.normalize_states_over_period()

		self.h_noncrit.add_exit_state(self.recovered, 1)
		self.h_noncrit.normalize_states_over_period()

		self.h_icu.add_exit_state(self.deceased, self.stats.icu_deathrate)
		self.h_icu.add_exit_state(self.h_crit, self.stats.icu_recovery_rate)
		self.h_icu.normalize_states_over_period()

		self.h_crit.add_exit_state(self.recovered, 1)
		self.h_crit.normalize_states_over_period()

	# Add N people to the list of infected
	def apply_infections(self, infections):
		self.isolated.store_pending(infections * self.stats.isolate)
		self.h_noncrit.store_pending(infections * self.stats.h_noncrit)
		self.h_icu.store_pending(infections * self.stats.h_crit)

	def calculate_redistributions(self):
		self.isolated.pass_downstream()
		self.h_noncrit.pass_downstream()
		self.h_crit.pass_downstream()
		self.h_icu.pass_downstream()

	def apply_pending(self):
#		print(f"apply_pending {self.name} ")
		self.isolated.apply_pending()
		self.h_noncrit.apply_pending()
		self.h_crit.apply_pending()
		self.h_icu.apply_pending()
		self.recovered.apply_pending()
		self.deceased.apply_pending()


class ProbState:
	def __init__(self, period, count=0, name=None):
		self.name = name
		self.period = period
		self.count = count
		self.exit_states = []
		self.domain = [count]
		self.pending = 0
		self.capacity = None
		self.overflowstate = None

	def set_capacity(self, capacity, overflowstate):
		self.capacity = capacity
		self.overflowstate = overflowstate

	def add_exit_state(self, probability, state):
		self.exit_states.append(ExitState(probability, state))

	def normalize_states_over_period(self):
		total = 0.0
		for state in self.exit_states:
			total += state.distribution
		for state in self.exit_states:
			state.probability = state.distribution / (total * self.period)
			if self.name == 'incubating':
				print(f"{state.probability} = {state.distribution} / ({total} * {self.period})")

	def get_state_redist(self, count_in=None):
		if count_in == None:
			count_in = self.count
		count_out = []
		for outstate in self.exit_states:
			count_out.append(outstate.probability * count_in)
		return count_out

	def pass_downstream(self):
		# if self.name != None:
		# 	print(f"pass_downstream {self.name}: {self.count} / {self.period}")
		for state in self.exit_states:
			self.pending -= state.pass_downstream(self.count)

	def store_pending(self, value):
		self.pending += value
		if self.capacity != None and (self.count + self.pending) > self.capacity:
			pass_along = (self.count + self.pending) > self.capacity
			self.pending -= pass_along
			self.overflowstate.store_pending(pass_along)


	def apply_pending(self):
#		if self.name != None:
#		print(f"Apply Pending {self.name} {len(self.domain)}")
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
