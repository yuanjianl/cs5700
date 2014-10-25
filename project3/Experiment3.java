import java.util.Arrays;
import java.io.IOException;
import java.lang.InterruptedException;

public class Experiment3 extends Experiment {
	private String[] TCP_KIND = {"Reno", "SACK"};
	private String[] QUEUE_METHOD = {"DropTail", "RED"};
	private float tcp_start_time;
	private float tcp_end_time;
	private float cbr_start_time;
	private float cbr_end_time;
	private float indexTime;
	private float granuity = 0.5f;

	private int i = 0, j = 0;
	private int tcpLen = TCP_KIND.length;
	private int queLen = QUEUE_METHOD.length;
	private float[][] brandwidths;
	private float[][] delays;

	// To be used to record total number of packets received in a period of time
	private int totalPacketReceived;

	// To be used to record send time of each packet, initialize to -1.0f
	private float[] tcp_packet_sent_time;
	private float total_latency;

	// Constructor with given 4 arguments, which set TCP and CBR flow start/ end time
	public Experiment3(float tcp_start_time, float tcp_end_time, float cbr_start_time, float cbr_end_time) {
		this.indexTime = tcp_start_time + granuity;
		this.tcp_start_time = tcp_start_time;
		this.tcp_end_time = tcp_end_time;
		this.cbr_start_time = cbr_start_time;
		this.cbr_end_time = cbr_end_time;
		this.brandwidths = new float[Math.round((tcp_end_time - tcp_start_time) / granuity) - 1][2];
		this.delays = new float[Math.round((tcp_end_time - tcp_start_time) / granuity) - 1][2];
		initAllCaculatingValues();
	}

	// Initialize parameters clean up each time finish reading a file
	public void initAllCaculatingValues() {
		totalPacketReceived = 0;

		tcp_packet_sent_time = new float[ESTIMATED_TCP_PACKET_NUMBER];
		Arrays.fill(tcp_packet_sent_time, INIT_SENT_TIME);

		total_latency = 0.0f;
		// System.out.println("indexTime1: "+indexTime);
		indexTime = tcp_start_time + granuity;
		// System.out.println("indexTime1: "+indexTime);
	}

	public static void main(String[] args) {
		if(args.length != 4) {
			System.out.print("Arguments: TCP start time, TCP end time, CBR start time, CBR end time");
			System.exit(1);
		}
		Experiment3 ex3 = new Experiment3(Float.parseFloat(args[0]), Float.parseFloat(args[1]),
										  Float.parseFloat(args[2]), Float.parseFloat(args[3]));
		ex3.start();
	}

	public void start() {
		// Execute the script to generate the result files from NS
		for(i = 0; i < tcpLen; i++) {
			for(j = 0; j < queLen; j++) {
				String shellScript = "/course/cs4700f12/ns-allinone-2.35/bin/ns experiment3.tcl " + TCP_KIND[i] + " " + QUEUE_METHOD[j] + 
				" " + tcp_start_time + " " + tcp_end_time + " " + cbr_start_time + " " + cbr_end_time;
				try { 
					Runtime.getRuntime().exec(shellScript);
				} catch (IOException ex) {
					ex.printStackTrace();
				}
			}
		}

		// Wait for all traces are ready
		try {
			Thread.sleep(152222);
		} catch (InterruptedException ex) {
			ex.printStackTrace();
		}

		// Parse the results
		// Here we have the problem with dealing the large experiment file. StringBuilder tends to get crush, so
		// we need to append the manipulation output each time after finish reading a line
		for (i = 0; i < tcpLen; i++) {
			for (j = 0; j < queLen; j++) {
				readFile("my_experimental3_output_" + TCP_KIND[i] + "_" + QUEUE_METHOD[j] + ".tr");
				for(int i = 0; i < brandwidths.length; i++) {
					StringBuilder brandwidthStr = new StringBuilder();
					StringBuilder delayStr = new StringBuilder();
					for(int j = 0; j < 2; j++) {
						brandwidthStr.append(brandwidths[i][j]).append(" ");
						delayStr.append(delays[i][j]).append(" ");
					}
					brandwidthStr.append("\n");
            		delayStr.append("\n");	
					Experiment.writeToFile("report/experiment3/Report3_brandwidth_"+TCP_KIND[this.i]+"_"+QUEUE_METHOD[this.j], brandwidthStr.toString());
        			Experiment.writeToFile("report/experiment3/Report3_delay_"+TCP_KIND[this.i]+"_"+QUEUE_METHOD[this.j], delayStr.toString());
				}
			}
		}		
	}

	// Caculate throughput and latency for each period of time
	public void caculateThroughputAndLatency(float timeIndex) {
		int index = Math.round((timeIndex - tcp_start_time) / granuity) - 1;
		int total_bytes = 1040 * totalPacketReceived;

		brandwidths[index][0] = timeIndex - granuity;		
		brandwidths[index][1] = (float) total_bytes / (granuity * 1000 * 1000);

		delays[index][0] = timeIndex - granuity;
		delays[index][1] = 1000 * total_latency / totalPacketReceived;
		// Increase the time limit
		indexTime += granuity;
 		total_latency = 0;
 		totalPacketReceived = 0;
	}

	public void getFeed (String line) {
		String[] trace = line.split(" ");
		if(trace.length < 10)
			return;

		String messageType = trace[MESSAGE_TYPE];
		if (messageType.equals(DEQUEUED) && trace[SENDER].equals("0")) {
			// This the case node 1 has sent out a packet
			float time = Float.parseFloat(trace[TIME]);
			int seqNum = Integer.parseInt(trace[trace.length - 2]);
			// If the current float[] array size is not big enough, double it.
			if(seqNum >= tcp_packet_sent_time.length) {
				increaseArraySize();
			}

			if(tcp_packet_sent_time[seqNum] == INIT_SENT_TIME) {
				tcp_packet_sent_time[seqNum] = time;
			}
 		} else if (messageType.equals(RECEIVED) && trace[RECEIVER].equals("0") && trace[PACKET_TYPE].equals(ACK)) {
 			// This is the case node 1 has received a ACK message for the packet he sent
 			float time = Float.parseFloat(trace[TIME]);
 			int seqNum = Integer.parseInt(trace[trace.length - 2]);

 			// If the sent time is -1.0, there is an error. Ignore it.
 			if(tcp_packet_sent_time[seqNum] != INIT_SENT_TIME) {
 				if (time < indexTime) {
 					total_latency += (time - tcp_packet_sent_time[seqNum]);
 					totalPacketReceived += 1;
 				} else{
 					// Number of successfully sent packets during the period has been recorded
 					caculateThroughputAndLatency(indexTime);
 				}
 				// System.out.println("totalPacketReceived: " + totalPacketReceived);
 			}
		}
	}

	// This funciton is called when more packets sent information need to be filled in the array, we double size it
	public void increaseArraySize () {
		float[] temp = new float[tcp_packet_sent_time.length * 2];
		Arrays.fill(temp, INIT_SENT_TIME);
		System.arraycopy(tcp_packet_sent_time, 0, temp, 0, tcp_packet_sent_time.length);
		tcp_packet_sent_time = temp;
	}

	// Each time finishing reading a file, all parameters need to initialized
	protected void result() {
		initAllCaculatingValues();
	}
}
