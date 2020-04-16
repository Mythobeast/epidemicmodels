from datetime import datetime, timedelta
import json
import math
import sys

import matplotlib.pyplot as plt
import numpy as np

from parts.amortizedmarkov import ProbState
from parts.hospitalized_agegroup import AgeGroup
from parts.constants import *
from models.basic_math import calc_beta, calc_infected

from scenarios.scenario import EpiScenario
from scenarios.fitset import COLORADO_ACTUAL as FITSET


class ScenarioDrivenModel:
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
			self.subgroups[key] = AgeGroup(value, name=key)

#		self.fitness = None

	def run(self):
		self.run_r0_set(self.scenario.r0_date_offsets, self.scenario.r0_values)

	def set_r0(self, value):
		self.r0 = value

	def run_r0_set(self, date_offsets, r0_values):
		self.scenario.hospital_door_aggregator = []
		day_counter = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(r0_values[itr])
			self.beta = calc_beta(r0_values[itr], self.infectious.period)
			while day_counter < date_offsets[itr]:
				self.step_day()
				day_counter += 1
		self.scenario.hospital_door_aggregator.append(self.scenario.hospital_door_aggregator[-1])

	def step_day(self):
		new_infections = calc_infected(self.population, self.beta, self.susceptible.count, self.infectious.count)
		#print(f"Day {self.total_days} infections: {new_infections} = {self.beta} * {self.susceptible.count} * {self.infectious.count} / {self.population}")
		self.susceptible.store_pending(-new_infections)
		self.incubating.store_pending(new_infections)
		self.incubating.pass_downstream()
		self.infectious.pass_downstream()

		diagnosed = self.isolated_holding.pending
		if len(self.scenario.hospital_door_aggregator) == 0:
			diagnagg = diagnosed
		else:
			diagnagg = self.scenario.hospital_door_aggregator[-1] + diagnosed
		self.scenario.hospital_door_aggregator.append(diagnagg)

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
		time_increments = len(self.susceptible.domain)
		self.scenario.out_susceptible = self.susceptible.domain
		self.scenario.out_incubating = self.incubating.domain
		self.scenario.out_infectious = self.infectious.domain
		self.scenario.sum_isolated  = [0] * time_increments
		self.scenario.sum_noncrit   = [0] * time_increments
		self.scenario.sum_icu       = [0] * time_increments
		self.scenario.sum_icu_vent  = [0] * time_increments
		self.scenario.sum_recovered = [0] * time_increments
		self.scenario.sum_deceased  = [0] * time_increments
		self.scenario.sum_hospitalized  = [0] * time_increments

		for key, value in self.subgroups.items():
			self.scenario.sum_isolated  = np.add(self.scenario.sum_isolated, value.isolated.domain)
			self.scenario.sum_noncrit   = np.add(self.scenario.sum_noncrit, value.h_noncrit.domain)
			self.scenario.sum_icu       = np.add(self.scenario.sum_icu, value.h_icu.domain)
			self.scenario.sum_icu_vent  = np.add(self.scenario.sum_icu_vent, value.h_icu_vent.domain)
			self.scenario.sum_recovered = np.add(self.scenario.sum_recovered, value.recovered.domain)
			self.scenario.sum_deceased  = np.add(self.scenario.sum_deceased, value.deceased.domain)

		self.scenario.sum_hospitalized  = np.add(self.scenario.sum_hospitalized, self.scenario.sum_icu)
		self.scenario.sum_hospitalized  = np.add(self.scenario.sum_hospitalized, self.scenario.sum_noncrit)
		self.scenario.sum_hospitalized  = np.add(self.scenario.sum_hospitalized, self.scenario.sum_icu_vent)

		self.scenario.fitset = dict()
		cursor = self.scenario.initial_date
		stoptime = cursor + timedelta(self.total_days)
		itr = 0
		while cursor < stoptime:
			if cursor not in self.scenario.fitset:
				self.scenario.fitset[cursor] = dict()
			self.scenario.fitset[cursor]['current_hosp'] = self.scenario.sum_hospitalized[itr]
			self.scenario.fitset[cursor]['total_hosp'] = self.scenario.hospital_door_aggregator[itr]
			self.scenario.fitset[cursor]['total_deceased'] = self.scenario.sum_deceased[itr]
			itr += 1
			cursor += ONEDAY


	def save_results(self, iteration):
		result = dict()

		result['iteration'] = iteration
		result['fitness'] = self.scenario.fitness
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
		finaldate = cursor + timedelta(self.total_days)
		act_hosp = []
		act_death = []

		while cursor < finaldate:
			if cursor in FITSET:
				act_hosp.append(FITSET[cursor]['hospitalized'])
				act_death.append(FITSET[cursor]['deceased'])
			else:
				act_hosp.append(None)
				act_death.append(None)
			cursor += ONEDAY
		act_death.append(None)
		act_hosp.append(None)
		return act_hosp, act_death

	def generate_png(self):

		hospitalized = self.scenario.hospital_door_aggregator

		startdate = self.scenario.initial_date
		time_domain = [startdate]
		cursor = startdate
		for _ in range(0, self.total_days):
			cursor += ONEDAY
			time_domain.append(cursor)

	#	time_domain = np.linspace(0, model.total_days, model.total_days + 1)

		fig = plt.figure(facecolor='w')
		# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
		ax = fig.add_subplot(111, axisbelow=True)

	### Vertical line indicating today
		plt.axvline(x=datetime.today(), alpha=.5, lw=2, label='Today')


	#-------------
	#  Actual numbers, displayed when GA fitting
	#-------------
		act_hosp, act_death = self.actual_curves()
	###   Actual Hospitalized, as specified in the constants
		ax.plot(time_domain, act_hosp, color=(0, 0, .5), alpha=1, lw=2, label='Actual Hospitalized', linestyle='-')
	###   Actual Deaths, as specified in the constants
		ax.plot(time_domain, act_death, color=(0, 0, .5), alpha=1, lw=2, label='Actual Deaths', linestyle='-')

	#-------------
	#  Basic SEIR
	#-------------
	###   Susceptible line, usually too tall
