import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint

from covid.sir_model.constants import *

chart_title = f"Model: SIR | Denver | R0=2.65 | 5.0 Days per Generation"
outfilename = "_".join(chart_title.replace("|"," ").replace(":", " ").replace(".", " ").split())



class SIRParameters:
	def __init__(self):
		# ref: https://annals.org/aim/fullarticle/2762808/incubation-period-coronavirus-disease-2019-covid-19-from-publicly-reported
		self.dayspergen = 6.8
		self.incubation = 0
		self.daystoisolation = 0
		self.daystorecovery = 0
		self.population = POP_DENVER
		self.exposed = 0
		self.infected = 1
		self.recovered = 0
		self.succeptible = self.population - 1
		self.r0 = 2.65
		self.alpha = 0.2
		self.gamma = 1.0 /self.dayspergen
		self.beta = self.r0 / self.dayspergen
		self.time_domain = None
		self.total_days = 0

		self.S_domain = []
		self.E_domain = []
		self.I_domain = []
		self.R_domain = []

	def reset(self):
		self.succeptible = self.population - 1
		self.exposed = 0
		self.infected = 1
		self.recovered = 0
		self.total_days = 0
		self.S_domain = []
		self.E_domain = []
		self.I_domain = []
		self.R_domain = []

	def set_mean_generation_days(self, value):
		self.dayspergen = value

	def set_incubation_period(self, value):
		self.incubation = value

	def set_days_to_isolation(self, value):
		self.daystoisolation = value

	def set_r0(self, value):
		self.r0 = value

	def set_population(self, value):
		self.population = value

	def set_exposed(self, value):
		self.exposed = value

	def set_infected(self, value):
		self.infected = value

	def set_recovered(self, value):
		self.recovered = value

	def run_sir_period(self, days):
		self.time_domain = np.linspace(0, days, days)
		# Initial conditions vector
		init = self.succeptible, self.infected, self.recovered
		# Integrate the SIR equations over the time grid, t.
		results = odeint(deriv_sir, init, self.time_domain, args=(self.population, self.beta, self.gamma))
		S, I, R = results.T
		self.total_days += days - 1
		self.S_domain.extend(S)
		self.I_domain.extend(I)
		self.R_domain.extend(R)
		self.succeptible = self.S_domain.pop()
		self.infected = self.I_domain.pop()
		self.recovered = self.R_domain.pop()

	def run_sir_r0_set(self, date_offsets, beta_values):
		self.succeptible = self.population - self.infected - self.recovered - self.exposed
		self.beta = self.r0 / self.dayspergen

		prev_date = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(beta_values[itr])
			span = date_offsets[itr] - prev_date + 1
			self.run_sir_period(span)
			prev_date = date_offsets[itr]

	def run_seir_period(self, days):
		self.time_domain = np.linspace(0, days, days)
		# Initial conditions vector
		init = self.succeptible, self.exposed, self.infected, self.recovered
		# Integrate the SIR equations over the time grid, t.
		results = odeint(deriv_seir, init, self.time_domain, args=(self.population, self.alpha, self.beta, self.gamma))
		S, E, I, R = results.T
		self.total_days += days - 1
		self.S_domain.extend(S)
		self.E_domain.extend(E)
		self.I_domain.extend(I)
		self.R_domain.extend(R)
		self.succeptible = self.S_domain.pop()
		self.exposed = self.E_domain.pop()
		self.infected = self.I_domain.pop()
		self.recovered = self.R_domain.pop()

	def recalculate(self):
		days_infectious = self.dayspergen - self.incubation
		print("Infectious = {days_infectious}")
		self.alpha = 1.0 / self.incubation
		self.beta = self.r0 / days_infectious
		self.gamma = 1.0 / self.daystoisolation


	def run_seir_r0_set(self, date_offsets, r0_values):

		self.succeptible = self.population - self.infected - self.recovered - self.exposed

		prev_date = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(r0_values[itr])
			self.recalculate()
			span = date_offsets[itr] - prev_date + 1
			self.run_seir_period(span)
			prev_date = date_offsets[itr]

# The SIR model differential equations.
def deriv_sir(y, t, N, beta, gamma):
	S_0, I_0, R_0 = y
	dSdt = -beta * S_0 * I_0 / N
	dIdt = beta * S_0 * I_0 / N - gamma * I_0
	dRdt = gamma * I_0
	return dSdt, dIdt, dRdt

