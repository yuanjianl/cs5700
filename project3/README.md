####README for [Project3](http://david.choffnes.com/classes/cs4700fa14/project3.php)####

All .tcl scripts, Java and python files we used to parse the results 
are in current folder ./

paper.pdf can be found under current folder ./

All experiment reports can be found in report/

The gnuplots scripts, experiment figures can be found under paper/plot

We used latex to write the paper, the paper.tex can be found under paper/




Approach:
In order to calculate throughput and latency over time, we records the 
number of packets/bytes sent and latency for all those packets during a 
short period of time. Then throughput can be known by dividing sent 
bytes with time, while latency is dividing total latency by number of 
pakects.

Problems have met:
In experiment 3, we have a very large file to be manipulated, which is 
the output of NS-2’s trace file. It’s get codes crushed if we only use 
one String parameter to store the manipulation output. Instead, we 
read the trace file line by line and append manipulation to a output 
file.

