# Epidemic Models


- calculates SIR, SEIR, and an extended model that includes some hospital capacities and outcomes
- outputs results as graph as PNG and data as CSV
- can run time-series subsets of R0 values to model social distancing effects
- extensible statistical model to allow finer differentiation of prognosis states
- can be used to model sub-populations
 
sirmodel.py: Just what you’d expect
seirmodel.py: adds in incubation delay
seirbedmodel.py: breaks the “recovered” period into hospitalization times to identify capacity requirements
extendedmodel.py: models hospital capacity concerns
