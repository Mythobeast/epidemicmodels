from parts.amortizedmarkov import ProbState
from parts.constants import TIMINGS

import logging

class PathsByAge:
	def __init__(self, subgroupstats, name=None):

		self.name = name
		self.stats = subgroupstats
		# Variables to store state changes

		# Probability states
		self.isolated    = ProbState(TIMINGS['days home isolation'],  name=f"{self.name}: isolated")

		self.nevercrit   = ProbState(TIMINGS['days noncrit'],  name=f"{self.name}: nevercrit")
		self.pre_icu     = ProbState(TIMINGS['days preicu'],  name=f"{self.name}: pre_icu")
		self.icu_novent  = ProbState(TIMINGS['days icu nonvent'], name=f"{self.name}: icu")
		self.icu_vent    = ProbState(TIMINGS['days icu vent'],  name=f"{self.name}: icu_vent")
		self.post_icu    = ProbState(TIMINGS['days posticu'],  name=f"{self.name}: post_icu")
		# Recovered and dead are presumed permanent
		self.recovered   = ProbState(1000,  name=f"{self.name}: recovered")
		self.deceased    = ProbState(1000,  name=f"{self.name}: deceased")

		self.isolated.add_exit_state(self.recovered, 1)
		self.isolated.normalize_states_over_period()

		self.nevercrit.add_exit_state(self.recovered, 1)
		self.nevercrit.normalize_states_over_period()

		self.pre_icu.add_exit_state(self.icu_novent, self.stats.p_icu_nonvent)
		self.pre_icu.add_exit_state(self.icu_vent, self.stats.p_icu_vent)
		self.pre_icu.normalize_states_over_period()

		self.icu_novent.add_exit_state(self.deceased, self.stats.p_icu_death)
		self.icu_novent.add_exit_state(self.post_icu, self.stats.p_icu_recovery)
		self.icu_novent.normalize_states_over_period()

		self.icu_vent.add_exit_state(self.deceased, self.stats.p_icu_death)
		self.icu_vent.add_exit_state(self.post_icu, self.stats.p_icu_recovery)
		self.icu_vent.normalize_states_over_period()

		self.post_icu.add_exit_state(self.recovered, 1)
		self.post_icu.normalize_states_over_period()


	def get_floor_counts(self):
		retval = []
		for itr in range(0, len(self.nevercrit.domain)):
			val = self.nevercrit.domain[itr] + self.pre_icu.domain[itr] + self.post_icu.domain[itr]
			retval.append(val)
		return retval


	def get_icu_counts(self):
		retval = []
		for itr in range(0, len(self.icu_novent.domain)):
			val = self.icu_novent.domain[itr] + self.icu_vent.domain[itr]
			retval.append(val)
		return retval


	# Add N people to the list of infected
	def apply_infections(self, infections):
		inf_float = float(infections)
		n_isolated = inf_float * self.stats.p_selfisolate
		n_nevercrit = inf_float * self.stats.p_nevercrit
		n_pre_icu = inf_float * self.stats.p_pre_icu
		n_icu_vent = inf_float * self.stats.p_urgent_icu_vent
		n_icu_novent = inf_float * self.stats.p_urgent_icu_novent

#		print(f"Storing infections {self.name}:  {n_nevercrit}, {n_pre_icu}, {n_icu_vent}, {n_icu_novent}")
		self.isolated.store_pending(n_isolated)
		self.nevercrit.store_pending(n_nevercrit)
		self.pre_icu.store_pending(n_pre_icu)
		self.icu_vent.store_pending(n_icu_vent)
		self.icu_novent.store_pending(n_icu_novent)



	def calculate_redistributions(self):
		self.isolated.pass_downstream()
		# self.ed_to_floor.pass_downstream()
		# self.ed_to_icu.pass_downstream()
		self.nevercrit.pass_downstream()
		self.pre_icu.pass_downstream()
		self.icu_novent.pass_downstream()
		self.icu_vent.pass_downstream()
		self.post_icu.pass_downstream()

	def apply_pending(self):
		self.isolated.apply_pending()

		# self.ed_to_floor.apply_pending()
		# self.ed_to_icu.apply_pending()
		self.nevercrit.apply_pending()
		self.pre_icu.apply_pending()
		self.icu_novent.apply_pending()
		self.icu_vent.apply_pending()
		self.post_icu.apply_pending()
		self.recovered.apply_pending()
		self.deceased.apply_pending()
