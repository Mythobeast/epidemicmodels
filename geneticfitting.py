
import math
import random
from datetime import datetime, timedelta
from operator import attrgetter
from scenario import EpiScenario
from scenariodriven import ScenarioDrivenModel

RUNCOUNT = 1000

def random_r0():
	return random.random() * 5.0

def random_start_date():
	date_offset = int(math.floor(random.random() * 40))
	base_date = datetime(2020, 2, 14)
	return base_date + timedelta(date_offset)

def create_random_scenario():
	retval = EpiScenario('scenario1.json')
	random_r0s = []
	for r0item in retval.r0_values:
		random_r0s.append(random_r0())
	retval.r0_values = random_r0s
	retval.initial_date = random_start_date()
	return retval

def mutate_scenario(scenario):
	retval = EpiScenario(scenario.parameters)
	print(f"Retval = {retval}")
	for itr in range(0, len(scenario.r0_values)):
		this_r0 = retval.r0_values[itr]
		adjust_max = this_r0 / 10
		adjustment = (random.random() * adjust_max) - (adjust_max/2)
		retval.r0_values[itr] += adjustment
	adjustment = int((random.random() * 6) - 3)
	retval.initial_date += timedelta(adjustment)
	return retval


def main():
	random.seed()

	scenarios = []
	for itr in range(0, 100):
		scenarios.append(create_random_scenario())

	print(f"Scenario {scenarios[0]}")
	for itr in range(0, RUNCOUNT):
		for scen in scenarios:
			model = ScenarioDrivenModel(scen)
			model.run()
			model.gather_sums()
			model.calculate_fit()

		outmodels = sorted(outmodels, key=attrgetter('fitness'))
		if itr % 100 == 0:
			outmodels[0].save_results(itr)
		scenarios = []
		for itr in range(0, 9):
			this_scen = outmodels[itr].scenario
			scenarios.append(this_scen)
			for itr in range(0, 9):
				scenarios.append(mutate_scenario(this_scen))


if __name__ == '__main__':
	main()



