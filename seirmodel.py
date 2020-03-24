
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint

from epidemicmodel import EpidemicModel
from constants import *

# Adding exposed delay before infectious
# https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology
class SEIRModel(EpidemicModel):
	def __init__(self):
		super().__init__()
		# ref: https://annals.org/aim/fullarticle/2762808/incubation-period-coronavirus-disease-2019-covid-19-from-publicly-reported
		self.incubation = 0
		self.exposed = 0
		self.daystoisolation = 0
		self.daystorecovery = 0
		self.E_domain = []
		self.alpha = 0.2

	def reset(self):
		super().reset()
		self.exposed = 0
		self.E_domain = []

	def set_exposed(self, value):
		self.exposed = value

	def set_incubation_period(self, value):
		self.incubation = value

	def set_days_to_isolation(self, value):
		self.daystoisolation = value

	def recalculate(self):
		days_infectious = self.dayspergen - self.incubation
		self.alpha = 1.0 / self.incubation
		self.beta = self.r0 / days_infectious
		self.gamma = 1.0 / self.daystoisolation

	def run_period(self, days):
		self.time_domain = np.linspace(0, days, days)
		# Initial conditions vector
		init = self.susceptible, self.exposed, self.infected, self.recovered
		# Integrate the SIR equations over the time grid, t.
		results = odeint(deriv_seir, init, self.time_domain, args=(self.population, self.alpha, self.beta, self.gamma))
		S, E, I, R = results.T
		self.total_days += days - 1
		self.S_domain.extend(S)
		self.E_domain.extend(E)
		self.I_domain.extend(I)
		self.R_domain.extend(R)
		self.susceptible = self.S_domain.pop()
		self.exposed = self.E_domain.pop()
		self.infected = self.I_domain.pop()
		self.recovered = self.R_domain.pop()

	def run_r0_set(self, date_offsets, r0_values):
		self.susceptible = self.population - self.infected - self.recovered - self.exposed

		prev_date = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(r0_values[itr])
			self.recalculate()
			span = date_offsets[itr] - prev_date + 1
			self.run_period(span)
			prev_date = date_offsets[itr]


# The SEIR model differential equations.
def deriv_seir(y, t, N, alpha, beta, gamma):
	S_0, E_0, I_0, R_0 = y
	infections = beta * S_0 * I_0 / N
	symptomatic = alpha * E_0
	recoveries = gamma * I_0
	dSdt = -infections
	dEdt = infections - symptomatic
	dIdt = symptomatic - recoveries
	dRdt = recoveries
	return dSdt, dEdt, dIdt, dRdt


def test_seir():
	seirmodel = SEIRModel()

	# ref: dola denver est 2020 (july) 737855
	# ref: https://www.colorado.gov/pacific/cdphe/2019-novel-coronavirus
	seirmodel.set_population(POP_DENVER)
	seirmodel.set_mean_generation_days(6.8)
	seirmodel.set_r0(BASE_R0)
	seirmodel.set_incubation_period(3)
	seirmodel.set_days_to_isolation(3.8)
	seirmodel.recalculate()
	seirmodel.run_period(160)

	Su = seirmodel.S_domain
	Eu = seirmodel.E_domain
	Iu = seirmodel.I_domain
	Ru = seirmodel.R_domain

	seirmodel.reset()

	# for calculating the effects of social distancing over time

	# social distancing 1 -- Day 35
	date_offsets = [		 36,   				  37,   	  	   38,   			     40,  		        43,  		   159]
	r0_values  = [BASE_R0 -.25, 		BASE_R0 -.5, 	  BASE_R0 -1, 			BASE_R0 -2, 	 BASE_R0 -2.5,	 BASE_R0 -2.5]

	# social distancing 2 -- 45
	# date_offsets = [	   45,   			47,   	  	     48,   			       50,  		  53,  			 159]
	# r0_values  = [BASE_R0-.25, 		BASE_R0-.5, 	  BASE_R0-1, 			BASE_R0-2, 	 BASE_R0-2.5,	 BASE_R0-2.5]

	seirmodel.run_r0_set(date_offsets, r0_values)

	Sc = seirmodel.S_domain
	Ec = seirmodel.E_domain
	Ic = seirmodel.I_domain
	Rc = seirmodel.R_domain

	time_domain = np.linspace(0, seirmodel.total_days, seirmodel.total_days)

	fig = plt.figure(facecolor='w')
	# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
	ax = fig.add_subplot(111, axisbelow=True)
	ax.plot(time_domain, Su,  color=TABLEAU_BLUE, alpha=0.5, lw=2, label=f"Susceptible, R0={BASE_R0}", linestyle='-')
	ax.plot(time_domain, Eu,  color=TABLEAU_ORANGE, alpha=0.5, lw=2, label=f"Exposed, R0={BASE_R0}", linestyle='-')
	ax.plot(time_domain, Iu, color=TABLEAU_RED, alpha=0.5, lw=2, label=f"Infected, R0={BASE_R0}", linestyle='-')
	ax.plot(time_domain, Ru, color=TABLEAU_GREEN, alpha=0.5, lw=2, label=f"Recovered, R0={BASE_R0}", linestyle='-')

	ax.plot(time_domain, Sc, color=TABLEAU_BLUE, alpha=0.5, lw=2, label=f"Susceptible, Social Distancing", linestyle='--')
	ax.plot(time_domain, Ec,  color=TABLEAU_ORANGE, alpha=0.5, lw=2, label=f"Exposed, Social Distancing", linestyle='--')
	ax.plot(time_domain, Ic, color=TABLEAU_RED, alpha=0.5, lw=2, label=f"Infected, Social Distancing", linestyle='--')
	ax.plot(time_domain, Rc, color=TABLEAU_GREEN, alpha=0.5, lw=2, label=f"Recovered, Social Distancing", linestyle='--')

	ax.set_xlabel('Days')
	ax.set_ylabel('Population')

	chart_title = f"COVID-19 SEIR Model, Denver County\n R0={BASE_R0} vs Social Distancing starting Day 35"
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
			outfile.write(f"{Sc[itr]:.6f}, {Ec[itr]:.6f}, {Ic[itr]:.6f}, {Rc[itr]:.6f}\n")

	plt.savefig(f"{outfilename}.png", bbox_inches="tight")
	plt.show()


if __name__ == '__main__':
	test_seir()
