# global settings
set terminal png
set termoption enhanced
set grid

# settings for plotting experiment3 throughput
set output "exp3-thp.png"
set title "Experiment 3 - Throughput"
set xlabel "Time (second)"
set xrange [0:75]
set ylabel "Bandwidth (Mbps)"
set yrange [0:]
plot "Report3_brandwidth_Reno_DropTail" with lines smooth bezier title "Reno DropTail", \
     "Report3_brandwidth_Reno_RED" with lines smooth bezier title "Reno RED", \
     "Report3_brandwidth_SACK_DropTail" with lines smooth bezier title "Sack DropTail", \
     "Report3_brandwidth_SACK_RED" with lines smooth bezier title "Sack RED"
unset output

# settings for plotting experiment3 latency
set output "exp3-lt.png"
set title "Experiment 3 - Latency"
set xlabel "Time (second)"
set xrange [0:75]
set ylabel "Latency (ms)"
set yrange [0:1000]
plot "Report3_delay_Reno_DropTail" title "Reno DropTail" with lines smooth bezier, \
     "Report3_delay_Reno_RED" title "Reno RED" with lines smooth bezier, \
     "Report3_delay_SACK_DropTail" title "Sack DropTail" with lines smooth bezier, \
     "Report3_delay_SACK_RED" title "Sack RED" with lines smooth bezier
unset output