import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint

from amortizedmarkov import ProbState
from constants import *


MAX_HOSPITAL_LOAD = 20000


def adjust_for_overload(noncritical, critical, icu, d_noncritical, d_critical, d_icu, d_unhospitalized):
	hospital_load = icu + critical + noncritical + d_icu + d_critical + d_noncritical
	if hospital_load < MAX_HOSPITAL_LOAD:
		return d_noncritical, d_critical, d_icu, d_unhospitalized

	overload = hospital_load - MAX_HOSPITAL_LOAD
	# First, noncritical are turned away
	if overload < d_noncritical:
		d_unhospitalized += overload
		d_noncritical -= overload
		return d_noncritical, d_critical, d_icu, d_unhospitalized

	d_unhospitalized += d_noncritical
	overload -= d_noncritical
	d_noncritical = 0

	# Second, noncritical are displaced
	if overload < noncritical:
		d_noncritical -= overload
		d_unhospitalized += overload
		return d_noncritical, d_critical, d_icu, d_unhospitalized

	d_unhospitalized += noncritical
	overload -= noncritical
	d_noncritical -= noncritical

	# third, critical are turned away
	if overload < d_critical:
		d_critical -= overload
		d_unhospitalized += overload
		return d_noncritical, d_critical, d_icu, d_unhospitalized

	d_unhospitalized += d_critical
	overload -= d_critical
	d_critical = 0

	# Fourth, ICU are turned away.
	# Mathematically, it should never get here because all ICU are critical relocations
	if overload < d_icu:
		d_icu -= overload
		d_unhospitalized += overload
		return d_noncritical, d_critical, d_icu, d_unhospitalized

	d_unhospitalized += d_icu
	d_icu = 0

	return d_noncritical, d_critical, d_icu, d_unhospitalized




# The SEIR model differential equations.
def deriv_seirh(y, t, model):
	(i_susceptible, i_incubating,
		 i_infectious, i_isolated,
		 i_noncritical, i_critical,
		 i_icu, i_unhospitalized,
		 i_recovered, i_dead) = y
	print(f"y={y}")
	pop_sum = (i_susceptible + i_incubating + i_infectious + i_isolated + i_noncritical + i_critical +
		 i_icu + i_unhospitalized + i_recovered + i_dead)
	if (pop_sum - POP_FRONTRANGE) > 10:
		raise ValueError(f"Pop sum {int(pop_sum)} != {POP_FRONTRANGE}")
	new_infections = model.beta * i_susceptible * i_infectious / model.population

	(new_symptomatic,) = model.incubating.get_state_redist(i_incubating)
	new_isolated, new_noncritical, new_critical = model.infectious.get_state_redist(i_infectious)
	(recovered1,) = model.isolated.get_state_redist(i_isolated)
	(recovered2,) = model.h_noncritical.get_state_redist(i_noncritical)
	(new_icu,) = model.h_critical.get_state_redist(i_critical)
	recovered3, dead1 = model.h_icu.get_state_redist(i_icu)
	recovered4, dead2 = model.unhospitalized.get_state_redist(i_unhospitalized)

	d_susceptible = -new_infections
	d_incubating = new_infections - new_symptomatic
	d_infectious = new_symptomatic - (new_isolated + new_noncritical + new_critical)
	d_isolated = new_isolated - recovered1
	d_noncritical = new_noncritical - recovered2
	d_critical = new_critical - new_icu
	d_icu = new_icu - (recovered3 + dead1)
	d_unhospitalized = -(recovered4 + dead2)
	d_recovered = recovered1 + recovered2 + recovered3 + recovered4
	d_dead = dead1 + dead2

	(d_noncritical, d_critical, d_icu, d_unhospitalized) = adjust_for_overload(
		i_noncritical, i_critical, i_icu, d_noncritical, d_critical, d_icu, d_unhospitalized)

	print(f"Outlist: {d_susceptible}, {d_incubating}, {d_infectious}, {d_isolated}, {d_noncritical},"\
			f"{d_critical}, {d_icu}, {d_unhospitalized}, {d_recovered}, {d_dead}")
	balances = (d_susceptible + d_incubating + d_infectious + d_isolated + d_noncritical + d_critical + \
	           d_icu + d_unhospitalized + d_recovered + d_dead)
	if int(balances) != 0:
		raise ValueError(f"balances {balances} != 0")

	return (d_susceptible, d_incubating, d_infectious, d_isolated, d_noncritical,
	        d_critical, d_icu, d_unhospitalized, d_recovered, d_dead)

