
This package includes scripts to compute a robust formulation of a given combinatorial integer program. The methods are described in
the masters thesis 'Recycling valid inequalities for combinatorial optimization under budgeted uncertainty'.

The core is the script 'robustformulation.py' which contains all the necessary methods. All other scripts are only
helper/evaluation/test functionality. They can be used at ones own risk, and are not as thoroughly documented.  

A best practice for the usage of 'robustformulation.py' is described in the file 'usagetemplate.py'.
It is strongly adviced to use the scripts as it is demonstrated in this particular file. 

The file separation_approach is at the time a half ready demonstration of a separation approach based on recycled Cover Inequalities.

The folder 'test instances' contains several files to test the functionality of the methods on easily verifiable
examples. 

The folder 'evaluation' contains methods to analyze the quality of a given solution and contains the test machinery used for the
master's thesis. Most methods are strongly path dependant and must be adjusted for own use.

The file 'mappedqueue.py' is a priority queue taken from Edward L. Platt (https://github.com/elplatt/python-priorityq) and modified
a little to suffice the demands of this package. It is 'only' used for the DSatur algorithms, which are not part of the suggested functionality.

 