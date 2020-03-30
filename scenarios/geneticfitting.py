
import math
import random
from datetime import datetime, timedelta
from operator import attrgetter
from scenario import EpiScenario
from scenariodriven import ScenarioDrivenModel

FIT_START = datetime(2020, 3, 18)
FIT_END = datetime(2020, 3, 27)
HOSP_FIT = [38, 44, 58, 58, 72, 84, 148, 176, 239, 274]
DEAD_FIT = [2, 4, 5, 6, 7, 11, 19, 24, 31, 44]

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

	ideal = dict()
	ideal['start'] = FIT_START
	ideal['end'] = FIT_END
	ideal['hospitalized'] = HOSP_FIT
	ideal['deceased'] = DEAD_FIT

	print(f"Scenario {scenarios[0]}")
	for itr in range(0, RUNCOUNT):
		print(f"Running itr {itr}")
		for scen in scenarios:
			model = ScenarioDrivenModel(scen)
			model.run()
			model.gather_sums()
			model.calculate_fit(ideal)

		scenarios = sorted(scenarios, key=attrgetter('fitness'))
		if itr % 100 == 0:
			scenarios[0].save_results(itr)
		new_scenarios = []
		for itr in range(0, 9):
			this_scen = scenarios[itr]
			new_scenarios.append(this_scen)
			# Add nine motations for each best
			for subitr in range(0, 9):
				new_scenarios.append(mutate_scenario(this_scen))
		scenarios = new_scenarios


if __name__ == '__main__':
	main()



