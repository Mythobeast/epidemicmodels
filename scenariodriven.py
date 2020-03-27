from datetime import datetime, timedelta
import json
import math

import matplotlib.pyplot as plt
import numpy as np

from amortizedmarkov import ProbState
from hospitalized_agegroup import AgeGroup
from constants import *

from scenario import EpiScenario


class ScenarioDrivenModel:
	def __init__(self, scenario):
		if isinstance(scenario, str):
			self.scenario = EpiScenario(scenario)
		elif isinstance(scenario, EpiScenario):
			self.scenario = scenario

		print(f"Scenario is {type(scenario)}")

		self.modelname = self.scenario.modelname
		self.total_days = 0
		self.population = self.scenario.totalpop

		self.susceptible = ProbState(period=0, count=self.scenario.susceptible, name='susceptible')
		self.incubating = ProbState(period=self.scenario.incubation_period, count=self.scenario.infected, name='incubating')
		self.infectious = ProbState(period=self.scenario.prediagnosis, count=self.scenario.infectious, name='infectious')
		self.isolated_holding = ProbState(period=90, name='isolated_holding')

		self.incubating.add_exit_state(self.infectious, 1)
		self.incubating.normalize_states_over_period()

		self.infectious.add_exit_state(self.isolated_holding, 1)
		self.infectious.normalize_states_over_period()

		self.subgroups = dict()
		for key, value in self.scenario.subgrouprates.items():
			self.subgroups[key] = AgeGroup(value, name=key)

		self.sum_isolated = None
		self.sum_noncrit = None
		self.sum_crit = None
		self.sum_icu = None
		self.sum_recovered = None
		self.sum_deceased = None
		self.stepcounter = 0
		self.fitness = None

	def run(self):
		self.run_r0_set(self.scenario.r0_date_offsets, self.scenario.r0_values)

	def gather_sums(self):
		self.sum_isolated  = [0] * len(self.susceptible.domain)
		self.sum_noncrit   =  [0] * len(self.susceptible.domain)
		self.sum_icu       =  [0] * len(self.susceptible.domain)
		self.sum_icu_vent  =  [0] * len(self.susceptible.domain)
		self.sum_recovered =  [0] * len(self.susceptible.domain)
		self.sum_deceased  =  [0] * len(self.susceptible.domain)

		for key, value in self.subgroups.items():
			self.sum_isolated  = np.add(self.sum_isolated, value.isolated.domain)
			self.sum_noncrit   = np.add(self.sum_noncrit, value.h_noncrit.domain)
			self.sum_icu       = np.add(self.sum_icu, value.h_icu.domain)
			self.sum_icu_vent  = np.add(self.sum_icu_vent, value.h_icu_vent.domain)
			self.sum_recovered = np.add(self.sum_recovered, value.recovered.domain)
			self.sum_deceased  = np.add(self.sum_deceased, value.deceased.domain)

	def set_r0(self, value):
		self.r0 = value

	def recalculate(self):
		self.beta = self.r0 / self.infectious.period

	def run_r0_set(self, date_offsets, r0_values):
		day_counter = 0
		for itr in range(0, len(date_offsets)):
			print(f"itr: {itr}: {r0_values[itr]}")
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
		print(f"subpop: {subpop_out}")
		self.susceptible.apply_pending()
		self.incubating.apply_pending()
		self.infectious.apply_pending()

		for key, agegroup in self.subgroups.items():
			agegroup.apply_pending()

		self.total_days += 1

	def calculate_fit(self, ideal):
		sum2 = 0
		infections = self.infectious.domain
		for itr in range(0, len(ideal)):
			sum2 += (infections[itr] - ideal[itr])^2
		self.fitness = math.sqrt(sum2)

	def save_results(self, iteration):
		result = dict()

		result['iteration'] = iteration
		result['fitness'] = self.fitness
		result['init_date'] = self.scenario.initial_date
		result['r0dates'] = self.scenario.r0_date_offsets
		result['r0set'] = self.scenario.r0_values

		result['modelname'] = self.modelname
		result['total_days'] = self.total_days
		result['totalpop'] = self.population
		result['sum_isolated'] = self.sum_isolated
		result['sum_noncrit'] = self.sum_noncrit
		result['sum_crit'] = self.sum_crit
		result['sum_icu'] = self.sum_icu
		result['sum_recovered'] = self.sum_recovered
		result['sum_deceased'] = self.sum_deceased

		with open(f"best_fit{iteration}", "w") as bfi:
			json.dump(result, bfi)



