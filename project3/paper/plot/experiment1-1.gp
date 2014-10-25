# global settings for experiment1
set terminal png
set termoption enhanced
set grid

# settings for plotting experiment1 throughput
set output "exp1-thp.png"
set title "Experiment 1 - Average Throughput"
set xlabel "CBR (Mbps)"
set ylabel "Average Throughput (MB)"
set xrange[5:10.5]
set yrange[0:]
plot "Report1_throughput" using 1:2 with lines smooth bezier title "Tahoe", \
     "Report1_throughput" using 1:3 with lines smooth bezier title "Reno", \
     "Report1_throughput" using 1:4 with lines smooth bezier title "NewReno", \
     "Report1_throughput" using 1:5 with lines smooth bezier title "Vegas"
unset output

# settings for plotting experiment1 drop rate
set output "exp1-dr.png"
set title "Experiment 1 - Average Packets Drop Rate"
set xlabel "CBR (Mbps)"
set ylabel "Average Packets Drop Rate (Percentage)"
set xrange[5:10.5]
set yrange[0:100]
plot "Report1_droprate" using 1:2 with lines smooth bezier title "Tahoe", \
     "Report1_droprate" using 1:3 with lines smooth bezier title "Reno", \
     "Report1_droprate" using 1:4 with lines smooth bezier title "NewReno", \
     "Report1_droprate" using 1:5 with lines smooth bezier title "Vegas"
unset output

# settings for plotting experiment1 latency
set output "exp1-lt.png"
set title "Experiment 1 - Average Latency"
set xlabel "CBR (Mbps)"
set ylabel "Average Latency (ms)"
set xrange[5:10.5]
set yrange[0:3000]
plot "Report1_delay" using 1:2 with lines smooth bezier title "Tahoe", \
     "Report1_delay" using 1:3 with lines smooth bezier title "Reno", \
     "Report1_delay" using 1:4 with lines smooth bezier title "NewReno", \
     "Report1_delay" using 1:5 with lines smooth bezier title "Vegas"
unset output