#		ax.plot(time_domain, self.scenario.out_susceptible, label='Susceptible', color=(0, 0, 1), alpha=.5, lw=2, linestyle='-')
	###   Exposed: pre-symptomatic, not infectious yet
#   	ax.plot(time_domain, self.scenario.incubating,      label='Exposed',     color=TABLEAU_ORANGE, alpha=0.1, lw=2, linestyle='-')
	###   Infectious patients, not isolated
#   	ax.plot(time_domain, self.scenario.infectious,      label='Infected',    color=TABLEAU_RED, alpha=0.5, lw=2, linestyle='-')
	###   Recovered/immune, usually too tall
#   	ax.plot(time_domain, self.scenario.sum_recovered,   label='Recovered',   color=(0, .5, 0), alpha=.5, lw=2, linestyle='--')
	###   Infected, isolated at home
#   	ax.plot(time_domain, self.scenario.sum_isolated,    label='Home Iso',    color=TAB_COLORS[8], alpha=.5, lw=2, linestyle='-')
	###   Deceased
		ax.plot(time_domain, self.scenario.sum_deceased,    label='Deceased',    color=(.25, .25, 0), alpha=.5, lw=2, linestyle='--')

	#-------------
	#  Hospital Capacities
	#-------------
#		ax.plot(time_domain, self.scenario.sum_floor, label='Floor Beds',         color=TABLEAU_BLUE, alpha=1, lw=2, linestyle='--')
#		ax.plot(time_domain, self.scenario.sum_icu,   label='ICU Beds',           color=TABLEAU_GREEN, alpha=1, lw=2, linestyle='--')
#		ax.plot(time_domain, self.scenario.sum_vent,  label='ICU + Vent Beds',    color=TABLEAU_RED, alpha=1, lw=2, linestyle='--')
		ax.plot(time_domain, hospitalized,            label='Total Hospitalized', color=(1, 0, 0), alpha=.25, lw=2, linestyle='-')

	#-------------
	#  Hospital Capacities - DH Specific
	#-------------
