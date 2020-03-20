
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint

from epidemicmodel import EpidemicModel
from constants import *

# SIR Model
# Loosely based on https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/

def deriv_sir(y, t, model):
	S_0, I_0, R_0 = y
	print(f"{S_0}, {I_0}, {R_0} {model.gamma}")

	infections = model.beta * S_0 * I_0 / model.population

	recoveries = model.gamma * I_0

	print(f"Returning:inf {infections}, rec {recoveries}")

	dSdt = -infections
	dIdt = infections - recoveries
	dRdt = recoveries
	return dSdt, dIdt, dRdt

class SIRModel(EpidemicModel):
	def __init__(self):
		super().__init__()

	def reset(self):
		super().reset()

	def recalculate(self):
		self.beta = self.r0 / self.dayspergen
		self.gamma = 1.0 / self.dayspergen

	def run_period(self, days):
		time_domain = np.linspace(0, days, days+1)
		# Initial conditions vector
		init = self.susceptible, self.infected, self.recovered
		# Integrate the SIR equations over the time grid, t.
		results = odeint(deriv_sir, init, time_domain, args=(self,))
		S, I, R = results.T
		self.total_days += days - 1
		self.S_domain.extend(S)
		self.I_domain.extend(I)
		self.R_domain.extend(R)
		self.susceptible = self.S_domain.pop()
		self.infected = self.I_domain.pop()
		self.recovered = self.R_domain.pop()

	def run_r0_set(self, date_offsets, beta_values):
		self.susceptible = self.population - self.infected - self.recovered - self.exposed
		self.beta = self.r0 / self.dayspergen

		prev_date = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(beta_values[itr])
			span = date_offsets[itr] - prev_date + 1
			self.run_period(span)
			prev_date = date_offsets[itr]

def test_sir():
	sirmodel = SIRModel()

	# ref: dola denver est 2020 (july) 737855
	# ref: https://www.colorado.gov/pacific/cdphe/2019-novel-coronavirus
	sirmodel.set_population(POP_DENVER)
	sirmodel.set_mean_generation_days(6.8)
	sirmodel.set_r0(BASE_R0)
	sirmodel.recalculate()
	sirmodel.run_period(160)

	Su = sirmodel.S_domain
	Iu = sirmodel.I_domain
	Ru = sirmodel.R_domain
	time_domain = np.linspace(0, sirmodel.total_days, sirmodel.total_days+1)
	fig = plt.figure(facecolor='w')
	# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
	ax = fig.add_subplot(111, axisbelow=True)
	ax.plot(time_domain, Su,  color=TABLEAU_BLUE, alpha=0.5, lw=2, label='Susceptible', linestyle='-')
	ax.plot(time_domain, Iu, color=TABLEAU_RED, alpha=0.5, lw=2, label='Infected', linestyle='-')
	ax.plot(time_domain, Ru, color=TABLEAU_GREEN, alpha=0.5, lw=2, label='Recovered', linestyle='-')

	ax.set_xlabel('Days')
	ax.set_ylabel('Number')

	chart_title = f"COVID-19 SIR Model | Denver | R0=2.65 | 6.8 Days per Generation"
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

	outfilename = "_".join(chart_title.replace("|"," ").replace(":", " ").replace(".", " ").split())


	# Write a CSV to this directory
	with open(f"{outfilename}.csv", 'w') as outfile:
		for itr in range(0, len(Su)):
			outfile.write(f"{Su[itr]:.6f}, {Iu[itr]:.6f}, {Ru[itr]:.6f}\n")

	plt.savefig(f"{outfilename}.png", bbox_inches="tight")
	# plt.savefig("Model_SIR_Denver_R0=23_21_Days_FirstCase.png", bbox_inches="tight")
	plt.show()


if __name__ == '__main__':
	test_sir()
