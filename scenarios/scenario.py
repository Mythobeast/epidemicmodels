
import json
import math
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from parts.constants import *
from parts.agegrouprates import SubgroupRates

DATEFORMAT = "%Y-%m-%d"
ONEDAY = timedelta(1)

SERIAL = 1


class EpiScenario:

	def __init__(self, configfile):
		self.fitness = None
		global SERIAL
		SERIAL += 1
		self.serial = SERIAL

		if isinstance(configfile, str):
			with open(configfile, 'r') as cf:
				self.parameters = json.load(cf)
		elif isinstance(configfile, dict):
			self.parameters = configfile.copy()

		self.modelname = self.parameters.get('modelname', 'Use modelname parameter of the scenario to fill the title')
		self.totalpop = self.parameters['totalpop']
		self.maxdays = self.parameters.get('chart_period', 160)
		self.incubation_period = self.parameters.get('incubation_period', 4)
		self.prediagnosis = self.parameters.get('prediagnosis_period', 3.6)

		self.init_susceptible = self.parameters['initial_values'].get('susceptible', self.totalpop-1)
		self.init_infected = self.parameters['initial_values'].get('infected', 0)
		self.init_infectious = self.parameters['initial_values'].get('infectious', 1)

		try:
			self.initial_date = datetime.strptime(self.parameters['initial_date'], DATEFORMAT)
		except ValueError as ve:
			if 'does not match format' in ve.message:
				print(f"Exception encountered while parsing initial date: {ve}")
			raise ve

		self.r0_date_offsets = []
		self.r0_values = [self.parameters['initial_r0']]

		try:
			self.initial_date = datetime.strptime(self.parameters['initial_date'], DATEFORMAT)
			for shift in self.parameters['r0_shifts']:
				newdate = datetime.strptime(shift['date'], DATEFORMAT)
				self.r0_date_offsets.append((newdate - self.initial_date).days)
				self.r0_values.append(shift['r0'])

		except ValueError as ve:
			if 'does not match format' in ve.message:
				print(f"Exception encountered while parsing r0 offsets: {ve}")
			raise ve

		self.r0_date_offsets.append(self.maxdays)
		self.age_distribution = self.parameters['age_distribution']
		self.age_projection = self.parameters['age_projection']

		self.subgrouprates = {
			AGE0x: SubgroupRates(self.age_projection[AGE0x], self.age_distribution[AGE0x]),
			AGE1x: SubgroupRates(self.age_projection[AGE1x], self.age_distribution[AGE1x]),
			AGE2x: SubgroupRates(self.age_projection[AGE2x], self.age_distribution[AGE2x]),
			AGE3x: SubgroupRates(self.age_projection[AGE3x], self.age_distribution[AGE3x]),
			AGE4x: SubgroupRates(self.age_projection[AGE4x], self.age_distribution[AGE4x]),
			AGE5x: SubgroupRates(self.age_projection[AGE5x], self.age_distribution[AGE5x]),
			AGE6x: SubgroupRates(self.age_projection[AGE6x], self.age_distribution[AGE6x]),
			AGE7x: SubgroupRates(self.age_projection[AGE7x], self.age_distribution[AGE7x]),
			AGE8x: SubgroupRates(self.age_projection[AGE8x], self.age_distribution[AGE8x])
		}

		# Output result variables
		self.out_susceptible = None
		self.out_incubating  = None
		self.out_infectious  = None
		self.sum_isolated  = None
		self.sum_ed        = None
		self.sum_floor     = None
		self.sum_icu       = None
		self.sum_vent      = None

		self.sum_recovered = None
		self.sum_deceased  = None
		self.sum_hospitalized  = None

		self.sum_noncrit = None
		self.sum_icu = None
		self.sum_icu_vent = None
		self.hospital_door_aggregator = None
		self.fitset = None


	def save_results(self, iteration):
		result = dict()

		result['iteration'] = iteration
		result['serial'] = self.serial
		result['fitness'] = self.fitness
		result['scenario'] = self.parameters
		result['output'] = dict()
		result['output']['susceptible'] = self.out_susceptible
		result['output']['incubating'] = self.out_incubating

		result['output']['infectious'] = self.out_infectious
		result['output']['hospitalized'] = self.hospital_door_aggregator
		result['output']['dead'] = list(self.sum_deceased)

		with open(f"best_fit{iteration}.json", "w") as bfi:
			json.dump(result, bfi)


	def calculate_fit(self, ideal):

		### Prefer models where R1 doesn't vary wildly
		prev_r0 = 3.0
		r0_r2 = 0
		avg_r0 = 0
		for current_r0 in self.r0_values:
			r0_r2 += (prev_r0 - current_r0) ** 2
			avg_r0 += current_r0
			prev_r0 = current_r0

		r2_hold = math.sqrt(r0_r2)
		avg_r0 /= len(self.r0_values)

