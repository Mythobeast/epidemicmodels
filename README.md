# Epidemic Models

## Release Notes

###  4/7/2020
* Genetic algorithm added for identifying periodic reproductive numbers in existing data
* Reorganized into subdirectories

### Initial (3/15/2000)
* seirbedmodel.py breaks the “recovered” period into hospitalization times to identify capacity requirements
* calculates SIR, SEIR, and an extended model that includes some hospital capacities and outcomes
* outputs results as graph as PNG and data as CSV
* Scenario/config file driven to facilitate multiple projections
* can run time-series subsets of R0 values to model social distancing effects
* extensible statistical model to allow finer differentiation of prognosis states
* can be used to model sub-populations

# Usage

    pip install -r requirements.txt
    python sierbedmodel.py

For early models (pre scenariodriven.py), assumptions can be adjusted in constants.py.

As of scenariodriven.py, assumptions can be adjusted in ga_fit.json. Configuration options will
expand as needed.


# Description

These models originated as SIR and SEIR based models that used Python's differential
equations models in order to generate curves. This method is still embodied in the
sirmodel.py and seirmodel.py files.

When attempting to deal with branching, standard differential equations proved
inadequate, so we switched to a Markov chain model. The math works out identically,
but this allows for finer grained outcome tracking.

Note: R0 for a period should be called R1, but I keep getting pushback when I use that.

# Scenario files

Scenario files are configuration for scenariodriven.py. Samples can be found in gaseed.json and ga_fit.json.

**modelname** : Goes at the top of the chart, and used for file names  
**totalpop**: How many people in your population  
**incubation_period**: Average period for infected, but not infectious  
**prediagnosis_period**: Average period for infectiousness  
**chart_min**: Reserved for future features  
**chart_period**: How many days out to project  
**initial_date**: When do you think first infection occurred?  
**initial_r0**: R0 at outset of outbreak  
**r0_shifts**: Used for describing when the R1 shifts. Specify the date of the shift and the new value.  
**initial_values**: Used to intialize basic SEIR values if you wish to simulate after day 0.  
**age_distribution**: Proportion of your population in each age group. Used to distribute infected.
**age_projection**: Expected outcomes for each age group, used to inform hospital paths.

### Notes
* incubation_period + (prediagnosis_period/2) should be equal to your mean cycle time.
* All initial values should add up to the totalpop
* Values are initialized to Colorado specific values. You'll want to look up your own demographics
* Age projections are derived from "[Impact of non-pharmaceutical interventions (NPIs) to reduce COVID19 mortality and healthcare demand](https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf)"

# Genetic algorithm

geneticfitting.py uses a least square fitness test over a thousand generations to generate
r0 values that fit a known infection pattern. It's currently configured to run this
fitting on total hospitalized and total deaths, but can be adjusted to compare a curve
to any of the numbers generated in the SEIR or hospital bed models.

gaseed.json is a scenario file (described above) used to define initial conditions for the
genetic mutations. Total population R0 shift dates are kept constant, but initial date and
all R0 values will be initially randomized and then mutated with each generation.

R0 shift dates are retained, allowing you to specify when social distancing measures were implemented.

The results of each generation are compared to actual data found in fitset.py via least squares.
Replace COLORADO_ACTUAL with your own actual data, then search and replace COLORADO_ACTUAL in the source code
with whatever variable name you come up with.

Initially it will randomly create 100 scenarios and score each of them. The ten lowest scores will be
kept and each mutated nine times, refilling up to 100 scenarios. Additionally, it will create 10 more random scenarios.

Initialization and mutation are both specified in geneticfitting.py. You will probably want to alter
MINDATE and MAXDATE so that random dates for initial outbreak will fall within your suspected range.

# Assumption generation

## Population

There is some question about how much of the front range needs to be considered in this model. The population described in scenario1.json (737855) presumes that Denver Health is the only hospital in Denver County, which is a shortcut that we took so that we could work on the implementation details.

A survey of the hospitals along the [[Front Range Urban Corrodor|https://en.wikipedia.org/wiki/Front_Range_Urban_Corridor]] indicates 10691 hospital beds for a population of 4,976,781. Denver Health's current reported beds is 457, ignoring surge capacity, or 4.27% of the total capacity, giving the Denver Health share of the responsibility as 212739. If you divide the total ICU bed count by DH's ICU bed count (1033 / 77), then DH's share is 370970.

## Time of outbreak

Due to poor testing, we are having to use this model to identify when initial infection reached Colorado. Estimates we have seen vary from the end of January to the beginning of March.

## R0 and social distancing

This is by far the hardest metric to identify. Our model involves a variable R0, adjustable on a daily basis based on the effects of social distancing. We are considering several models for this, and will perform statistical fitting to identify which values are most probable.

The best available measurements from Wuhan and Italy suggest an R0 between 3.8 and 4.2 before quarantine was established. (citation needed) Social distancing is being modeled as offsets from a default 3.8. Hard quarantine in Wuhan is reported to have dropped the R0 below 1.0.

## Incubation period and prediagnisis period

These values should be researched in order to identify the most recent findings. Mean cycle times have been
identified that are significantly shorter than the time to first symptoms.

# Suggested reading

https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf  
https://www.medrxiv.org/content/10.1101/2020.03.14.20035873v1.full.pdf  
https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30144-4/fulltext  
https://www.medrxiv.org/content/10.1101/2020.03.14.20036202v1.full.pdf  
https://www.medrxiv.org/content/10.1101/2020.03.05.20030502v1.full.pdf  
https://wwwnc.cdc.gov/eid/article/26/6/20-0357_article




