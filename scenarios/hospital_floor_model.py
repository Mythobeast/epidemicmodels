from datetime import datetime, timedelta
import json
import math

import matplotlib.pyplot as plt
import numpy as np

from parts.amortizedmarkov import ProbState
from parts.hosppaths_byage import PathsByAge
from parts.constants import *

from scenarios.scenario import EpiScenario

class HospFloorModel:
	def __init__(self, scenario):
		if isinstance(scenario, str):
			self.scenario = EpiScenario(scenario)
		elif isinstance(scenario, EpiScenario):
			self.scenario = scenario

		self.modelname = self.scenario.modelname
		self.total_days = 0
		self.r0 = self.scenario.parameters['initial_r0']
		self.beta = None
		self.population = self.scenario.totalpop

		self.susceptible = ProbState(period=0, count=self.scenario.init_susceptible, name='susceptible')
		self.incubating = ProbState(period=self.scenario.incubation_period, count=self.scenario.init_infected, name='incubating')
		self.infectious = ProbState(period=self.scenario.prediagnosis, count=self.scenario.init_infectious, name='infectious')
		self.isolated_holding = ProbState(period=90, name='isolated_holding')

		self.incubating.add_exit_state(self.infectious, 1)
		self.incubating.normalize_states_over_period()

		self.infectious.add_exit_state(self.isolated_holding, 1)
		self.infectious.normalize_states_over_period()

		self.subgroups = dict()
		for key, value in self.scenario.subgrouprates.items():
			self.subgroups[key] = PathsByAge(value, name=key)

		self.stepcounter = 0
		self.fitness = None

	def run(self):
		self.run_r0_set(self.scenario.r0_date_offsets, self.scenario.r0_values)


	def set_r0(self, value):
		self.r0 = value

	def recalculate(self):
		self.beta = self.r0 / self.infectious.period

	def run_r0_set(self, date_offsets, r0_values):
		day_counter = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(r0_values[itr])
			self.recalculate()
			while day_counter < date_offsets[itr]:
				self.step_day()
				day_counter += 1

	def step_day(self):
		self.stepcounter += 1
		new_infections = self.beta * self.susceptible.count * self.infectious.count / self.population
		self.susceptible.store_pending(-new_infections)
		self.incubating.store_pending(new_infections)
		self.incubating.pass_downstream()
		self.infectious.pass_downstream()

		diagnosed = self.isolated_holding.pending
		self.isolated_holding.pending = 0
		subpop_out = []
		for key, agegroup in self.subgroups.items():

			subpop = diagnosed * agegroup.stats.pop_dist
			subpop_out.append(subpop)
			agegroup.apply_infections(subpop)
			agegroup.calculate_redistributions()
		self.susceptible.apply_pending()
		self.incubating.apply_pending()
		self.infectious.apply_pending()

		for key, agegroup in self.subgroups.items():
			agegroup.apply_pending()

		self.total_days += 1


	def gather_sums(self):
		self.scenario.out_susceptible = self.susceptible.domain
		self.scenario.out_incubating  = self.incubating.domain
		self.scenario.out_infectious  = self.infectious.domain


		time_increments = len(self.susceptible.domain)
		self.scenario.sum_isolated  = [0] * time_increments
		self.scenario.sum_ed        = [0] * time_increments
		self.scenario.sum_floor     = [0] * time_increments
		self.scenario.sum_icu       = [0] * time_increments
		self.scenario.sum_vent      = [0] * time_increments

		self.scenario.sum_recovered = [0] * time_increments
		self.scenario.sum_deceased  = [0] * time_increments
		self.scenario.sum_hospitalized  = [0] * time_increments

		for key, value in self.subgroups.items():
			self.scenario.sum_isolated  = np.add(self.scenario.sum_isolated, value.isolated.domain)
			self.scenario.sum_ed        = np.add(self.scenario.sum_ed, value.get_ed_counts())
			self.scenario.sum_floor     = np.add(self.scenario.sum_floor, value.get_floor_counts())
			self.scenario.sum_icu       = np.add(self.scenario.sum_icu, value.get_icu_counts())
			self.scenario.sum_vent      = np.add(self.scenario.sum_vent, value.icu_vent.domain)
			self.scenario.sum_recovered = np.add(self.scenario.sum_recovered, value.recovered.domain)
			self.scenario.sum_deceased  = np.add(self.scenario.sum_deceased, value.deceased.domain)

		self.scenario.sum_hospitalized  = np.add(self.scenario.sum_hospitalized, self.scenario.sum_ed )
		self.scenario.sum_hospitalized  = np.add(self.scenario.sum_hospitalized, self.scenario.sum_floor)
		self.scenario.sum_hospitalized  = np.add(self.scenario.sum_hospitalized, self.scenario.sum_icu)

	def calculate_fit(self, ideal):
		initial_offset = (ideal['start'] - self.scenario.initial_date).days
		fitcount = (ideal['end'] - ideal['start']).days
		final_offset = initial_offset + fitcount + 1

		cursor = initial_offset
		fitcur = 0
		hosp = self.scenario.sum_hospitalized
		dead = self.scenario.sum_deceased
		hosp_sum = 0
		hosp_r2 = 0
		dead_sum = 0
		dead_r2 = 0
		while cursor < final_offset:
			hosp_sum += hosp[cursor]
			dead_sum += hosp[cursor]
			hosp_r2 += (hosp[cursor] - ideal['hospitalized'][fitcur]) ** 2
			dead_r2 += (dead[cursor] - ideal['deceased'][fitcur]) ** 2
			fitcur += 1
			cursor += 1

		hosp_hold = math.sqrt(hosp_r2)
		dead_hold = math.sqrt(dead_r2)
		hosp_avg = hosp_sum / fitcount
		dead_avg = dead_sum / fitcount

		self.scenario.fitness = (hosp_hold / hosp_avg) + (dead_hold / dead_avg)


	def save_results(self, iteration):
		result = dict()

		result['iteration'] = iteration
		result['fitness'] = self.fitness
		result['scenario'] = self.scenario.parameters

		result['modelname'] = self.modelname
		result['total_days'] = self.total_days
		result['totalpop'] = self.population
		result['sum_isolated'] = self.scenario.sum_isolated
		result['sum_noncrit'] = self.scenario.sum_noncrit
		result['sum_icu'] = self.scenario.sum_icu
		result['sum_icu_vent'] = self.scenario.sum_icu_vent
		result['sum_recovered'] = self.scenario.sum_recovered
		result['sum_deceased'] = self.scenario.sum_deceased

		with open(f"best_fit{iteration}", "w") as bfi:
			json.dump(result, bfi)

	def actual_curves(self):
		cursor = self.scenario.initial_date
		finaldate = cursor + timedelta(self.scenario.maxdays)
		act_hosp = []
		act_death = []

		while cursor < finaldate:
			if cursor in COLORADO_ACTUAL:
				act_hosp.append(COLORADO_ACTUAL[cursor]['hospitalized'])
				act_death.append(COLORADO_ACTUAL[cursor]['deaths'])
			else:
				act_hosp.append(None)
				act_death.append(None)
			cursor += ONEDAY
		act_death.append(None)
		act_hosp.append(None)
		return act_hosp, act_death

	def generate_png(self):

		startdate = self.scenario.initial_date
		time_domain = [startdate]
		cursor = startdate
		for _ in range(0, self.scenario.maxdays):
			cursor += ONEDAY
			time_domain.append(cursor)

	#	time_domain = np.linspace(0, model.total_days, model.total_days + 1)

		fig = plt.figure(facecolor='w')
		# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
		ax = fig.add_subplot(111, axisbelow=True)

	###   Lines for comparison to actual
