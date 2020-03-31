

# % who show up at the hospital
# % of ED who will never see ICU
# % of ED who go straight to ICU (can math pre-icu from this and above)
# % of ICU who need vent (can math non-vent from this)
# % of ICU who die (can math post-icu from this)

class SubgroupRates:
	def __init__(self, icd, pop_dist):
		self.pop_dist = pop_dist
		self.p_selfisolate  = 1 - icd['p_hospitalized']

		self.p_ed_to_icu    = icd['p_hospitalized'] * icd['p_urgent_icu']
		admitted_to_floor = 1 - icd['p_urgent_icu']
		self.p_ed_to_floor  = icd['p_hospitalized'] * admitted_to_floor

		self.p_nevercrit    = icd['p_noncrit'] / admitted_to_floor
		self.p_floor_to_icu = 1 - self.p_nevercrit

		self.p_icu_vent     = icd['p_icu_vent']
		self.p_icu_nonvent  = 1 - self.p_icu_vent
		self.p_icu_death    = icd['p_icu_death']
		self.p_icu_recovery = 1 - self.p_icu_death
