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
	 # model = ScenarioDrivenModel('DenverQuarterReducedAge.json')
    model = ScenarioDrivenModel('DenverQuarterPopulationAdjstments.json')

    # model = ScenarioDrivenModel('DenverQuarter.json')

    # model = ScenarioDrivenModel('DenverHalf.json')
    #  model = ScenarioDrivenModel('DenverFull.json')
    # model = ScenarioDrivenModel('DenverFull_Rolling.json')

    # model = ScenarioDrivenModel('5County.json')
    # model = ScenarioDrivenModel('7County.json')
    # model = ScenarioDrivenModel('colorado.json')

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

    time_domain = np.linspace(0, model.total_days, model.total_days + 1)
    hospitalized = []
    for itr in range(0, len(u_h_no)):
        hospitalized.append(u_h_no[itr] + u_h_ic[itr] + u_h_ve[itr])
    #print(model.scenario.
    print(model.r0)

    fig = plt.figure(facecolor='w')
    # ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
    ax = fig.add_subplot(111, axisbelow=True)

    #------------
    #basic SIER
    #------------

    #SEIR
    # ax.plot(time_domain, u_susc, color=TABLEAU_BLUE, alpha=.5, lw=2, label='Susceptible', linestyle='-')
    # ax.plot(time_domain, u_incu, color=TABLEAU_ORANGE, alpha=.75, lw=2, label='Exposed', linestyle='-')
    # ax.plot(time_domain, u_infe, color=TABLEAU_RED, alpha=0.5, lw=2, label='Infected', linestyle='-')
    # # ax.plot(time_domain, u_isol, color=TAB_COLORS[8], alpha=.5, lw=2, label='Home Isolated', linestyle='-')
    # ax.plot(time_domain, u_reco, color=TABLEAU_GREEN, alpha=.5, lw=2, label='Recovered', linestyle='--')
    # # ax.plot(time_domain, u_dead, color=(0, 0, 0), alpha=.5, lw=2, label='Dead', linestyle=':')

    #------------
    #hosp cap
    #------------
    ax.plot(time_domain, u_h_no, color=TABLEAU_GREEN, alpha=1, lw=1.5, label='Demand - Non-Critical', linestyle='-')
    ax.plot(time_domain, u_h_ic, color=TABLEAU_ORANGE, alpha=1, lw=1.5, label='Demand - ICU (w/o Ventilator)', linestyle='--')
    ax.plot(time_domain, u_h_ve, color=TABLEAU_RED, alpha=1, lw=1.5, label='Demand - ICU (w/ Ventilator)', linestyle='--')
    ax.plot(time_domain, hospitalized, color=TABLEAU_BLUE, alpha=1, lw=1.5, label='Demand - Total Hospitalized', linestyle='-')
    ax.plot(time_domain, u_h_ic+u_h_ve, color=TABLEAU_PURPLE, alpha=1, lw=1.5, label='Demand - Total ICU', linestyle='-')

    # ------------
    # Capacity Lines - Denver County - Empty
    # ------------

    # normal
    # ax.plot(time_domain, [695] * (model.total_days + 1), color=(0, 0, 0), alpha=.8, lw=1.5, label='Supply - 5C ICU Beds', linestyle='-')
    # ax.plot(time_domain, [5907] * (model.total_days + 1), color=(0, 0, 0), alpha=1, lw=1.5, label='Supply - 5C Total Beds', linestyle='-')

    # surge 1.5
    # ax.plot(time_domain, [1043] * (model.total_days + 1), color=(0, 0, 0), alpha=.5, lw=1.5, label='Supply - 1.5x 5C ICU Beds', linestyle='--')
    # ax.plot(time_domain, [8861] * (model.total_days + 1), color=(0, 0, 0), alpha=.5, lw=1.5, label='Supply - 1.5x 5C Total Beds', linestyle='--')

    #------------
    # Capacity Lines - 5 County - Empty
    #------------

    # normal
    # ax.plot(time_domain, [255] * (model.total_days + 1), color=(0, 0, 0), alpha=.8, lw=1.5, label='Supply - 2x County ICU Beds', linestyle='-')
    # ax.plot(time_domain, [1000] * (model.total_days + 1), color=(0, 0, 0), alpha=1, lw=1.5, label='Supply - 70% County Total Beds', linestyle='-')

    #surge 1.5
    # ax.plot(time_domain, [1043] * (model.total_days + 1), color=(0, 0, 0), alpha=.5, lw=1.5, label='Supply - 1.5x 5C ICU Beds', linestyle='--')
    # ax.plot(time_domain, [4135] * (model.total_days + 1), color=(0, 0, 0), alpha=.5, lw=1.5, label='Supply - 70% 5C Total Beds', linestyle='--')

    # ------------
    # Capacity Lines - 5 County - 50%
    # ------------

    # ax.plot(time_domain, [348] * (model.total_days + 1), color=(0, 0, 1), alpha=1, lw=1, label='Supply - 5County ICU', linestyle='--')
    # ax.plot(time_domain, [2954] * (model.total_days + 1), color=(1, 0, 0), alpha=1, lw=1, label='5County Tot', linestyle='-')
    #
    # ax.plot(time_domain, [521] * (model.total_days + 1), color=(0, 0, 1), alpha=1, lw=1, label='1.5x 5County ICU', linestyle='--')
    # ax.plot(time_domain, [4430] * (model.total_days + 1), color=(1, 0, 0), alpha=1, lw=1, label='1.5x 5County Tot', linestyle='-')
    #
    # ------------
    # Capacity Lines - DH  - Specific
    # # ------------
    ax.plot(time_domain, [86] * (model.total_days + 1), color=(0, 0, 0), alpha=.7, lw=1, label='Supply - DH ICU Beds', linestyle='--')
    ax.plot(time_domain, [129] * (model.total_days + 1), color=(0, 0, 0), alpha=1, lw=1, label='Supply - DH Total Beds', linestyle='-')


    #make pretty

    # set the style of the axes and the text color
    plt.rcParams['axes.edgecolor'] = '#333F4B'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['xtick.color'] = '#333F4B'
    plt.rcParams['ytick.color'] = '#333F4B'
    plt.rcParams['text.color'] = '#333F4B'

    # set axis
    ax.tick_params(axis='both', which='major', labelsize=12)

    # set labels
    ax.set_xlabel('Days')
    ax.set_ylabel('Number')


    chart_title = model.modelname
    plt.title(chart_title, fontsize=14)

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
            outfile.write(f"{u_susc[itr]:.6f}, "
                          f"{u_incu[itr]:.6f}, "
                          f"{u_infe[itr]:.6f}, "
                          f"{u_isol[itr]:.6f}, "
                          f"{u_h_no[itr]:.6f}, "
                          f"{u_h_ic[itr]:.6f}, "
                          f"{u_h_ve[itr]:.6f}, "
                          f"{u_reco[itr]:.6f}, "
                          f"{u_dead[itr]:.6f}, "
                          f"{hospitalized[itr]:.6f}\n")

    plt.savefig(f"{outfilename}.png", bbox_inches="tight")
    plt.show()

if __name__ == '__main__':
	main()
