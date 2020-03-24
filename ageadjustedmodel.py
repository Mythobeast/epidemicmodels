import matplotlib.pyplot as plt
import numpy as np

from amortizedmarkov import ProbState, AgeGroup
from constants import *


# Like SEIR, but moves 15% of the "recovered" into the hospital for an average length hospital stay
# https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology
class AgeAdjustedModel:
	def __init__(self):
		self.r0 = 2.65
		self.total_days = 0
		self.population = POP_DENVER

		self.susceptible = ProbState(period=0, count=self.population-1, name='susceptible')
		self.incubating = ProbState(period=3, name='incubating')
		self.infectious = ProbState(period=3.8, count=1, name='infectious')
		self.isolated_holding = ProbState(period=90, name='isolated_holding')

		self.incubating.add_exit_state(self.infectious, 1)
		self.incubating.normalize_states_over_period()

		self.infectious.add_exit_state(self.isolated_holding, 1)
		self.infectious.normalize_states_over_period()

		self.subgroups = dict()
		for key, value in AGE_BASED_RATES.items():
			self.subgroups[key] = AgeGroup(value, name=key)

		self.sum_isolated = None
		self.sum_noncrit = None
		self.sum_crit = None
		self.sum_icu = None
		self.sum_recovered = None
		self.sum_deceased = None

	def gather_sums(self):
		print(f"base:{len(self.susceptible.domain)}")
		self.sum_isolated = [0] * len(self.susceptible.domain)
		self.sum_noncrit =  [0] * len(self.susceptible.domain)
		self.sum_crit =  [0] * len(self.susceptible.domain)
		self.sum_icu =  [0] * len(self.susceptible.domain)
		self.sum_recovered =  [0] * len(self.susceptible.domain)
		self.sum_deceased =  [0] * len(self.susceptible.domain)
		print(f"final isolated 0-9:{len(self.subgroups['0-9'].isolated.domain)} {self.subgroups['0-9'].isolated.pending}, {self.subgroups['0-9'].isolated.count}")

		for key, value in self.subgroups.items():
			print(f"adding isolated {key}:  {self.sum_isolated} {value.isolated.domain}")
			self.sum_isolated  = np.add(self.sum_isolated, value.isolated.domain)
			self.sum_noncrit   = np.add(self.sum_noncrit, value.h_noncrit.domain)
			self.sum_crit      = np.add(self.sum_crit, value.h_crit.domain)
			self.sum_icu       = np.add(self.sum_icu, value.h_icu.domain)
			self.sum_recovered = np.add(self.sum_recovered, value.recovered.domain)
			self.sum_deceased  = np.add(self.sum_deceased, value.deceased.domain)

	def reset(self):
		self.total_days = 0
		self.susceptible.reset()
		self.susceptible.count = self.population - 1
		self.incubating.reset()
		self.infectious.reset()
		self.infectious.count = 1

		self.subgroups = dict()
		for key, value in AGE_BASED_RATES.items():
			self.subgroups[key] = AgeGroup(value, name=key)

	def set_r0(self, value):
		self.r0 = value

	def set_population(self, value):
		self.population = value

	def recalculate(self):
		self.beta = self.r0 / self.infectious.period

	def run_period(self, days):
		# Integrate the SIR equations over the time grid, t.
		for _ in range(0, days):
			self.step_day()

	def run_r0_set(self, date_offsets, r0_values):
		self.reset()

		day_counter = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(r0_values[itr])
			self.recalculate()
			while day_counter < date_offsets[itr]:
				self.step_day()
				day_counter += 1

	def step_day(self):
		new_infections = self.beta * self.susceptible.count * self.infectious.count / self.population
		print(f"Day {self.total_days}, {self.beta} * {self.susceptible.count} * {self.infectious.count} / {self.population} = {new_infections}")
		self.susceptible.store_pending(-new_infections)
		self.incubating.store_pending(new_infections)
		self.incubating.pass_downstream()
		self.infectious.pass_downstream()

		diagnosed = self.isolated_holding.pending
		self.isolated_holding.pending = 0

		for key, agegroup in self.subgroups.items():
			subpop = diagnosed * agegroup.stats.pop_dist
			agegroup.apply_infections(subpop)
			agegroup.calculate_redistributions()
