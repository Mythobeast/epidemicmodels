import matplotlib.pyplot as plt
import numpy as np

from amortizedmarkov import ProbState, SubgroupRates
from hospitalized_agegroup import AgeGroup
from constants import *
import csv
from datetime import datetime, timedelta

INPUT_FILENAME = "testsocial.csv"

# Like SEIR, but moves 15% of the "recovered" into the hospital for an average length hospital stay
# https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology
class ExternallyDrivenModel:
	def __init__(self):
		self.r0 = 2.65
		self.total_days = 0
		self.population = POP_DENVER

		self.subgroups = dict()
		for key, value in AGE_DISTRIBUTION.items():
			self.subgroups[key] = AgeGroup(SubgroupRates(ICD[key], value), name=key)

		self.sum_isolated = None
		self.sum_noncrit = None
		self.sum_crit = None
		self.sum_icu = None
		self.sum_recovered = None
		self.sum_deceased = None

		self.daily_input = None

	def load_daily_hospitalized(self, filename):
		self.daily_input = []
		with open(filename, newline='') as inf:
			thereader = csv.reader(inf)
			for row in thereader:
				self.daily_input.append(row)

	def gather_sums(self):
#		print(f"base:{len(self.susceptible.domain)}")
		daycount = len(self.subgroups[AGE0x].isolated.domain)
		self.sum_isolated =  [0] * daycount
		self.sum_noncrit =   [0] * daycount
		self.sum_icu =       [0] * daycount
		self.sum_icu_vent =  [0] * daycount
		self.sum_recovered = [0] * daycount
		self.sum_deceased =  [0] * daycount
#		print(f"final isolated 0-9:{len(self.subgroups['0-9'].isolated.domain)} {self.subgroups['0-9'].isolated.pending}, {self.subgroups['0-9'].isolated.count}")

		for key, value in self.subgroups.items():
#			print(f"adding isolated {key}:  {self.sum_isolated} {value.isolated.domain}")
			self.sum_isolated  = np.add(self.sum_isolated, value.isolated.domain)
			self.sum_noncrit   = np.add(self.sum_noncrit, value.h_noncrit.domain)
			self.sum_icu       = np.add(self.sum_icu, value.h_icu.domain)
			self.sum_icu_vent  = np.add(self.sum_icu_vent, value.h_icu_vent.domain)
			self.sum_recovered = np.add(self.sum_recovered, value.recovered.domain)
			self.sum_deceased  = np.add(self.sum_deceased, value.deceased.domain)

	def reset(self):
		self.total_days = 0
		self.subgroups = dict()
		for key, value in AGE_DISTRIBUTION.items():
			self.subgroups[key] = AgeGroup(SubgroupRates(ICD[key], value), name=key)

	def set_population(self, value):
		self.population = value

	def run(self):
		self.reset()
		while len(self.daily_input) > 0:
			self.step_day()

	def step_day(self):

		todayset = self.daily_input.pop(0)
		self.subgroups[AGE0x].apply_infections(todayset[1])
		self.subgroups[AGE0x].calculate_redistributions()
		self.subgroups[AGE1x].apply_infections(todayset[2])
		self.subgroups[AGE1x].calculate_redistributions()
		self.subgroups[AGE2x].apply_infections(todayset[3])
		self.subgroups[AGE2x].calculate_redistributions()
		self.subgroups[AGE3x].apply_infections(todayset[4])
		self.subgroups[AGE3x].calculate_redistributions()
		self.subgroups[AGE4x].apply_infections(todayset[5])
		self.subgroups[AGE4x].calculate_redistributions()
		self.subgroups[AGE5x].apply_infections(todayset[6])
		self.subgroups[AGE5x].calculate_redistributions()
		self.subgroups[AGE6x].apply_infections(todayset[7])
		self.subgroups[AGE6x].calculate_redistributions()
		self.subgroups[AGE7x].apply_infections(todayset[8])
		self.subgroups[AGE7x].calculate_redistributions()
		self.subgroups[AGE8x].apply_infections(todayset[9])
		self.subgroups[AGE8x].calculate_redistributions()

		for key, agegroup in self.subgroups.items():
			agegroup.apply_pending()

		self.total_days += 1

ONEDAY = timedelta(1)


def main():
	model = ExternallyDrivenModel()

	# ref: dola denver est 2020 (july) 737855
	# ref: https://www.colorado.gov/pacific/cdphe/2019-novel-coronavirus
	model.set_population(POP_DENVER)
	model.load_daily_hospitalized(INPUT_FILENAME)

	model.run()
	model.gather_sums()

	u_isol = model.sum_isolated
	u_h_no = model.sum_noncrit
	u_h_ic = model.sum_icu
	u_h_ve = model.sum_icu_vent
	u_reco = model.sum_recovered
	u_dead = model.sum_deceased

	startdate = datetime(2020, 2, 15)
	time_domain = [startdate]
	cursor = startdate
	for _ in range(1, len(u_isol)):
		cursor += ONEDAY
		time_domain.append(cursor)

#	time_domain = np.linspace(0, model.total_days, model.total_days + 1)
	hospitalized = []
	for itr in range(0, len(u_h_ic)):
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

	chart_title = f"COVID-19 Hospitalization Projection\nDenver County | Socially modeled"
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
		for itr in range(0, len(u_h_no)):
			outfile.write(f" {u_isol[itr]:.6f}"
			              f", {u_h_no[itr]:.6f}, {u_h_ic[itr]:.6f}, {u_h_ve[itr]:.6f}, {u_reco[itr]:.6f}"
			              f", {u_dead[itr]:.6f}, {hospitalized[itr]:.6f}\n")

	plt.savefig(f"{outfilename}.png", bbox_inches="tight")
	plt.show()


if __name__ == '__main__':
	main()
