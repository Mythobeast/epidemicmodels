

BASE_R0 = 3.8

# Total population, N.
#dola denver est 2020 (july) 737855\
POP_DENVER = 737855
POP_DENVERMETRO = 2932415
POP_COLORADO_SPRINGS = 668000
POP_WELD_COUNTY = 305274

# Age group enumeration
AGE0x = '0-9'
AGE1x = '10-19'
AGE2x = '20-29'
AGE3x = '30-39'
AGE4x = '40-49'
AGE5x = '50-59'
AGE6x = '60-69'
AGE7x = '70-79'
AGE8x = '80+'

# From: https://demography.dola.colorado.gov/population/
AGE_DISTRIBUTION = {
	AGE0x: .1184998,
	AGE1x: .1310645,
	AGE2x: .1461177,
	AGE3x: .1456213,
	AGE4x: .1303838,
	AGE5x: .1266992,
	AGE6x: .1090715,
	AGE7x: .0612498,
	AGE8x: .0312923
}

# Imperial College Data: Age based prognoses and outcomes
# from  https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf?fbclid=IwAR1D9-CBinlhc9glEyn4-oGjPNtOl4a4CkUp5Q9J2CBO8xVvidq9srwi8P0
# hosp_rate is the portion of those showing symptoms who must be hospitalized
# crit_rate is the portion of those identified above who require critical care
# fatality is the portion of those showing symptoms who will die
ICD = {
	AGE0x: { 'hosp_rate': .001, 'crit_rate': .05,  'fatality': .00002 },
	AGE1x: { 'hosp_rate': .003, 'crit_rate': .05,  'fatality': .00006 },
	AGE2x: { 'hosp_rate': .012, 'crit_rate': .05,  'fatality': .0003 },
	AGE3x: { 'hosp_rate': .032, 'crit_rate': .05,  'fatality': .0008 },
	AGE4x: { 'hosp_rate': .049, 'crit_rate': .063, 'fatality': .0015 },
	AGE5x: { 'hosp_rate': .102, 'crit_rate': .122, 'fatality': .006 },
	AGE6x: { 'hosp_rate': .166, 'crit_rate': .274, 'fatality': .022 },
	AGE7x: { 'hosp_rate': .243, 'crit_rate': .432, 'fatality': .051 },
	AGE8x: { 'hosp_rate': .273, 'crit_rate': .709, 'fatality': .093 }
}

# This class uses IC information to populate state-change percentages
class SubgroupRates:
	def __init__(self, icd, pop_dist):
		self.pop_dist = pop_dist
		self.isolate = 1 - icd['hosp_rate']
		self.h_crit = icd['hosp_rate'] * icd['crit_rate']
		self.h_noncrit = icd['hosp_rate'] - self.h_crit
		self.icu_deathrate = icd['fatality'] / self.h_crit
		self.icu_recovery_rate = 1 - self.icu_deathrate

AGE_BASED_RATES = {
	AGE0x: SubgroupRates(ICD[AGE0x], AGE_DISTRIBUTION[AGE0x]),
	AGE1x: SubgroupRates(ICD[AGE1x], AGE_DISTRIBUTION[AGE1x]),
	AGE2x: SubgroupRates(ICD[AGE2x], AGE_DISTRIBUTION[AGE2x]),
	AGE3x: SubgroupRates(ICD[AGE3x], AGE_DISTRIBUTION[AGE3x]),
	AGE4x: SubgroupRates(ICD[AGE4x], AGE_DISTRIBUTION[AGE4x]),
	AGE5x: SubgroupRates(ICD[AGE5x], AGE_DISTRIBUTION[AGE5x]),
	AGE6x: SubgroupRates(ICD[AGE6x], AGE_DISTRIBUTION[AGE6x]),
	AGE7x: SubgroupRates(ICD[AGE7x], AGE_DISTRIBUTION[AGE7x]),
	AGE8x: SubgroupRates(ICD[AGE8x], AGE_DISTRIBUTION[AGE8x])
}





## Make Pretty

# These are the "Tableau 20" colors as RGB.
tableau20 = [
		(31, 119, 180),
		(174, 199, 232),
		(255, 127, 14),
		(255, 187, 120),
		(44, 160, 44),
		(152, 223, 138),
		(214, 39, 40),
		(255, 152, 150),
		(148, 103, 189),
		(197, 176, 213),
		(140, 86, 75),
		(196, 156, 148),
		(227, 119, 194),
		(247, 182, 210),
		(127, 127, 127),
		(199, 199, 199),
		(188, 189, 34),
		(219, 219, 141),
		(23, 190, 207),
		(158, 218, 229)
]


TAB_COLORS = [
		(0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
		(0.6823529411764706, 0.7803921568627451, 0.9098039215686274),
		(1.0, 0.4980392156862745, 0.054901960784313725),
		(1.0, 0.7333333333333333, 0.47058823529411764),
		(0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
		(0.596078431372549, 0.8745098039215686, 0.5411764705882353),
		(0.8392156862745098, 0.15294117647058825, 0.1568627450980392),
		(1.0, 0.596078431372549, 0.5882352941176471),
		(0.5803921568627451, 0.403921568627451, 0.7411764705882353),
		(0.7725490196078432, 0.6901960784313725, 0.8352941176470589),
		(0.5490196078431373, 0.33725490196078434, 0.29411764705882354),
		(0.7686274509803922, 0.611764705882353, 0.5803921568627451),
		(0.8901960784313725, 0.4666666666666667, 0.7607843137254902),
		(0.9686274509803922, 0.7137254901960784, 0.8235294117647058),
		(0.4980392156862745, 0.4980392156862745, 0.4980392156862745),
		(0.7803921568627451, 0.7803921568627451, 0.7803921568627451),
		(0.7372549019607844, 0.7411764705882353, 0.13333333333333333),
		(0.8588235294117647, 0.8588235294117647, 0.5529411764705883),
		(0.09019607843137255, 0.7450980392156863, 0.8117647058823529),
		(0.6196078431372549, 0.8549019607843137, 0.8980392156862745)
	]


TABLEAU_BLUE = TAB_COLORS[0]
TABLEAU_ORANGE = TAB_COLORS[2]
TABLEAU_GREEN = TAB_COLORS[4]
TABLEAU_RED = TAB_COLORS[6]
