#Create a simulator object
set ns [new Simulator]

# TCP kind
set variant [lindex $argv 0]
# CBR rate
set rate [lindex $argv 1]

#Open the trace file (before you start the experiment!)
set tf [open my_experimental1_output_${variant}_${rate}.tr w]
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
if {$variant eq "Tahoe"} {
    set tcp [new Agent/TCP]
} elseif {$variant eq "Reno"} {
    set tcp [new Agent/TCP/Reno]
} elseif {$variant eq "NewReno"} {
    set tcp [new Agent/TCP/Newreno]
} elseif {$variant eq "Vegas"} {
    set tcp [new Agent/TCP/Vegas]
}

$tcp set class_ 1
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink

#setup a FTP Application
set ftp [new Application/FTP]
$ftp attach-agent $tcp


#Schedule events for the CBR and TCP agents
$ns at 0.0 "$cbr start"
$ns at 0.0 "$ftp start"
$ns at 10.0 "$cbr stop"
$ns at 10.0 "$ftp stop"

$ns at 10.0 "finish"

#Print CBR packet size and interval
# puts "CBR packet size = [$cbr set packet_size_]"
# puts "CBR interval = [$cbr set interval_]"

#Run the simulation
$ns run