#		act_hosp, act_death = self.actual_curves()
	###   Actual Hospitalized, as specified in the constants
#		ax.plot(time_domain, act_hosp, color=(0, 0, .5), alpha=1, lw=2, label='Actual Hospitalized', linestyle='-')
	###   Actual Deaths, as specified in the constants
#		ax.plot(time_domain, act_death, color=(0, 0, .5), alpha=1, lw=2, label='Actual Deaths', linestyle='-')

	###   Susceptible line, usually too tall
#   	ax.plot(time_domain, self.scenario.susceptible, color=(0, 0, 1), alpha=.5, lw=2, label='Susceptible', linestyle='-')
	###   Recovered/immune, usually too tall
#   	ax.plot(time_domain, self.scenario.sum_recovered, color=(0, .5, 0), alpha=.5, lw=2, label='Recovered', linestyle='--')

	###   Infected patients who aren't infectious yet
#   	ax.plot(time_domain, self.scenario.incubating, color=TABLEAU_ORANGE, alpha=0.1, lw=2, label='Exposed', linestyle='-')
	###   Infectious patients who don't know they have it
#   	ax.plot(time_domain, self.scenario.infectious, color=TABLEAU_RED, alpha=0.5, lw=2, label='Infected', linestyle='-')
	###   Known and unknown infected, isolated at home