ONEDAY = timedelta(1)

def main():
	model = ScenarioDrivenModel('scenario1.json')

	model.run()
	model.gather_sums()

	u_susc = model.susceptible.domain
	u_incu = model.incubating.domain
	u_infe = model.infectious.domain
	u_isol = model.sum_isolated
	u_h_no = model.sum_noncrit
	u_h_ic = model.sum_icu
	u_h_ve = model.sum_icu_vent
	u_reco = model.sum_recovered
	u_dead = model.sum_deceased

	startdate = model.scenario.initial_date
	time_domain = [startdate]
	cursor = startdate
	for _ in range(0, model.scenario.maxdays):
		cursor += ONEDAY
		time_domain.append(cursor)

#	time_domain = np.linspace(0, model.total_days, model.total_days + 1)
	hospitalized = []
	for itr in range(0, len(u_h_no)):
		print(f"Hospit: {u_h_no[itr] + u_h_ic[itr] + u_h_ve[itr]}")
		hospitalized.append(u_h_no[itr] + u_h_ic[itr] + u_h_ve[itr])


	fig = plt.figure(facecolor='w')
	# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
	ax = fig.add_subplot(111, axisbelow=True)
#	ax.plot(time_domain, u_susc, color=(0, 0, 1), alpha=.5, lw=2, label='Susceptible', linestyle='-')
#	ax.plot(time_domain, u_incu, color=TABLEAU_ORANGE, alpha=0.1, lw=2, label='Exposed', linestyle='-')
#	ax.plot(time_domain, u_infe, color=TABLEAU_RED, alpha=0.5, lw=2, label='Infected', linestyle='-')
#	ax.plot(time_domain, u_isol, color=TAB_COLORS[8], alpha=.5, lw=2, label='Home Iso', linestyle='-')
	ax.plot(time_domain, u_h_no, color=TABLEAU_BLUE, alpha=1, lw=2, label='Noncrit', linestyle='--')
	ax.plot(time_domain, u_h_ic, color=TABLEAU_GREEN, alpha=1, lw=2, label='ICU', linestyle='--')
	ax.plot(time_domain, u_h_ve, color=TABLEAU_RED, alpha=1, lw=2, label='ICU + Ventilator', linestyle='--')
	ax.plot(time_domain, hospitalized, color=(1, 0, 0), alpha=.25, lw=2, label='Total Hospitalized', linestyle='-')
#	ax.plot(time_domain, u_reco, color=(0, .5, 0), alpha=.5, lw=2, label='Recovered', linestyle='--')
#	ax.plot(time_domain, u_dead, color=(0, 0, 0), alpha=.5, lw=2, label='Dead', linestyle=':')

	ax.plot(time_domain, [511] * (model.total_days + 1), color=(0, 0, 1), alpha=1, lw=1, label='511 Beds', linestyle='-')
	ax.plot(time_domain, [77] * (model.total_days + 1), color=(1, 0, 0), alpha=1, lw=1, label='77 ICU units', linestyle='-')
	plt.axvline(x=datetime.today(), alpha=.5, lw=2, label='Today')

	ax.set_xlabel('Days')
	ax.set_ylabel('Number')

	chart_title = model.modelname
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

	outfilename = "_".join(chart_title.replace("|", " ").replace(":", " ").replace(".", " ").split())

	# Write a CSV to this directory
	with open(f"{outfilename}.csv", 'w') as outfile:
		for itr in range(0, len(u_susc)):
			outfile.write(f"{u_susc[itr]:.6f}, {u_incu[itr]:.6f}, {u_infe[itr]:.6f}, {u_isol[itr]:.6f}"
			              f", {u_h_no[itr]:.6f}, {u_h_ic[itr]:.6f}, {u_h_ve[itr]:.6f}, {u_reco[itr]:.6f}"
			              f", {u_dead[itr]:.6f}, {hospitalized[itr]:.6f}\n")

	plt.savefig(f"{outfilename}.png", bbox_inches="tight")
	plt.show()


if __name__ == '__main__':
	main()
