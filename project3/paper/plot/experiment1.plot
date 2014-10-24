# global settings for experiment1
set terminal png
set termoption enhanced
set grid

# settings for plotting experiment1 throughput
set output "exp1-thp.png"
set title "Experiment 1 - Average Throughput"
set xlabel "CBR (Mbps)"
set ylabel "Average Throughput (MB)"
set xrange[1:]
set yrange[0:]
plot "../report/Report1_throughput" using 1 with lines smooth bezier title "Tahoe", \
     "../report/Report1_throughput" using 2 with lines smooth bezier title "Reno", \
     "../report/Report1_throughput" using 3 with lines smooth bezier title "NewReno", \
     "../report/Report1_throughput" using 4 with lines smooth bezier title "Vegas"
unset output

# settings for plotting experiment1 throughput
set output "exp1-thp-deviation.png"
set title "Experiment 1 - Deviation of Throughput"
set xlabel "CBR (Mbps)"
set ylabel "Deviation of Throught"
set yrange[0:0.05]
plot "throughput" using 1 with lines smooth bezier title "Tahoe", \
     "throughput" using 2 with lines smooth bezier title "Reno", \
     "throughput" using 3 with lines smooth bezier title "NewReno", \
     "throughput" using 4 with lines smooth bezier title "Vegas"
unset output

# settings for plotting experiment1 drop rate
set output "exp1-dr.png"
set title "Experiment 1 - Average Packets Drop Rate"
set xlabel "CBR (Mbps)"
set ylabel "Average Packets Drop Rate (Percentage)"
set yrange[0:100]
plot "../report/Report1_droprate" using 1 with lines smooth bezier title "Tahoe", \
     "../report/Report1_droprate" using 2 with lines smooth bezier title "Reno", \
     "../report/Report1_droprate" using 3 with lines smooth bezier title "NewReno", \
     "../report/Report1_droprate" using 4 with lines smooth bezier title "Vegas"
unset output

# settings for plotting experiment1 throughput
set output "exp1-dr-deviation.png"
set title "Experiment 1 - Deviation of Packets Drop Rate"
set xlabel "CBR (Mbps)"
set ylabel "Deviation of Packets Drop Rate"
set yrange[0:12]
plot "droprate" using 1 with lines smooth bezier title "Tahoe", \
     "droprate" using 2 with lines smooth bezier title "Reno", \
     "droprate" using 3 with lines smooth bezier title "NewReno", \
     "droprate" using 4 with lines smooth bezier title "Vegas"
unset output

# settings for plotting experiment1 latency
set output "exp1-lt.png"
set title "Experiment 1 - Average Latency"
set xlabel "CBR (Mbps)"
set ylabel "Average Latency (ms)"
set yrange[0:3000]
plot "../report/Report1_delay" using 1 with lines smooth bezier title "Tahoe", \
     "../report/Report1_delay" using 2 with lines smooth bezier title "Reno", \
     "../report/Report1_delay" using 3 with lines smooth bezier title "NewReno", \
     "../report/Report1_delay" using 4 with lines smooth bezier title "Vegas"
unset output

# settings for plotting experiment1 latency
set output "exp1-lt-deviation.png"
set title "Experiment 1 - Deviation of Latency"
set xlabel "CBR (Mbps)"
set ylabel "Deviation of Latency (ms)"
set yrange[0:3000]
plot "delay" using 1 with lines smooth bezier title "Tahoe", \
     "delay" using 2 with lines smooth bezier title "Reno", \
     "delay" using 3 with lines smooth bezier title "NewReno", \
     "delay" using 4 with lines smooth bezier title "Vegas"
unset output