#		print(f"isolated 0-9:{len(self.subgroups['0-9'].isolated.domain)} {self.subgroups['0-9'].isolated.pending}, {self.subgroups['0-9'].isolated.count}")

		self.susceptible.apply_pending()
		self.incubating.apply_pending()
		self.infectious.apply_pending()

		for key, agegroup in self.subgroups.items():
			agegroup.apply_pending()

#		print(f"isolated 0-9:{len(self.subgroups['0-9'].isolated.domain)} {self.subgroups['0-9'].isolated.pending}, {self.subgroups['0-9'].isolated.count}")

		self.total_days += 1





def main():
	model = AgeAdjustedModel()

	# ref: dola denver est 2020 (july) 737855
	# ref: https://www.colorado.gov/pacific/cdphe/2019-novel-coronavirus
	model.set_population(POP_DENVER)

	date_offsets = [30, 45, 53, 60, 68, 159]
	r0_values = [BASE_R0, BASE_R0 - .2, BASE_R0 - .5, BASE_R0 - 1, 1.55, BASE_R0]

	model.run_r0_set(date_offsets, r0_values)
	model.gather_sums()

	u_susc = model.susceptible.domain
	u_incu = model.incubating.domain
	u_infe = model.infectious.domain
	u_isol = model.sum_isolated
	u_h_no = model.sum_noncrit
	u_h_cr = model.sum_crit
	u_h_ic = model.sum_icu
	u_reco = model.sum_recovered
	u_dead = model.sum_deceased

	time_domain = np.linspace(0, model.total_days, model.total_days + 1)
	hospitalized = []
	for itr in range(0, len(u_h_cr)):
		hospitalized.append(u_h_no[itr] + u_h_cr[itr] + u_h_ic[itr])

	fig = plt.figure(facecolor='w')
	# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
	ax = fig.add_subplot(111, axisbelow=True)
#	ax.plot(time_domain, u_susc, color=(0, 0, 1), alpha=.5, lw=2, label='Susceptible', linestyle='-')
#	ax.plot(time_domain, u_incu, color=TABLEAU_ORANGE, alpha=0.1, lw=2, label='Exposed', linestyle='-')
#	ax.plot(time_domain, u_infe, color=TABLEAU_RED, alpha=0.5, lw=2, label='Infected', linestyle='-')
#	ax.plot(time_domain, u_isol, color=TAB_COLORS[8], alpha=.5, lw=2, label='Home Iso', linestyle='-')
	ax.plot(time_domain, u_h_no, color=TAB_COLORS[10], alpha=.5, lw=2, label='Hosp Noncrit', linestyle=':')
	ax.plot(time_domain, u_h_cr, color=TAB_COLORS[12], alpha=.5, lw=2, label='Hosp Crit', linestyle=':')
	ax.plot(time_domain, u_h_ic, color=(1, 0, 0), alpha=.5, lw=2, label='ICU', linestyle=':')
	ax.plot(time_domain, hospitalized, color=(1, 0, 0), alpha=1, lw=2, label='Total Hospitalized', linestyle='-')
#	ax.plot(time_domain, u_reco, color=(0, .5, 0), alpha=.5, lw=2, label='Recovered', linestyle='--')
	ax.plot(time_domain, u_dead, color=(0, 0, 0), alpha=.5, lw=2, label='Dead', linestyle='--')

	ax.plot(time_domain, [511] * (model.total_days + 1), color=(0, 0, 1), alpha=1, lw=1, label='511 Beds', linestyle='-')
	ax.plot(time_domain, [77] * (model.total_days + 1), color=(1, 0, 0), alpha=1, lw=1, label='77 ICU units', linestyle='-')

	ax.set_xlabel('Days')
	ax.set_ylabel('Number')

	chart_title = f"COVID-19 Hospitalization Projection\nDenver County | Variable R0"
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
			              f", {u_h_no[itr]:.6f}, {u_h_cr[itr]:.6f}, {u_h_ic[itr]:.6f}, {u_reco[itr]:.6f}"
			              f", {u_dead[itr]:.6f}, {hospitalized[itr]:.6f}\n")

	plt.savefig(f"{outfilename}.png", bbox_inches="tight")
	plt.show()


if __name__ == '__main__':
	main()
