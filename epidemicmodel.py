
from constants import *

class EpidemicModel:
	#Initialized for COVID-19
	def __init__(self):
		self.population = POP_DENVER
		self.dayspergen = 6.8
		self.r0 = 2.65

		self.susceptible = self.population - 1
		self.infected = 1
		self.recovered = 0

		# Infections caused while infected
		self.beta = self.r0 / self.dayspergen
		# Recoveries of infected per day
		self.gamma = 1.0 / self.dayspergen
		self.total_days = 0

		self.S_domain = []
		self.I_domain = []
		self.R_domain = []

	def reset(self):
		self.susceptible = self.population - 1
		self.infected = 1
		self.recovered = 0
		self.total_days = 0
		self.S_domain = []
		self.I_domain = []
		self.R_domain = []

	def set_r0(self, value):
		self.r0 = value

	def set_mean_generation_days(self, value):
		self.dayspergen = value

	def set_population(self, value):
		self.population = value

	def set_infected(self, value):
		self.infected = value

	def set_recovered(self, value):
		self.recovered = value
