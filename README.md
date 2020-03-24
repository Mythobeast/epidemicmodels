# Epidemic Models

- calculates SIR, SEIR, and an extended model that includes some hospital capacities and outcomes
- outputs results as graph as PNG and data as CSV
- can run time-series subsets of R0 values to model social distancing effects
- extensible statistical model to allow finer differentiation of prognosis states
- can be used to model sub-populations

# Usage

  pip install -r requirements.txt
  python sierbedmodel.py
  
Each of the models is designed to be run independently. For early models (pre scenariodriven.py), assumptions can be adjusted in constants.py,  New visualizations of results can be derived from the example executable.

As of scenariodriven.py, assumptions can be adjusted in scenario1.json. Configuration options will continue to expand as we add them.

seirbedmodel.py: breaks the “recovered” period into hospitalization times to identify capacity requirements

# Description

These models originated as SIR and SEIR based models that used Python's differential equations models in order to generate curves. This method is still embodied in the sirmodel.py and seirmodel.py files.

When attempting to deal with branching, standard differential equations proved inadequate, so we switched to a Markov chain model. The math works out identically, but this allows for finer grained outcome tracking. 

# Assumption generation

## Population

There is some question about how much of the front range needs to be considered in this model. The population described in scenario1.json (737855) presumes that Denver Health is the only hospital in Denver County, which is a shortcut that we took so that we could work on the implementation details.

A survey of the hospitals along the [[Front Range Urban Corrodor|https://en.wikipedia.org/wiki/Front_Range_Urban_Corridor]] indicates 10691 hospital beds for a population of 4,976,781. Denver Health's current reported beds is 457, ignoring surge capacity, or 4.27% of the total capacity, giving the Denver Health share of the responsibility as 212739. If you divide the total ICU bed count by DH's ICU bed count (1033 / 77), then DH's share is 370970.

## Time of outbreak

Due to poor testing, we are having to use this model to identify when initial infection reached Colorado. Estimates we have seen vary from the end of January to the beginning of March.

## R0 and social distancing

This is by far the hardest metric to identify. Our model involves a variable R0, adjustable on a daily basis based on the effects of social distancing. We are considering several models for this, and will perform statistical fitting to identify which values are most probable.

The best available measurements from Wuhan and Italy suggest an R0 between 3.8 and 4.2 before quarantine was established. (citation needed) Social distancing is being modeled as offsets from a default 3.8. Hard quarantine in Wuhan is reported to have dropped the R0 below 1.0.