# Like SEIR, but moves 15% of the "recovered" into the hospital for an average length hospital stay
# https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology
class HospitalFullModel:
	def __init__(self):
		self.r0 = 2.65
		self.total_days = 0
		self.population = POP_DENVERMETRO - 1

		self.susceptible = ProbState(period=0, count=self.population)
		self.incubating = ProbState(period=3)
		self.infectious = ProbState(period=3.8, count=1)
		self.isolated = ProbState(period=14)
		self.unhospitalized = ProbState(period=14)
		self.h_noncritical = ProbState(period=8)
		self.h_critical = ProbState(period=6)
		self.h_icu = ProbState(period=10)
		self.recovered = ProbState(period=10000)
		self.dead = ProbState(period=10000)

		self.incubating.add_exit_state(self.infectious, 1)
		self.incubating.normalize_states_over_period()

		self.isolated.add_exit_state(self.recovered, 1)
		self.isolated.normalize_states_over_period()

		self.unhospitalized.add_exit_state(self.recovered, .25)
		self.unhospitalized.add_exit_state(self.dead, .75)
		self.unhospitalized.normalize_states_over_period()

		self.infectious.add_exit_state(self.isolated, .85)
		self.infectious.add_exit_state(self.h_noncritical, .11)
		self.infectious.add_exit_state(self.h_critical, .4)
		self.infectious.normalize_states_over_period()

		self.h_noncritical.add_exit_state(self.recovered, 1)
		self.h_noncritical.normalize_states_over_period()

		self.h_critical.add_exit_state(self.recovered, 1)
		self.h_critical.normalize_states_over_period()

		self.h_icu.add_exit_state(self.recovered, .75)
		self.h_icu.add_exit_state(self.dead, .25)
		self.h_icu.normalize_states_over_period()

	def reset(self):
		self.total_days = 0
		self.susceptible.reset()
		self.susceptible.count = self.population - 1
		self.incubating.reset()
		self.infectious.reset()
		self.infectious.count = 1
		self.isolated.reset()
		self.unhospitalized.reset()
		self.h_noncritical.reset()
		self.h_critical.reset()
		self.h_icu.reset()
		self.recovered.reset()
		self.dead.reset()

	def set_r0(self, value):
		self.r0 = value

	def set_mean_generation_days(self, value):
		self.dayspergen = value

	def set_population(self, value):
		self.population = value

	def recalculate(self):
		self.beta = self.r0 / self.infectious.period

	def run_period(self, days):
		time_domain = np.linspace(0, days, days + 1)
		# Initial conditions vector

		init = (self.susceptible.count,
			self.incubating.count,
			self.infectious.count,
			self.isolated.count,
			self.h_noncritical.count,
			self.h_critical.count,
			self.h_icu.count,
			self.unhospitalized.count,
			self.recovered.count,
			self.dead.count)
		print(f"{init}")
		# Integrate the SIR equations over the time grid, t.
		results = odeint(deriv_seirh, init, time_domain, args=(self,))
		(d_susceptible, d_incubating, d_infectious, d_isolated, d_noncritical,
		 d_critical, d_icu, d_unhospitalized, d_recovered, d_dead) = results.T
		self.total_days += days
		self.susceptible.extend(d_susceptible)
		self.incubating.extend(d_incubating)
		self.infectious.extend(d_infectious)
		self.isolated.extend(d_isolated)
		self.h_noncritical.extend(d_noncritical)
		self.h_critical.extend(d_critical)
		self.h_icu.extend(d_icu)
		self.unhospitalized.extend(d_unhospitalized)
		self.recovered.extend(d_recovered)
		self.dead.extend(d_dead)


	def run_period2(self, days):
		time_domain = np.linspace(0, days, days + 1)

		# Integrate the SIR equations over the time grid, t.
		for _ in range(0, days):
			self.step_day()


	def run_r0_set(self, date_offsets, r0_values):
		self.reset()

		prev_date = 0
		for itr in range(0, len(date_offsets)):
			self.set_r0(r0_values[itr])
			self.recalculate()
			span = date_offsets[itr] - prev_date + 1
			self.run_period2(span)
			prev_date = date_offsets[itr]
			if len(self.unhospitalized.domain) != len(self.dead.domain):
				raise ValueError(f"oops, {len(self.unhospitalized.domain)} != {len(self.dead.domain)}")



	def step_day(self):
		new_infections = self.beta * self.susceptible.count * self.infectious.count / self.population

		(new_symptomatic,) = self.incubating.get_state_redist()
		new_isolated, new_noncritical, new_critical = self.infectious.get_state_redist()
		(recovered1,) = self.isolated.get_state_redist()
		(recovered2,) = self.h_noncritical.get_state_redist()
		(new_icu,) = self.h_critical.get_state_redist()
		recovered3, dead1 = self.h_icu.get_state_redist()
		recovered4, dead2 = self.unhospitalized.get_state_redist()

		d_susceptible = -new_infections
		d_incubating = new_infections - new_symptomatic
		d_infectious = new_symptomatic - (new_isolated + new_noncritical + new_critical)
		d_isolated = new_isolated - recovered1
		d_noncritical = new_noncritical - recovered2
		d_critical = new_critical - new_icu
		d_icu = new_icu - (recovered3 + dead1)
		d_unhospitalized = -(recovered4 + dead2)
		d_recovered = recovered1 + recovered2 + recovered3 + recovered4
		d_dead = dead1 + dead2

		(d_noncritical, d_critical, d_icu, d_unhospitalized) = adjust_for_overload(
			self.h_noncritical.count, self.h_critical.count, self.h_icu.count,
			d_noncritical, d_critical, d_icu, d_unhospitalized)
		balances = (d_susceptible + d_incubating + d_infectious + d_isolated + d_noncritical + d_critical + \
				d_icu + d_unhospitalized + d_recovered + d_dead)
		if int(balances) != 0:
			raise ValueError(f"balances {balances} != 0")

		self.susceptible.adjust(d_susceptible)
		self.incubating.adjust(d_incubating)
		self.infectious.adjust(d_infectious)
		self.isolated.adjust(d_isolated)
		self.h_noncritical.adjust(d_noncritical)
		self.h_critical.adjust(d_critical)
		self.h_icu.adjust(d_icu)
		self.unhospitalized.adjust(d_unhospitalized)
		self.recovered.adjust(d_recovered)
		self.dead.adjust(d_dead)
		self.total_days += 1




