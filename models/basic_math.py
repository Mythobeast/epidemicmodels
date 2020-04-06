


def calc_beta(r0, periods_infectious):
	return r0 / periods_infectious

def calc_infected(total_pop, beta, susceptible, infected):
	base_infected = beta * infected
	immunity_factor = susceptible / total_pop
	return base_infected * immunity_factor
