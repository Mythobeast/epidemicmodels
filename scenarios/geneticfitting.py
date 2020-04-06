
import json
import math
import random
from datetime import datetime, timedelta
from operator import attrgetter
from scenarios.scenario import EpiScenario
from scenarios.scenariodriven import ScenarioDrivenModel

from scenarios.fitset import COLORADO_ACTUAL

RUNCOUNT = 1001
DATEFORMAT = "%Y-%m-%d"
MINDATE = datetime(2020, 2, 14)
MAXDATE = datetime(2020, 3, 3)

def random_r0():
	return random.random() * 5.0

def random_start_date():
	datebredth = (MAXDATE - MINDATE).days
	date_offset = int(math.floor(random.random() * datebredth))
	return MINDATE + timedelta(date_offset)

def create_random_scenario():
	with open('gaseed.json') as fp:
		newparms = json.load(fp)
#	newparms['initial_r0'] = random_r0()
	for shift in newparms['r0_shifts']:
		shift['r0'] = random_r0()
	newparms['initial_date'] = random_start_date().strftime(DATEFORMAT)
	return EpiScenario(newparms)

def mutate_scenario(scenario):
	newparms = json.loads(json.dumps(scenario.parameters))

	this_r0 = newparms['initial_r0']
	adjust_max = this_r0 / 5
	adjustment = (random.random() * adjust_max) - (adjust_max/2)
	newparms['initial_r0'] += adjustment
	for shift in newparms['r0_shifts']:
		this_r0 = shift['r0']
		adjust_max = this_r0 / 5
		adjustment = (random.random() * adjust_max) - (adjust_max/2)
		shift['r0'] += adjustment
	current_init_dt = datetime.strptime(newparms['initial_date'], DATEFORMAT)
	adjustment = int((random.random() * 6) - 3)
	newparms['initial_date'] = (current_init_dt + timedelta(adjustment)).strftime(DATEFORMAT)
	return EpiScenario(newparms)

def run_scenario(scenario):
	model = ScenarioDrivenModel(scenario)
	model.run()
	model.gather_sums()
	model.scenario.calculate_fit(ideal)
	fitlist.append(model.scenario.fitness)



def main():
	random.seed()

	scenarios = []
	for itr in range(0, 100):
		scenarios.append(create_random_scenario())

	ideal = COLORADO_ACTUAL

	print(f"Scenario {scenarios[0]}")
	for iteration_counter in range(0, RUNCOUNT):
		print(f"Running itr {iteration_counter}")
		fitlist = []
		for scen in scenarios:
			model = ScenarioDrivenModel(scen)
			model.run()
			model.gather_sums()
			model.scenario.calculate_fit(ideal)
			fitlist.append(model.scenario.fitness)
		print(f"fitlist: {fitlist}")

#		print(f"First few = {scenarios[0].serial}:{scenarios[0].fitness},{scenarios[1].serial}:{scenarios[1].fitness},{scenarios[2].serial}:{scenarios[2].fitness}")
		scenarios = sorted(scenarios, key=attrgetter('fitness'))
#		print(f"reordered few = {scenarios[0].serial}:{scenarios[0].fitness},{scenarios[1].serial}:{scenarios[1].fitness},{scenarios[2].serial}:{scenarios[2].fitness}")
		if iteration_counter % 100 == 0:
			for itr2 in range(0, 10):
				scenarios[itr2].save_results(iteration_counter + itr2)
		new_scenarios = scenarios[:9]
		for itr2 in range(0, 10):
			this_scen = new_scenarios[itr2]
			# Add nine motations for each best
			for _ in range(0, 10):
				new_scenarios.append(mutate_scenario(new_scenarios[0]))
		for itr2 in range(0, 10):
			new_scenarios.append(create_random_scenario())
		print(f"scen 50: {new_scenarios[50].initial_date} {new_scenarios[50].r0_values}")
		scenarios = new_scenarios


if __name__ == '__main__':
	main()