# The SIR model differential equations.
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

# The SIR model differential equations.
def deriv_siyhor(y, t, N, alpha, beta, gamma, hosp_req_factor):
	S_0, E_0, I_0, R_0 = y
	infections = beta * S_0 * I_0 / N
	symptomatic = alpha * E_0
	hospitalized = I_0 * hosp_req_factor
	isolated = I_0 * isolated_factor



	recoveries = gamma * I_0
	susceptible_d = -infections
	infected_d =
	infectious_d
	unisolated_d
	isolated_d
	hospitalized_d
	dead_d
	recovered_d
	return dSdt, dEdt, dIdt, dRdt


# ref: https://www.medrxiv.org/content/10.1101/2020.03.10.20033761v1.full.pdf
# ref: https://www.thelancet.com/action/showPdf?pii=S0140-6736%2820%2930260-9
BASE_R0 = 2.65

sirmodel = SIRParameters()

# ref: dola denver est 2020 (july) 737855
# ref: https://www.colorado.gov/pacific/cdphe/2019-novel-coronavirus
sirmodel.set_population(POP_DENVER)

sirmodel.set_mean_generation_days(6.8)
sirmodel.set_r0(BASE_R0)

sirmodel.run_sir_period(160)

Su = sirmodel.S_domain
Eu = sirmodel.E_domain
Iu = sirmodel.I_domain
Ru = sirmodel.R_domain

sirmodel.reset()

#date_offsets = [30,                45,           53,          60,   68,     159]
#beta_values  = [BASE_R0, BASE_R0 - .2, BASE_R0 - .5, BASE_R0 - 1, 1.55, BASE_R0]

#date_offsets = [30,    44,   58,  159]
#beta_values  = [2.65, 2.0, 1.05, 1.65]

# ref: https://annals.org/aim/fullarticle/2762808/incubation-period-coronavirus-disease-2019-covid-19-from-publicly-reported
sirmodel.set_incubation_period(5)
sirmodel.set_days_to_isolation(1.8)

date_offsets = [159]
r0_values  = [2.65]

sirmodel.run_seir_r0_set(date_offsets, r0_values)
#sirmodel.run_seir_r0_set(date_offsets, beta_values)

print(f"Found for days {sirmodel.total_days}")

Sc = sirmodel.S_domain
Ec = sirmodel.E_domain
Ic = sirmodel.I_domain
Rc = sirmodel.R_domain
time_domain = np.linspace(0, sirmodel.total_days, sirmodel.total_days)

with open(f"{outfilename}.csv", 'w') as outfile:
	for itr in range(0, len(Su)):
		outfile.write(f"{Sc[itr]:.6f}, {Ic[itr]:.6f}, {Rc[itr]:.6f}\n")



# Plot the data on three separate curves for S(t), I(t) and R(t)
fig = plt.figure(facecolor='w')
# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
ax = fig.add_subplot(111, axisbelow=True)
ax.plot(time_domain, Su,  color=TABLEAU_BLUE, alpha=0.5, lw=2, label='Susceptible', linestyle='-')
if len(Eu) > 0:
	ax.plot(time_domain, Eu,  color=TABLEAU_ORANGE, alpha=0.5, lw=2, label='Exposed', linestyle='-')
ax.plot(time_domain, Iu, color=TABLEAU_RED, alpha=0.5, lw=2, label='Infected', linestyle='-')
ax.plot(time_domain, Ru, color=TABLEAU_GREEN, alpha=0.5, lw=2, label='Recovered', linestyle='-')

ax.plot(time_domain, Sc, color=TABLEAU_BLUE, alpha=0.5, lw=2, label='Susceptible', linestyle='--')
if len(Ec) > 0:
	ax.plot(time_domain, Ec,  color=TABLEAU_ORANGE, alpha=0.5, lw=2, label='Exposed', linestyle='--')
ax.plot(time_domain, Ic, color=TABLEAU_RED, alpha=0.5, lw=2, label='Uncontrolled', linestyle='--')
ax.plot(time_domain, Rc, color=TABLEAU_GREEN, alpha=0.5, lw=2, label='Recovered', linestyle='--')



ax.set_xlabel('Days')
ax.set_ylabel('Number')

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

plt.savefig(f"{outfilename}.png", bbox_inches="tight")
# plt.savefig("Model_SIR_Denver_R0=23_21_Days_FirstCase.png", bbox_inches="tight")
plt.show()
