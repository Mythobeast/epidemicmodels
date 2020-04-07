




def main():
	random.seed()

	scenarios = []
	for itr in range(0, 100):
		scenarios.append(create_random_scenario())

	ideal =

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