def test():
	model = HospitalFullModel()
	model.set_population(POP_DENVERMETRO)

	date_offsets = [30, 45, 53, 60, 68, 159]
	r0_values = [BASE_R0, BASE_R0 - .2, BASE_R0 - .5, BASE_R0 - 1, 1.55, 1.55]

	model.run_r0_set(date_offsets, r0_values)

	u_susc = model.susceptible.domain
	u_incu = model.incubating.domain
	u_infe = model.infectious.domain
	u_isol = model.isolated.domain
	u_h_no = model.h_noncritical.domain
	u_h_cr = model.h_critical.domain
	u_h_ic = model.h_icu.domain
	u_unho = model.unhospitalized.domain
	u_reco = model.recovered.domain
	u_dead = model.dead.domain

	time_domain = np.linspace(0, model.total_days, model.total_days + 1)
	hospitalized = []
	for itr in range(0, len(u_h_cr)):
		hospitalized.append(u_h_no[itr] + u_h_cr[itr] + u_h_ic[itr])

	fig = plt.figure(facecolor='w')
	# ax = fig.add_subplot(111, axis_bgcolor='#dddddd', axisbelow=True)
	ax = fig.add_subplot(111, axisbelow=True)
	ax.plot(time_domain, u_susc, color=(0, 0, 1), alpha=.5, lw=2, label='Susceptible', linestyle='-')
	ax.plot(time_domain, u_incu, color=TABLEAU_ORANGE, alpha=0.1, lw=2, label='Exposed', linestyle='-')
	ax.plot(time_domain, u_infe, color=TABLEAU_RED, alpha=0.5, lw=2, label='Infected', linestyle='-')
	ax.plot(time_domain, u_isol, color=TAB_COLORS[8], alpha=.5, lw=2, label='Home Iso', linestyle='-')
	ax.plot(time_domain, u_h_no, color=TAB_COLORS[10], alpha=.5, lw=2, label='Hosp Noncrit', linestyle=':')
	ax.plot(time_domain, u_h_cr, color=TAB_COLORS[12], alpha=.5, lw=2, label='Hosp Crit', linestyle=':')
	ax.plot(time_domain, u_h_ic, color=(1, 0, 0), alpha=.5, lw=2, label='ICU', linestyle=':')
	ax.plot(time_domain, hospitalized, color=(1, 0, 0), alpha=1, lw=2, label='Total Hospitalized', linestyle='-')
	ax.plot(time_domain, u_unho, color=(.5, .5, .5), alpha=1, lw=2, label='Not hospitalized', linestyle='-')
	ax.plot(time_domain, u_reco, color=(0, .5, 0), alpha=.5, lw=2, label='Recovered', linestyle='--')
	ax.plot(time_domain, u_dead, color=(0, 0, 0), alpha=.5, lw=2, label='Dead', linestyle='--')

	ax.set_xlabel('Days')
	ax.set_ylabel('Number')

	chart_title = f"COVID-19 20k bed cap projection\nDenver County | Variable R0"
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
	test()