#		print(f"while {cursor} < {final_offset}, {ideal['start']}, {ideal['end']}")

		### For fitting "currently hospitalized"
#		hosp = self.sum_hospitalized
		# for key, value in ideal.items():
		# 	midhosp = self.fit_hosp[key] / value['hospitalized']
		# 	if midhosp < 1:
		# 		midhosp = 1/midhosp
		# 	hosp_sum += midhosp


		### For fitting Colorado actual
		hosp_r2 = 0
		hosp_avg = 0
		dead_r2 = 0
		dead_avg = 0
		fitcount = 0

		for key, value in ideal.items():
			if key not in self.fitset:
				raise ValueError(f"{key} not found in {self.fitset}")
			fitcount += 1
#			print(f"comparing {self.fitset[key]['total_hosp']} to {value['hospitalized']}")
			hosp_off = self.fitset[key]['total_hosp'] - value['hospitalized']
			hosp_avg += value['hospitalized']
#			if hosp_off < 0:
#				hosp_off = -hosp_off
			hosp_r2 += hosp_off ** 2

			death_off = self.fitset[key]['total_deceased'] - value['deceased']
#			if death_off < 0:
#				death_off = -death_off
			dead_r2 += death_off ** 2
			dead_avg += value['hospitalized']

		hosp_hold = math.sqrt(hosp_r2)
		dead_hold = math.sqrt(dead_r2)
#		print(f"hosp_hold = {hosp_hold}, dead_hold = {dead_hold}")

		self.fitness =  hosp_hold + dead_hold + r2_hold/3


	def generate_png(self):

		startdate = self.initial_date
		time_domain = [startdate]
		cursor = startdate
		for _ in range(0, self.maxdays):
			cursor += ONEDAY
			time_domain.append(cursor)

		hospitalized = []
		for itr in range(0, len(self.sum_noncrit)):
#			print(f"Hospit: {self.sum_noncrit[itr] + self.sum_icu[itr] + self.sum_icu_vent[itr]}")
			self.sum_hospitalized.append(self.sum_noncrit[itr] + self.sum_icu[itr] + self.sum_icu_vent[itr])

		fig = plt.figure(facecolor='w')
		ax = fig.add_subplot(111, axisbelow=True)
		ax.plot(time_domain, self.sum_noncrit, color=TABLEAU_BLUE, alpha=1, lw=2, label='Noncrit', linestyle='--')
		ax.plot(time_domain, self.sum_icu, color=TABLEAU_GREEN, alpha=1, lw=2, label='ICU', linestyle='--')
		ax.plot(time_domain, self.sum_icu_vent, color=TABLEAU_RED, alpha=1, lw=2, label='ICU + Ventilator', linestyle='--')
		ax.plot(time_domain, self.sum_hospitalized, color=(1, 0, 0), alpha=.25, lw=2, label='Total Hospitalized', linestyle='-')

		ax.plot(time_domain, [511] * (self.maxdays + 1), color=(0, 0, 1), alpha=1, lw=1, label='511 Beds', linestyle='-')
		ax.plot(time_domain, [77] * (self.maxdays + 1), color=(1, 0, 0), alpha=1, lw=1, label='77 ICU units', linestyle='-')
		plt.axvline(x=datetime.today(), alpha=.5, lw=2, label='Today')

		ax.set_xlabel('Days')
		ax.set_ylabel('Number')

		chart_title = self.modelname
		plt.title(chart_title, fontsize=14)
		ax.yaxis.set_tick_params(length=4)
		ax.xaxis.set_tick_params(length=4)
		ax.grid()
		legend = ax.legend()
		legend.get_frame().set_alpha(0.5)
		for spine in ('top', 'right', 'bottom', 'left'):
			ax.spines[spine].set_visible(False)

		outfilename = "_".join(chart_title.replace("|", " ").replace(":", " ").replace(".", " ").split())

		# Write a CSV to this directory
		with open(f"{outfilename}.csv", 'w') as outfile:
			for itr in range(0, len(self.out_susceptible)):
				outfile.write(f"{self.out_susceptible[itr]:.6f}, {self.out_incubating[itr]:.6f}, {self.out_infectious[itr]:.6f}, "
						f"{self.sum_isolated[itr]:.6f}, {self.sum_noncrit[itr]:.6f}, {self.sum_icu[itr]:.6f}, "
						f"{self.sum_icu_vent[itr]:.6f}, {self.sum_recovered[itr]:.6f}, {self.sum_deceased[itr]:.6f}, "
						f"{self.sum_hospitalized[itr]:.6f}\n")

		return plt