#		ax.plot(time_domain, [86] * (self.total_days + 1) , label='Supply - DH ICU Beds'  , color=(1, 0, 0), alpha=1, lw=1, linestyle='-')
#		ax.plot(time_domain, [229] * (self.total_days + 1), label='Supply - DH Total Beds', color=(0, 0, 1), alpha=1, lw=1, linestyle='-')

	#-------------
	#  Hospital Capacities - Denver County
	#-------------
#		ax.plot(time_domain, [695] * (self.total_days + 1) , label='Supply - 5C ICU Beds'  , color=(1, 0, 0), alpha=1, lw=1, linestyle='-')
#		ax.plot(time_domain, [5907] * (self.total_days + 1), label='Supply - 5C Total Beds', color=(0, 0, 1), alpha=1, lw=1, linestyle='-')
#		ax.plot(time_domain, [1043] * (self.total_days + 1), label='Supply - 5C ICU Beds'  , color=(1, 0, 0), alpha=1, lw=1, linestyle='-')
#		ax.plot(time_domain, [8861] * (self.total_days + 1), label='Supply - 5C Total Beds', color=(0, 0, 1), alpha=1, lw=1, linestyle='-')

	#-------------
	#  Hospital Capacities - Five County
	#-------------
#		ax.plot(time_domain, [255] * (self.total_days + 1) , label='Supply - 5C ICU Beds'  , color=(1, 0, 0), alpha=1, lw=1, linestyle='-')
#		ax.plot(time_domain, [1000] * (self.total_days + 1), label='Supply - 5C Total Beds', color=(0, 0, 1), alpha=1, lw=1, linestyle='-')
#		ax.plot(time_domain, [1043] * (self.total_days + 1), label='Supply - 5C ICU Beds'  , color=(1, 0, 0), alpha=1, lw=1, linestyle='-')
#		ax.plot(time_domain, [4135] * (self.total_days + 1), label='Supply - 5C Total Beds', color=(0, 0, 1), alpha=1, lw=1, linestyle='-')

    # ------------
    # Hospital Capacities - Five County - 50%
    # ------------
#       ax.plot(time_domain, [348] * (model.total_days + 1) , label='Supply - 5County ICU', color=(0, 0, 1), alpha=1, lw=1, linestyle='--')
#       ax.plot(time_domain, [2954] * (model.total_days + 1), label='Supply - 5County Tot', color=(1, 0, 0), alpha=1, lw=1, linestyle='-')
#       ax.plot(time_domain, [521] * (model.total_days + 1) , label='1.5x 5County ICU'    , color=(0, 0, 1), alpha=1, lw=1, linestyle='--')
#       ax.plot(time_domain, [4430] * (model.total_days + 1), label='1.5x 5County Tot'    , color=(1, 0, 0), alpha=1, lw=1, linestyle='-')

    #make pretty

    # set the style of the axes and the text color
		plt.rcParams['axes.edgecolor'] = '#333F4B'
		plt.rcParams['axes.linewidth'] = 0.8
		plt.rcParams['xtick.color'] = '#333F4B'
		plt.rcParams['ytick.color'] = '#333F4B'
		plt.rcParams['text.color'] = '#333F4B'

    # set axis
		ax.tick_params(axis='both', which='major', labelsize=12)

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
							f"{self.scenario.sum_isolated[itr]:.6f}, "
							f"{self.scenario.sum_noncrit[itr]:.6f}, "
							f"{self.scenario.sum_icu[itr]:.6f}, "
							f"{self.scenario.sum_icu_vent[itr]:.6f}, "
							f"{self.scenario.sum_recovered[itr]:.6f}, "
							f"{self.scenario.sum_deceased[itr]:.6f}, "
							f"{self.scenario.sum_hospitalized[itr]:.6f}\n")

ONEDAY = timedelta(1)

def main():
	if len(sys.argv) > 1:
		scenariofile = sys.argv[1]
	else:
		scenariofile = 'ga_fit.json'
	model = ScenarioDrivenModel(scenariofile)

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
