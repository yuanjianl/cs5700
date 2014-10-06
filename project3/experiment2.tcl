#Create a simulator object
set ns [new Simulator]

# TCP kind
set firstTCP [lindex $argv 0]
set secondTCP [lindex $argv 1]
# CBR rate
set rate [lindex $argv 2]

#Open the trace file (before you start the experiment!)
set tf [open my_experimental2_output_${firstTCP}_${secondTCP}_${rate}.tr w]
$ns trace-all $tf

# Close the trace file (after you finish the experiment!)
proc finish {} {
    global ns tf
    $ns flush-trace
    close $tf
    exit 0
}

#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n5 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Setup a CBR over UDP at N2, set a null at N3 and then connect them.
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp

set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null

set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp

$cbr set type_ CBR
$cbr set rate_ ${rate}mb

#Setup a TCP stream between N1 and N4.
if {$firstTCP eq "Tahoe"} {
    set tcp1 [new Agent/TCP]
} elseif {$firstTCP eq "Reno"} {
    set tcp1 [new Agent/TCP/Reno]
} elseif {$firstTCP eq "NewReno"} {
    set tcp1 [new Agent/TCP/Newreno]
} elseif {$firstTCP eq "Vegas"} {
    set tcp1 [new Agent/TCP/Vegas]
}
#The class is the flow_id in output.
$tcp1 set class_ 1
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1

#setup a FTP Application
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1


#Setup a TCP stream between N1 and N4.
if {$secondTCP eq "Tahoe"} {
    set tcp2 [new Agent/TCP]
} elseif {$secondTCP eq "Reno"} {
    set tcp2 [new Agent/TCP/Reno]
} elseif {$secondTCP eq "NewReno"} {
    set tcp2 [new Agent/TCP/Newreno]
} elseif {$secondTCP eq "Vegas"} {
    set tcp2 [new Agent/TCP/Vegas]
}
$tcp2 set class_ 2
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2

#setup a FTP Application
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2


#Schedule events for the CBR and TCP agents
$ns at 0.0 "$cbr start"
$ns at 0.0 "$ftp1 start"
$ns at 0.0 "$ftp2 start"
$ns at 10.0 "$cbr stop"
$ns at 10.0 "$ftp1 stop"
$ns at 10.0 "$ftp2 stop"

$ns at 10.0 "finish"

#Print CBR packet size and interval
# puts "CBR packet size = [$cbr set packet_size_]"
# puts "CBR interval = [$cbr set interval_]"

#Run the simulation
$ns run