#   	ax.plot(time_domain, self.scenario.sum_isolated, color=TAB_COLORS[8], alpha=.5, lw=2, label='Home Iso', linestyle='-')

	###   Hospital floor patients
		ax.plot(time_domain, self.scenario.sum_floor, color=TABLEAU_BLUE, alpha=1, lw=2, label='Noncrit', linestyle='--')
	###   Non-ventilated ICU patients
		ax.plot(time_domain, self.scenario.sum_icu, color=TABLEAU_GREEN, alpha=1, lw=2, label='ICU', linestyle='--')
	###   Ventilated ICU patients
		ax.plot(time_domain, self.scenario.sum_vent, color=TABLEAU_RED, alpha=1, lw=2, label='ICU + Ventilator', linestyle='--')
	###   Total hospitalized in all areas
		ax.plot(time_domain, self.scenario.sum_hospitalized, color=(1, 0, 0), alpha=.25, lw=2, label='Total Hospitalized', linestyle='-')
	###   Deceased
		ax.plot(time_domain, self.scenario.sum_deceased, color=(0, 0, 0), alpha=.5, lw=2, label='Dead', linestyle=':')

	###   Max non-icu capacity
#		ax.plot(time_domain, [229] * (self.total_days + 1), color=(0, 0, 1), alpha=1, lw=1, label='229 Floor beds', linestyle='-')
	###   Max ICU capacity
#		ax.plot(time_domain, [86] * (self.total_days + 1), color=(1, 0, 0), alpha=1, lw=1, label='86 ICU units', linestyle='-')

	### Vertical line indicating today
		plt.axvline(x=datetime.today(), alpha=.5, lw=2, label='Today')

		ax.set_xlabel('Days')
		ax.set_ylabel('Number')

		chart_title = self.modelname
		plt.title(chart_title, fontsize=14)
		# ax.set_ylim(0,1.2)
		ax.yaxis.set_tick_params(length=4)
		ax.xaxis.set_tick_params(length=4)
		# ax.grid(b=True, which='minor', c='w', lw=1, ls='--')
		ax.grid()
		legend = ax.legend()
		legend.get_frame().set_alpha(0.5)
		for spine in ('top', 'right', 'bottom', 'left'):
			ax.spines[spine].set_visible(False)

		return plt

	def generate_csv(self):

		chart_title = self.modelname
		outfilename = "_".join(chart_title.replace("|", " ").replace(":", " ").replace(".", " ").split())

		# Write a CSV to this directory
		with open(f"{outfilename}.csv", 'w') as outfile:
			for itr in range(0, len(self.scenario.out_susceptible)):
				outfile.write(f"{self.scenario.out_susceptible[itr]:.6f}, "
				              f"{self.scenario.out_incubating[itr]:.6f}, "
						f"{self.scenario.out_infectious[itr]:.6f}, "
						      f"{self.scenario.sum_isolated[itr]:.6f}"
						f", {self.scenario.sum_floor[itr]:.6f}, "
						      f"{self.scenario.sum_icu[itr]:.6f}, "
						f"{self.scenario.sum_vent[itr]:.6f}, "
						      f"{self.scenario.sum_recovered[itr]:.6f}"
						f", {self.scenario.sum_deceased[itr]:.6f}, "
						      f"{self.scenario.sum_hospitalized[itr]:.6f}\n")




ONEDAY = timedelta(1)

def main():
	model = HospFloorModel('../bestscenario.json')

	model.run()
	model.gather_sums()

	model.generate_csv()
	thisplot = model.generate_png()
	chart_title = model.modelname
	outfilename = "_".join(chart_title.replace("|", " ").replace(":", " ").replace(".", " ").split())
	thisplot.savefig(f"{outfilename}.png", bbox_inches="tight")

	thisplot.show()


if __name__ == '__main__':
	main()
